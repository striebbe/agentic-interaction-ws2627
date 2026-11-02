"""Logging for the calendar assistant."""

import json
from datetime import UTC, datetime
from pathlib import Path

from agent.config import Config
from agent.types import Event


class Logger:
    """Writes the events of a single run to its own JSONL file."""

    def __init__(self):
        """Create the logs/ folder and open a new log file with a unique run_id."""
        self.stopwatch = StopWatch()

        root = Path(__file__).resolve().parent.parent
        log_dir = root / "logs"
        log_dir.mkdir(exist_ok=True)

        stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S-%f")
        self.run_id = f"run-{stamp}"

        self.file = (log_dir / f"{self.run_id}.jsonl").open("w", encoding="utf-8")

    def log(
        self,
        event: Event,
        tool: str | None = None,
        args: str | None = None,
        ok: bool | None = None,
        stopwatch: str | None = None,
    ):
        """Write a log entry to the JSONL file."""
        duration = self.stopwatch.stop(stopwatch) if stopwatch else None
        record = {
            "ts": datetime.now(UTC).isoformat(),
            "run_id": self.run_id,
            "event": event.value,
            "tool": tool,
            "args": args,
            "ok": ok,
            "model": Config.MODEL,
            "duration_ms": duration,
        }
        record = {k: v for k, v in record.items() if v is not None}
        self.file.write(json.dumps(record, ensure_ascii=False) + "\n")
        # Flush so the log stays complete if the run crashes.
        self.file.flush()


class StopWatch:
    """A simple stopwatch for measuring durations."""

    def __init__(self):
        """Initialize the StopWatch class."""
        self._stopWatches = {}

    def start(self, name: str):
        """Start a stopwatch with the given name."""
        self._stopWatches[name] = datetime.now(UTC)

    def stop(self, name: str) -> int:
        """Stop the stopwatch with the given name.

        return the duration between start and end in milliseconds.
        """
        if name not in self._stopWatches:
            raise ValueError(f"No stopwatch found with name '{name}'")
        end_timestamp = datetime.now(UTC)
        start_timestamp = self._stopWatches.pop(name)
        duration = (end_timestamp - start_timestamp).total_seconds() * 1000
        return int(duration)
