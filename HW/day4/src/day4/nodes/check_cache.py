from ..logger import logger
from ..state import AgentState

from typing import Literal


async def check_cache_node(state: AgentState) -> dict[str, str]:
    logger.info("node arrived")
    cache = state["cache"]
    user_input = state["user_input"]
    if user_input in cache:
        logger.info("cache hit: {}", cache[user_input])
        return {"cache_hit_answer": cache[user_input]}
    return {}


def check_cache_router(state: AgentState) -> Literal["planner", "final_answer"]:
    logger.info("router arrived")
    if state["cache_hit_answer"]:
        return "final_answer"
    return "planner"


__all__ = ["check_cache_node", "check_cache_router"]
