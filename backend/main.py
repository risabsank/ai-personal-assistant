# backend/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from router import route_intent
from agent import run_agent
from tools import (
    tool_get_tomorrow_events,
    tool_get_free_slots,
    format_events,
    format_slots,
    tool_list_unread_emails,
    format_emails
)

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

# TODO: Replace with real Google creds loader
creds = None


def handle_request(user_input):
    intent = route_intent(user_input)

    if intent == "get_tomorrow_events":
        events = tool_get_tomorrow_events(creds)
        return format_events(events)

    elif intent == "get_free_slots":
        slots = tool_get_free_slots(creds)
        return format_slots(slots)

    elif intent == "list_unread_emails":
        emails = tool_list_unread_emails(creds)
        return format_emails(emails)

    else:
        return run_agent(user_input, creds)


@app.post("/chat")
def chat(req: ChatRequest):
    response = handle_request(req.message)
    return {"response": response}