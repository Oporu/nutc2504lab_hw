from ..utils import save_cache, clean_tokens
from ..logger import logger
from ..model import model
from ..state import AgentState

from langchain_core.prompts import PromptTemplate
from langchain.agents import create_agent
from pathlib import Path
from langchain_core.messages import AIMessage, HumanMessage


final_answer_node_prompt_template = PromptTemplate.from_file(
    Path(__file__).resolve().parent.parent / "prompts" / "final_answer.jinja2"
)


async def final_answer_node(state: AgentState):
    logger.info("node arrived")
    user_input = state["user_input"]
    cache_hit_answer = state["cache_hit_answer"]
    if cache_hit_answer:
        return {"messages": AIMessage(cache_hit_answer)}

    prompt = final_answer_node_prompt_template.format(
        search_results=state["search_results"],
    )
    logger.debug("prompt: {}", prompt)
    agent = create_agent(model, system_prompt=prompt)
    stream = agent.astream(
        {"messages": [HumanMessage(user_input)]}, stream_mode="values"
    )

    response_chunks = []
    first = True
    async for c in stream:
        if first:
            first = False
            continue
        content = c["messages"][-1].content
        response_chunks += content
    response = "".join(response_chunks)
    response = clean_tokens(response)

    cache = state["cache"]
    cache[user_input] = response
    await save_cache(cache)

    return {"messages": AIMessage(response), "cache": cache}


__all__ = ["final_answer_node"]
