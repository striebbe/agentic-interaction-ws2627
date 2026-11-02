# agentic-interaction-ws2627

Calendar assistant for the exercise *Agentic Interaction* (WS 2026/27, Ulm University).
The model calls the tool `get_calendar_day` to read the appointments of a single day
and answers the question with the result (model → tool → model).

## Setup

Requires Python 3.12+, tested with Python 3.15.2 (see `.python-version`).

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the repository root (never commit it). Environment
variables take precedence over the file.

| Variable          | Meaning                                                     |
|-------------------|-------------------------------------------------------------|
| `OPENAI_BASE_URL` | OpenAI-compatible endpoint, e.g. `https://api.groq.com/openai/v1` |
| `MODEL`           | Model name sent to the endpoint, e.g. `openai/gpt-oss-20b`  |
| `OPENAI_API_KEY`  | API key                                                     |
| `DATA_BASE_URL`   | `https://jhbelz.github.io/agentic-interaction-data/v1`      |

## Usage

Run from the repository root:

```bash
python -m agent "Was steht am 2026-10-29 im Kalender?"
```

The answer goes to standard output. Exit codes:

| Code | Meaning                                        |
|------|------------------------------------------------|
| 0    | Answer produced                                |
| 1    | Unexpected error (message on stderr)           |
| 2    | No question given                              |
| 3    | Step limit (`MAX_STEPS`) reached without answer |

## Project structure

| File               | Content                                                         |
|--------------------|-----------------------------------------------------------------|
| `agent/__main__.py`| Entry point, agent loop, tool implementation `get_calendar_day` |
| `agent/config.py`  | Configuration from `.env` file, and static configuration values |
| `agent/logger.py`  | `Logger` and `StopWatch` classes for logging and timekeeping    |
| `agent/types.py`   | `Event` enum with the log event types                           |

## Tool

`get_calendar_day(date)` reads `{DATA_BASE_URL}/calendar/{YYYY-MM-DD}.json`.
A 404 yields an empty event list (free day); other errors are returned to the
model as `{"error": ...}`.

## Logs

Every run writes its own JSONL file `logs/run-<timestamp>.jsonl` (one JSON
object per line; the folder is git-ignored). Fields without a value are omitted.

| Field         | Content                                                          |
|---------------|------------------------------------------------------------------|
| `ts`          | Timestamp, ISO 8601 (UTC)                                        |
| `run_id`      | One ID per run                                                   |
| `event`       | `user_task`, `tool_call`, `tool_result`, `final`, `error`        |
| `tool`, `args`| Tool name and raw arguments                                      |
| `ok`          | Whether the step succeeded                                       |
| `model`       | Model name as sent to the endpoint                               |
| `duration_ms` | Duration of the step (tool execution, or model step for `final`) |

Example:

```json
{"ts": "2026-10-29T10:00:00+00:00", "run_id": "run-20261029-100000-000000", "event": "tool_result", "tool": "get_calendar_day", "args": "{\"date\": \"2026-10-29\"}", "ok": true, "model": "openai/gpt-oss-20b", "duration_ms": 120}
```
