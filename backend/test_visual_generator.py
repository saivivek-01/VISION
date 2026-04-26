# test_visual_generator.py

import os
from utils.visual_generator import generate_visuals_tti

#  Test input sentences
TEST_SENTENCES = [
    "Photosynthesis is the process by which green plants convert sunlight into food.",
    "Newton's Third Law states that for every action, there is an equal and opposite reaction.",
    "The water cycle describes how water evaporates, condenses, and precipitates in the environment."
]

def main():
    print("[TEST] Starting test for visual_generator.py...")
    
    output_folder = "test_outputs"
    os.makedirs(output_folder, exist_ok=True)

    
    frames_dir = generate_visuals_tti(TEST_SENTENCES, output_folder)

    print(f"[TEST] Images saved at: {frames_dir}")
    print("[TEST] Done. Check the output folder for generated frames.")

if __name__ == "__main__":
    main()