# utils/visual_generator.py
import replicate
import os, uuid, requests, time
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()


REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
HEADERS_REPLICATE = {
    "Authorization": f"Token {REPLICATE_API_TOKEN}",
    "Content-Type": "application/json"
}


PRIMARY_REPLICATE_MODEL = "black-forest-labs/flux-schnell"
FALLBACK_REPLICATE_MODEL = "google/imagen-3-fast"


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

        image = generate_with_replicate_model(PRIMARY_REPLICATE_MODEL, prompt)

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



def generate_video_with_veo(prompt):
    headers = {
        "Authorization": f"Bearer {os.getenv('GOOGLE_VEO_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "duration": 4,
        "resolution": "720p"
    }
    res = requests.post("https://api.generativeai.google/v1/video:generate", headers=headers, json=payload)
    res.raise_for_status()
    video_url = res.json()["video_url"]
    return requests.get(video_url).content


LTX_VIDEO_MODEL = "wan-video/wan-2.2-t2v-fast"


def generate_visuals_ttv(enhanced_scene_prompts, output_folder):
    scene_dir = os.path.join(
        output_folder,
        f"ttv_scenes_{uuid.uuid4().hex}"
    )
    os.makedirs(scene_dir, exist_ok=True)

    for idx, prompt in enumerate(enhanced_scene_prompts):
        print(f"[INFO] Generating video scene {idx}")

        output = replicate.run(
            LTX_VIDEO_MODEL,
            input={
                "prompt": prompt,

                "width": 854,
                "height": 480,

                "num_frames": 81,

                "fps": 6,

                "guidance_scale": 7.5
            }
        )

        video_path = os.path.join(scene_dir, f"scene_{idx:04d}.mp4")

        with open(video_path, "wb") as f:
            f.write(output.read())

        print(f"[SUCCESS] Saved scene: {video_path}")

    return scene_dir