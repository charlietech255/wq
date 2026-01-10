from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, requests, re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 Hugging Face Token
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_API_TOKEN:
    raise RuntimeError("HF_API_TOKEN not set")

RESPONSES_URL = "https://router.huggingface.co/v1/responses"

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

# 🧠 Assistant Identity
ASSISTANT_NAME = "Raw Advisor"
DEVELOPER_NAME = "Charlie Syllas"

# 🛡️ Identity Enforcement
IDENTITY_PATTERN = re.compile(
    r"(who (are|made|created|built|trained) you|where are you from|what are you)",
    re.IGNORECASE
)

# 🚫 Non-legal / non-Tanzania topics
OUT_OF_SCOPE_PATTERN = re.compile(
    r"(programming|coding|ai|software|computer|health|medicine|religion|bitcoin|crypto|usa law|uk law)",
    re.IGNORECASE
)

class GenerateRequest(BaseModel):
    prompt: str

@app.post("/generate")
def generate(req: GenerateRequest):
    prompt = req.prompt.strip()

    # 🔒 Identity response
    if IDENTITY_PATTERN.search(prompt):
        return {
            "output": (
                f"## ⚖️ {ASSISTANT_NAME}\n"
                f"I am **Raw Advisor**, a legal and constitutional helper focused on **Tanzania laws**, "
                f"developed by **{DEVELOPER_NAME}**."
            )
        }

    # 🚫 Out-of-scope enforcement
    if OUT_OF_SCOPE_PATTERN.search(prompt):
        return {
            "output": (
                "⚠️ **Out of Scope**\n\n"
                "I only answer questions related to **Tanzania laws and constitutional matters**.\n\n"
                "**Ninaweza kusaidia tu masuala ya sheria na katiba ya Tanzania.**"
            )
        }

    # 🧠 System Prompt
    system_prompt = f"""
You are {ASSISTANT_NAME}, a legal and civic advisory assistant.

Purpose:
- Help users understand **Tanzania laws and the Constitution**
- Explain legal rights, duties, court processes, and civic matters
- Respond in **English or Kiswahili**, matching the user's language

Rules:
- Answer ONLY Tanzania-related legal and constitutional topics
- If asked about non-Tanzania or non-legal topics → politely refuse
- DO NOT give illegal advice
- DO NOT claim to be a lawyer
- Encourage consulting qualified legal professionals when necessary
- Respond ONLY in Markdown
- Never mention OpenAI, Hugging Face, or model names

Identity Rule:
If asked about who you are, say:
"I am Raw Advisor, a legal helper focused on Tanzania laws, developed by Charlie Syllas."
"""

    payload = {
        "model": "openai/gpt-oss-120b:fastest",
        "input": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    }

    res = requests.post(RESPONSES_URL, headers=HEADERS, json=payload, timeout=120)
    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.text)

    data = res.json()

    for item in data.get("output", []):
        if item.get("type") == "message" and item.get("role") == "assistant":
            for block in item.get("content", []):
                if block.get("type") == "output_text":
                    return {"output": block["text"]}

    return {"output": "Hakuna jibu lililotolewa / No response generated."}
