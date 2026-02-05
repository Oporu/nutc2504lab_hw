from ..utils import clean_tokens
from ..model import model
from ..state import AgentState
from ..logger import logger

from typing import Literal
from pathlib import Path
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

planner_node_prompt_template = PromptTemplate.from_file(
    Path(__file__).resolve().parent.parent / "prompts" / "planner.jinja2"
)


async def planner_node(state: AgentState):
    logger.info("node arrived")
    prompt = planner_node_prompt_template.format(
        online_search_data=state["search_results"],
        search_times=state["search_times"],
    )
    agent = create_agent(model=model, system_prompt=prompt)
    user_input = state["user_input"]
    result = await agent.ainvoke({"messages": [HumanMessage(user_input)]})
    response = result["messages"][1].content
    response = clean_tokens(response)
    logger.info("planner response: {}", response)

    if response.startswith("yes"):
        return {"planner_go_search": True}
    return {"planner_go_search": False}


async def planner_router(state: AgentState) -> Literal["query_gen", "final_answer"]:
    if state["planner_go_search"]:
        return "query_gen"
    return "final_answer"


__all__ = ["planner_node", "planner_router"]
