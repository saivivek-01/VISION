from utils.video_renderer import render_video_with_audio

frames_dir = "assets/output_images_test/frames_f18e45f80f784129b7dcdd2938412d8b"
audio_path = "/Users/villainvivek/VISION/assets/output_videos/speech_db2cd697cd684afb87456e1cf298df80.mp3"
output_dir = "assets/video_output"

narration_text = """
The water cycle involves evaporation, condensation, and precipitation.
Sunlight heats water bodies, turning water into vapor.
This vapor rises, cools, and condenses to form clouds.
Eventually, water returns to the Earth as rain, snow, or hail.
"""

print("[TEST] Starting video rendering test...")
result_path = render_video_with_audio(frames_dir, audio_path, output_dir, narration_text=narration_text)
print(f" Video rendering successful: {result_path}")