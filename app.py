import uuid

from chatbot_backend import chatbot, llm
import streamlit as st
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, SystemMessage

st.set_page_config(page_title="LangGraph Chatbot", page_icon=":speech_balloon:")

st.title("LangGraph Stateful Chatbot")

INTRO_MESSAGE = (
    "Ask me anything. This chat uses LangGraph checkpointing with a thread_id "
    "to keep conversation state."
)


def new_thread_id():
    return str(uuid.uuid4())


def new_thread():
    return {
        "title": "",
        "title_generated": False,
        "has_user_message": False,
        "messages": [{"role": "assistant", "content": INTRO_MESSAGE}],
    }


def create_thread():
    thread_id = new_thread_id()
    st.session_state["threads"][thread_id] = new_thread()
    st.session_state["thread_order"].append(thread_id)
    st.session_state["thread_id"] = thread_id


def active_thread():
    return st.session_state["threads"][st.session_state["thread_id"]]


def has_user_message(messages):
    return any(message["role"] == "user" for message in messages)


def normalize_threads():
    for thread in st.session_state["threads"].values():
        thread.setdefault("title", "")
        thread.setdefault("title_generated", bool(thread["title"]))
        thread.setdefault("messages", [{"role": "assistant", "content": INTRO_MESSAGE}])
        thread.setdefault("has_user_message", has_user_message(thread["messages"]))


def title_messages(messages_history):
    langchain_messages = []

    for message in messages_history:
        if message["content"] == INTRO_MESSAGE:
            continue

        if message["role"] == "user":
            langchain_messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            langchain_messages.append(AIMessage(content=message["content"]))

    return langchain_messages


def clean_title(title):
    return title.strip().strip('"').strip("'") or "Untitled conversation"


def stream_thread_title(messages):
    title_prompt = SystemMessage(
        content=(
            "Generate a short title for this conversation. "
            "Use the same language as the user. "
            "Maximum 4 words. Return only the title, with no quotes."
        )
    )

    for chunk in llm.stream([title_prompt, *messages[:6]]):
        if chunk.content:
            yield chunk.content


if "threads" not in st.session_state:
    first_thread_id = st.session_state.get("thread_id", new_thread_id())
    previous_messages = st.session_state.get(
        "messages_history", [{"role": "assistant", "content": INTRO_MESSAGE}]
    )
    st.session_state["thread_id"] = first_thread_id
    st.session_state["thread_order"] = [first_thread_id]
    st.session_state["threads"] = {
        first_thread_id: {
            "title": "",
            "title_generated": False,
            "has_user_message": False,
            "messages": previous_messages,
        }
    }

normalize_threads()

if st.sidebar.button("New chat"):
    create_thread()
    st.rerun()

st.sidebar.caption("Recent conversations")

for thread_id in reversed(st.session_state["thread_order"]):
    thread = st.session_state["threads"][thread_id]

    if not thread["has_user_message"]:
        continue

    if st.sidebar.button(thread["title"], key=f"thread_{thread_id}"):
        st.session_state["thread_id"] = thread_id
        st.rerun()

current_title = st.sidebar.empty()
if active_thread()["title"]:
    current_title.markdown(f"**{active_thread()['title']}**")

for message in active_thread()["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input(placeholder="Type your message here...")

if user_input:
    thread = active_thread()
    thread["has_user_message"] = True
    thread["messages"].append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    config = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {"thread_id": st.session_state["thread_id"]},
        "run_name": "streamlit_chat",
    }

    with st.chat_message("assistant"):
        ai_message = st.write_stream(
            message_chunk.content
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode="messages",
            )
            if isinstance(message_chunk, (AIMessage, AIMessageChunk))
        )

    thread["messages"].append({"role": "assistant", "content": ai_message})

    if not thread["title_generated"]:
        title = ""

        for title_chunk in stream_thread_title(title_messages(thread["messages"])):
            title += title_chunk
            current_title.markdown(f"**{clean_title(title)}**")

        thread["title"] = clean_title(title)
        thread["title_generated"] = True
