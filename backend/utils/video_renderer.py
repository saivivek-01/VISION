# utils/video_renderer.py

import os
import uuid
import subprocess
import re

def format_srt_time(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"

def render_video_with_audio(image_dir: str, audio_path: str, output_dir: str,
                            narration_text: str = None,
                            sentence_durations: list = None,
                            sentences: list = None) -> str:
    try:
        print("[INFO] Rendering video with FFmpeg...")

        image_files = sorted([f for f in os.listdir(image_dir) if f.endswith(".png")])
        image_count = len(image_files)

        if sentence_durations is None or sentences is None:
            raise Exception("Sentence durations and sentences list required for precise syncing.")

        if image_count != len(sentence_durations):
            raise Exception(f"Mismatch: {image_count} images vs {len(sentence_durations)} durations")

        # Step 1: Create subtitles (.srt)
        srt_path = os.path.join(output_dir, f"subtitles_{uuid.uuid4().hex}.srt")
        with open(srt_path, "w", encoding="utf-8") as srt:
            current_time = 0.0
            for idx, (sentence, duration) in enumerate(zip(sentences, sentence_durations)):
                start = format_srt_time(current_time)
                end = format_srt_time(current_time + duration)
                srt.write(f"{idx + 1}\n{start} --> {end}\n{sentence.strip()}\n\n")
                current_time += duration

        # Step 2: Build FFmpeg input list (escaped absolute paths)
        ffmpeg_list_path = os.path.join(output_dir, f"ffmpeg_frames_{uuid.uuid4().hex}.txt")
        with open(ffmpeg_list_path, "w") as f:
            for i in range(image_count):
                frame_file = os.path.abspath(os.path.join(image_dir, f"frame_{i:04d}.png"))
                duration = sentence_durations[i]
                f.write(f"file '{frame_file}'\n")
                f.write(f"duration {duration:.2f}\n")
            # Repeat last frame (FFmpeg requirement)
            f.write(f"file '{frame_file}'\n")

        # Step 3: Create raw video (image + durations)
        raw_video_path = os.path.join(output_dir, f"video_raw_{uuid.uuid4().hex}.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", ffmpeg_list_path,
            "-vsync", "vfr", "-pix_fmt", "yuv420p", raw_video_path
        ], check=True)

        # Step 4: Combine raw video + audio + subtitles
        final_path = os.path.join(output_dir, f"video_local_{uuid.uuid4().hex}.mp4")
        subprocess.run([
            "ffmpeg", "-y",
            "-i", raw_video_path,
            "-i", audio_path,
            "-vf", f"subtitles={os.path.abspath(srt_path)}",
            "-c:v", "libx264", "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p",
            final_path
        ], check=True)

        print(f"[SUCCESS] Video saved at: {final_path}")
        return final_path

    except Exception as e:
        print(f"[ERROR] Video rendering failed: {e}")
        raise Exception("Video rendering failed.")
    
def combine_video_clips_with_audio(video_dir: str, audio_path: str, output_dir: str,
                                    narration_text: str = None,
                                    sentence_durations: list = None,
                                    sentences: list = None) -> str:
    try:
        print("[INFO] Combining multiple video clips...")

        video_files = sorted([f for f in os.listdir(video_dir) if f.endswith(".mp4")])
        if not video_files:
            raise Exception("No video clips found to combine.")

        list_file = os.path.join(output_dir, f"video_list_{uuid.uuid4().hex}.txt")
        with open(list_file, "w") as f:
            for vid in video_files:
                abs_path = os.path.abspath(os.path.join(video_dir, vid))
                f.write(f"file '{abs_path}'\n")

        combined_path = os.path.join(output_dir, f"combined_{uuid.uuid4().hex}.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
            "-c", "copy", combined_path
        ], check=True)

        final_path = os.path.join(output_dir, f"video_final_{uuid.uuid4().hex}.mp4")

        # Optional: generate subtitles if sentence data is available
        srt_path = None
        if sentence_durations and sentences:
            srt_path = os.path.join(output_dir, f"subtitles_{uuid.uuid4().hex}.srt")
            with open(srt_path, "w", encoding="utf-8") as srt:
                current_time = 0.0
                for idx, (sentence, duration) in enumerate(zip(sentences, sentence_durations)):
                    start = format_srt_time(current_time)
                    end = format_srt_time(current_time + duration)
                    srt.write(f"{idx + 1}\n{start} --> {end}\n{sentence.strip()}\n\n")
                    current_time += duration

        ffmpeg_command = [
            "ffmpeg", "-y",
            "-i", combined_path,
            "-i", audio_path,
            "-c:v", "libx264", "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p",
        ]

        if srt_path:
            ffmpeg_command += ["-vf", f"subtitles={os.path.abspath(srt_path)}"]

        ffmpeg_command.append(final_path)

        subprocess.run(ffmpeg_command, check=True)

        print(f"[SUCCESS] Final full video saved: {final_path}")
        return final_path

    except Exception as e:
        print(f"[ERROR] Full video rendering failed: {e}")
        raise Exception("Video rendering failed in full video mode.")
