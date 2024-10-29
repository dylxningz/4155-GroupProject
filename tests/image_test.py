from PIL import Image
import requests
import os
import base64

url = r"http://localhost:8000/images"

def convert_png_to_jpg(png_path):
    with Image.open(png_path) as img:
        rgb_img = img.convert("RGB")
        rgb_img.save(f"{png_path[:-3]}jpg", "JPEG")
    os.remove(png_path)
    og_path = png_path.replace("\\", "/")
    og_path = og_path[:-3]
    return og_path + "jpg"

def convert_jpg_to_binary(jpg_path):
    with open(jpg_path, "rb") as file:
        # Read the binary data
        binary_data = file.read()
    return binary_data

def process_images(image):
    if image.endswith(".png"):
        processed_image = convert_png_to_jpg(image)
    else:
        processed_image = image

    binary_data = convert_jpg_to_binary(processed_image)
    print(f"Binary data for {processed_image}: {binary_data[:20]}...")
    binary_data = base64.b64encode(binary_data).decode("utf-8")

    data = {
        "listing_id": 2,
        "img_data": binary_data
    }
    requests.post(url, json=data)

directory_path = r"test_image.png"
process_images(directory_path)
