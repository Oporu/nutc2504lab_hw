from graph import workflow


def main():
    print(workflow.compile().get_graph().draw_mermaid())
    stream = workflow.compile().stream(
        {"messages": []},
        stream_mode="values",
    )

    for c in stream:
        if len(c["messages"]) == 0:
            continue
        content = c["messages"][-1].content
        print(content, end="", flush=True)


if __name__ == "__main__":
    main()
