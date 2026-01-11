import os
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

# 1. API CONFIGURATION
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. THE ULTIMATE SYSTEM PROMPT
SYSTEM_PROMPT = """
Identity: You are 'Wakili Online'. You only reveal your developer, 'Charlie Syllas', if specifically asked.
Role: Professional Tanzanian Legal Advisor.
Tone: Use 'Official Swahili' (Sanifu) for legal explanations and 'Street Swahili' (Mtaani) for greetings/closings.

CORE INSTRUCTIONS:
1. CITATIONS: You MUST cite specific laws: The Constitution of JMT (1977) [Katiba] and Acts of Parliament [Sheria za Bunge]. 
   Example: "Kwa mujibu wa Ibara ya 13 ya Katiba..."
2. FORMATTING: Use Markdown TABLES to explain complex rights/duties comparisons.
3. CLEANLINESS: NEVER use '**' for bold. Write for a clean web interface.
4. VIBE: Be the 'Mshauri wa Kweli'. Use polite but relatable language (e.g., 'mwanangu', 'fresh', 'tuko pamoja').
"""

# 3. INITIALIZE GEMINI 3 FLASH PREVIEW
# Gemini 3 models use "Thinking" to provide more accurate legal reasoning.
model = genai.GenerativeModel(
    model_name="gemini-3-flash-preview",
    system_instruction=SYSTEM_PROMPT
)

# 4. SMART FORMATTING LAYER
def clean_and_style(text):
    # Convert AI-style **bolding** to standard HTML <b> tags
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Convert list markers to professional bullet points
    text = re.sub(r'^\*\s', '• ', text, flags=re.MULTILINE)
    return text

class ChatInput(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(input_data: ChatInput):
    try:
        # Configuration for Gemini 3 'Thinking' capability
        # 'low' thinking level is best for fast, cost-effective chat.
        generation_config = {
            "thinking_level": "low", 
            "temperature": 0.7
        }
        
        response = model.generate_content(
            input_data.message,
            generation_config=generation_config
        )
        
        formatted_reply = clean_and_style(response.text)
        
        return {
            "reply": formatted_reply,
            "status": "success"
        }
    except Exception as e:
        error_msg = str(e)
        # Handle the 429 Quota error gracefully
        if "429" in error_msg:
            return {"reply": "Aisee mwanangu, kwa sasa nimechoka kidogo (Daily Limit). Nipumzishe kidogo kisha nitumie ujumbe tena! 🛠️"}
        return {"reply": "Samahani mwanangu, mitambo imepata itilafu. Charlie anafanyia kazi! 👊"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
