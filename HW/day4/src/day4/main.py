from .utils import load_cache
from .state import AgentState
from .graph import workflow
from .logger import logger

import asyncio


@logger.catch()
async def amain() -> None:
    state: AgentState = {
        "user_input": input("user input:"),
        "messages": [],
        "cache": await load_cache(),
        "cache_hit_answer": None,
        "planner_go_search": False,
        "search_query": None,
        "search_results": None,
        "search_times": 0,
    }
    print(workflow.compile().get_graph().draw_mermaid())
    astream = workflow.compile().astream(state, stream_mode="values")

    async for c in astream:
        if len(c["messages"]) == 0:
            continue
        message = c["messages"][-1].content
        print(message, end="", flush=True)
    print()

    logger.info("end stream")


def main() -> None:
    asyncio.run(amain())


__all__ = ["main", "amain"]
