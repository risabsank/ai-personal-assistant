from googleapiclient.discovery import build
from datetime import datetime, timedelta
from dateutil import tz
from typing import List, Dict, Optional

# ----------------------
# Google Calendar service
# ----------------------
def get_calendar_service(creds):
    """Return a Google Calendar service object from credentials."""
    return build("calendar", "v3", credentials=creds)

# ----------------------
# Helper functions
# ----------------------
def local_now() -> datetime:
    """Return current local datetime."""
    return datetime.now(tz=tz.tzlocal())

def start_of_day(dt: datetime) -> datetime:
    """Return datetime set to start of the day (00:00 local time)."""
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)

# ----------------------
# Event retrieval
# ----------------------
def get_events(
    creds,
    start: datetime,
    end: datetime,
    calendar_id: str = "primary",
    keyword: Optional[str] = None,
) -> List[Dict]:
    """
    Retrieve calendar events between start and end datetimes.
    Optionally filter by a keyword in the title.
    """
    service = get_calendar_service(creds)
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = events_result.get("items", [])
    if keyword:
        events = [e for e in events if keyword.lower() in e.get("summary", "").lower()]

    return events

def get_tomorrow_events(creds) -> List[Dict]:
    """Return all events for tomorrow."""
    tomorrow_start = start_of_day(local_now() + timedelta(days=1))
    tomorrow_end = tomorrow_start + timedelta(days=1)
    return get_events(creds, tomorrow_start, tomorrow_end)

# ----------------------
# Busy/Free computation
# ----------------------
def get_busy_intervals(creds, start: datetime, end: datetime) -> List[tuple]:
    """Return (start, end) datetime tuples for busy intervals."""
    events = get_events(creds, start, end)
    intervals = []
    for e in events:
        s = e["start"].get("dateTime") or e["start"].get("date")
        e_ = e["end"].get("dateTime") or e["end"].get("date")
        intervals.append((datetime.fromisoformat(s), datetime.fromisoformat(e_)))
    return intervals

def get_free_slots(creds, start: datetime, end: datetime, min_duration_minutes: int = 30):
    """Return free time slots between start and end."""
    busy = get_busy_intervals(creds, start, end)
    busy.sort()
    free_slots = []

    current = start
    for s, e in busy:
        if current < s and (s - current).total_seconds() >= min_duration_minutes * 60:
            free_slots.append((current, s))
        current = max(current, e)

    if current < end and (end - current).total_seconds() >= min_duration_minutes * 60:
        free_slots.append((current, end))

    return free_slots

# ----------------------
# Utility functions
# ----------------------
def get_first_event(creds, start: datetime, end: datetime) -> Optional[Dict]:
    """Return the first event in a range."""
    events = get_events(creds, start, end)
    if not events:
        return None
    first = events[0]
    return {
        "title": first.get("summary", "No title"),
        "start_time": datetime.fromisoformat(first["start"].get("dateTime")),
        "end_time": datetime.fromisoformat(first["end"].get("dateTime")),
    }

# ----------------------
# Write functions (optional)
# ----------------------
def schedule_meeting(creds, start: datetime, end: datetime, title: str, attendees: Optional[List[str]] = None):
    """
    Schedule a new meeting.
    Returns the Google Calendar event link.
    """
    service = get_calendar_service(creds)
    event = {
        "summary": title,
        "start": {"dateTime": start.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end.isoformat(), "timeZone": "UTC"},
        "attendees": [{"email": a} for a in attendees] if attendees else [],
    }
    created = service.events().insert(calendarId="primary", body=event, sendUpdates="all").execute()
    return created.get("htmlLink")
