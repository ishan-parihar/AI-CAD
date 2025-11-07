import os
from pydantic import BaseModel
from typing import Optional, Dict


class Settings(BaseModel):
    # OpenAI Compatible API Configuration (from environment)
    openai_base_url: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_model_name: Optional[str] = None
    
    # Legacy API Keys (for backward compatibility)
    openai_api_key_legacy: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./aicad.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Application
    app_name: str = "AI-CAD Automation"
    debug: bool = False
    log_level: str = "INFO"
    port: int = 8100
    
    # AI Model Settings
    default_model: str = "gpt-4"
    max_tokens: int = 4000
    temperature: float = 0.7
    
    # File Storage
    output_directory: str = "./outputs"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    
    # CAD Settings
    dxf_version: str = "R2010"
    units: str = "Meters"
    
    # AI Integration Settings
    ai_integration_enabled: bool = True
    ai_timeout: int = 30  # seconds
    ai_max_retries: int = 3
    
    def __init__(self, **data):
        super().__init__(**data)
        # Load from environment variables
        self.openai_base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("BASE_URL")
        self.openai_api_key = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")
        self.openai_model_name = os.getenv("OPENAI_MODEL_NAME") or os.getenv("MODEL_NAME")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        port_value = os.getenv("PORT")
        self.port = int(port_value) if port_value and port_value.isdigit() else 8100
    
    class Config:
        extra = "allow"
    
    def get_openai_config(self) -> Dict[str, str]:
        """Get OpenAI configuration for API client"""
        config = {}
        if self.openai_base_url:
            config["base_url"] = self.openai_base_url
        if self.openai_api_key:
            config["api_key"] = self.openai_api_key
        if self.openai_model_name:
            config["model"] = self.openai_model_name
        return config
    
    def is_openai_configured(self) -> bool:
        """Check if OpenAI compatible API is configured"""
        return bool(self.openai_base_url and self.openai_api_key)


# Global settings instance
settings = Settings()