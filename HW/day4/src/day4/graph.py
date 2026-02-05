from .nodes import (
    check_cache_node,
    check_cache_router,
    final_answer_node,
    planner_node,
    planner_router,
    query_gen_node,
    search_tool_node,
)
from .state import AgentState
from langgraph.graph import END, StateGraph

workflow = StateGraph(AgentState)
workflow.add_node("check_cache", check_cache_node)
workflow.add_node("final_answer", final_answer_node)
workflow.add_node("planner", planner_node)
workflow.add_node("query_gen", query_gen_node)
workflow.add_node("search_tool", search_tool_node)

workflow.set_entry_point("check_cache")
workflow.add_conditional_edges(
    "check_cache",
    check_cache_router,
    {"planner": "planner", "final_answer": "final_answer"},
)
workflow.add_conditional_edges(
    "planner",
    planner_router,
    {"query_gen": "query_gen", "final_answer": "final_answer"},
)

workflow.add_edge("query_gen", "search_tool")
workflow.add_edge("search_tool", "planner")
workflow.add_edge("final_answer", END)

__all__ = ["workflow"]
