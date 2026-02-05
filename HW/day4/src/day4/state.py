from typing import Annotated, Optional, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    cache: dict[str, str]
    user_input: str
    cache_hit_answer: Optional[str]
    planner_go_search: Optional[bool]
    search_query: Optional[str]
    search_results: Optional[str]
    search_times: int
