# Google Cloud Functions Deployment

## Clean Project Structure

Your deployment root should look like this:

```
main.py
requirements.txt
README.md
```

For local testing and legacy scripts, use the `local/` folder:

```
local/generate_gif.py
local/sample/
```

## Deploy Command

To deploy your GIF generator as a Google Cloud Function, run:

```
gcloud functions deploy generate_gif_http --runtime python311 --trigger-http --allow-unauthenticated --entry-point generate_gif_http
```

This will make your function available via a public HTTP endpoint.

## Usage

Send a POST request with JSON:

```
{
	"images": ["<base64_image1>", "<base64_image2>", ...],
	"duration": 100,
	"fade_frames": 10,
	"fade_duration": 50
}
```

The response will contain a base64-encoded GIF.
# GIF Generator

A Python script to generate animated GIFs from a sequence of images, with smooth cross-fade transitions and customizable frame durations.

## Features
- Centers all images on a common canvas
- Smooth cross-fade (blend) transitions between images
- Customizable number of fade frames and durations
- Supports any number of input images

## Requirements
- Python 3.7+
- Pillow (`pip install Pillow`)

## Usage

```
python generate_gif.py <output.gif> <duration_ms> <img1> <img2> ... <imgN> [fade_frames] [fade_duration_ms]
```

- `<output.gif>`: Path to the output GIF file
- `<duration_ms>`: Duration (in ms) for each static image frame
- `<img1> <img2> ... <imgN>`: List of image files (JPG, PNG, etc.)
- `[fade_frames]` (optional): Number of cross-fade frames between each image (default: 10)
- `[fade_duration_ms]` (optional): Duration (in ms) for each fade frame (default: 100)

### Example

```
python generate_gif.py put.gif 100 sample/after.jpg sample/before.jpg sample/mid.jpg 20 50
```
- This creates a GIF with 3 images, 20 fade frames between each, 100ms per static frame, and 50ms per fade frame.

### On Windows PowerShell
If using wildcards, expand them first:

```
$images = Get-ChildItem sample\*.jpg | ForEach-Object { $_.FullName }
python generate_gif.py put.gif 100 $images 20 50
```

## License
MIT
