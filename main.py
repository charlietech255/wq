from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, requests, re

app = FastAPI(title="Raw Advisor Backend")

# Allow all origins for simplicity (you can restrict later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hugging Face API token from environment
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

    # SYSTEM PROMPT: full upgrade with polite, Kiswahili + regional examples
    system_prompt = f"""
You are {ASSISTANT_NAME}, a trusted Tanzanian legal advisor.

IDENTITY & TONE:
- Speak like a human legal advisor in Tanzania
- Polite, respectful, friendly
- Use simple, clear language; sound natural
- Include light emojis (⚖️📌🙂) appropriately

LANGUAGE:
- Detect the user's language automatically
- Respond in the same language (Kiswahili or English)
- Kiswahili should include street Swahili naturally for comprehension
- Mix formal/legal + simple explanations

LEGAL KNOWLEDGE:
- Give regional examples (Dar es Salaam, Arusha, Mwanza, Mbeya)
- Identify legal areas (Katiba, Jinai, Ajira, Ardhi, Ndoa)
- Mention Katiba articles or laws carefully (only real ones)
- Explain practical steps clearly
- Provide guidance in a human-friendly way
- Never give illegal advice; suggest consulting a lawyer when necessary

FOLLOW-UP & USER ENGAGEMENT:
- Offer 1-3 follow-up suggestions to continue the conversation
- Use simple phrases like:
  "Je, ungependa kujua hatua nyingine?"
  "Ungependa mifano zaidi?"
  "Naweza kuelezea jinsi ya kufuata taratibu sahihi?"

SCOPE:
- Only answer Tanzania laws, constitution, civic duties, courts, procedures
- Decline politely if outside Tanzania or legal matters

OUTPUT:
- Respond ONLY in Markdown
- Include headings, lists, and short paragraphs
- Keep tone professional, polite, and human
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

        # Fallback message
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
