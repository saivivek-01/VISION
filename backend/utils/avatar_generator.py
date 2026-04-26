import replicate
from PIL import Image
from io import BytesIO

SDXL_MODEL = "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc"

def generate_avatar_from_photo(photo_path, output_path):
    """
    Generate semi-realistic tutor avatar from user photo using SDXL
    """

    prompt = (
        "Semi-realistic educational tutor, full body, standing, holding a pointing stick, "
        "professional classroom instructor, neutral expression, cinematic lighting, "
        "sharp focus, transparent background, the background should be strictly transparent in RGBA."
    )

    # IMPORTANT: pass file object directly
    with open(photo_path, "rb") as photo_file:
        output = replicate.run(
            SDXL_MODEL,
            input={
                "width": 768,
                "height": 768,
                "prompt": prompt,
                "image": photo_file,          # ✅ THIS IS THE FIX
                "refine": "expert_ensemble_refiner",
                "apply_watermark": False,
                "num_inference_steps": 25
            }
        )

    # Save generated avatar
    img_bytes = output[0].read()
    Image.open(BytesIO(img_bytes)).convert("RGBA").save(output_path)