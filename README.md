# News Agent

Researches recent news on topics you define, using only Configured sources and avoiding a general web search tool, and writes a Markdown digest.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

## Run

```bash
python interactive_agent.py
```

## Add News Source in the System Instructions

under Configured sources

