from langgraph.graph import StateGraph, END
from nodes.writer import writer_node
from state import AgentState
from nodes.asr import asr_node
from nodes.minutes_taker import minutes_taker_node
from nodes.summarizer import summarizer_node

workflow = StateGraph(AgentState)
workflow.add_node("asr", asr_node)
workflow.add_node("minutes_taker", minutes_taker_node)
workflow.add_node("summarizer", summarizer_node)
workflow.add_node("writer", writer_node)
workflow.add_edge("asr", "minutes_taker")
workflow.add_edge("asr", "summarizer")
workflow.add_edge("minutes_taker", "writer")
workflow.add_edge("summarizer", "writer")
workflow.add_edge("writer", END)

workflow.set_entry_point("asr")
