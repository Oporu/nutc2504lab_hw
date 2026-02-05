from ..utils import clean_tokens
from ..model import model
from ..state import AgentState
from ..logger import logger

from pathlib import Path
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

planner_node_prompt_template = PromptTemplate.from_file(
    Path(__file__).resolve().parent.parent / "prompts" / "query_gen.jinja2"
)


async def query_gen_node(state: AgentState):
    logger.info("node arrived")
    prompt = planner_node_prompt_template.format(
        already_searched_data=state["search_results"]
    )
    agent = create_agent(model=model, system_prompt=prompt)
    user_input = state["user_input"]

    result = await agent.ainvoke({"messages": [HumanMessage(user_input)]})
    response = result["messages"][1].content
    # stream = agent.astream(
    #     {"messages": [HumanMessage(user_input)]}, stream_mode="values"
    # )
    # response_chunks = []
    # async for c in stream:
    #     content = c["messages"][-1].content
    #     response_chunks += content
    #     print(content, end="", flush=True)
    # print()
    # response = "".join(response_chunks)

    response = clean_tokens(response)

    logger.info("query gen response: {}", response)
    return {"search_query": response}


__all__ = ["query_gen_node"]
