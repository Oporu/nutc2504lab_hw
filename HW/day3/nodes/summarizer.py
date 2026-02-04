from langchain_core.messages import (
    HumanMessage,
)
from langchain.agents import create_agent
from state import AgentState
from model import model


def summarizer_node(state: AgentState):
    agent = create_agent(model, system_prompt="取摘要, 不要聊天")
    print("summary node begin")
    response = []

    data = f"""
    <srt>
        {state["srt_text"]}
    </srt>
    <逐字稿>
        {state["txt_text"]}
    </逐字稿>
    """

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

    print("summary node end")
    return {"summarizer_result": "".join(response)}
