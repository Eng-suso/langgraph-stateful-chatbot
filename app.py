import uuid

from chatbot_backend import chatbot
import streamlit as st
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage

st.set_page_config(page_title="LangGraph Chatbot", page_icon=":speech_balloon:")

st.title("LangGraph Stateful Chatbot")


def new_thread_id():
    return str(uuid.uuid4())


if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = new_thread_id()

if "messages_history" not in st.session_state:
    st.session_state["messages_history"] = [
        {
            "role": "assistant",
            "content": "Ask me anything. This chat uses LangGraph checkpointing with a thread_id to keep conversation state.",
        }
    ]

if st.sidebar.button("New chat"):
    st.session_state["thread_id"] = new_thread_id()
    st.session_state["messages_history"] = [
        {
            "role": "assistant",
            "content": "New LangGraph thread started. The previous checkpoint remains isolated under its own thread_id.",
        }
    ]
    st.rerun()

st.sidebar.caption("Current LangGraph thread")
st.sidebar.code(st.session_state["thread_id"])

for message in st.session_state["messages_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input(placeholder="Type your message here...")

if user_input:
    st.session_state["messages_history"].append(
        {"role": "user", "content": user_input}
    )

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

    st.session_state["messages_history"].append(
        {"role": "assistant", "content": ai_message}
    )
