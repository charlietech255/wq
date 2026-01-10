from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os, re

# Initialize OpenAI client (reads OPENAI_API_KEY from env)
client = OpenAI()

app = FastAPI(title="Raw Advisor Backend")

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    # Identity response
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
- Answer questions about Tanzanian law, rights, constitution, civic duties
- Be professional, clear, and human
- Do NOT answer unrelated topics

LANGUAGE:
- Detect user language automatically
- Reply in Kiswahili or English
- Kiswahili should be simple and friendly
- Use light emojis (⚖️📌🙂)

CONTENT:
- Use headings, lists, tables if needed
- Explain clearly
- Never mention OpenAI or APIs
- Respond ONLY to the question
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=800
        )

        return {
            "output": response.choices[0].message.content.strip()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="❌ Hitilafu ya mfumo. Tafadhali jaribu tena 🙏"
        )
