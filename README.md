# SmartLife AI Assistant

An intelligent personal assistant powered by Google Gemini 2.5 Flash, built for the Indian context.

## What it does
- Career guidance & job interview preparation
- Finance & budget planning (Indian rupee context)
- Study planning & exam preparation
- Life advice & decision making
- LinkedIn post writing help

## Tech Stack
- Python + FastAPI (backend)
- Google Gemini 2.5 Flash API
- HTML/CSS/JS (frontend)
- Docker + Google Cloud Run (deployment)

## How to run locally
```bash
export GEMINI_API_KEY="your_key_here"
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080
Live Demo
https://smartlife-ai-113032201251.us-central1.run.app
Architecture
User sends message → FastAPI backend → Gemini 2.5 Flash API → Response with Indian context
Challenge Vertical
Smart dynamic assistant with logical decision making based on user context, using Google Gemini as the core Google Service.
