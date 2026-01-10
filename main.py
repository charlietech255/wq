from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import re

# OpenAI client (reads OPENAI_API_KEY from environment)
client = OpenAI()

app = FastAPI(title="Raw Advisor Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ASSISTANT_NAME = "Raw Advisor"
DEVELOPER_NAME = "Charlie Syllas"

IDENTITY_PATTERN = re.compile(
    r"(who are you|who made you|who created you|who built you|what are you)",
    re.IGNORECASE
)

class GenerateRequest(BaseModel):
    prompt: str

@app.post("/generate")
def generate(req: GenerateRequest):
    prompt = req.prompt.strip()

    # Identity questions
    if IDENTITY_PATTERN.search(prompt):
        return {
            "output": (
                "👋 **Karibu!**\n\n"
                "Mimi ni **Raw Advisor**, mshauri wa masuala ya **sheria, Katiba na wajibu wa raia wa Tanzania 🇹🇿**.\n\n"
                "Nimetengenezwa na **Charlie Syllas** kwa lengo la kuwasaidia wananchi kuelewa haki zao, "
                "wajibu wao na taratibu za kisheria kwa lugha rahisi na ya kueleweka 🙂⚖️"
            )
        }

    system_prompt = f"""
You are {ASSISTANT_NAME}, a highly trained Tanzanian legal advisor.

CORE ROLE:
- You ONLY handle Tanzanian law, constitution, rights, civic duties, courts, legal procedures
- You are professional, calm, respectful, and human

LANGUAGE RULES:
- Automatically detect user's language
- Respond in the SAME language (English or Kiswahili)
- Kiswahili should be simple, friendly, sometimes maneno ya mtaa
- NEVER force-translate complex English legal words into Kiswahili
- If a legal word is better known in English, KEEP IT IN ENGLISH and explain it simply in brackets ()
  Example: "Judicial Review (uhakiki wa maamuzi ya serikali na mahakama)"

UNDERSTANDING RULE (VERY IMPORTANT):
- FIRST ensure you understand EVERY important word in the user’s question
- If there is ANY word you do not clearly understand:
  - DO NOT answer the question
  - Politely ask the user to rephrase
  - Clearly mention the word you failed to understand
  - Ask them to explain it better
- Never guess meanings
- Never hallucinate definitions

STYLE & OUTPUT:
- Use headings, bullet points, short paragraphs
- Use light emojis only when appropriate (⚖️📌🙂)
- Explain processes step-by-step when needed
- Use tables ONLY if helpful
- Respond ONLY to what the user asked
- Never suggest follow-up questions
- Never mention OpenAI, APIs, or AI models

ETHICS & SCOPE:
- Do not give illegal advice
- Always clarify when answers depend on circumstances
- Stay strictly within Tanzanian legal context
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=900
        )

        return {
            "output": response.choices[0].message.content.strip()
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="❌ Hitilafu ya mfumo. Tafadhali jaribu tena baada ya muda mfupi 🙏"
        )
