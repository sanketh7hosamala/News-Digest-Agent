# News Agent

Researches recent news on topics you define, using Claude's built-in web search tool, and writes a Markdown digest.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

Web search must be enabled for your organization in the Anthropic Console.

## Run

```bash
python news_agent.py                      # topics from topics.json
python news_agent.py -t "EU AI Act" -t "Bundesliga"   # ad-hoc topics
```

Digests are saved to `digests/YYYY-MM-DD.md`.

## Topic options (topics.json)

| Field | Meaning |
|---|---|
| `name` | Topic to research (required) |
| `focus` | Angle or sub-themes to prioritise |
| `days` | Time window in days (default 2) |
| `max_searches` | Cap on web searches per topic (default 5) |
| `allowed_domains` / `blocked_domains` | Restrict or exclude sources (use one, not both) |

Set `NEWS_AGENT_MODEL` to change the model (default `claude-sonnet-5-5`).

## Run it daily

```cron
0 7 * * * cd /path/to/news-agent && .venv/bin/python news_agent.py >> agent.log 2>&1
```
