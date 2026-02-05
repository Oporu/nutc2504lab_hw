from os import environ
from pydantic import SecretStr
from types import SimpleNamespace

config = SimpleNamespace(
    openai_api_key=SecretStr(environ["OPENAI_API_KEY"]),
    openai_base_url=environ["OPENAI_BASE_URL"],
    openai_model=environ["OPENAI_MODEL"],
    cache_file_path=environ["CACHE_FILE_PATH"],
    searxng_url=environ["SEARXNG_URL"],
)

__all__ = ["config"]
