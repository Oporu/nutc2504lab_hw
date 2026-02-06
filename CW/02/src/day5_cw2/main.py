from pathlib import Path
from qdrant_client.models import PointStruct, QueryRequest

from .utils import text_from_file, markdown_to_csv
from .logger import logger
from .utils import embed, getEmbedSizeByTesting
from .config import config
from .model import model
import asyncio
from qdrant_client import AsyncQdrantClient, models
from langchain_text_splitters import CharacterTextSplitter, TokenTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

qdrant_client = AsyncQdrantClient(
    url=config.qdrant_url,
    api_key=config.qdrant_api_key,
)
collection_name_base = "collection_day5_cw2"
collection_name_token = collection_name_base + "_token"
collection_name_char = collection_name_base + "_char"
collection_names = [collection_name_token, collection_name_char]


char_splitter = CharacterTextSplitter(
    chunk_size=50, chunk_overlap=0, length_function=len, separator=""
)
token_splitter = TokenTextSplitter(chunk_size=100, chunk_overlap=10, model_name="gpt-4")


async def setup_vectorstore():
    size = await getEmbedSizeByTesting()
    logger.info("embed size: {}", size)

    logger.info("deleting collections {} if exists...", collection_names)
    await asyncio.gather(
        *(qdrant_client.delete_collection(collection_name=n) for n in collection_names)
    )

    logger.info("creating collections {}", collection_names)
    await asyncio.gather(
        *(
            qdrant_client.create_collection(
                collection_name=n,
                vectors_config=models.VectorParams(
                    size=size, distance=models.Distance.COSINE
                ),
            )
            for n in collection_names
        )
    )

def printEm(text_queries, way, responses):
    for i in range(len(text_queries)):
        logger.info(
            "query {}, {} result: \n{}",
            way,
            text_queries[i],
            "\n".join(
                [
                    f'"{q.payload["origin"]}" score {q.score}'
                    for q in responses[i].points
                ]
            ),
        )

async def text_txt_tests():
    await setup_vectorstore()
    t = await text_from_file(config.data_source_folder / "text.txt")

    char_split_chunks = char_splitter.split_text(t)
    token_split_chunks = token_splitter.split_text(t)
    logger.info("char split chunks len {}", len(char_split_chunks))
    logger.info("token split chunks len {}", len(token_split_chunks))

    logger.info("embedding...")
    [char_split_embeds, token_split_embeds] = await asyncio.gather(
        embed(char_split_chunks), embed(token_split_chunks)
    )

    char_points = [
        PointStruct(
            id=i, vector=char_split_embeds[i], payload={"origin": char_split_chunks[i]}
        )
        for i in range(len(char_split_chunks))
    ]

    token_points = [
        PointStruct(
            id=i,
            vector=token_split_embeds[i],
            payload={"origin": token_split_chunks[i]},
        )
        for i in range(len(token_split_chunks))
    ]

    logger.info("upserting to qdrant server...")
    await asyncio.gather(
        qdrant_client.upsert(collection_name_char, points=char_points),
        qdrant_client.upsert(collection_name_token, points=token_points),
    )

    logger.info("end")

    text_queries = ["what is RAG?"]
    queryEmbeds = await embed(text_queries)

    queries = [QueryRequest(query=e, with_payload=True, limit=3) for e in queryEmbeds]
    [queryCharResponses, queryTokenResponses] = [
        await qdrant_client.query_batch_points(
            collection_name=n,
            requests=queries,
        )
        for n in collection_names
    ]

    printEm(text_queries, "char", queryCharResponses)
    printEm(text_queries, "token", queryTokenResponses)


