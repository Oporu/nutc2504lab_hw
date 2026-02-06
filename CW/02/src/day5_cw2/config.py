from os import environ
from pathlib import Path
from types import SimpleNamespace
from pydantic import SecretStr

config = SimpleNamespace(
    openai_api_key=SecretStr(environ["OPENAI_API_KEY"]),
    openai_base_url=environ["OPENAI_BASE_URL"],
    openai_model=environ["OPENAI_MODEL"],
    embedding_url=environ["EMBEDDING_URL"],
    qdrant_url=environ["QDRANT_URL"],
    qdrant_api_key=environ["QDRANT_API_KEY"],
    data_source_folder=Path(environ["DATA_SOURCE_FOLDER_PATH"]),
)

__all__ = ["config"]
