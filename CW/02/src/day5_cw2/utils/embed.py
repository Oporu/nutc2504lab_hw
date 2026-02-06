import httpx
from ..config import config
from ..logger import logger


async def embed(
    texts: list[str],
    normalize: bool = True,
    batch_size: int = 32,
):
    async with httpx.AsyncClient(timeout=1000) as client:
        a = await client.post(
            url=config.embedding_url,
            json={
                "texts": texts,
                "task_description": "檢索技術文件",
                "normalize": normalize,
                "batch_size": batch_size,
            },
        )
        embeddings = a.json()["embeddings"]

        return embeddings


async def getEmbedSizeByTesting() -> int:
    result = await embed(["yee"])
    return len(result[0])
