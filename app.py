from chatbot_backend import chatbot
import streamlit as st
from langchain_core.messages import HumanMessage

st.title("Bpmn assistant")
CONFIG = {"configurable": {"thread_id": "conversation_1"}}

if 'messages_history' not in st.session_state:
    st.session_state['messages_history'] = []

for message in st.session_state['messages_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

user_input = st.chat_input(placeholder='Type your message here...')

if user_input:
    st.session_state['messages_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.markdown(user_input)

    # first add the message to message_history
    with st.chat_message('assistant'):

        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config= CONFIG,
                stream_mode= 'messages'
            )
        )
    st.session_state['messages_history'].append({'role': 'assistant', 'content': ai_message})
