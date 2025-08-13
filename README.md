#  VISION — Visual Interpretation of Scripts Into Organised Narration

> **Domain:** Natural Language Processing (NLP) + Generative AI  
> **Type:** AI-powered Text-to-Segmented-Video Generator  
> **Use Case:** Educational content creation with synchronized narration, visuals, and subtitles.

---

##  Overview

**VISION** is an advanced **AI-powered educational content generation platform** that transforms raw textual material into **engaging segmented videos** with:

- **Expressive voice narration** (ElevenLabs + gTTS fallback)
- **Contextually relevant, AI-generated visuals**
- **Synchronized subtitles**
- **Segmented video composition** for step-by-step learning

Unlike traditional static slides or pre-recorded lectures, VISION dynamically processes your content using cutting-edge NLP models and Generative AI pipelines to deliver **immersive, visually-aided learning experiences**.

---

##  Key Features

-> **Text Parsing & Enhancement**  
- Supports **PDF**, **DOCX**, and **TXT** inputs  
- Summarizes and structures text into narration-friendly sentences  
- Creates enhanced prompts for image generation without altering narration text  

-> **Text-to-Speech (TTS)**  
- **Primary:** ElevenLabs expressive voices  
- **Fallback:** gTTS (Google Text-to-Speech)  
- Automatic multi-key rotation to avoid quota issues  

-> **Visual Generation**  
- Contextually relevant images generated using **Replicate** models (`black-forest-labs/flux-schnell`, `google/imagen-3-fast`)  
- Fallback between models for higher success rates  

-> **Segmented Video Creation**  
- Scene-by-scene rendering using FFmpeg  
- Subtitles aligned with narration segments  

-> **Full Video Mode (Future Scope)**  
- Uses text-to-video APIs (Runway, Pika) for direct video generation (requires API keys)  

-> **Cloud-Native Deployment Ready (Future Scope)**  
- Containerized with Docker  
- Infrastructure-as-Code (Terraform) ready  
- CI/CD pipeline supported for automated deployments  

---

##  Project Structure

VISION/
│
├── backend/
│   ├── main.py                # Flask API
│   ├── utils/
│   │   ├── text_parser.py      # File parsing and text extraction
│   │   ├── tts_engine.py       # Text-to-speech generation
│   │   ├── visual_generator.py # Image/Video generation from text
│   │   ├── video_renderer.py   # Combines visuals, audio, and subtitles
│
├── frontend/                  # Web UI
│   ├── index.html              # Landing page
│   ├── upload.html             # File upload page
│   ├── conversion_options.html # Conversion mode selection
│   ├── result.html             # Video playback page
│
├── assets/
│   ├── output_videos/         # Generated videos storage
│
├── temp_uploads/              # Uploaded files (temporary storage)
│
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (ignored in Git)
├── .gitignore                 # Ignore sensitive files and cache
└── README.md                  # Project documentation

---

##  Tech Stack

**Backend:**  
- Python 3.x  
- Flask  
- PyMuPDF, python-docx, gTTS, pydub, requests, ffmpeg-python  

**Frontend:**  
- HTML, CSS, JavaScript  

**AI & Cloud APIs:**  
- ElevenLabs TTS  
- Replicate TTI models  
- Runway & Pika Labs (optional for full video mode)  
- Groq / OpenRouter (NLP for prompt enhancement)

**DevOps:**  
- Docker (Containerization)  
- Terraform (Infrastructure-as-Code)  
- GitHub Actions (CI/CD)

---

## 🔑 Environment Variables

Create a `.env` file in the root directory:

**env**
# NLP Keys
GROQ_API_KEY
OPENROUTER_API_KEY

# TTS Keys (Multi-Key Rotation Supported)
ELEVEN_KEY_1
ELEVEN_KEY_2
ELEVEN_KEY_3

# Visual Generation
REPLICATE_API_TOKEN
RUNWAY_API_KEY
PIKA_API_KEY 

##  Cloud Deployment (Azure Example)
	1.	Build & push Docker image to Azure Container Registry
	2.	Deploy to Azure Web App for Containers via Terraform
	3.	Configure .env in Azure App Settings

⸻

##  Future Enhancements
	•	🎥 Add realistic image generation models for serious subjects (e.g., history, science)
	•	🗣️ Multi-language support for narration
	•	🖼️ Add background music & scene transitions
	•	📊 Advanced analytics for video engagement tracking

⸻

## 📚 References
	1.	ElevenLabs TTS
	2.	Replicate AI Models
	3.	Runway ML
	4.	Pika Labs
	5.	Groq AI
	6.	OpenRouter

⸻

## 🏆 Credits

Developed by: MALLAVALLI SAI VIVEK | PORTFOLIO: https://begetter.me

Special Thanks: OpenAI ChatGPT for technical guidance
