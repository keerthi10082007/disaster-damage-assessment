"""Emergency priority calculation service"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schemas.priority import PriorityResult, PriorityResponse, PriorityFactor


class PriorityService:
    """Service for calculating emergency response priority"""
    
    async def calculate_priority(self, latitude: float, longitude: float,
                                damage_severity: Optional[str] = None,
                                population_exposure: Optional[int] = None,
                                affected_area: Optional[float] = None,
                                infrastructure_impact: Optional[List[str]] = None,
                                accessibility: Optional[str] = None) -> PriorityResponse:
        """Calculate emergency priority score deterministically"""
        
        score = 0.0
        factors_used = []
        unavailable_factors = []
        reason_parts = []
        
        # Factor 1: Damage Severity (40% weight)
        if damage_severity:
            severity_scores = {
                "Critical": 40,
                "High": 30,
                "Medium": 15,
                "Low": 5
            }
            severity_score = severity_scores.get(damage_severity, 0)
            score += severity_score
            factors_used.append(PriorityFactor(
                name="Damage Severity",
                value=damage_severity,
                weight=0.4,
                contribution=severity_score
            ))
            reason_parts.append(f"{damage_severity} damage severity")
        else:
            unavailable_factors.append("Damage Severity")
        
        # Factor 2: Population Exposure (30% weight)
        if population_exposure is not None:
            # Scale population to 0-30 points
            pop_score = min(30, (population_exposure / 1000) * 3)
            score += pop_score
            factors_used.append(PriorityFactor(
                name="Population Exposure",
                value=population_exposure,
                weight=0.3,
                contribution=pop_score
            ))
            reason_parts.append(f"significant population exposure ({population_exposure:,} people)")
        else:
            unavailable_factors.append("Population Exposure")
        
        # Factor 3: Affected Area (15% weight)
        if affected_area is not None:
            # Scale area to 0-15 points
            area_score = min(15, (affected_area / 10) * 3)
            score += area_score
            factors_used.append(PriorityFactor(
                name="Affected Area",
                value=affected_area,
                weight=0.15,
                contribution=area_score
            ))
            reason_parts.append(f"large affected area ({affected_area:.1f} sq km)")
        else:
            unavailable_factors.append("Affected Area")
        
        # Factor 4: Infrastructure Impact (10% weight)
        if infrastructure_impact:
            # Each critical infrastructure adds 2-3 points
            infra_score = min(10, len(infrastructure_impact) * 2)
            score += infra_score
            factors_used.append(PriorityFactor(
                name="Critical Infrastructure Impact",
                value=infrastructure_impact,
                weight=0.1,
                contribution=infra_score
            ))
            reason_parts.append(f"critical infrastructure impacted ({', '.join(infrastructure_impact[:3])})")
        else:
            unavailable_factors.append("Critical Infrastructure Impact")
        
        # Factor 5: Accessibility (5% weight)
        if accessibility:
            accessibility_scores = {
                "Severely Limited": 5,
                "Limited": 3,
                "Partial": 1,
                "Open": 0
            }
            access_score = accessibility_scores.get(accessibility, 0)
            score += access_score
            factors_used.append(PriorityFactor(
                name="Road Accessibility",
                value=accessibility,
                weight=0.05,
                contribution=access_score
            ))
            if access_score > 0:
                reason_parts.append(f"reduced road accessibility")
        else:
            unavailable_factors.append("Road Accessibility")
        
        # Determine priority level
        if score >= 70:
            level = "HIGH"
        elif score >= 40:
            level = "MEDIUM"
        else:
            level = "LOW"
        
        # Build reason text
        if reason_parts:
            reason = f"The available analysis indicates {', '.join(reason_parts)}. This assessment is based on {len(factors_used)} available data factors."
        else:
            reason = "Insufficient data available for priority assessment."
        
        if unavailable_factors:
            reason += f" Note: {', '.join(unavailable_factors)} data not available."
        
        result = PriorityResult(
            score=round(score, 1),
            level=level,
            factors_used=factors_used,
            unavailable_factors=unavailable_factors,
            reason=reason
        )
        
        return PriorityResponse(
            result=result,
            timestamp=datetime.utcnow().isoformat()
        )


# Global instance
priority_service = PriorityService()
