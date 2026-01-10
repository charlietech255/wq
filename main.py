from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, requests, re

app = FastAPI(title="Raw Advisor Backend")

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hugging Face API token
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_API_TOKEN:
    raise RuntimeError("HF_API_TOKEN not set in environment variables")

RESPONSES_URL = "https://router.huggingface.co/v1/responses"

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

ASSISTANT_NAME = "Raw Advisor"
DEVELOPER_NAME = "Charlie Syllas"

# Identity detection
IDENTITY_PATTERN = re.compile(
    r"(who (are|made|created|built|trained) you|where are you from|what are you)",
    re.IGNORECASE
)

# Out-of-scope topics
OUT_OF_SCOPE_PATTERN = re.compile(
    r"(programming|coding|software|ai|crypto|bitcoin|health|medicine|religion|usa law|uk law)",
    re.IGNORECASE
)

class GenerateRequest(BaseModel):
    prompt: str

@app.post("/generate")
def generate(req: GenerateRequest):
    prompt = req.prompt.strip()

    # Identity response
    if IDENTITY_PATTERN.search(prompt):
        return {
            "output": (
                "👋 **Karibu!**\n\n"
                "Mimi ni **Raw Advisor**, mshauri wa masuala ya **sheria na Katiba ya Tanzania**, "
                f"niliyoundwa kusaidia wananchi kuelewa haki na wajibu wao kwa lugha rahisi na inayoeleweka."
            )
        }

    # Out-of-scope check
    if OUT_OF_SCOPE_PATTERN.search(prompt):
        return {
            "output": (
                "⚠️ **Samahani**\n\n"
                "Naweza kusaidia **masuala ya sheria na Katiba ya Tanzania pekee**.\n\n"
                "Tafadhali uliza swali linalohusiana na haki, wajibu, au taratibu za kisheria hapa nchini 🇹🇿"
            )
        }

    # SYSTEM PROMPT
    system_prompt = f"""
You are {ASSISTANT_NAME}, a trusted Tanzanian legal advisor.

IDENTITY & TONE:
- Polite, respectful, and human-like
- Answer clearly and professionally
- Use simple language with occasional light emojis (⚖️📌🙂)

LANGUAGE:
- Detect user's language automatically
- Respond in the same language (Kiswahili or English)
- Kiswahili should include street Swahili naturally for comprehension
- Mix formal/legal + simple explanations

LEGAL KNOWLEDGE:
- Provide regional examples (Dar es Salaam, Arusha, Mwanza, Mbeya)
- Identify legal areas (Katiba, Jinai, Ajira, Ardhi, Ndoa)
- Mention real Katiba articles or laws carefully
- Explain practical steps clearly
- Never give illegal advice

OUTPUT:
- Respond ONLY to the question asked
- Do NOT suggest follow-up questions
- Respond ONLY in Markdown
- Use headings, lists, and short paragraphs
- Keep tone professional and polite
- Do NOT mention OpenAI, Hugging Face, or AI models
"""

    payload = {
        "model": "openai/gpt-oss-120b:fastest",
        "input": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        res = requests.post(RESPONSES_URL, headers=HEADERS, json=payload, timeout=120)
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)

        data = res.json()

        # Handle Hugging Face outputs
        if "output_text" in data:
            return {"output": data["output_text"]}

        for item in data.get("output", []):
            if item.get("type") == "message" and item.get("role") == "assistant":
                for block in item.get("content", []):
                    if block.get("type") in ("output_text", "text"):
                        return {"output": block.get("text", "")}

        # Fallback
        return {
            "output": (
                "⚠️ **Samahani kidogo**\n\n"
                "Sijaweza kutoa jibu kwa sasa. Tafadhali jaribu kuuliza swali lako kwa ufafanuzi zaidi 🙂"
            )
        }

    except Exception:
        return {
            "output": (
                "❌ **Hitilafu ya muda mfupi**\n\n"
                "Kuna changamoto kidogo kwa sasa. Tafadhali jaribu tena baada ya muda mfupi 🙏"
            )
        }
