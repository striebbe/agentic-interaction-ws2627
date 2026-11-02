"""Configuration for the calendar assistant."""

from typing import ClassVar

from environs import Env
from openai.types.chat import (
    ChatCompletionToolParam,
)

env = Env()
env.read_env()


class Config:
    """Configuration for the calendar assistant."""

    OPENAI_BASE_URL: str = env.str("OPENAI_BASE_URL")
    MODEL: str = env.str("MODEL")
    OPENAI_API_KEY: str = env.str("OPENAI_API_KEY")
    DATA_BASE_URL: str = env.str("DATA_BASE_URL")

    MAX_STEPS: int = 5

    TOOLS: ClassVar[list[ChatCompletionToolParam]] = [
        {
            "type": "function",
            "function": {
                "name": "get_calendar_day",
                "description": (
                    "Liefert alle Kalendertermine (Titel, Start, Ende, Ort)"
                    "eines einzelnen Tages. Ein freier Tag hat eine leere Liste."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": (
                                "Datum im Format YYYY-MM-DD, z.B. 2026-10-28"
                            ),
                        },
                    },
                },
            },
        }
    ]
