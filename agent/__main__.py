"""A simple calendar assistant that uses the OpenAI Chat Completions API with tool calls."""  # noqa: E501

import json
import sys
import urllib.error
import urllib.request

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionMessageFunctionToolCall,
)

from agent.config import Config
from agent.logger import Logger
from agent.types import Event

client = OpenAI(base_url=Config.OPENAI_BASE_URL, api_key=Config.OPENAI_API_KEY)
logger = Logger()


def get_calendar_day(date: str):
    """Return all calendar events (title, start, end, location) for a single day."""
    url = f"{Config.DATA_BASE_URL.rstrip('/')}/calendar/{date}.json"
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Return an empty list for a free day, instead of an error.
            return {"date": date, "events": [], "note": "keine Daten (404)"}
        return {"error": f"HTTP {e.code}"}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


def main():
    """Run the calendar assistant with a user question from the command line."""
    # get the users question from the command line arguments
    if len(sys.argv) < 2:
        print("Aufruf: python -m agent <Frage>", file=sys.stderr)
        return 2
    question = " ".join(sys.argv[1:])

    # The openai chat api is stateless,
    # so the conversation has to be stored in a list of messages,
    # which is sent with each request.
    messages = [
        {
            "role": "system",
            "content": "Du bist ein Kalenderassistent."
            "Nutze die Funktion get_calendar_day, um Informationen über"
            "Termine und Ereignisse zu liefern."
            "Antworte nur mit den relevanten Informationen und verwende keine"
            "unnötigen Erklärungen.",
        },
        {"role": "user", "content": question},
    ]
    logger.log(Event.USER_TASK)

    answer = ""
    try:
        # Limit the number of steps to avoid infinite loops
        # if the model keeps requesting tool calls.
        for _ in range(Config.MAX_STEPS):
            logger.stopwatch.start("full_run")

            # Asks the model for a response
            # passes the current conversation
            # and the list of tools (functions) it can call.
            response = client.chat.completions.create(
                model=Config.MODEL,
                messages=messages,  # type: ignore
                tools=Config.TOOLS,
            )

            message = response.choices[0].message
            messages.append(message.model_dump(exclude_none=True))  # type: ignore

            # If the model has not requested any tool calls, it has finished the run.
            if not message.tool_calls:
                answer = message.content or ""
                logger.log(Event.FINAL, ok=True, stopwatch="full_run")
                break

            for tool_call in message.tool_calls:
                # type check to keep the linter happy
                if not isinstance(tool_call, ChatCompletionMessageFunctionToolCall):
                    # respond to the model with an error message
                    result = {
                        "error": "ungültiger Tool Call:"
                        "es wird ein Funktionsname als Tool erwartet"
                    }
                    logger.log(
                        Event.TOOL_CALL,
                        ok=False,
                    )
                # The model requests get_calendar_day
                elif tool_call.function.name == "get_calendar_day":
                    try:
                        # get the arguments from the model request
                        # and call the get_calendar_day function with the date argument.
                        arguments = json.loads(tool_call.function.arguments)

                        logger.log(
                            Event.TOOL_CALL,
                            tool=tool_call.function.name,
                            args=tool_call.function.arguments,
                        )
                        logger.stopwatch.start("tool_call")

                        # respond to the model with the result of the
                        # get_calendar_day function call.
                        result = get_calendar_day(arguments["date"])

                        logger.log(
                            Event.TOOL_RESULT,
                            tool=tool_call.function.name,
                            args=tool_call.function.arguments,
                            ok="error" not in result,
                            stopwatch="tool_call",
                        )
                    except (json.JSONDecodeError, KeyError) as e:
                        # respond to the model with an error message
                        result = {
                            "error": f"ungültige Argumente für get_calendar_day: {e}"
                        }
                        logger.log(
                            Event.TOOL_CALL,
                            tool=tool_call.function.name,
                            args=tool_call.function.arguments,
                            ok=False,
                        )
                # the model requested a tool that is not implemented
                else:
                    # respond to the model with an error message
                    result = {"error": f"unbekanntes Tool: {tool_call.function.name}"}
                    logger.log(
                        Event.TOOL_CALL,
                        tool=tool_call.function.name,
                        args=tool_call.function.arguments,
                        ok=False,
                    )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )
        else:
            logger.log(Event.FINAL, ok=False)
            print("Error: maximale Anzahl an Versuchen erreicht", file=sys.stderr)
            return 3
    except Exception as e:  # noqa: BLE001
        logger.log(Event.ERROR, ok=False)
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(answer)
    return 0


if __name__ == "__main__":
    sys.exit(main())
