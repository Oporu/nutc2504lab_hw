from langchain_openai import ChatOpenAI
from .config import config

model = ChatOpenAI(
    model=config.openai_model,
    api_key=config.openai_api_key,
    base_url=config.openai_base_url,
    temperature=0,
    streaming=True,
    max_completion_tokens=300,
)

__all__ = ["model"]
