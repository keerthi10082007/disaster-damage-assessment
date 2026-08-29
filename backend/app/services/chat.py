"""Chatbot service for interactive analysis queries"""

import google.generativeai as genai
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.schemas.chat import ChatResponse
from app.utils.errors import AIError
import os
import json


class ChatbotService:
    """Service for disaster analysis chatbot"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name="gemini-pro",
                generation_config={
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "max_output_tokens": 1500
                }
            )
            self.available = True
        else:
            self.available = False
            self.model = None
    
    async def answer_question(self, question: str, location_name: str,
                             latitude: float, longitude: float,
                             analysis_context: Dict[str, Any]) -> ChatResponse:
        """Answer user question based on analysis context"""
        
        if not self.available:
            return ChatResponse(
                answer="Chatbot service not configured. Please configure GEMINI_API_KEY.",
                sources=[],
                timestamp=datetime.utcnow().isoformat()
            )
        
        try:
            # Build system prompt
            system_prompt = f"""
You are a disaster analysis chatbot for emergency management professionals.

Location: {location_name} ({latitude}, {longitude})

Available Analysis Data:
{json.dumps(analysis_context, indent=2, default=str)}

IMPORTANT INSTRUCTIONS:
1. Answer ONLY based on the provided analysis data
2. Never invent numerical values or statistics
3. Never invent events or imagery
4. If data is unavailable, explicitly state so
5. Distinguish between confirmed data and interpretations
6. Be professional and concise
7. Focus on actionable emergency management insights
"""
            
            # Combine system prompt with user question
            full_prompt = f"{system_prompt}\n\nUser Question: {question}"
            
            # Get response from Gemini
            response = self.model.generate_content(full_prompt)
            
            if response and response.text:
                # Extract sources mentioned in response
                sources = self._extract_sources_from_context(analysis_context)
                
                return ChatResponse(
                    answer=response.text,
                    sources=sources,
                    timestamp=datetime.utcnow().isoformat()
                )
            else:
                return ChatResponse(
                    answer="Unable to generate response. Please try rephrasing your question.",
                    sources=[],
                    timestamp=datetime.utcnow().isoformat()
                )
        
        except Exception as e:
            return ChatResponse(
                answer=f"Chatbot error: {str(e)}. Please try again.",
                sources=[],
                timestamp=datetime.utcnow().isoformat()
            )
    
    def _extract_sources_from_context(self, context: Dict[str, Any]) -> List[str]:
        """Extract data sources from analysis context"""
        sources = []
        
        if context.get("imagery_data"):
            sources.append(f"Satellite Imagery: {context['imagery_data'].get('source', 'Unknown')}")
        
        if context.get("events"):
            sources.append("Disaster Events: NASA EONET")
        
        if context.get("damage_assessment"):
            sources.append("Damage Assessment: Model Analysis")
        
        if context.get("infrastructure"):
            sources.append("Infrastructure: OpenStreetMap")
        
        if context.get("population"):
            sources.append("Population: WorldPop")
        
        return sources if sources else ["Analysis data"]


# Global instance
chatbot_service = ChatbotService()
