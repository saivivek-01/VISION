# utils/visual_generator.py

import os, uuid, requests, time
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
HEADERS_REPLICATE = {
    "Authorization": f"Token {REPLICATE_API_TOKEN}",
    "Content-Type": "application/json"
}

# --- TTI Models ---
PRIMARY_REPLICATE_MODEL = "black-forest-labs/flux-schnell"
FALLBACK_REPLICATE_MODEL = "google/imagen-3-fast"

# Image settings
WIDTH, HEIGHT = 768, 768

def generate_with_replicate_model(model_name, prompt):
    try:
        print(f"[INFO] Using Replicate model: {model_name}")
        url = "https://api.replicate.com/v1/predictions"
        data = {
            "version": model_name,
            "input": {
                "prompt": prompt
            }
        }
        response = requests.post(url, headers=HEADERS_REPLICATE, json=data)
        prediction = response.json()

        if "urls" not in prediction:
            print("[WARN] Replicate API unexpected response:", prediction)
            return None

        status_url = prediction["urls"]["get"]
        while prediction["status"] not in ["succeeded", "failed"]:
            time.sleep(1.5)
            prediction = requests.get(status_url, headers=HEADERS_REPLICATE).json()

        if prediction["status"] == "succeeded":
            image_url = prediction["output"][0]
            img_data = requests.get(image_url).content
            return Image.open(BytesIO(img_data))

        print("[ERROR] Replicate generation failed:", prediction)
        return None

    except Exception as e:
        print(f"[ERROR] Replicate model {model_name} failed: {e}")
        return None

def generate_visuals_tti(enhanced_prompts, output_folder):
    frames_dir = os.path.join(output_folder, f"frames_{uuid.uuid4().hex}")
    os.makedirs(frames_dir, exist_ok=True)

    successful_prompts = []
    for idx, prompt in enumerate(enhanced_prompts):
        print(f"[INFO] Generating image for scene {idx}: {prompt}")

        # primary model 
        image = generate_with_replicate_model(PRIMARY_REPLICATE_MODEL, prompt)

        # Fallback model
        if not image:
            image = generate_with_replicate_model(FALLBACK_REPLICATE_MODEL, prompt)

        if image:
            image = image.resize((WIDTH, HEIGHT))
            image.save(os.path.join(frames_dir, f"frame_{len(successful_prompts):04d}.png"))
            successful_prompts.append(prompt)
            print(f"[SUCCESS] Image saved for scene {idx}")
        else:
            print(f"[ERROR] All image generation models failed for scene {idx}")

    print(f" All images generated. Frames directory: {frames_dir}")
    return frames_dir, successful_prompts

# ========== FULL VIDEO (TTV) ==========(FUTURE SCOPE)==========

def generate_video_with_runway(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('RUNWAY_API_KEY')}",
            "Content-Type": "application/json"
        }
        res = requests.post("https://api.runwayml.com/v1/generate", headers=headers, json={"prompt": prompt})
        res.raise_for_status()
        result = res.json()
        video_url = result.get("video_url")
        if video_url:
            video_data = requests.get(video_url).content
            return BytesIO(video_data)
        return None
    except Exception as e:
        print(f"[WARN] Runway Gen-2 failed: {e}")
        return None

def generate_video_with_pika(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('PIKA_API_KEY')}",
            "Content-Type": "application/json"
        }
        res = requests.post("https://api.pika.art/v1/generate", headers=headers, json={"prompt": prompt})
        video_url = res.json().get("video_url")
        if video_url:
            video_data = requests.get(video_url).content
            return BytesIO(video_data)
        return None
    except Exception as e:
        print(f"[WARN] Pika Labs failed: {e}")
        return None

def generate_visuals_ttv(enhanced_scene_prompts, output_folder):
    scene_dir = os.path.join(output_folder, f"ttv_scenes_{uuid.uuid4().hex}")
    os.makedirs(scene_dir, exist_ok=True)

    for idx, prompt in enumerate(enhanced_scene_prompts):
        print(f"[INFO] Generating video for scene {idx}: {prompt}")

        video_io = generate_video_with_runway(prompt)
        if not video_io:
            video_io = generate_video_with_pika(prompt)

        if video_io:
            out_path = os.path.join(scene_dir, f"scene_{idx:04d}.mp4")
            with open(out_path, "wb") as f:
                f.write(video_io.read())
            print(f"[SUCCESS] Saved: {out_path}")
        else:
            print(f"[ERROR] All video generation models failed for scene {idx}")

    print(f"🎬 Scene generation complete. Folder: {scene_dir}")
    return scene_dir