import os
import re
import argparse
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

import praw  # ✅ Reddit API
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# ---------------- Models ----------------
model = SentenceTransformer('all-MiniLM-L6-v2')

sentiment_pipeline = pipeline(
    'sentiment-analysis',
    model='cardiffnlp/twitter-roberta-base-sentiment-latest'
)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ---------------- Chroma setup (with persistence) ----------------
PERSIST_DIR = "./chroma_db"

vectorstore = Chroma(
    collection_name="Post",
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR,   # ✅ automatic persistence
    collection_metadata={"hnsw:space": "cosine"}
)

# ---------------- LangChain setup (Google Gemini) ----------------
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 20})
)

print("CLIENT_ID:", os.getenv("REDDIT_CLIENT_ID"))
print("CLIENT_SECRET:", os.getenv("REDDIT_CLIENT_SECRET"))
print("USER_AGENT:", os.getenv("REDDIT_USER_AGENT"))

# ---------------- Utils ----------------
def fetch_posts(niche, max_results=30):
    """Fetch posts from Reddit using praw"""
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),  # fixed key name
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )

    posts = []
    for submission in reddit.subreddit("all").search(niche, limit=max_results):
        posts.append({
            "id": submission.id,
            "text": submission.title + " " + (submission.selftext or ""),
            "created_at": datetime.utcfromtimestamp(
                submission.created_utc
            ).isoformat() + "Z",
            "metrics": submission.score
        })

    print(f"Fetched {len(posts)} Reddit posts for niche '{niche}'.")
    return posts


def chunk_text(text):
    """Split text into sentences for embedding"""
    return re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)


def index_posts(posts):
    """Index posts into Chroma"""
    texts, metadatas = [], []
    for post in posts:
        chunks = chunk_text(post['text'])
        for chunk in chunks:
            if chunk.strip():
                texts.append(chunk)
                metadatas.append({
                    "metrics": post.get("metrics", 0),
                    "created_at": post.get("created_at", "")
                })

    if texts:
        vectorstore.add_texts(texts=texts, metadatas=metadatas)
        print("Indexed posts successfully.")
    else:
        print("No texts to index.")


def query_vectorstore(niche):
    results = vectorstore.similarity_search(niche, k=20)
    return [
        {"text": doc.page_content, "metrics": doc.metadata.get("metrics", 0)}
        for doc in results
    ]


def add_sentiment(retrieved_posts):
    sentiment_counts = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
    for post in retrieved_posts:
        result = sentiment_pipeline(post['text'])[0]
        post['sentiment'] = result['label']
        if result['label'] == 'POSITIVE':
            sentiment_counts["POSITIVE"] += 1
        elif result['label'] == 'NEGATIVE':
            sentiment_counts["NEGATIVE"] += 1
        else:
            sentiment_counts["NEUTRAL"] += 1
    return retrieved_posts, sentiment_counts


def generate_trends(retrieved_posts):
    prompt = "Analyze sentiment and top trends from these posts: " + str(retrieved_posts)
    return qa_chain.invoke({"query": prompt})["result"]


def generate_ideas(trends):
    prompt = f"Generate 5 viral Reddit/X post ideas with captions and hashtags based on these trends: {trends}"
    return qa_chain.invoke({"query": prompt})["result"]


# ---------------- Main ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--niche", required=True)
    args = parser.parse_args()

    niche = args.niche
    try:
        posts = fetch_posts(niche)
        if not posts:
            print("No posts fetched. Check API key/quota.")
            exit(1)

        index_posts(posts)
        retrieved = query_vectorstore(niche)
        if not retrieved:
            print("No posts retrieved. Check indexing/query.")
            exit(1)

        retrieved_with_sent, sentiment_counts = add_sentiment(retrieved)
        trends = generate_trends(retrieved_with_sent)
        ideas = generate_ideas(trends)

        print("\nTrends/Insights:", trends)
        print("Sentiment Counts:", sentiment_counts)
        print("Generated Ideas:", ideas)

    except Exception as e:
        print("Error:", str(e))
