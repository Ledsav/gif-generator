"""
Secure GIF Generation Cloud Function with Firebase Authentication and Rate
Limiting
"""

import base64
from io import BytesIO
from datetime import datetime, timedelta
from typing import Tuple
from PIL import Image
import functions_framework
import json
import firebase_admin
from firebase_admin import firestore, auth

# Initialize Firebase Admin SDK (only once)
if not firebase_admin._apps:
    firebase_admin.initialize_app()

# Firestore client
db = firestore.client()

# Rate limit configuration
RATE_LIMIT_DAYS = 7  # 1 week


def verify_token(request) -> Tuple[str, dict, int]:
    """
    Verify Firebase ID token from Authorization header
    Returns (user_id, error_response, status_code) tuple
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None, {"error": "Missing Authorization header"}, 401

    # Extract token from "Bearer <token>"
    parts = auth_header.split(" ")
    if len(parts) != 2 or parts[0] != "Bearer":
        return None, {"error": "Invalid Authorization header format"}, 401

    token = parts[1]

    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token["uid"]
        return user_id, None, None
    except auth.InvalidIdTokenError:
        return None, {"error": "Invalid authentication token"}, 401
    except auth.ExpiredIdTokenError:
        return None, {"error": "Authentication token expired"}, 401
    except Exception as e:
        print(f"Token verification error: {e}")
        return None, {"error": "Authentication failed"}, 401


def check_rate_limit(user_id: str) -> Tuple[bool, dict, int]:
    """
    Check if user has exceeded rate limit
    Returns (allowed, error_response, status_code) tuple
    """
    try:
        # Get user's rate limit document from Firestore
        rate_limit_ref = db.collection("rate_limits").document(user_id)
        rate_limit_doc = rate_limit_ref.get()

        if rate_limit_doc.exists:
            data = rate_limit_doc.to_dict()
            last_generation = data.get("last_generation")

            if last_generation:
                # Convert Firestore timestamp to datetime
                last_gen_time = last_generation
                current_time = datetime.utcnow()

                # Check if enough time has passed
                time_diff = current_time - last_gen_time
                if time_diff < timedelta(days=RATE_LIMIT_DAYS):
                    # Calculate time remaining
                    time_remaining = timedelta(days=RATE_LIMIT_DAYS) - time_diff
                    days_remaining = time_remaining.days
                    hours_remaining = time_remaining.seconds // 3600

                    return (
                        False,
                        {
                            "error": f"Rate limit exceeded. Please wai{days_remaining} days and {hours_remaining} hours before generating another GIF.",
                            "retry_after": (
                                last_gen_time + timedelta(days=RATE_LIMIT_DAYS)
                            ).isoformat(),
                        },
                        429,
                    )

        # User is allowed to generate GIF
        return True, None, None

    except Exception as e:
        print(f"Rate limit check error: {e}")
        # In case of error, allow the request (fail open)
        return True, None, None


def update_rate_limit(user_id: str):
    """Update user's rate limit timestamp in Firestore"""
    try:
        rate_limit_ref = db.collection("rate_limits").document(user_id)
        rate_limit_ref.set({"last_generation": datetime.utcnow(), "user_id": user_id})
    except Exception as e:
        print(f"Error updating rate limit: {e}")


def generate_gif(images, duration=100, fade_frames=10, fade_duration=100):
    """Your existing GIF generation logic - UNCHANGED"""
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
    """
    HTTP Cloud Function for secure GIF generation
    Requires Firebase authentication and enforces rate limiting
    """
    # Set CORS headers
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "3600",
        }
        return ("", 204, headers)

    headers = {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"}

    try:
        # 1. Verify authentication
        user_id, error, status = verify_token(request)
        if error:
            return (json.dumps(error), status, headers)

        # 2. Check rate limit
        allowed, error, status = check_rate_limit(user_id)
        if not allowed:
            return (json.dumps(error), status, headers)

        # 3. Parse request
        data = request.get_json(silent=True)
        if not data:
            return (json.dumps({"error": "Invalid JSON payload"}), 400, headers)

        images_b64 = data.get("images", [])
        duration = int(data.get("duration", 100))
        fade_frames = int(data.get("fade_frames", 10))
        fade_duration = int(data.get("fade_duration", 100))

        if not images_b64 or len(images_b64) < 2:
            return (json.dumps({"error": "At least 2 images required"}), 400, headers)

        if len(images_b64) > 3:
            return (json.dumps({"error": "Maximum 3 images allowed"}), 400, headers)

        # 4. Generate GIF (your existing logic)
        images = [
            Image.open(BytesIO(base64.b64decode(img_b64))).convert("RGBA")
            for img_b64 in images_b64
        ]
        gif_bytes = generate_gif(images, duration, fade_frames, fade_duration)
        gif_b64 = base64.b64encode(gif_bytes.read()).decode("utf-8")

        # 5. Update rate limit
        update_rate_limit(user_id)

        # 6. Return result
        return (json.dumps({"gif": gif_b64}), 200, headers)

    except Exception as e:
        print(f"Error generating GIF: {e}")
        return (json.dumps({"error": "Internal server error"}), 500, headers)
