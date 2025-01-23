from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from rag_pipeline import fetch_posts, index_posts, query_vectorstore, add_sentiment, generate_trends, generate_ideas

load_dotenv()
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NicheRequest(BaseModel):
    niche: str

@app.post("/trends")
async def get_trends(request: NicheRequest):
    try:
        posts = fetch_posts(request.niche)
        if not posts:
            raise HTTPException(status_code=400, detail="No posts fetched. Check subreddit or API quota.")
        index_posts(posts)
        retrieved = query_vectorstore(request.niche)
        if not retrieved:
            raise HTTPException(status_code=400, detail="No posts retrieved from vector store.")
        retrieved_with_sent, sentiment_counts = add_sentiment(retrieved)
        trends = generate_trends(retrieved_with_sent)
        return {"trends": trends, "sentiment_counts": sentiment_counts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating trends: {str(e)}")

@app.post("/ideas")
async def get_ideas(request: NicheRequest):
    try:
        posts = fetch_posts(request.niche)
        if not posts:
            raise HTTPException(status_code=400, detail="No posts fetched. Check subreddit or API quota.")
        index_posts(posts)
        retrieved = query_vectorstore(request.niche)
        if not retrieved:
            raise HTTPException(status_code=400, detail="No posts retrieved from vector store.")
        retrieved_with_sent, sentiment_counts = add_sentiment(retrieved)
        trends = generate_trends(retrieved_with_sent)
        ideas = generate_ideas(trends)
        return {"ideas": ideas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating ideas: {str(e)}")