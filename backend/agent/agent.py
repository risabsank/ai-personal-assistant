# agent.py

import json
from config import client, MODEL, TOOLS
from memory import add_message, get_messages
from tools import (
    tool_get_tomorrow_events,
    tool_get_free_slots,
    tool_schedule_meeting,
    tool_list_unread_emails,
    tool_get_unread_from_sender,
    tool_send_email
)


def run_agent(user_input, creds=None):
    add_message("user", user_input)

    MAX_STEPS = 6
    step_count = 0

    while step_count < MAX_STEPS:
        step_count += 1

        messages = get_messages()

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
        )

        message = response.choices[0].message

        # Final answer
        if not message.tool_calls:
            add_message("assistant", message.content)
            return message.content

        # Save assistant tool call
        add_message("assistant", message.model_dump_json())

        # Execute tools
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            try:
                if name == "get_tomorrow_events":
                    result = tool_get_tomorrow_events(creds)

                elif name == "get_free_slots":
                    result = tool_get_free_slots(creds)

                elif name == "schedule_meeting":
                    result = tool_schedule_meeting(creds, **args)

                elif name == "list_unread_emails":
                    result = tool_list_unread_emails(creds, **args)

                elif name == "get_unread_from_sender":
                    result = tool_get_unread_from_sender(creds, **args)

                elif name == "send_email":
                    result = tool_send_email(creds, **args)

                else:
                    result = {"error": "Unknown tool"}

            except Exception as e:
                result = {"error": str(e)}

            add_message("tool", json.dumps(result))

    return "I couldn't complete the task."
