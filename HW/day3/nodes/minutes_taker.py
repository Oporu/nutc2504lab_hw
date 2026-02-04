from langchain_core.messages import (
    HumanMessage,
)
from langchain.agents import create_agent
from state import AgentState
from model import model


def minutes_taker_node(state: AgentState):
    agent = create_agent(
        model, system_prompt="根據使用者輸入產生出詳細的逐字稿, 不要聊天"
    )
    print("minutes_taker_node begin")
    response = []
    first = True

    data = f"""
    <srt>
        {state["srt_text"]}
    </srt>
    <逐字稿>
        {state["txt_text"]}
    </逐字稿>
    """

    for c in agent.stream(
        {"messages": [HumanMessage(data)]},
        stream_mode="values",
    ):
        if first:
            first = False
            continue
        content = c["messages"][-1].content
        response += content

    print("minutes_taker_node end")
    return {"minute_taker_result": "".join(response)}
