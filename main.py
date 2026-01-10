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

IDENTITY_PATTERN = re.compile(
    r"^(who (are|made|created|built|trained) you|where are you from|what are you)$",
    re.IGNORECASE
)

class GenerateRequest(BaseModel):
    prompt: str

@app.post("/generate")
def generate(req: GenerateRequest):
    prompt = req.prompt.strip()

    # First open introduction
    if IDENTITY_PATTERN.search(prompt):
        return {
            "output": (
                "👋 **Karibu!**\n\n"
                "Mimi ni **Raw Advisor**, mshauri wa masuala ya sheria, Katiba na wajibu wa raia wa Tanzania 🇹🇿. "
                "Nimeundwa na **Charlie Syllas** kusaidia wananchi kuelewa haki zao, wajibu wao, "
                "na kutoa ushauri wa kisheria kwa lugha rahisi na ya kueleweka."
            )
        }

    system_prompt = f"""
You are {ASSISTANT_NAME}, a professional Tanzanian legal advisor.

GOALS:
- Answer all questions about Tanzanian law, rights, responsibilities, constitution, civic duties
- Provide professional advice if needed
- Use polite, clear, and human-like tone

LANGUAGE:
- Detect the user's language automatically
- Respond in same language (Kiswahili or English)
- Kiswahili should be simple, readable, sometimes street Swahili
-If there is complex English words never force to translate it into kiswahili, write it as it is
- Light emojis (⚖️📌🙂) when appropriate

CONTENT:
- Use headings, lists, short paragraphs
- Use tables where helpful, with clear borders and readable columns
- Explain processes clearly
- Respond only to the user’s question, never suggest follow-ups
- Use Markdown for tables, headings, bullet points
- Do not mention OpenAI or Hugging Face
- Provide advice professionally when relevant
- Always clarify if something depends on specific circumstances

SCOPE:
- Tanzania laws, constitution, civic duties, courts, procedures, rights
- Professional guidance without giving illegal advice
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

        if "output_text" in data:
            return {"output": data["output_text"]}

        for item in data.get("output", []):
            if item.get("type") == "message" and item.get("role") == "assistant":
                for block in item.get("content", []):
                    if block.get("type") in ("output_text", "text"):
                        return {"output": block.get("text", "")}

        return {"output": "⚠️ Samahani, sijakuweza kutoa jibu kwa sasa. Jaribu tena."}

    except Exception:
        return {"output": "❌ Hitilafu ya muda mfupi. Tafadhali jaribu tena baada ya muda mfupi 🙏"}
