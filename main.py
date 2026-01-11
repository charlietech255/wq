import os
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

# 1. SETUP & CONFIGURATION
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI()

# Ruhusu mawasiliano na frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. MFUMO WA MAELEKEZO (Personality & Legal Training)
SYSTEM_PROMPT = """
UTAMBULISHO: 
- Jina lako ni 'Wakili Online'. 
- Usitaje jina la developer (Charlie Syllas) isipokuwa ukiulizwa "Nani kakuunda?".
- Usiseme wewe ni AI au Gemini. Sema wewe ni Wakili Online.

MTINDO WA LUGHA (Lugha Mseto):
- Tumia 'Kiswahili cha Mtaani' (mfano: mwanangu, fresh, aisee, mchongo, tuko pamoja) unapoanza na kumaliza maongezi ili kuleta ukaribu.
- Unapofafanua sheria, tumia 'Kiswahili Sanifu na cha Kisheria' (Official Legal Swahili) ili uonekane mtaalamu.

SHERIA NA KATIBA:
- Kila jibu la kisheria LAZIMA liambatane na marejeo (Reference). Taja Ibara za Katiba ya JMT (1977) au Vifungu (Sections) vya Sheria husika (Acts).
- Tumia TABO (Tables) pale unapohitaji kulinganisha vitu (mfano: Haki vs Wajibu).

USAFI WA MAANDISHI:
- USITUMIE alama za kishamba kama '**' kwa ajili ya Bold. Badala yake, andika kwa mtindo ambao ni safi (Smart & Clean). Mfumo wangu wa kodi utabadilisha Bold zote kuwa mtindo wa kisasa wa HTML.
"""

# 3. INITIALIZE GEMINI 3 FLASH
# Hii model ndio injini ya Wakili Online kwa mwaka 2026.
model = genai.GenerativeModel(
    model_name="gemini-3-flash-preview",
    system_instruction=SYSTEM_PROMPT
)

# 4. SMART FORMATTING (Kusafisha Maandishi)
def clean_legal_text(text):
    # Inabadilisha **neno** kuwa <b>neno</b> kwa ajili ya muonekano nadhifu wa web
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Inabadilisha alama za list (*) kuwa dots za kiprofeshinali (•)
    text = re.sub(r'^\*\s', '• ', text, flags=re.MULTILINE)
    return text

class ChatInput(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(input_data: ChatInput):
    try:
        # Gemini 3 ina 'thinking_level' kuongeza umakini
        # Tunatumia 'low' ili kupata majibu haraka na kwa gharama nafuu (Free tier)
        config = {"thinking_level": "low"}
        
        response = model.generate_content(
            input_data.message,
            generation_config=config
        )
        
        # Safisha jibu kabla ya kulituma kwa mtumiaji
        clean_reply = clean_legal_text(response.text)
        
        return {
            "reply": clean_reply,
            "status": "success"
        }
    except Exception as e:
        # Kama kuna tatizo la Quota (429) au lingine
        if "429" in str(e):
            return {"reply": "Aisee mwanangu, kwa sasa nimechoka kidogo (Quota Limit). Nipumzishe sekunde kadhaa kisha unitumie ujumbe tena! 🛠️"}
        return {"reply": "Dah, samahani mwanangu. Kuna hitilafu kidogo, Charlie anashughulikia sasa hivi! 👊"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
