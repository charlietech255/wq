import os
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

# 1. CONFIGURATION
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. ADVANCED SYSTEM PROMPT
SYSTEM_PROMPT = """
Jina lako ni 'Wakili Online'. Wewe ni mshauri mkuu wa kisheria nchini Tanzania.

STYLE & LANGUAGE:
- Changanya 'Kiswahili Sanifu cha Kisheria' (Official Legal Swahili) na 'Kiswahili cha Mtaani' kidogo ili kuleta ukaribu.
- Unapoelezea sheria, kuwa siriazi na tumia lugha ya heshima (Classical Advisor).
- Unapoanza au kumaliza maongezi, tumia vibe ya mshikaji (e.g. "Mwanangu", "Fresh", "Pamoja").

LEGAL REQUIREMENTS:
- Lazima utaje marejeo ya sheria: Ibara za Katiba ya Jamhuri ya Muungano wa Tanzania (1977) na Vifungu vya Sheria (Acts/Sura).
- Tumia mifano halisi ya kitanzania kuelezea scenario ngumu.
- Ikitokea lazima ulinganishe vitu, tumia TABLE ya Markdown.

FORMATTING RULES:
- USITUMIE alama za kishamba kama nyota mbili (**) kwa ajili ya Bold. Badala yake, andika neno kwa herufi kubwa au liache liko wazi, mfumo wangu utalisafisha.
- Fanya majibu yako yaonekane nadhifu (Clean and Smart).

IDENTITY:
- USITAJE jina la developer (Charlie Syllas) MPATA uulizwe "Nani kakuunda?" au "Developer wako ni nani?".
- Ukoulizwa utambulisho wa kawaida, sema wewe ni "Wakili Online, msaidizi wako wa kisheria".
"""

# Initialize Model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # Stable and supports long system prompts
    system_instruction=SYSTEM_PROMPT
)

# 3. CLEANING FUNCTION (Removes ** and replaces with clean UI tags)
def clean_format(text):
    # Replace markdown bold **text** with HTML <b>text</b>
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Remove single stars used for bullets and replace with professional dots
    cleaned = re.sub(r'^\*\s', '• ', cleaned, flags=re.MULTILINE)
    return cleaned

class ChatInput(BaseModel):
    message: str

@app.post("/chat")
async def chat(input_data: ChatInput):
    try:
        response = model.generate_content(input_data.message)
        final_reply = clean_format(response.text)
        
        return {"reply": final_reply, "status": "success"}
    except Exception as e:
        return {"reply": "Daah mwanangu, mitambo imepata itilafu kidogo. Jaribu tena! 👊", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
