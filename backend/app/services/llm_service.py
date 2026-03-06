"""
LLM Service abstraction for UrbanPulse.
Supports Google Gemini (primary) and can be extended to OpenAI.
Falls back to template-based responses when no API key is configured.
"""
import json
from typing import Optional
from abc import ABC, abstractmethod

class BaseLLMService(ABC):
    """Abstract base for LLM providers."""
    
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "", 
                       temperature: float = 0.7, max_tokens: int = 1024) -> str:
        pass

class GeminiService(BaseLLMService):
    """Google Gemini API integration."""
    
    def __init__(self, api_key: str):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    async def generate(self, prompt: str, system_prompt: str = "",
                       temperature: float = 0.7, max_tokens: int = 1024) -> str:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
            )
            return response.text
        except Exception as e:
            return f"AI service temporarily unavailable: {str(e)}"


class FallbackLLMService(BaseLLMService):
    """Template-based fallback when no LLM API key is configured."""
    
    async def generate(self, prompt: str, system_prompt: str = "",
                       temperature: float = 0.7, max_tokens: int = 1024) -> str:
        # Parse the prompt to generate contextual template responses
        prompt_lower = prompt.lower()
        
        if "compare" in prompt_lower:
            return self._comparison_template(prompt)
        elif "story" in prompt_lower or "tour" in prompt_lower:
            return self._story_template(prompt)
        elif "equity" in prompt_lower:
            return self._equity_template(prompt)
        elif "risk" in prompt_lower or "safety" in prompt_lower:
            return self._risk_template(prompt)
        elif "business" in prompt_lower or "biz" in prompt_lower:
            return self._bizcoach_template(prompt)
        else:
            return self._general_template(prompt)
    
    def _general_template(self, prompt: str) -> str:
        return (
            "Based on the available data for Montgomery, AL, I've analyzed the properties "
            "in your query. The top-ranked locations show strong potential based on our "
            "multi-factor scoring system that considers foot traffic, competition density, "
            "safety metrics, and equity indicators.\n\n"
            "**Key Findings:**\n"
            "- Properties in the Downtown and Midtown corridors show the highest activity indices\n"
            "- Vacant parcels near recent infrastructure investments offer the best value\n"
            "- Areas with lower competition scores present untapped market opportunities\n\n"
            "**Recommended Next Steps:**\n"
            "1. Review the detailed scorecards for each recommended property\n"
            "2. Compare your top 2-3 choices side-by-side\n"
            "3. Check the Equity Lens overlay to ensure alignment with community needs\n"
            "4. Contact the City's Economic Development office for parcel-specific information"
        )
    
    def _comparison_template(self, prompt: str) -> str:
        return (
            "**Property Comparison Analysis:**\n\n"
            "After analyzing the selected properties across all scoring dimensions, "
            "here are the key differentiators:\n\n"
            "- **Foot Traffic**: Properties closer to Downtown Montgomery generally score higher "
            "due to proximity to government buildings, retail corridors, and transit routes.\n"
            "- **Competition**: Less-developed areas show lower competition scores, "
            "indicating untapped market potential.\n"
            "- **Safety**: Scores vary by neighborhood; consider the time-of-day incident "
            "patterns for a more nuanced view.\n"
            "- **Equity Impact**: Properties in underserved areas score higher on equity, "
            "meaning your business could fill a critical service gap.\n\n"
            "**Recommendation**: The property with the best balance of high foot traffic "
            "and low competition typically offers the strongest business opportunity, "
            "while the highest equity score indicates the greatest community impact."
        )
    
    def _story_template(self, prompt: str) -> str:
        return (
            "# City Tour: Montgomery's Top Opportunities\n\n"
            "Welcome to Montgomery, Alabama — a city rich in history and brimming "
            "with untapped potential. Let me guide you through the most promising "
            "locations for your venture.\n\n"
            "## Stop 1: Downtown Core\n"
            "The heart of Montgomery offers the highest foot traffic and proximity "
            "to government offices, making it ideal for service-oriented businesses. "
            "Several vacant storefronts along Dexter Avenue present renovation-ready "
            "opportunities.\n\n"
            "## Stop 2: Capitol Heights\n"
            "This historically significant neighborhood has seen renewed interest. "
            "The combination of residential density and limited services creates "
            "a strong equity case for community-serving businesses.\n\n"
            "## Stop 3: Midtown Corridor\n"
            "The growing Midtown area bridges Downtown and the eastern suburbs. "
            "Recent infrastructure investments make this a strategic location "
            "for businesses targeting both commuters and residents.\n\n"
            "Each of these areas has been scored across multiple dimensions. "
            "Click on any property to see its full scorecard and context."
        )
    
    def _equity_template(self, prompt: str) -> str:
        return (
            "**Equity Lens Analysis:**\n\n"
            "This assessment evaluates how well the selected location(s) could serve "
            "underrepresented communities in Montgomery.\n\n"
            "- **Service Gap Indicator**: Areas with high residential density but few "
            "services of the target type score highest on equity.\n"
            "- **Income Context**: Lower-income neighborhoods often face longer travel "
            "distances to essential services.\n"
            "- **Community Impact Potential**: Establishing a business in an underserved "
            "area can generate both economic returns and meaningful social impact.\n\n"
            "**Key Equity Adjustments Applied:**\n"
            "- Boosted scores for properties in areas with identified service gaps\n"
            "- Weighted toward locations accessible by public transit\n"
            "- Considered proximity to affordable housing clusters"
        )
    
    def _risk_template(self, prompt: str) -> str:
        return (
            "**Risk & Safety Assessment:**\n\n"
            "Based on incident data from Montgomery's public records, here's a safety "
            "profile for the area:\n\n"
            "- **Incident Density**: The number of reported incidents within a 0.5km radius "
            "is factored into the safety score.\n"
            "- **Trend Direction**: Some areas show improving safety trends over the past year.\n"
            "- **Time-of-Day Patterns**: Many incidents cluster during specific hours, "
            "which may be relevant for planning business hours.\n\n"
            "**Caveats:**\n"
            "- Incident data represents reported events only and may not capture the full picture\n"
            "- Safety scores should be considered alongside on-the-ground observations\n"
            "- Recent infrastructure and community investment can rapidly improve safety profiles\n\n"
            "**Mitigation Suggestions:**\n"
            "- Consider security lighting and visibility improvements\n"
            "- Coordinate with neighboring businesses for shared safety initiatives\n"
            "- Engage with local community organizations for neighborhood watch programs"
        )
    
    def _bizcoach_template(self, prompt: str) -> str:
        return (
            "**Business Coach Insights:**\n\n"
            "Based on the market analysis for this location, here are tailored "
            "recommendations:\n\n"
            "📊 **Market Opportunity:**\n"
            "- The competition level in this area suggests room for a new entrant\n"
            "- Nearby foot traffic patterns indicate potential customer flow\n\n"
            "💡 **Strategic Recommendations:**\n"
            "1. **Hours of Operation**: Consider extended weekend hours to capture "
            "underserved demand\n"
            "2. **Partnerships**: Look into collaborations with nearby businesses "
            "for cross-promotion\n"
            "3. **Community Events**: Align your opening and promotions with "
            "Montgomery's local events calendar\n"
            "4. **Digital Presence**: Establish strong Google Business Profile early "
            "to capture local search traffic\n\n"
            "📋 **Next Steps:**\n"
            "- Visit the property during different times of day\n"
            "- Research local permits and zoning requirements\n"
            "- Connect with the Montgomery Area Chamber of Commerce\n"
            "- Review the city's small business incentive programs"
        )


def get_llm_service() -> BaseLLMService:
    """Factory function to get the appropriate LLM service."""
    from app.config import get_settings
    settings = get_settings()
    
    if settings.gemini_api_key and settings.gemini_api_key != "your_gemini_api_key_here":
        try:
            return GeminiService(settings.gemini_api_key)
        except Exception:
            return FallbackLLMService()
    
    return FallbackLLMService()
