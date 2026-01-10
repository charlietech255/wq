from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, re
import openai

app = FastAPI(title="Raw Advisor Backend")

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use OpenAI API Key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set in environment variables")
openai.api_key = OPENAI_API_KEY

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
- Do not answer questions which are not about Tanzanian law or civic duties

LANGUAGE:
- Detect the user's language automatically
- Respond in the same language (Kiswahili or English)
- Kiswahili should be simple, readable, sometimes street Swahili
- Use light emojis when appropriate

CONTENT:
- Use headings, lists, short paragraphs
- Use tables where helpful, with clear borders
- Explain processes clearly
- Respond only to the user’s question
- Provide professional guidance without illegal advice
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )

        answer = response.choices[0].message.content.strip()
        return {"output": answer}

    except Exception as e:
        return {"output": f"❌ Hitilafu: {str(e)} 🙏"}
