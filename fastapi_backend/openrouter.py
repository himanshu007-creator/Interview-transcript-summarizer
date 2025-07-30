import os
from typing import Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


class ChatOpenRouter(ChatOpenAI):
    """OpenRouter integration for LangChain using ChatOpenAI interface."""

    def __init__(self,
                 model_name: str = "anthropic/claude-3.5-sonnet",
                 openai_api_key: Optional[str] = None,
                 **kwargs):
        
        # Get API key from parameter or environment
        api_key = openai_api_key or os.environ.get("OPENROUTER_API_KEY")
        
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY must be set in environment or passed as parameter")
        
        # Initialize with OpenRouter base URL
        super().__init__(
            model=model_name,
            base_url="https://openrouter.ai/api/v1",
            openai_api_key=api_key,
            **kwargs
        )


def get_openrouter_model(model_name: str = "anthropic/claude-3.5-sonnet"):
    """Get an OpenRouter model instance."""
    return ChatOpenRouter(model_name=model_name)