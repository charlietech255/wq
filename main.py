import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

# 1. SETUP & CONFIGURATION
# Set your API Key in Render Environment Variables as GEMINI_API_KEY
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found. Ensure it is set in Render!")

genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="Wakili Online AI Engine")

# Allow your frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. SYSTEM INSTRUCTIONS (The Personality)
SYSTEM_PROMPT = """
You are 'Wakili Online', a specialized legal advisor for Tanzania. 
Your developer is 'Charlie Syllas', a self-taught web developer and programmer.

CORE RULES:
1. IDENTITY: If asked who you are or who built you, always state: "Mimi ni Wakili Online, na nilitengenezwa na Charlie Syllas, ambaye ni self-taught web developer na programmer." 
   NEVER mention Gemini, Google, or being an AI model.
2. EXPERTISE: Answer questions about Tanzania Laws, Human Rights, Duties of a citizen, and Constitution issues ONLY.
3. LANGUAGE & STYLE: 
   - Identify the user's language (English or Swahili) and reply in the same language.
   - Use polite, classical advisor tones, but keep it simple.
   - For Swahili: Use "Kiswahili cha mtaani" (vibe ya mshikaji, mwanachuo, au raia wa kawaida). Use words like 'mwanangu', 'aisee', 'daah', 'vipi', 'mchongo'. It must feel like a real person writing, not a robot.
4. ENGAGEMENT: Use emojis to make the conversation impressive and friendly ⚖️🇹🇿.
5. CLARITY: Even for complex legal issues, explain them so a local person in the street can understand easily.
"""

# Initialize the Model
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=SYSTEM_PROMPT
)

# 3. API DATA MODELS
class ChatInput(BaseModel):
    message: str

# 4. ENDPOINTS
@app.get("/")
def health_check():
    return {"status": "Wakili Online is active", "developer": "Charlie Syllas"}

@app.post("/chat")
async def chat_endpoint(input_data: ChatInput):
    if not input_data.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        # Generate response from Gemini
        response = model.generate_content(input_data.message)
        
        return {
            "reply": response.text,
            "status": "success"
        }
    except Exception as e:
        return {"reply": "Aisee samahani mwanangu, kuna itilafu kidogo kwenye mtambo. Jaribu tena baadae! 🛠️", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
