import base64
from io import BytesIO
from PIL import Image
import functions_framework
import json


def generate_gif(images, duration=100, fade_frames=10, fade_duration=100):
    # Center and blend logic adapted from your script
    max_w = max(img.width for img in images)
    max_h = max(img.height for img in images)
    centered = []
    for img in images:
        canvas = Image.new("RGBA", (max_w, max_h), (0, 0, 0, 0))
        x = (max_w - img.width) // 2
        y = (max_h - img.height) // 2
        canvas.paste(img, (x, y), img)
        centered.append(canvas)
    frames = [centered[0]]
    durations = [duration]
    for i in range(1, len(centered)):
        prev = centered[i - 1]
        curr = centered[i]
        for f in range(1, fade_frames + 1):
            alpha = f / (fade_frames + 1)
            blended = Image.blend(prev, curr, alpha)
            frames.append(blended)
            durations.append(fade_duration)
        frames.append(curr)
        durations.append(duration)
    frames = [f.convert("P", dither=Image.NONE, palette=Image.ADAPTIVE) for f in frames]
    output = BytesIO()
    frames[0].save(
        output,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=False,
        disposal=2,
    )
    output.seek(0)
    return output


@functions_framework.http
def generate_gif_http(request):
    # Expect JSON: { "images": [base64_image1, base64_image2, ...], "duration": 100, "fade_frames": 10, "fade_duration": 50 }
    data = request.get_json()
    images_b64 = data["images"]
    duration = int(data.get("duration", 100))
    fade_frames = int(data.get("fade_frames", 10))
    fade_duration = int(data.get("fade_duration", 100))
    images = [
        Image.open(BytesIO(base64.b64decode(img_b64))).convert("RGBA")
        for img_b64 in images_b64
    ]
    gif_bytes = generate_gif(images, duration, fade_frames, fade_duration)
    gif_b64 = base64.b64encode(gif_bytes.read()).decode("utf-8")
    return json.dumps({"gif": gif_b64}), 200, {"Content-Type": "application/json"}
