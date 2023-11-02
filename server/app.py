import os
import torch
from flask import Flask, request, jsonify, send_file, abort
from torchvision import transforms
from PIL import Image
from oml.models import ViTExtractor
from oml.registry.transforms import get_transforms_for_pretrained
from oml.inference.flat import inference_on_images
from oml.utils.misc_torch import pairwise_dist
import traceback

app = Flask(__name__)

# Load the pre-trained model
model = ViTExtractor.from_pretrained("vits16_inshop")
transform, im_reader = get_transforms_for_pretrained("vits16_inshop")
image_path  = "./image/"
tmp_path    = "./tmp/"


# Define the API endpoint
@app.route('/predict', methods=['POST'])
def predict():
    global model, transform, image_path
    
    file        = request.files['image']
    filename    = file.filename
    
    i = 1
    while os.path.exists(os.path.join(image_path, filename)):
        filename = f"{os.path.splitext(file.filename)[0]}_{i}{os.path.splitext(file.filename)[1]}"
        i += 1
    save_path = os.path.join(tmp_path, filename)
    print(save_path)
    file.save(save_path)
    
    query       = [save_path]
    galleries   = [os.path.join(image_path, filename) for filename in os.listdir(image_path) if filename.endswith(('.jpg', '.jpeg', '.png'))]
    
    args = {"num_workers": 0, "batch_size": 8}
    features_queries     = inference_on_images(model, paths=query, transform=transform, **args)
    features_galleries   = inference_on_images(model, paths=galleries, transform=transform, **args)
    
    dist_mat    = pairwise_dist(x1=features_queries, x2=features_galleries)
    ii_closest  = torch.argmin(dist_mat, dim=1)
    
    closest_img_path = galleries[ii_closest[0].item()]
    print(closest_img_path)

    # Return the image file as a response
    try:
        return send_file(os.path.join("../", closest_img_path), mimetype='image/jpeg')
    except Exception as e:
        traceback.print_exc()
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)
