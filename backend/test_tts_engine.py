# backend/test_tts_engine.py

from utils.tts_engine import generate_audio

if __name__ == "__main__":
    sample = "The water cycle involves evaporation, condensation, and precipitation. Sunlight heats water bodies, turning water into vapor. This vapor rises, cools, and condenses to form clouds. Eventually, water returns to the Earth as rain, snow, or hail"
    try:
        path = generate_audio(sample, "assets/output_videos")
        print(" Audio generated at:", path)
    except Exception as err:
        print(" TTS Engine Error:", err)