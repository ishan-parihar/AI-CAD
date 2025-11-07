"""
OpenAI Compatible API Client Module
Provides integration with OpenAI and OpenAI-compatible API endpoints
"""

import openai
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from src.utils.config import settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI Compatible API Client"""
    
    def __init__(self):
        self.client = None
        self.model_name = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the OpenAI client with configuration"""
        try:
            if not settings.is_openai_configured():
                logger.warning("OpenAI compatible API not configured. AI features will be limited.")
                logger.info("To configure AI, set OPENAI_BASE_URL, OPENAI_API_KEY, and OPENAI_MODEL_NAME environment variables.")
                return
            
            client_config = settings.get_openai_config()
            
            # Create OpenAI client with custom endpoint support
            self.client = openai.OpenAI(
                api_key=client_config.get("api_key"),
                base_url=client_config.get("base_url"),
                timeout=30.0,  # 30 second timeout
                max_retries=3  # 3 retries
            )
            
            self.model_name = client_config.get("model", settings.default_model)
            
            logger.info(f"OpenAI client initialized successfully")
            logger.info(f"  Base URL: {client_config.get('base_url')}")
            logger.info(f"  Model: {self.model_name}")
            logger.info(f"  API Key: {'*' * 20}{client_config.get('api_key', '')[-4:] if client_config.get('api_key') else 'None'}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            logger.error("Please check your OPENAI_BASE_URL, OPENAI_API_KEY, and OPENAI_MODEL_NAME configuration.")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if OpenAI client is available and configured"""
        return self.client is not None
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Optional[str]:
        """Generate response using OpenAI compatible API"""
        
        if not self.is_available():
            logger.error("OpenAI client not available - check configuration")
            return None
        
        try:
            logger.debug(f"Generating response with model: {self.model_name}")
            logger.debug(f"Messages count: {len(messages)}")
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens or settings.max_tokens,
                temperature=temperature or settings.temperature,
                **kwargs
            )
            
            content = response.choices[0].message.content
            logger.debug(f"Response generated successfully (length: {len(content or '')})")
            return content
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return None
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            return None
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None
    
    async def analyze_cad_requirements(
        self,
        user_requirements: str,
        context: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Analyze CAD requirements using AI"""
        
        system_prompt = """
        You are an AI assistant specialized in architectural floor plan generation.
        Analyze the user's requirements and extract structured information for CAD generation.
        
        Return a JSON object with the following structure:
        {
            "building_type": "residential|commercial|industrial|mixed",
            "total_area": number_in_square_meters,
            "rooms": [
                {
                    "name": "room_name",
                    "type": "bedroom|living|kitchen|bathroom|office|etc",
                    "min_area": number_in_square_meters,
                    "preferred_area": number_in_square_meters,
                    "requirements": ["specific_requirements"]
                }
            ],
            "constraints": {
                "width": number_in_meters,
                "height": number_in_meters,
                "min_rooms": number,
                "max_rooms": number
            },
            "preferences": {
                "style": "modern|traditional|minimalist|etc",
                "special_features": ["features"]
            }
        }
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User Requirements:\n{user_requirements}"}
        ]
        
        if context:
            messages.insert(1, {
                "role": "system", 
                "content": f"Additional Context:\n{json.dumps(context, indent=2)}"
            })
        
        response = await self.generate_response(messages)
        
        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                return None
        
        return None
    
    async def suggest_optimizations(
        self,
        current_layout: Dict,
        issues: List[str]
    ) -> Optional[List[Dict]]:
        """Suggest layout optimizations using AI"""
        
        system_prompt = """
        You are an AI assistant specialized in architectural floor plan optimization.
        Analyze the current layout and issues, then suggest specific improvements.
        
        Return a JSON array of optimization suggestions:
        [
            {
                "type": "room_relocation|wall_adjustment|door_relocation|etc",
                "description": "Detailed description of the optimization",
                "impact": "high|medium|low",
                "implementation": "Step-by-step implementation guide"
            }
        ]
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user", 
                "content": f"""
                Current Layout:
                {json.dumps(current_layout, indent=2)}
                
                Identified Issues:
                {json.dumps(issues, indent=2)}
                """
            }
        ]
        
        response = await self.generate_response(messages)
        
        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI suggestions as JSON: {e}")
                return None
        
        return None


# Global OpenAI client instance
openai_client = OpenAIClient()