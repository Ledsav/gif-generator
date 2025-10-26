import base64
import json
import requests
from pathlib import Path

# Update this with your deployed function URL
CLOUD_FUNCTION_URL = (
    "https://us-central1-python-functions-476223.cloudfunctions.net/generate_gif_http"
)

# Load sample images and encode as base64
image_paths = [
    "local/sample/after.jpg",
    "local/sample/before.jpg",
    "local/sample/mid.jpg",
]

images_b64 = []
for path in image_paths:
    if Path(path).stat().st_size > 0:
        with open(path, "rb") as f:
            images_b64.append(base64.b64encode(f.read()).decode("utf-8"))
    else:
        print(f"Warning: {path} is empty and will be skipped.")

payload = {
    "images": images_b64,
    # Set these values to control animation smoothness and speed:
    "duration": 500,  # Show each image for 500ms
    "fade_frames": 20,  # Use 20 frames for the fade
    "fade_duration": 50,  # Each fade frame lasts 50ms
}

response = requests.post(
    CLOUD_FUNCTION_URL,
    headers={"Content-Type": "application/json"},
    data=json.dumps(payload),
)

if response.status_code == 200:
    result = response.json()
    gif_b64 = result["gif"]
    with open("test_output.gif", "wb") as f:
        f.write(base64.b64decode(gif_b64))
    print("GIF saved as test_output.gif")
else:
    print("Error:", response.status_code, response.text)
