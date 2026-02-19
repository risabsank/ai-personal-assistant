# tools.py

from datetime import datetime, timedelta
from dateutil import tz
from typing import List, Dict, Optional

from backend.calendar_api import (
    get_tomorrow_events,
    get_free_slots as api_get_free_slots,
    schedule_meeting as api_schedule_meeting,
    local_now,
    start_of_day,
)

from backend.gmail_api import (
    list_messages,
    get_message,
    get_unread_from_sender as api_get_unread_from_sender,
    send_email as api_send_email,
)

# --------------------------------
# Helpers
# --------------------------------

def format_datetime(dt: datetime) -> str:
    """Format datetime for human-readable output."""
    return dt.astimezone(tz.tzlocal()).strftime("%Y-%m-%d %I:%M %p")


def parse_iso_datetime(dt_str: str) -> datetime:
    """
    Parse ISO string into datetime.
    Assumes ISO 8601 input.
    """
    return datetime.fromisoformat(dt_str)


# --------------------------------
# TOOL: Get Tomorrow Events
# --------------------------------

def tool_get_tomorrow_events(creds):
    events = get_tomorrow_events(creds)

    formatted = []
    for e in events:
        start_str = e["start"].get("dateTime") or e["start"].get("date")
        end_str = e["end"].get("dateTime") or e["end"].get("date")

        start_dt = datetime.fromisoformat(start_str)
        end_dt = datetime.fromisoformat(end_str)

        formatted.append({
            "summary": e.get("summary", "No title"),
            "start": format_datetime(start_dt),
            "end": format_datetime(end_dt),
        })

    return formatted


# --------------------------------
# TOOL: Get Free Slots (Tomorrow)
# --------------------------------

def tool_get_free_slots(creds, min_duration_minutes: int = 30):
    tomorrow_start = start_of_day(local_now() + timedelta(days=1))
    tomorrow_end = tomorrow_start + timedelta(days=1)

    free_slots = api_get_free_slots(
        creds,
        tomorrow_start,
        tomorrow_end,
        min_duration_minutes=min_duration_minutes,
    )

    formatted = []
    for start_dt, end_dt in free_slots:
        formatted.append({
            "start": format_datetime(start_dt),
            "end": format_datetime(end_dt),
        })

    return formatted


# --------------------------------
# TOOL: Schedule Meeting
# --------------------------------

def tool_schedule_meeting(
    creds,
    title: str,
    start_time: str,
    end_time: str,
    attendees: Optional[List[str]] = None,
):
    """
    start_time and end_time must be ISO strings.
    """

    try:
        start_dt = parse_iso_datetime(start_time)
        end_dt = parse_iso_datetime(end_time)

        link = api_schedule_meeting(
            creds,
            start=start_dt,
            end=end_dt,
            title=title,
            attendees=attendees,
        )

        return {
            "status": "success",
            "title": title,
            "start": format_datetime(start_dt),
            "end": format_datetime(end_dt),
            "event_link": link,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


# --------------------------------
# FORMATTERS (for deterministic routing)
# --------------------------------

def format_events(events: List[Dict]) -> str:
    if not events:
        return "You have no events tomorrow."

    response = "Tomorrow's schedule:\n"
    for i, e in enumerate(events, 1):
        response += f"{i}. {e['summary']} from {e['start']} to {e['end']}\n"

    return response


def format_slots(slots: List[Dict]) -> str:
    if not slots:
        return "No free slots available tomorrow."

    response = "Available time slots tomorrow:\n"
    for s in slots:
        response += f"- {s['start']} to {s['end']}\n"

    return response


# --------------------------------
# TOOL: List Unread Emails
# --------------------------------

def tool_list_unread_emails(creds, max_results: int = 5):
    messages = list_messages(creds, query="is:unread", max_results=max_results)

    formatted = []

    for m in messages:
        full = get_message(creds, m["id"])

        headers = {
            h["name"]: h["value"]
            for h in full["payload"]["headers"]
        }

        formatted.append({
            "id": m["id"],
            "from": headers.get("From"),
            "subject": headers.get("Subject"),
            "date": headers.get("Date"),
        })

    return formatted


# --------------------------------
# TOOL: Get Unread From Sender
# --------------------------------

def tool_get_unread_from_sender(creds, sender_email: str):
    messages = api_get_unread_from_sender(creds, sender_email)

    formatted = []

    for full in messages:
        headers = {
            h["name"]: h["value"]
            for h in full["payload"]["headers"]
        }

        formatted.append({
            "from": headers.get("From"),
            "subject": headers.get("Subject"),
            "date": headers.get("Date"),
        })

    return formatted


# --------------------------------
# TOOL: Send Email
# --------------------------------

def tool_send_email(creds, to: str, subject: str, body: str):
    try:
        msg_id = api_send_email(creds, to=to, subject=subject, body=body)

        return {
            "status": "sent",
            "message_id": msg_id,
            "to": to,
            "subject": subject,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


# --------------------------------
# FORMATTERS (Deterministic Output)
# --------------------------------

def format_emails(emails):
    if not emails:
        return "No emails found."

    response = ""
    for i, e in enumerate(emails, 1):
        response += (
            f"{i}. From: {e.get('from')}\n"
            f"   Subject: {e.get('subject')}\n"
            f"   Date: {e.get('date')}\n\n"
        )

    return response