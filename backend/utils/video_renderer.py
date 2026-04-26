# # utils/video_renderer.py


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


def render_video_with_audio(
    image_dir: str,
    audio_path: str,
    output_dir: str,
    narration_text: str = None,
    sentence_durations: list = None,
    sentences: list = None,
    avatar_path: str = None
) -> str:

    image_files = sorted(f for f in os.listdir(image_dir) if f.endswith(".png"))
    if not image_files:
        raise Exception("No frames found")

    if len(image_files) != len(sentence_durations):
        raise Exception("Image/audio duration mismatch")

    
    srt_path = os.path.join(output_dir, f"sub_{uuid.uuid4().hex}.srt")
    with open(srt_path, "w", encoding="utf-8") as srt:
        t = 0.0
        for i, (txt, dur) in enumerate(zip(sentences, sentence_durations)):
            srt.write(
                f"{i+1}\n"
                f"{format_srt_time(t)} --> {format_srt_time(t+dur)}\n"
                f"{txt.strip()}\n\n"
            )
            t += dur

    
    list_file = os.path.join(output_dir, f"frames_{uuid.uuid4().hex}.txt")
    with open(list_file, "w") as f:
        for i, dur in enumerate(sentence_durations):
            f.write(f"file '{os.path.abspath(os.path.join(image_dir, f'frame_{i:04d}.png'))}'\n")
            f.write(f"duration {dur:.2f}\n")
        f.write(f"file '{os.path.abspath(os.path.join(image_dir, f'frame_{i:04d}.png'))}'\n")

    raw_video = os.path.join(output_dir, f"raw_{uuid.uuid4().hex}.mp4")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-pix_fmt", "yuv420p",
        raw_video
    ], check=True)

    if not avatar_path:
        avatar_path = os.path.abspath("assets/avatars/default.png")

    final_path = os.path.join(output_dir, f"final_{uuid.uuid4().hex}.mp4")

    subprocess.run([
        "ffmpeg", "-y",
        "-i", raw_video,
        "-i", audio_path,
        "-i", avatar_path,
        "-filter_complex",
        (
            "[2:v]scale=iw*0.15:-1[avatar];"
            "[0:v][avatar]overlay=x=(W-w)/2 + (W-w)/2*sin(2*PI*t/10):y=20,"
            f"subtitles={os.path.abspath(srt_path)}[v]"
        ),
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-c:a", "aac",
        "-movflags", "+faststart",
        final_path
    ], check=True)

    return final_path


def combine_video_clips_with_audio(
    video_dir: str,
    audio_path: str,
    output_dir: str,
    narration_text: str = None,
    sentence_durations: list = None,
    sentences: list = None,
    avatar_path=None
):
    try:
        print("[INFO] Combining multiple video clips...")

        video_files = sorted(f for f in os.listdir(video_dir) if f.endswith(".mp4"))
        if not video_files:
            raise Exception("No video clips found")

        list_file = os.path.join(output_dir, f"videos_{uuid.uuid4().hex}.txt")
        with open(list_file, "w") as f:
            for v in video_files:
                f.write(f"file '{os.path.abspath(os.path.join(video_dir, v))}'\n")

        combined_video = os.path.join(output_dir, f"combined_{uuid.uuid4().hex}.mp4")

        
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", list_file,
            "-vf", "scale=1280:720:flags=lanczos",
            "-r", "24",
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            combined_video
        ], check=True)

        
        def get_duration(path):
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries",
                 "format=duration", "-of", "csv=p=0", path],
                stdout=subprocess.PIPE, text=True
            )
            return float(result.stdout.strip())

        video_duration = get_duration(combined_video)
        audio_duration = get_duration(audio_path)

        speed_factor = video_duration / audio_duration
        print(f"[INFO] Speed factor: {speed_factor:.4f}")

       
        srt_path = None
        if sentence_durations and sentences:
            srt_path = os.path.join(output_dir, f"sub_{uuid.uuid4().hex}.srt")
            t = 0.0
            with open(srt_path, "w", encoding="utf-8") as srt:
                for i, (txt, dur) in enumerate(zip(sentences, sentence_durations)):
                    srt.write(
                        f"{i+1}\n"
                        f"{format_srt_time(t)} --> {format_srt_time(t+dur)}\n"
                        f"{txt.strip()}\n\n"
                    )
                    t += dur

        if not avatar_path:
            avatar_path = os.path.abspath("assets/avatars/default.png")
        else:
            avatar_path = os.path.abspath(avatar_path)

        final_path = os.path.join(output_dir, f"final_{uuid.uuid4().hex}.mp4")

        
        filter_complex = (
            f"[0:v]setpts=PTS/{speed_factor},"
            f"scale=1280:720[base];"
            f"[2:v]scale=iw*0.15:-1[avatar];"
            f"[base][avatar]overlay="
            f"x=(W-w)/2 + (W-w)/2*sin(2*PI*t/10):y=20[v]"
        )

        if srt_path:
            filter_complex += f";[v]subtitles={os.path.abspath(srt_path)}[vout]"
            vmap = "[vout]"
        else:
            vmap = "[v]"

        subprocess.run([
            "ffmpeg", "-y",
            "-i", combined_video,
            "-i", audio_path,
            "-i", avatar_path,
            "-filter_complex", filter_complex,
            "-map", vmap,
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-movflags", "+faststart",
            final_path
        ], check=True)

        print(f"[SUCCESS] Final full video saved: {final_path}")
        return final_path

    except Exception as e:
        print(f"[ERROR] Full video rendering failed: {e}")
        raise

def build_avatar_overlay_filter():
    x_expr = "(W-w)/2 + (W-w)/2*sin(2*PI*t/10)"
    y_expr = "20"
    return (
        "[2:v]scale=iw*0.15:-1[avatar];"
        "[0:v][avatar]"
        f"overlay=x={x_expr}:y={y_expr}"
    )