async def table_md_tests():
    await setup_vectorstore()
    t = await text_from_file(config.data_source_folder / "table" / "table_txt.md")

    csv = markdown_to_csv(t)

    logger.info("csv {}", csv)
    prompt_template = PromptTemplate.from_file(
        Path(__file__).resolve().parent / "prompts" / "table_summary.jinja2"
    )
    prompt = prompt_template.format(Table_Content=csv)
    summary_result = await model.ainvoke(prompt)

    logger.info("summary result {}", summary_result.content)

    t = str(summary_result.content)
    char_split_chunks = char_splitter.split_text(t)
    token_split_chunks = token_splitter.split_text(t)
    logger.info("char split chunks len {}", len(char_split_chunks))
    logger.info("token split chunks len {}", len(token_split_chunks))

    logger.info("embedding...")
    [char_split_embeds, token_split_embeds] = await asyncio.gather(
        embed(char_split_chunks), embed(token_split_chunks)
    )

    char_points = [
        PointStruct(
            id=i, vector=char_split_embeds[i], payload={"origin": char_split_chunks[i]}
        )
        for i in range(len(char_split_chunks))
    ]

    token_points = [
        PointStruct(
            id=i,
            vector=token_split_embeds[i],
            payload={"origin": token_split_chunks[i]},
        )
        for i in range(len(token_split_chunks))
    ]

    logger.info("upserting to qdrant server...")
    await asyncio.gather(
        qdrant_client.upsert(collection_name_char, points=char_points),
        qdrant_client.upsert(collection_name_token, points=token_points),
    )

    logger.info("end")
    text_queries = ["半導體如何?"]
    queryEmbeds = await embed(text_queries)

    queries = [QueryRequest(query=e, with_payload=True, limit=3) for e in queryEmbeds]
    [queryCharResponses, queryTokenResponses] = [
        await qdrant_client.query_batch_points(
            collection_name=n,
            requests=queries,
        )
        for n in collection_names
    ]

    printEm(text_queries, "char", queryCharResponses)
    printEm(text_queries, "token", queryTokenResponses)


async def table_html_tests():
    await setup_vectorstore()
    import pandas as pd
    aaa = pd.read_html(config.data_source_folder / "table" / "table_html.html")
    csv = aaa[0].to_csv()

    logger.info("csv {}", csv)
    prompt_template = PromptTemplate.from_file(
        Path(__file__).resolve().parent / "prompts" / "table_summary.jinja2"
    )
    prompt = prompt_template.format(Table_Content=csv)
    summary_result = await model.ainvoke(prompt)

    logger.info("summary result {}", summary_result.content)

    t = str(summary_result.content)
    char_split_chunks = char_splitter.split_text(t)
    token_split_chunks = token_splitter.split_text(t)
    logger.info("char split chunks len {}", len(char_split_chunks))
    logger.info("token split chunks len {}", len(token_split_chunks))

    logger.info("embedding...")
    [char_split_embeds, token_split_embeds] = await asyncio.gather(
        embed(char_split_chunks), embed(token_split_chunks)
    )

    char_points = [
        PointStruct(
            id=i, vector=char_split_embeds[i], payload={"origin": char_split_chunks[i]}
        )
        for i in range(len(char_split_chunks))
    ]

    token_points = [
        PointStruct(
            id=i,
            vector=token_split_embeds[i],
            payload={"origin": token_split_chunks[i]},
        )
        for i in range(len(token_split_chunks))
    ]

    logger.info("upserting to qdrant server...")
    await asyncio.gather(
        qdrant_client.upsert(collection_name_char, points=char_points),
        qdrant_client.upsert(collection_name_token, points=token_points),
    )

    logger.info("end")
    text_queries = ["三民校區"]
    queryEmbeds = await embed(text_queries)

    queries = [QueryRequest(query=e, with_payload=True, limit=3) for e in queryEmbeds]
    [queryCharResponses, queryTokenResponses] = [
        await qdrant_client.query_batch_points(
            collection_name=n,
            requests=queries,
        )
        for n in collection_names
    ]


    printEm(text_queries, "char", queryCharResponses)
    printEm(text_queries, "token", queryTokenResponses)

@logger.catch()
async def amain() -> None:
    logger.info("=====text.txt=====")
    await text_txt_tests()
    logger.info("=====table_txt.md=====")
    await table_md_tests()
    logger.info("=====table_html.html=====")
    await table_html_tests()


def main() -> None:
    asyncio.run(amain())


__all__ = ["main", "amain"]
