import os
import fitz
import uuid
import requests
from docx import Document
from dotenv import load_dotenv

load_dotenv()

# Load API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Set model names
GROQ_MODEL = "llama3-8b-8192"  
OPENROUTER_MODEL = "meta-llama/llama-3-8b-instruct"

def parse_text_file(filepath):
    ext = os.path.splitext(filepath)[-1].lower()
    if ext == ".pdf":
        text = extract_text_from_pdf(filepath)
    elif ext == ".docx":
        text = extract_text_from_docx(filepath)
    elif ext in [".txt", ".md"]:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    else: 
        raise Exception(f"Unsupported file type: {ext}")

    try:
        return call_groq(text)
    except Exception as e1:
        print("[WARN] Groq failed:", e1)
        try:
            return call_openrouter(text)
        except Exception as e2:
            print("[ERROR] OpenRouter also failed:", e2)
            raise Exception("All parsing models failed.")

def extract_text_from_pdf(path):
    print(f"[DEBUG] Opening PDF with PyMuPDF at: {path}")
    doc = fitz.open(path)  
    return "\n".join([page.get_text() for page in doc])

def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join([para.text for para in doc.paragraphs])

def call_groq(prompt_text):
    if not GROQ_API_KEY:
        raise Exception("Missing GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions" 
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are an educational assistant. Clean and summarize the following into narration-style text."},
            {"role": "user", "content": prompt_text}
        ],
        "temperature": 0.5
    }
    res = requests.post(url, headers=headers, json=data, timeout=30)
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"].strip()

def call_openrouter(prompt_text):
    if not OPENROUTER_API_KEY:
        raise Exception("Missing OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": "You are an educational assistant. Clean and summarize the following into narration-style text."},
            {"role": "user", "content": prompt_text}
        ],
        "temperature": 0.5
    }
    res = requests.post(url, headers=headers, json=data, timeout=30)
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"].strip()

def enhance_prompt_list(sentences: list[str]) -> list[str]:
    enhanced = []
    for s in sentences:
        try:
            enhanced.append(call_groq(f"Convert the following educational sentence into a highly detailed, realistic, context-specific image prompt for a serious educational illustration. Avoid cartoon style. Focus on accuracy and relevance : {s}"))
        except Exception as e:
            print("[WARN] Groq failed for sentence enhancement:", e)
            try:
                enhanced.append(call_openrouter(f"Convert the following educational sentence into a highly detailed, realistic, context-specific image prompt for a serious educational illustration. Avoid cartoon style. Focus on accuracy and relevance: {s}"))
            except Exception as e2:
                print("[ERROR] OpenRouter also failed:", e2)
                enhanced.append(s)  # fallback: use raw sentence
    return enhanced
