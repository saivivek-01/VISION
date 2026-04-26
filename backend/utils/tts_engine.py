# utils/tts_engine.py

import os
import uuid
import re
from pydub import AudioSegment
from dotenv import load_dotenv
from gtts import gTTS
import requests

load_dotenv()


ELEVEN_KEYS = [
    os.getenv("ELEVEN_KEY_PRIMARY"),
    os.getenv("ELEVEN_KEY_FALLBACK1"),
    os.getenv("ELEVEN_KEY_FALLBACK2")
]


def call_elevenlabs_tts(text, output_file, language=None):
    
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.8,
            "style": 0.3,
            "use_speaker_boost": True
        }
    }
    if language:
        payload["language"] = language

    for key in ELEVEN_KEYS:
        headers = {
            "xi-api-key": key,
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                print(f"[INFO] ElevenLabs success with key ending in ...{key[-4:]}")
                return True
            else:
                print(f"[WARN] ElevenLabs failed ({key[-4:]}): {response.status_code} {response.text}")
        except Exception as e:
            print(f"[ERROR] ElevenLabs exception with key ...{key[-4:]}: {e}")

    return False 


def split_into_sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.?!])\s+', text) if s.strip()]


def generate_audio(text: str, output_folder: str, language: str = "en"):
    os.makedirs(output_folder, exist_ok=True)
    sentences = split_into_sentences(text)
    audio_segments = []
    sentence_durations = []
    print(f"[INFO] Splitting into {len(sentences)} sentences...")

    for idx, sentence in enumerate(sentences):
        output_file = os.path.join(output_folder, f"sentence_{idx}.mp3")

        # Try ElevenLabs 
        success = call_elevenlabs_tts(sentence, output_file, language)

        if not success:
            try:
                tts = gTTS(text=sentence, lang=language)
                tts.save(output_file)
                print(f"[INFO] gTTS fallback success: Sentence {idx}")
            except Exception as gtts_e:
                print(f"[ERROR] Both TTS engines failed for sentence {idx}: {gtts_e}")
                audio_segments.append(AudioSegment.silent(duration=1000))
                sentence_durations.append(1.0)
                continue

        
        segment = AudioSegment.from_file(output_file)
        audio_segments.append(segment)
        sentence_durations.append(segment.duration_seconds)

    
    final_audio = sum(audio_segments)
    final_path = os.path.join(output_folder, f"speech_{uuid.uuid4().hex}.mp3")
    final_audio.export(final_path, format="mp3")
    print(f"[SUCCESS] Final audio saved: {final_path}")

    return final_path, sentence_durations, sentences

def generate_audio_from_sentences(sentences, output_folder, language="en"):
    audio_segments = []
    sentence_durations = []

    for idx, sentence in enumerate(sentences):
        sentence = sentence.replace(",", ", ").replace(".", ". ")
        output_file = os.path.join(output_folder, f"sentence_{idx}.mp3")

        success = call_elevenlabs_tts(sentence, output_file, language)

        if not success:
            tts = gTTS(text=sentence, lang=language)
            tts.save(output_file)

        segment = AudioSegment.from_file(output_file)
        audio_segments.append(segment)
        sentence_durations.append(segment.duration_seconds)

    final_audio = sum(audio_segments)
    final_path = os.path.join(output_folder, f"speech_{uuid.uuid4().hex}.mp3")
    final_audio.export(final_path, format="mp3")

    return final_path, sentence_durations