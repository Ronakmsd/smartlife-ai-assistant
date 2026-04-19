from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
import logging
import time
import hashlib
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(_name_)

app = FastAPI(
    title="SmartLife AI Assistant",
    description="Intelligent assistant for Physical Event Experience powered by Google Gemini",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

rate_limit_store = defaultdict(list)

def check_rate_limit(ip: str) -> bool:
    now = time.time()
    rate_limit_store[ip] = [t for t in rate_limit_store[ip] if now - t < 60]
    if len(rate_limit_store[ip]) >= 20:
        return False
    rate_limit_store[ip].append(now)
    return True

def sanitize_input(text: str) -> str:
    for d in ['<script>', '</script>', 'javascript:', 'eval(', 'exec(']:
        text = text.replace(d, '')
    return text.strip()

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not set")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

response_cache = {}
conversation_history = []

SYSTEM_PROMPT = """You are SmartLife AI — an intelligent assistant for Physical Event Experience and life guidance in Indian context.

You specialize in:
1. Physical Event Planning — venue selection, logistics, attendee management, budget in INR
2. Career guidance — job interviews, resume tips, skill development
3. Finance planning — budgeting in Indian Rupees, investments, savings
4. Study planning — exam preparation, learning strategies
5. Life decisions and problem solving

Always provide structured, actionable advice. Be warm and encouraging."""

@app.get("/", response_class=HTMLResponse)
async def root():
    try:
        with open("index.html", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="index.html not found")

@app.post("/chat")
async def chat(request: Request):
    client_ip = request.client.host
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait.")
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    user_message = data.get("message", "")
    if not user_message or not user_message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if len(user_message) > 2000:
        raise HTTPException(status_code=400, detail="Message too long")
    user_message = sanitize_input(user_message)
    cache_key = hashlib.md5(user_message.encode()).hexdigest()
    if cache_key in response_cache:
        return {"reply": response_cache[cache_key], "status": "success", "cached": True}
    conversation_history.append({"role": "user", "parts": [user_message]})
    full_prompt = SYSTEM_PROMPT + "\n\nConversation:\n"
    for msg in conversation_history[-8:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        full_prompt += f"{role}: {msg['parts'][0]}\n"
    full_prompt += "Assistant:"
    start = time.time()
    try:
        response = model.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=1024,
                temperature=0.7,
            )
        )
        elapsed = time.time() - start
        logger.info(f"Gemini response in {elapsed:.2f}s")
        reply = response.text
        conversation_history.append({"role": "model", "parts": [reply]})
        if len(response_cache) < 100:
            response_cache[cache_key] = reply
        return {"reply": reply, "status": "success", "response_time": round(elapsed, 2)}
    except Exception as e:
        logger.error(f"Gemini error: {str(e)}")
        raise HTTPException(status_code=500, detail="AI service error. Please try again.")

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model": "gemini-2.5-flash",
        "service": "SmartLife AI Assistant",
        "version": "2.0.0",
        "google_services": ["Gemini API", "Cloud Run"]
    }

@app.get("/api/info")
async def info():
    return {
        "name": "SmartLife AI Assistant",
        "version": "2.0.0",
        "description": "Physical Event Experience + Life Assistant",
        "tech_stack": ["FastAPI", "Google Gemini 2.5 Flash", "Google Cloud Run", "Docker"],
        "features": ["event_planning", "career_guidance", "finance_planning", "study_help"]
    }
