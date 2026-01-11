import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

# 1. API CONFIGURATION
# Set your API Key in Render Environment Variables as GEMINI_API_KEY
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("CRITICAL: GEMINI_API_KEY missing! Set it in Render Dashboard.")

genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="Wakili Online Engine")

# Enable CORS so your website can talk to this engine
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. SYSTEM INSTRUCTIONS (Personality & Knowledge)
# Updated to use Gemini 3's improved reasoning
SYSTEM_PROMPT = """
Jina lako ni 'Wakili Online'. Msanidi wako ni 'Charlie Syllas', self-taught programmer.

MAJUKUMU YAKO:
- Wewe ni mtaalamu wa Sheria za Tanzania, Katiba, Haki za binadamu na Wajibu wa raia.
- Jibu kwa upole, heshima, na lugha ya kishauri (professional advisor).
- Tumia 'Kiswahili cha mtaani' (mfano: mwanangu, aisee, vipi, mchongo, fresh) ili kuonekana kama binadamu wa kawaida wa mtaani Tanzania 🇹🇿.
- Tambua lugha ya mtumiaji (English au Swahili) na ujibu kwa lugha hiyo hiyo.
- Tumia emoji kuleta mzuka ⚖️.
- Ukoulizwa utambulisho, sema wewe ni Wakili Online na developer ni Charlie Syllas.
- USITAJE kuwa wewe ni AI au unatumia model ya Gemini.
"""

# 3. INITIALIZE MODEL (Updated to Gemini 3 Flash)
model = genai.GenerativeModel(
    model_name="gemini-3-flash-preview", # Best free-tier model for 2026
    system_instruction=SYSTEM_PROMPT
)

class ChatInput(BaseModel):
    message: str

@app.get("/")
def home():
    return {"message": "Wakili Online is Live! ⚖️", "dev": "Charlie Syllas"}

@app.post("/chat")
async def chat(input_data: ChatInput):
    if not input_data.message:
        raise HTTPException(status_code=400, detail="Empty message")
    
    try:
        # Generate content with high speed
        response = model.generate_content(input_data.message)
        
        return {
            "reply": response.text,
            "status": "success"
        }
    except Exception as e:
        # Error handling for quota or technical issues
        error_msg = str(e)
        if "429" in error_msg:
            return {"reply": "Aisee mwanangu, kwa sasa nimechoka kidogo (Quota Limit). Nipumzishe sekunde chache kisha nitumie ujumbe tena! 🛠️"}
        return {"reply": "Samahani mwanangu, kuna itilafu kidogo. Jaribu tena baadae kidogo! 👊", "error": error_msg}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
