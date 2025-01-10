from flask import Flask, request, jsonify
from PIL import Image
import io
from model_utils import load_model, predict

app = Flask(__name__)

# Load model once at startup
model = load_model()

@app.route('/predict', methods=['POST'])
def handle_predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    image = Image.open(image_file.stream).convert('RGB')

    try:
        result = predict(model, image)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return open("index.html").read()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
