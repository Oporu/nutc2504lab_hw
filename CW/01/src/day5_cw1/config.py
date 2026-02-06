from os import environ
from types import SimpleNamespace

config = SimpleNamespace(
    qdrant_url=environ["QDRANT_URL"],
    qdrant_api_key=environ["QDRANT_API_KEY"],
)

__all__ = ["config"]
