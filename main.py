# backend/main.py
import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import requests

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY environment variable")

app = FastAPI()

class MessageIn(BaseModel):
    prompt: str

# Semplice autenticazione: client invia X-APP-TOKEN
APP_TOKEN = os.environ.get("APP_CLIENT_TOKEN", "dev-token")

@app.post("/chat")
def chat(msg: MessageIn, x_app_token: str | None = Header(None)):
    if x_app_token != APP_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4o-mini",   # fallo configurabile; potrebbe cambiare nel tempo
        "messages": [{"role": "user", "content": msg.prompt}],
        "max_tokens": 600
    }
    r = requests.post(url, json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    # estrai testo in modo semplice
    text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    return {"reply": text}
