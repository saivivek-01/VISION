from flask import Flask, request, jsonify, send_file, session
from utils.text_parser import parse_text_file, enhance_prompt_list
from utils.tts_engine import generate_audio
from utils.visual_generator import generate_visuals_tti, generate_visuals_ttv
from utils.video_renderer import render_video_with_audio, combine_video_clips_with_audio
import os
import uuid

app = Flask(__name__, static_folder="../frontend", static_url_path="", template_folder="../frontend")
app.secret_key = "vision_secret"

UPLOAD_FOLDER = "temp_uploads"
OUTPUT_FOLDER = "assets/output_videos"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/upload.html")
def upload_page():
    return app.send_static_file("upload.html")

@app.route("/conversion_options.html")
def conversion_page():
    return app.send_static_file("conversion_options.html")

@app.route("/result.html")
def result_page():
    return app.send_static_file("result.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    file_id = uuid.uuid4().hex
    saved_filename = f"{file_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, saved_filename)
    file.save(filepath)

    session["filename"] = saved_filename
    return jsonify({"filename": saved_filename})

@app.route("/generate", methods=["POST"])
def generate_video():
    print("[DEBUG] Incoming form data:", request.form)
    try:
        conversion_mode = request.form.get("mode") 
        if not conversion_mode:
            return jsonify({"error": "Missing conversion mode"}), 400

        filename = request.form.get("filename") or session.get("filename")
        if not filename:
            return jsonify({"error": "Missing filename"}), 400

        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({"error": "Uploaded file not found"}), 404

        print("[INFO] Parsing text...")
        parsed_text = parse_text_file(filepath)

        print("[INFO] Generating audio...")
        audio_path, sentence_durations, sentences = generate_audio(parsed_text, OUTPUT_FOLDER)

        if conversion_mode == "segmented":
            print("[INFO] Enhancing prompts for segmented video...")
            enhanced_prompts = enhance_prompt_list(sentences)
            print("[INFO] Generating visuals for segmented video...")
            frames_dir, filtered_sentences = generate_visuals_tti(enhanced_prompts, OUTPUT_FOLDER)

            # Adjust durations accordingly to match the sentences
            if len(filtered_sentences) != len(sentence_durations):
                print("[WARN] Mismatch between visuals and durations — truncating to match visuals")
                sentence_durations = sentence_durations[:len(filtered_sentences)]

            print("[INFO] Rendering final segmented video...")
            video_path = render_video_with_audio(
                frames_dir,
                audio_path,
                OUTPUT_FOLDER,
                narration_text=parsed_text,
                sentence_durations=sentence_durations,
                sentences=sentences
            )
        elif conversion_mode == "full":
            enhanced_prompts = enhance_prompt_list(sentences)
            print("[INFO] Generating short scene videos for full video mode...")
            scene_video_dir = generate_visuals_ttv(enhanced_prompts, OUTPUT_FOLDER)

            print("[INFO] Combining short videos into full-length video...")
            video_path = combine_video_clips_with_audio(
                scene_video_dir,
                audio_path,
                OUTPUT_FOLDER,
                narration_text=parsed_text,
                sentence_durations=sentence_durations,
                sentences=sentences
            )
        else:
            return jsonify({"error": "Invalid conversion mode"}), 400

        print(f"[INFO] Final video ready at {video_path}")
        from werkzeug.utils import safe_join

        abs_path = safe_join(os.getcwd(), video_path)
        return send_file(abs_path, mimetype="video/mp4")

    except Exception as e:
        print("[ERROR]", str(e))
        return jsonify({"error": f"Generation failed: {str(e)}"}), 500

@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)