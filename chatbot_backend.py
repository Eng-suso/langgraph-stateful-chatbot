import os
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages

load_dotenv()

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

llm = ChatOpenAI(
    model_name=MODEL_NAME,
    temperature=0.25,
    max_completion_tokens=1000,
    timeout=(10, 60),
    max_retries=3,
    stream_usage=True,
)


class ChatState(TypedDict):
    """Conversation state managed by LangGraph."""

    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):
    """Run one LLM turn and append the assistant response to state."""

    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


checkpoint = MemorySaver()
graph = StateGraph(ChatState)

graph.add_node("chatbot", chat_node)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

# Compiled LangGraph app with checkpointing enabled.
# The configurable thread_id controls which conversation memory is loaded.
chatbot = graph.compile(checkpointer=checkpoint)


def run_cli():
    thread_id = "conversation_1"

    while True:
        user_input = input("User: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        config = {"configurable": {"thread_id": thread_id}}
        initial_state = {"messages": [HumanMessage(content=user_input)]}
        response = chatbot.invoke(initial_state, config=config)

        print("Assistant:", response["messages"][-1].content)


if __name__ == "__main__":
    run_cli()
