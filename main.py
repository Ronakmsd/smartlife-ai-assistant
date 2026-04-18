import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

# Store conversation history (in-memory for this project)
conversation_history = []

SYSTEM_PROMPT = """You are a highly intelligent, empathetic, and smart personal assistant. 
Your primary goal is to provide exceptional advice and guidance on career, finance, study, and life matters, 
specifically tailored to an Indian context. 
Be exceptionally helpful, providing structured, actionable, and culturally relevant advice."""

api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.get("/")
async def get_index():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>index.html not found</h1>", status_code=404)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    global conversation_history
    
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set. Please set the environment variable.")
    
    user_msg = request.message
    
    try:
        # Build history for Gemini
        formatted_history = []
        for msg in conversation_history:
            formatted_history.append({"role": msg["role"], "parts": [msg["text"]]})
            
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=SYSTEM_PROMPT
        )
        
        chat = model.start_chat(history=formatted_history)
        response = chat.send_message(user_msg)
        reply = response.text
        
        # Update history
        conversation_history.append({"role": "user", "text": user_msg})
        conversation_history.append({"role": "model", "text": reply})
        
        # Keep last 10 messages (5 user + 5 model = 10 entries)
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
            
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
