import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

# Dynamically define class labels from your dataset
# Replace this with your actual dataset loading code if running standalone
# For now, assuming you have access to dataset["train"]["label"] from your notebook
try:
    # If running in your notebook environment with 'dataset' defined
    CLASS_NAMES = sorted(set(dataset["train"]["label"]))  # Extract unique labels
except NameError:
    # Fallback: manually define class names if running standalone (adjust as needed)
    CLASS_NAMES = [
    "Actinic keratoses", "Basal cell carcinoma", "Benign keratosis-like lesions",
    "Chickenpox", "Cowpox", "Dermatofibroma", "Healthy", "HFMD", "Measles",
    "Melanocytic nevi", "Melanoma", "Monkeypox", "Squamous cell carcinoma", "Vascular lesions"
    ]  # Example placeholder
    print("Warning: Using placeholder class names. Replace with actual dataset labels.")

def load_model(path='vgg19_skin_disease.pth'):
    # Load VGG-19 architecture without pretrained weights
    model = models.vgg19(pretrained=False)
    
    # Modify the classifier to match the number of classes in your dataset
    model.classifier[6] = nn.Linear(4096, len(CLASS_NAMES))  # VGG-19's default in_features is 4096
    
    # Load the trained weights (use map_location for CPU/GPU compatibility)
    model.load_state_dict(torch.load(path, map_location=torch.device('cpu')))
    
    # Set model to evaluation mode
    model.eval()
    return model

def preprocess_image(image):
    # Define transformations matching your training setup for VGG-19
    transform = transforms.Compose([
        transforms.Resize((224, 224)),  # VGG-19 input size from your training
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                             std=[0.229, 0.224, 0.225])  # ImageNet stats from your training
    ])
    # Apply transform and add batch dimension
    return transform(image).unsqueeze(0)

def predict(model, image):
    # Preprocess the input image
    tensor = preprocess_image(image)
    
    # Run inference
    with torch.no_grad():
        output = model(tensor)
        _, predicted = torch.max(output, 1)  # Get index of the highest score
    
    # Return the predicted class name
    return CLASS_NAMES[predicted.item()]

# Example usage (optional, for testing)
if __name__ == "__main__":
    # Load the model
    model = load_model('vgg19_skin_disease.pth')
    
    # Load a sample image (replace with your image path)
    sample_image = Image.open("path_to_your_image.jpg").convert("RGB")
    
    # Predict
    prediction = predict(model, sample_image)
    print(f"Predicted class: {prediction}")