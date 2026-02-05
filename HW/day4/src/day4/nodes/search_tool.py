from ..logger import logger
from ..model import model
from ..state import AgentState
from ..utils import search_searxng, clean_tokens

from pathlib import Path
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

search_tool_node_prompt_template = PromptTemplate.from_file(
    Path(__file__).resolve().parent.parent / "prompts" / "search_tool.jinja2"
)


def search_searxng_formatted(query: str) -> str:
    results = search_searxng(query=query, limit=3)
    response = f"📊 搜尋結果 ({len(results)} 筆):"

    if results:
        for idx, item in enumerate(results, 1):
            response += f"\n[{idx}] {item.get('title', '無標題')}"
            response += f"    🔗 連結: {item.get('url', '無連結')}"
            # 顯示部分摘要，去除過多空白
            snippet = item.get("content", "無摘要").strip().replace("\n", " ")[:100]
            response += f"    📝 摘要: {snippet}..."
    else:
        response += "沒有找到相關結果，請檢查關鍵字或伺服器連線。"
    return response


async def search_tool_node(state: AgentState):
    logger.info("node arrived")
    if not state["search_query"]:
        logger.error("state search_query not set")
        return {}

    search_result = search_searxng_formatted(state["search_query"])
    prompt = search_tool_node_prompt_template.format(user_input=state["user_input"])
    agent = create_agent(model=model, system_prompt=prompt)

    logger.info("is this search result? {}", search_result)
    result = await agent.ainvoke(
        {
            "messages": [
                HumanMessage("<search_result>" + search_result + "</search_result>")
            ]
        }
    )
    response = result["messages"][1].content
    response = clean_tokens(response)
    logger.info("search tool summary response: {}", response)

    if not state["search_results"]:
        return {"search_results": response}
    return {
        "search_results": state["search_results"] + response,
        "search_times": state["search_times"] + 1,
    }


__all__ = ["search_tool_node"]
