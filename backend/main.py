from flask import Flask, request, jsonify, send_file, session, send_from_directory
from utils.text_parser import parse_text_file, enhance_prompt_list
from utils.tts_engine import generate_audio_from_sentences
from utils.visual_generator import generate_visuals_tti, generate_visuals_ttv
from utils.video_renderer import render_video_with_audio, combine_video_clips_with_audio
from utils.text_parser import enhance_prompt_for_ttv
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
    LANGUAGE_MAP = {
        "en": "English",
        "hi": "Hindi",
        "ta": "Tamil",
        "te": "Telugu",
        "kn": "Kannada",
        "ml": "Malayalam",
        "fr": "French",
        "es": "Spanish"
    }
    avatar_path = session.get("avatar_path")
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

        language = request.form.get("language", "en")
        from utils.tts_engine import split_into_sentences
        english_sentences = split_into_sentences(parsed_text)
        if language != "en":
            from utils.text_parser import translate_text
            print(f"[INFO] Translating content to {language}")
            translated_sentences = []
            for s in english_sentences:
                try:
                    translated_sentences.append(
                        translate_text(s, LANGUAGE_MAP.get(language, "English"))
                    )
                except Exception as e:
                    print("[WARN] Translation failed, falling back to English:", e)
                    translated_sentences.append(s)
        else:
            translated_sentences = english_sentences
        print("[INFO] Generating audio...")
       
        audio_path, sentence_durations = generate_audio_from_sentences(
        translated_sentences,
        OUTPUT_FOLDER,
        language
        )

        if conversion_mode == "segmented":
            print("[INFO] Enhancing prompts for segmented video...")
            enhanced_prompts = enhance_prompt_list(english_sentences)
            print("[INFO] Generating visuals for segmented video...")
            frames_dir, filtered_sentences = generate_visuals_tti(enhanced_prompts, OUTPUT_FOLDER)

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
                sentences = english_sentences,
                avatar_path=avatar_path
            )
        elif conversion_mode == "full":
            enhanced_prompts = [enhance_prompt_for_ttv(s) for s in english_sentences]
            print("[INFO] Generating short scene videos for full video mode...")
            scene_video_dir = generate_visuals_ttv(enhanced_prompts, OUTPUT_FOLDER)

            print("[INFO] Combining short videos into full-length video...")
            video_path = combine_video_clips_with_audio(
                scene_video_dir,
                audio_path,
                OUTPUT_FOLDER,
                narration_text=parsed_text,
                sentence_durations=sentence_durations,
                sentences=english_sentences,
                avatar_path=avatar_path
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

@app.route("/upload_avatar", methods=["POST"])
def upload_avatar():
    photo = request.files.get("photo")
    if not photo:
        return jsonify({"error": "No photo uploaded"}), 400

    os.makedirs("assets/avatars", exist_ok=True)

    photo_path = f"assets/avatars/photo_{uuid.uuid4().hex}.jpg"
    avatar_path = f"assets/avatars/avatar_{uuid.uuid4().hex}.png"

    photo.save(photo_path)

    from utils.avatar_generator import generate_avatar_from_photo
    generate_avatar_from_photo(photo_path, avatar_path)

    session["avatar_path"] = avatar_path
    return jsonify({"avatar_path": avatar_path})

@app.route("/avatar.html")
def avatar_page():
    return app.send_static_file("avatar.html")

@app.route("/create_avatar", methods=["POST"])
def create_avatar():
    photo = request.files.get("photo")
    if not photo:
        return jsonify({"error": "No photo uploaded"}), 400

    os.makedirs("assets/avatars", exist_ok=True)

    avatar_id = uuid.uuid4().hex
    photo_path = f"assets/avatars/photo_{avatar_id}.jpg"
    avatar_path = f"assets/avatars/avatar_{avatar_id}.png"

    photo.save(photo_path)

    from utils.avatar_generator import generate_avatar_from_photo
    generate_avatar_from_photo(photo_path, avatar_path)

    session["avatar_path"] = avatar_path

    return jsonify({
        "avatar_path": avatar_path
    })

@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory(os.path.abspath("assets"), filename)

if __name__ == "__main__":
    app.run(debug=True)