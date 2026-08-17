# AI-agents-

A sandbox for building and evaluating AI agents with [deepagents](https://github.com/langchain-ai/deepagents) and LangChain.

## Stack

- **[deepagents](https://pypi.org/project/deepagents/)** — agent orchestration on top of LangChain/LangGraph
- **[langchain-openai](https://pypi.org/project/langchain-openai/)** — model client, currently pointed at [Moonshot AI](https://www.moonshot.ai/)'s Kimi models through their OpenAI-compatible API
- **[anthropic](https://pypi.org/project/anthropic/)** — Claude SDK, for agents/tools built directly against the Anthropic API
- **[tavily-python](https://pypi.org/project/tavily-python/)** — web search tool for agents
- **[deepeval](https://pypi.org/project/deepeval/)** — LLM evaluation framework
- **[langsmith](https://pypi.org/project/langsmith/)** — tracing/observability for LangChain runs

## Setup

Requires Python 3.13 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

Create a `.env` file in the project root (see [Environment variables](#environment-variables) below).

## Running

```bash
uv run main.py
```

`main.py` currently wires up a minimal deep agent with a single dummy `get_weather` tool as a smoke test that the model, tool-calling, and agent loop all work end to end.

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `MOONSHOT_API_KEY` | Yes | API key for Moonshot AI's Kimi models |
| `LANGSMITH_TRACING` | No | Set to `true` to enable LangSmith tracing |
| `LANGSMITH_ENDPOINT` | No | LangSmith API endpoint |
| `LANGSMITH_API_KEY` | No | API key for LangSmith |
| `LANGSMITH_PROJECT` | No | LangSmith project name to log traces under |

`.env` is loaded automatically via `python-dotenv` and is gitignored — never commit it.
