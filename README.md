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
