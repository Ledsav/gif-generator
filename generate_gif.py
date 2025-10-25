import sys
import os
from PIL import Image


def generate_gif(
    image_paths, output_path, duration=500, fade_frames=10, fade_duration=100
):

    images = [Image.open(img).convert("RGBA") for img in image_paths]

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

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=False,
        disposal=2,
    )
    print(f"GIF saved to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(
            "Usage: python generate_gif.py <output.gif> <duration_ms> <img1> <img2> ... <imgN> [fade_frames] [fade_duration_ms]"
        )
        sys.exit(1)
    output_gif = sys.argv[1]
    duration = int(sys.argv[2])

    possible_images = sys.argv[3:]
    fade_frames = 10
    fade_duration = 100

    if (
        len(possible_images) > 1
        and possible_images[-1].isdigit()
        and possible_images[-2].isdigit()
    ):
        fade_duration = int(possible_images[-1])
        fade_frames = int(possible_images[-2])
        image_files = possible_images[:-2]
    elif possible_images and possible_images[-1].isdigit():
        fade_frames = int(possible_images[-1])
        image_files = possible_images[:-1]
    else:
        image_files = possible_images

    valid_exts = (".jpg", ".jpeg", ".png", ".bmp", ".gif")
    image_files = [f for f in image_files if f.lower().endswith(valid_exts)]
    if not image_files:
        print("No valid image files provided.")
        sys.exit(1)
    generate_gif(image_files, output_gif, duration, fade_frames, fade_duration)
