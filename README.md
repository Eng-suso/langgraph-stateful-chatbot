# LangGraph Stateful Chatbot

Streamlit chatbot built with LangGraph, OpenAI, streaming responses, and thread-based checkpoint memory.

This project is designed as an AI engineering portfolio repo: it separates the UI from the agent backend, uses LangGraph state management, and demonstrates how conversation memory is controlled through `thread_id` checkpoints.

## Product Motivation

Most chatbot demos answer one message at a time, but real AI products need continuity. Users expect the assistant to remember the current conversation, separate one session from another, and respond in a way that feels live instead of blocking the interface.

The goal of this project is to show how a simple LLM chat interface can be designed like a real product foundation:

- each conversation has its own isolated memory
- the UI streams responses instead of waiting for the full completion
- the backend owns the AI workflow instead of mixing model logic into the interface
- configuration is kept outside the code so the app can move between local development and deployment

This demonstrates an AI engineering skill that goes beyond prompting: turning an LLM call into a stateful, maintainable application pattern.

## Features

- LangGraph `StateGraph` backend
- Checkpointed conversation memory with `MemorySaver`
- Thread-based chat sessions through `configurable.thread_id`
- Streaming assistant responses in Streamlit
- OpenAI model configuration through environment variables
- Separate backend and UI entry points

## Architecture

```text
app.py
  Streamlit UI
  - renders chat messages
  - creates a unique thread_id per conversation
  - streams assistant tokens from LangGraph

chatbot_backend.py
  LangGraph backend
  - defines ChatState
  - calls ChatOpenAI
  - appends messages with add_messages
  - compiles the graph with MemorySaver checkpointing
```

## Why LangGraph Checkpointing Matters

LangGraph checkpointing lets the app keep separate conversation histories without manually rebuilding the full prompt every time.

Each chat session has its own:

- `thread_id`
- message state
- checkpointed graph memory

The Streamlit app passes the active thread like this:

```python
config = {
    "configurable": {"thread_id": st.session_state["thread_id"]}
}
```

That `thread_id` tells LangGraph which conversation state to load and update.

## Tech Stack

- Python 3.12+
- Streamlit
- LangGraph
- LangChain Core
- LangChain OpenAI
- OpenAI API
- uv

## Setup

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/langgraph-stateful-chatbot.git
cd langgraph-stateful-chatbot
```

Install dependencies:

```bash
uv sync
```

Create your environment file:

```bash
cp .env.example .env
```

Add your OpenAI API key:

```text
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Run the Streamlit app:

```bash
uv run streamlit run app.py
```

## Repository Structure

```text
.
├── app.py
├── chatbot_backend.py
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
└── README.md
```

## Current Limitations

- `MemorySaver` keeps checkpoints in memory, so conversations reset when the process restarts.
- No authentication layer is included.
- No persistent database checkpointer is configured yet.
- No LangSmith tracing is enabled yet.

## Next Improvements

- Replace `MemorySaver` with SQLite or Postgres checkpoint persistence.
- Add LangSmith tracing for observability.
- Add automated tests for graph execution and thread isolation.
- Add Docker support for reproducible deployment.
- Add prompt/version tracking for production evaluation.

## License

This project is licensed under the MIT License.
