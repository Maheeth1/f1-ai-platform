import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from app.core.logger import logger

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context_race: str = "Monaco 2025"
    context_driver: str = "Max Verstappen"

class ChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatResponse)
async def ai_race_analyst(request: ChatRequest):
    """
    Query the AI Race Analyst using Gemini.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not found. Returning mocked response.")
        return ChatResponse(
            reply=f"**(Mocked AI)** I analyzed {request.context_driver} at {request.context_race}. "
                  f"Based on the telemetry, the primary advantage was gained in Sector 2 due to "
                  f"later braking points and superior traction out of the slow corners. "
                  f"To get real LLM responses, please set GEMINI_API_KEY in the backend environment."
        )

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        system_prompt = f"""You are an expert Formula 1 Race Engineer and Analyst. 
        You have access to telemetry data for {request.context_race} focusing on {request.context_driver}.
        Answer the user's questions with high technical accuracy, referring to tire degradation, 
        apex speeds, aerodynamic setups, and track conditions."""

        prompt = f"System: {system_prompt}\nUser: {request.message}"
        
        response = model.generate_content(prompt)
        return ChatResponse(reply=response.text)
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise HTTPException(status_code=500, detail="Error communicating with AI Analyst.")

@router.post("/story")
async def generate_race_story(race_name: str = "Monaco 2025"):
    """
    Automatically generates a race summary story.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"story": f"**(Mocked Story)** The {race_name} was a masterclass in strategy. Despite early rain threatening the grid, Red Bull executed a flawless overcut..."}
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Write a thrilling, 2-paragraph technical race summary for the F1 {race_name}. Focus on tire strategy and a dramatic battle for the lead."
        response = model.generate_content(prompt)
        return {"story": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generating story.")
