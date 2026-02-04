from os import environ
from langchain_openai import ChatOpenAI
from pydantic import SecretStr


model = ChatOpenAI(
    model="google/gemma-3-27b-it",
    api_key=SecretStr(environ["OPENAI_API_KEY"]),
    base_url=environ["OPENAI_BASE_URL"],
    temperature=0,
    streaming=True,
    max_completion_tokens=300,
)
