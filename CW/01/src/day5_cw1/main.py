from qdrant_client.models import PointStruct, QueryRequest
from .logger import logger
from .utils import embed, getEmbedSizeByTesting
from .config import config
import asyncio
from qdrant_client import AsyncQdrantClient, models

qdrant_client = AsyncQdrantClient(
    url=config.qdrant_url,
    api_key=config.qdrant_api_key,
)
collection_name = "collection_day5_cw1"

random_data = [
    "DDR要40塊",
    "DDR很難",
    "dance rush我不知道",
    "ITG是in the groove",
    "DDR是dance dance revolution",
    "potato",
    "apple",
]

text_queries = input("queries separated by space: ").split()


async def setup_vectorstore():
    size = await getEmbedSizeByTesting()
    logger.info("embed size: {}", size)
    logger.info("deleting collection {} if exists...", collection_name)
    await qdrant_client.delete_collection(collection_name=collection_name)
    logger.info("creating collection {}", collection_name)
    await qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=size, distance=models.Distance.COSINE),
    )


@logger.catch()
async def amain() -> None:
    await setup_vectorstore()

    vectors = await embed(random_data)
    queryEmbeds = await embed(text_queries)

    points = [
        PointStruct(id=i, vector=vectors[i], payload={"origin": random_data[i]})
        for i in range(len(random_data))
    ]
    logger.info("inserting points...")
    await qdrant_client.upsert(collection_name=collection_name, points=points)
    logger.info("inserted")

    logger.info("quering {}", text_queries)

    queries = [QueryRequest(query=e, with_payload=True, limit=3) for e in queryEmbeds]
    queryResponses = await qdrant_client.query_batch_points(
        collection_name=collection_name,
        requests=queries,
    )

    for i in range(len(text_queries)):
        logger.info(
            "query {} result: \n{}",
            text_queries[i],
            "\n".join(
                [
                    f'"{q.payload["origin"]}" score {q.score}'
                    for q in queryResponses[i].points
                ]
            ),
        )


def main() -> None:
    asyncio.run(amain())


__all__ = ["main", "amain"]
