from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages

load_dotenv()
llm = ChatOpenAI(model_name="gpt-4.1-mini", 
                 temperature=0.25, 
                 max_completion_tokens=1000, 
                 timeout= (10,60),  
                 max_retries=3,
                 stream_usage=True,
                 )


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):
    #take user query from the state and send it to the LLM
    messages = state["messages"]
    #send to llm
    response = llm.stream(messages)

    #add the response to the state
    return {'messages': [response]}

checkpoint = MemorySaver()

graph = StateGraph(ChatState)

graph.add_node('chatbot', chat_node)

graph.add_edge(START, 'chatbot')
graph.add_edge('chatbot', END)
graph.compile(checkpointer=checkpoint)
