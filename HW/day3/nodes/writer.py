from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)
from langchain.agents import create_agent
from state import AgentState
from model import model


def writer_node(state: AgentState):
    agent = create_agent(
        model, system_prompt="整理好使用者提供的資料, 提供詳細的逐字稿和summary"
    )
    print("writer_node begin")
    summary_result = state["summarizer_result"]
    minutes_taker_result = state["minute_taker_result"]
    data = f"""
    <summary_result>
    {summary_result}
    </summary_result>
    <minutes_taker_result>
    {minutes_taker_result}
    </minutes_taker_result>
    """
    response = []

    first = True
    for c in agent.stream(
        {"messages": [HumanMessage(data)]},
        stream_mode="values",
    ):
        if first:
            first = False
            continue
        content = c["messages"][-1].content
        response += content

    print("writer_node end")
    return {"messages": [AIMessage("".join(response))]}
