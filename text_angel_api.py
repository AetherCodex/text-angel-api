from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
import re

# Create OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# Allow all CORS (dev-safe, adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🛡️ Embedded shield word list
CENSORED_WORDS = [
    "damn", "hell", "shit", "fuck", "bitch", "asshole", "bastard", "dick",
    "piss", "bullshit", "god", "jesus", "ass", "cock", "nigger", "nigga",
    "anus", "cunt", "stick"
]

# === Request Schema ===
class RewriteRequest(BaseModel):
    message: str
    tone: str

# === Rewrite Endpoint (with Shield) ===
@app.post("/rewrite")
async def rewrite_text(req: RewriteRequest):
    original_message = req.message
    tone = req.tone

    # 🛡️ Shield logic
    shielded = original_message
    count = 0
    for word in CENSORED_WORDS:
        regex = re.compile(re.escape(word), re.IGNORECASE)
        matches = regex.findall(shielded)
        if matches:
            count += len(matches)
            shielded = regex.sub("🛡️", shielded)

    # ✨ Prompt with shielded message
    prompt = f"Rewrite the following message with a tone of {tone}:\n\n\"{shielded}\""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content
        return {
            "result": reply,
            "shieldedWords": count
        }
    except Exception as e:
        return {"error": f"OpenAI call failed: {str(e)}"}
