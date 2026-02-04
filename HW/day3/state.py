from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    srt_text: str
    txt_text: str
    minute_taker_result: str
    summarizer_result: str
