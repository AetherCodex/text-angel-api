from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import json
import os
import re

app = FastAPI()

# Allow all CORS (for dev use, can be secured later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load filter words once
with open("shield_filter_words.json", "r") as f:
    CENSORED_WORDS = json.load(f)

# === Schemas ===
class RewriteRequest(BaseModel):
    message: str
    tone: str

class ShieldRequest(BaseModel):
    message: str

# === Rewrite Endpoint ===
@app.post("/rewrite")
async def rewrite_text(req: RewriteRequest):
    prompt = f"Rewrite the following message with a tone of {req.tone}:\n\n\"{req.message}\""
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content
        return {"result": reply}
    except Exception as e:
        return {"error": f"OpenAI call failed: {str(e)}"}

# === Shield Endpoint ===
@app.post("/shield")
async def shield_text(req: ShieldRequest):
    message = req.message
    shielded = message
    count = 0

    for word in CENSORED_WORDS:
        regex = re.compile(re.escape(word), re.IGNORECASE)
        matches = regex.findall(shielded)
        if matches:
            count += len(matches)
            shielded = regex.sub("🛡️", shielded)

    return {"shielded": shielded, "count": count}
