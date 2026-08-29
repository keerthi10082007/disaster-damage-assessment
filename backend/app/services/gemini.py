"""Gemini AI service for analysis and explanation"""

import google.generativeai as genai
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.schemas.ai import AIAnalysisResponse
from app.utils.errors import AIError
import os
import json


class GeminiService:
    """Service for AI-powered analysis using Google Gemini"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name="gemini-pro",
                generation_config={
                    "temperature": 0.2,  # Lower temperature for more factual responses
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 2000
                }
            )
            self.available = True
        else:
            self.available = False
            self.model = None
    
    async def analyze_disaster(self, location_name: str, latitude: float, longitude: float,
                              analysis_data: Dict[str, Any]) -> AIAnalysisResponse:
        """Analyze disaster using Gemini AI"""
        
        if not self.available:
            return AIAnalysisResponse(
                situation_summary="Gemini AI service not configured.",
                detected_disaster="Unknown",
                damage_summary="Unable to assess without AI service.",
                change_analysis="N/A",
                priority_explanation="Unable to explain without AI service.",
                recommended_response="Recommended action pending configuration.",
                data_sources=[],
                data_limitations=["Gemini API not configured"],
                timestamp=datetime.utcnow().isoformat()
            )
        
        try:
            # Build analysis context
            analysis_context = self._build_context(location_name, latitude, longitude, analysis_data)
            
            # Get situation summary
            situation_summary = await self._get_summary(analysis_context)
            
            # Get damage summary
            damage_summary = await self._get_damage_assessment(analysis_data.get("damage_data", {}))
            
            # Get change analysis
            change_analysis = await self._get_change_analysis(analysis_data.get("imagery_data", {}))
            
            # Get priority explanation
            priority_explanation = await self._get_priority_explanation(analysis_data.get("priority_data", {}))
            
            # Get recommended response
            recommended_response = await self._get_recommended_response(
                analysis_data.get("disaster_type", "Unknown"),
                analysis_data.get("damage_data", {})
            )
            
            # Get data sources
            data_sources = self._extract_data_sources(analysis_data)
            
            # Get data limitations
            data_limitations = self._extract_data_limitations(analysis_data)
            
            return AIAnalysisResponse(
                situation_summary=situation_summary,
                detected_disaster=analysis_data.get("disaster_type", "Unknown"),
                damage_summary=damage_summary,
                change_analysis=change_analysis,
                priority_explanation=priority_explanation,
                recommended_response=recommended_response,
                data_sources=data_sources,
                data_limitations=data_limitations,
                timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            raise AIError(f"Gemini analysis failed: {str(e)}")
    
    def _build_context(self, location_name: str, latitude: float, longitude: float,
                      analysis_data: Dict[str, Any]) -> str:
        """Build context for Gemini analysis"""
        return f"""
Disaster Analysis Report
Location: {location_name} ({latitude}, {longitude})
Disaster Type: {analysis_data.get('disaster_type', 'Unknown')}

Available Data:
{json.dumps(analysis_data, indent=2)}

Instructions:
1. Use ONLY the supplied data above
2. Never invent numerical values
3. Never invent events or imagery
4. Clearly state if information is unavailable
5. Distinguish between observed data and interpretation
"""
    
    async def _get_summary(self, context: str) -> str:
        """Get situation summary from Gemini"""
        try:
            prompt = f"{context}\n\nProvide a brief 2-3 sentence situation summary based ONLY on the data above."
            response = self.model.generate_content(prompt)
            return response.text if response else "Unable to generate summary."
        except:
            return "Situation summary unavailable."
    
    async def _get_damage_assessment(self, damage_data: Dict[str, Any]) -> str:
        """Get damage assessment from Gemini"""
        try:
            if not damage_data:
                return "No damage assessment data available."
            
            prompt = f"""
Based on the following damage data:
{json.dumps(damage_data, indent=2)}

Provide a summary of the damage. Use only the values provided. If a value is missing, state that it is unavailable.
"""
            response = self.model.generate_content(prompt)
            return response.text if response else "Unable to generate damage assessment."
        except:
            return "Damage assessment unavailable."
    
    async def _get_change_analysis(self, imagery_data: Dict[str, Any]) -> str:
        """Get change analysis from Gemini"""
        try:
            if not imagery_data:
                return "No imagery data available for change analysis."
            
            prompt = f"""
Based on satellite imagery comparison data:
{json.dumps(imagery_data, indent=2)}

Describe the observed changes between historical and current imagery. Distinguish between confirmed damage and other changes (e.g., seasonal vegetation, water levels).
"""
            response = self.model.generate_content(prompt)
            return response.text if response else "Unable to generate change analysis."
        except:
            return "Change analysis unavailable."
    
    async def _get_priority_explanation(self, priority_data: Dict[str, Any]) -> str:
        """Get priority explanation from Gemini"""
        try:
            if not priority_data:
                return "No priority data available."
            
            prompt = f"""
Based on the priority assessment:
{json.dumps(priority_data, indent=2)}

Explain why this location has been assigned this priority level for emergency response.
"""
            response = self.model.generate_content(prompt)
            return response.text if response else "Unable to explain priority."
        except:
            return "Priority explanation unavailable."
    
    async def _get_recommended_response(self, disaster_type: str, damage_data: Dict[str, Any]) -> str:
        """Get recommended response from Gemini"""
        try:
            prompt = f"""
For a {disaster_type} disaster with the following characteristics:
{json.dumps(damage_data, indent=2)}

Provide specific, actionable emergency response recommendations. Base recommendations ONLY on the data provided.
"""
            response = self.model.generate_content(prompt)
            return response.text if response else "Unable to generate recommendations."
        except:
            return "Response recommendations unavailable."
    
    def _extract_data_sources(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Extract data sources from analysis"""
        sources = []
        
        if analysis_data.get("imagery_data", {}).get("source"):
            sources.append(f"Satellite Imagery: {analysis_data['imagery_data']['source']}")
        
        if analysis_data.get("disaster_events"):
            sources.append("Disaster Events: NASA EONET")
        
        if analysis_data.get("damage_data"):
            sources.append(f"Damage Assessment: {analysis_data['damage_data'].get('model', 'Unknown')}")
        
        if analysis_data.get("population_data"):
            sources.append(f"Population Data: {analysis_data['population_data'].get('source', 'Unknown')}")
        
        if analysis_data.get("infrastructure_data"):
            sources.append(f"Infrastructure: {analysis_data['infrastructure_data'].get('source', 'Unknown')}")
        
        return sources if sources else ["Multiple available sources"]
    
    def _extract_data_limitations(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Extract data limitations from analysis"""
        limitations = []
        
        if not analysis_data.get("imagery_data"):
            limitations.append("Satellite imagery not available")
        
        if not analysis_data.get("disaster_events"):
            limitations.append("No active disaster events detected")
        
        if not analysis_data.get("damage_data"):
            limitations.append("Damage assessment model not configured")
        
        if not analysis_data.get("population_data"):
            limitations.append("Population data not available")
        
        if not analysis_data.get("infrastructure_data"):
            limitations.append("Infrastructure data incomplete")
        
        return limitations if limitations else ["All available data sources integrated"]


# Global instance
gemini_service = GeminiService()
