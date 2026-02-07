# /// script
# dependencies = [
#     "aiofiles>=25.1.0",
#     "aiopath>=0.6.11",
#     "httpx>=0.28.1",
#     "langchain-text-splitters>=1.1.0",
#     "loguru>=0.7.3",
#     "pandas>=3.0.0",
#     "qdrant-client>=1.16.2",
#     "semantic-text-splitter>=0.29.0",
# ]
# ///

import httpx
import aiofiles
from loguru import logger
import asyncio
import aiopath
from pathlib import Path
from numpy import average
from qdrant_client import AsyncQdrantClient, models
from langchain_text_splitters import (
    CharacterTextSplitter,
)
from semantic_text_splitter import TextSplitter as SemanticTextSplitter
import uuid
import pandas as pd
from os import environ
from types import SimpleNamespace

config = SimpleNamespace(
    embedding_url=environ["EMBEDDING_URL"],
    qdrant_url=environ["QDRANT_URL"],
    qdrant_api_key=environ["QDRANT_API_KEY"],
    homework_submit_url=environ["HOMEWORK_SUBMIT_URL"],
    data_source_folder=Path(environ["DATA_SOURCE_FOLDER_PATH"]),
    output_file_path=Path(environ["OUTPUT_FILE_PATH"]),
)

qdrant_client = AsyncQdrantClient(
    url=config.qdrant_url,
    api_key=config.qdrant_api_key,
    prefer_grpc=True,
)

collection_name = "collection_hw5"

data_files_to_read = [
    "data_01.txt",
    "data_02.txt",
    "data_03.txt",
    "data_04.txt",
    "data_05.txt",
]

splitter_functions = {
    "fixed": CharacterTextSplitter(
        chunk_size=150, chunk_overlap=0, separator=""
    ).split_text,
    "sliding_window": CharacterTextSplitter(
        chunk_size=150, chunk_overlap=50, separator=""
    ).split_text,
    "semantic": SemanticTextSplitter((100, 200)).chunks,
}

splitter_functions_size = len(splitter_functions)

method_map = {
    "fixed": "固定大小",
    "sliding_window": "滑動視窗",
    "semantic": "語意切塊",
}

data_source_folder: Path = config.data_source_folder


async def embed(
    texts: list[str],
    normalize: bool = True,
    batch_size: int = 32,
):
    async with httpx.AsyncClient(timeout=200) as client:
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


async def text_from_file(file_path: str) -> str:
    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
        return await f.read()


async def texts_from_files(file_paths: list[str]) -> list[str]:
    return await asyncio.gather(*(text_from_file(fp) for fp in file_paths))


async def get_question_score(q_id: int, answer: str) -> int:
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            url=config.homework_submit_url,
            json={"q_id": q_id, "student_answer": answer},
        )
        response_json = response.json()
        if not response_json["score"]:
            logger.error("score submit not success {}", response_json)
        return response_json["score"]


async def setup_vectorstore():
    size = await getEmbedSizeByTesting()
    logger.info("embedding size: {}", size)
    logger.info("deleting collection {} if exists", collection_name)
    await qdrant_client.delete_collection(collection_name)
    logger.info("creating collection {}", collection_name)
    await qdrant_client.create_collection(
        collection_name,
        vectors_config=models.VectorParams(size=size, distance=models.Distance.COSINE),
    )

    logger.info("creating payload index on {}", collection_name)
    await qdrant_client.create_payload_index(
        collection_name=collection_name,
        field_name="splitter_function_name",
        field_schema="keyword",
    )

    if not await aiopath.AsyncPath(data_source_folder).exists():
        raise ValueError(f"folder {data_source_folder} not found")
    logger.info("reading files...")
    file_datas = await texts_from_files(
        [str(data_source_folder / fn) for fn in data_files_to_read]
    )

    logger.info("splitting...")
    splitted_datas = [
        {
            "file_name": data_files_to_read[i],
            "chunk": chunk,
            "splitter_function_name": splitter_function_name,
        }
        for i, file_data in enumerate(file_datas)
        for splitter_function_name, splitter_function in splitter_functions.items()
        for chunk in splitter_function(file_data)
    ]

    # prints amount of chunk for each text split method
    for splitter_function_name in splitter_functions.keys():
        logger.info(
            "splitter | len(chunks): {} {}",
            splitter_function_name,
            len(
                [
                    d
                    for d in splitted_datas
                    if d["splitter_function_name"] == splitter_function_name
                ]
            ),
        )

    chunks_to_embed = [data["chunk"] for data in splitted_datas]
    logger.info("embedding {} chunks...", len(chunks_to_embed))
    chunks_embeded = await embed(chunks_to_embed)

    logger.info("mapping to points")
    points = [
        models.PointStruct(
            id=uuid.uuid4(),
            vector=vector,
            payload={
                "file_name": splitted_data["file_name"],
                "origin": splitted_data["chunk"],
                "splitter_function_name": splitted_data["splitter_function_name"],
            },
        )
        for splitted_data, vector in zip(splitted_datas, chunks_embeded)
    ]

    logger.info("uploading {} points...", len(points))

    # no async, why qdrant :sob:
    qdrant_client.upload_points(
        collection_name=collection_name,
        points=points,
        max_retries=5,
        wait=True,
    )

    logger.info("finished uploading")

    logger.info("reading questions.csv...")
    csv = pd.read_csv(data_source_folder / "questions.csv")
    questions = csv.to_dict()
    question_size = len(questions["q_id"])

    logger.info("embedding questions...")
    question_embeds = await embed(list(questions["questions"].values()))

    question_queries = [
        models.QueryRequest(
            query=e,
            with_payload=True,
            limit=1,
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="splitter_function_name",
                        match=models.MatchValue(value=splitter_name),
                    )
                ]
            ),
        )
        for e in question_embeds
        for splitter_name in splitter_functions.keys()
    ]

    logger.info("query batch...")
    result_points = await qdrant_client.query_batch_points(
        collection_name=collection_name, requests=question_queries
    )

    logger.info("getting scores...")
    scores = await asyncio.gather(
        *(
            get_question_score(
                q_id=q_id,
                answer=result_points[q_id_i * splitter_functions_size + j]
                .points[0]
                .payload["origin"],
            )
            for q_id_i, q_id in questions["q_id"].items()
            for j in range(len(splitter_functions))
        )
    )
    logger.info("score avg: {}", average(scores))
    for i, splitter_function_name in enumerate(splitter_functions.keys()):
        logger.info(
            "splitter | score_avg: {} {}",
            splitter_function_name,
            average(scores[i::splitter_functions_size]),
        )

    answer_data = [
        {
            "id": i * splitter_functions_size + j + 1,
            "q_id": questions["q_id"][i],
            "method": method_map.get(splitter_function_name, splitter_function_name),
            "retrieve_text": result_points[i * splitter_functions_size + j]
            .points[0]
            .payload["origin"],
            "score": scores[i * splitter_functions_size + j],
            "source": result_points[i * splitter_functions_size + j]
            .points[0]
            .payload["file_name"],
        }
        for i in range(question_size)
        for j, splitter_function_name in enumerate(splitter_functions.keys())
    ]

    # logger.info("answer_data: {}", answer_data)

    logger.info("saving results...")
    pd.DataFrame(answer_data).to_csv(
        config.output_file_path,
        columns=["id", "q_id", "method", "retrieve_text", "score", "source"],
        index=False,
    )
    logger.info("saved to {}", config.output_file_path)


@logger.catch
async def amain() -> None:
    await setup_vectorstore()


def main() -> None:
    asyncio.run(amain())


if __name__ == "__main__":
    main()
