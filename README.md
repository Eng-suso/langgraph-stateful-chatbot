# LangGraph Stateful Chatbot

Stateful AI chatbot built with Streamlit, LangGraph, OpenAI, streaming responses, SQLite checkpointing, and LLM-generated conversation titles.

## Product Motivation

Most chatbot demos are stateless: they answer one message at a time and lose the feeling of continuity. Real AI products need persistent conversations, fast perceived response time, and a clean separation between user experience and model orchestration.

This project demonstrates how to turn a basic LLM call into a product-style chatbot foundation:

- conversation memory is isolated by thread
- assistant responses stream in real time
- conversation titles are generated from context
- UI logic is separated from the LangGraph backend
- local persistence is handled without exposing user data in Git

## Features

- Streamlit chat interface
- LangGraph `StateGraph` backend
- OpenAI chat model integration
- Token streaming for assistant responses
- SQLite-backed checkpoints with `SqliteSaver`
- Persistent sidebar conversation history
- LLM-generated chat titles
- Hidden technical thread IDs
- `.env.example` for safe configuration

## Architecture

```text
app.py
  Streamlit UI, chat rendering, sidebar history, streamed thread titles

chatbot_backend.py
  In-memory LangGraph version using MemorySaver

chatbot_backend_db.py
  SQLite-backed LangGraph version using SqliteSaver
  Stores checkpoint state and conversation metadata
```

The app uses `chatbot_backend_db.py` by default. `chatbot_backend.py` is kept as a simpler in-memory version to show the progression from prototype memory to persistent memory.

## Persistence

LangGraph checkpoints are stored in `chatbot_memory.db`, while conversation metadata such as `thread_id`, title, and timestamps is stored in a SQLite table. This lets the app rebuild the sidebar after refresh or restart.

Runtime files are intentionally excluded from Git, so cloned copies start with an empty local memory:

```text
*.db
*.db-shm
*.db-wal
.env
.env.*
```

## Tech Stack

- Python 3.12+
- Streamlit
- LangGraph
- LangChain
- OpenAI
- SQLite
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

Create a local environment file:

```bash
cp .env.example .env
```

Add your OpenAI API key:

```text
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Run the app:

```bash
uv run streamlit run app.py
```

## Repository Structure

```text
.
|-- app.py
|-- chatbot_backend.py
|-- chatbot_backend_db.py
|-- pyproject.toml
|-- uv.lock
|-- .env.example
|-- .gitignore
|-- LICENSE
`-- README.md
```

## Future Improvements

- Replace local SQLite with Postgres for production multi-user persistence
- Add LangSmith tracing for observability
- Add automated tests for graph execution and thread isolation
- Add Docker support for reproducible deployment

## License

MIT License
