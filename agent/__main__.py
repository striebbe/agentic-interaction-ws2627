"""A simple calendar assistant that uses the OpenAI Chat Completions API with tool calls."""  # noqa: E501

import json
import sys
import urllib.error
import urllib.request
from datetime import date, datetime

import openai
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionMessageFunctionToolCall,
)

from agent.config import Config
from agent.logger import Logger
from agent.types import Event

client = OpenAI(
    base_url=Config.OPENAI_BASE_URL,
    api_key=Config.OPENAI_API_KEY,
    timeout=Config.TIMEOUT,
    max_retries=Config.MAX_RETRIES,
)
logger = Logger()


def get_calendar_day(date: str):
    """Return all calendar events (title, start, end, location) for a single day."""
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except (TypeError, ValueError):
        return {"error": f"invalid date '{date}', expected YYYY-MM-DD"}

    url = f"{Config.DATA_BASE_URL.rstrip('/')}/calendar/{date}.json"
    try:
        with urllib.request.urlopen(url, timeout=Config.TIMEOUT) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Return an empty list for a free day, instead of an error.
            return {"date": date, "events": [], "note": "keine Daten (404)"}
        return {"error": f"HTTP {e.code}"}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


def run_tool(tool_call: ChatCompletionMessageFunctionToolCall):
    """Run a tool call and return the result."""
    tool_name = tool_call.function.name
    tool_arguments = tool_call.function.arguments

    logger.log(Event.TOOL_CALL, tool=tool_name, args=tool_arguments)
    logger.stopwatch.start("tool_call")

    try:
        if tool_name == "get_calendar_day":
            # get the arguments from the model request
            # and call the get_calendar_day function with the date argument.
            arguments = json.loads(tool_arguments)

            # respond to the model with the result of the
            # get_calendar_day function call.
            result = get_calendar_day(arguments["date"])
        else:
            # the model requested a tool that is not implemented
            result = {"error": f"unbekanntes Tool: {tool_call.function.name}"}
    except Exception as e:  # noqa: BLE001
        # respond to the model with an error message
        result = {"error": f"ungültige Argumente für {tool_call.function.name}: {e}"}

    logger.log(
        Event.TOOL_RESULT,
        tool=tool_name,
        args=tool_arguments,
        ok="error" not in result,
        stopwatch="tool_call",
    )
    return result


def main():
    """Run the calendar assistant with a user question from the command line."""
    # get the users question from the command line arguments
    if len(sys.argv) < 2:
        print("Aufruf: python -m agent <Frage>", file=sys.stderr)
        return 2
    question = " ".join(sys.argv[1:])
    if question.strip() == "":
        print("Fehler: keine Frage angegeben", file=sys.stderr)
        return 2

    # The openai chat api is stateless,
    # so the conversation has to be stored in a list of messages,
    # which is sent with each request.
    messages = [
        {
            "role": "system",
            "content": (
                "Du bist ein Kalenderassistent. "
                f"Heute ist {date.today().isoformat()}. "
                "Nutze get_calendar_day (ein Aufruf pro Tag), um Termine abzufragen. "
                "Antworte nur mit den relevanten Informationen. "
                "Liefert ein Tool einen Fehler, korrigiere den Aufruf oder sage, "
                "dass die Information nicht verfügbar ist."
            ),
        },
        {"role": "user", "content": question},
    ]
    logger.log(Event.USER_TASK)

    answer = ""
    try:
        logger.stopwatch.start("full_run")

        # Limit the number of steps to avoid infinite loops
        # if the model keeps requesting tool calls.
        for _ in range(Config.MAX_STEPS):
            try:
                # Asks the model for a response
                # passes the current conversation
                # and the list of tools (functions) it can call.
                response = client.chat.completions.create(
                    model=Config.MODEL,
                    messages=messages,  # type: ignore
                    tools=Config.TOOLS,
                )
            except openai.BadRequestError as e:
                if "tool call validation failed" in str(e):
                    logger.log(Event.ERROR, ok=False)
                    print(
                        "Error: ungültiger Tool Call vom Modell angefordert",
                        file=sys.stderr,
                    )
                    continue
                else:
                    raise
            except openai.RateLimitError:
                logger.log(Event.ERROR, ok=False)
                print(
                    "Error: Rate limit des Modells erreicht",
                    file=sys.stderr,
                )
                continue

            message = response.choices[0].message
            messages.append(message.model_dump(exclude_none=True))  # type: ignore

            # If the model has not requested any tool calls, it has finished the run.
            if not message.tool_calls:
                answer = (message.content or "").strip()
                logger.log(Event.FINAL, ok=bool(answer), stopwatch="full_run")
                if not answer:
                    print("Error: keine Antwort vom Modell erhalten", file=sys.stderr)
                    return 1
                break

            for tool_call in message.tool_calls:
                if isinstance(tool_call, ChatCompletionMessageFunctionToolCall):
                    result = run_tool(tool_call)
                else:
                    result = {
                        "error": "ungültiger Tool Call:"
                        "es wird ein Funktionsname als Tool erwartet"
                    }
                    logger.log(Event.TOOL_CALL, ok=False)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )
        else:
            logger.log(Event.FINAL, ok=False)
            print("Error: maximale Anzahl an Aufrufen erreicht", file=sys.stderr)
            return 3

    except Exception as e:  # noqa: BLE001
        logger.log(Event.ERROR, ok=False)
        print(f"Error: unerwarteter Fehler ({type(e).__name__}): {e}", file=sys.stderr)
        return 1

    print(answer)
    return 0


if __name__ == "__main__":
    sys.exit(main())
