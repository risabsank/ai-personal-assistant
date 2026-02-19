# router.py

def route_intent(user_input: str):
    text = user_input.lower()

    if "tomorrow" in text and ("what" in text or "do i have" in text):
        return "get_tomorrow_events"

    if "free slot" in text or "available time" in text:
        return "get_free_slots"

    if "schedule" in text or "book meeting" in text:
        return "schedule_meeting"
    
    if "unread email" in text or "check email" in text:
        return "list_unread_emails"

    if "email from" in text:
        return "get_unread_from_sender"

    if "send email" in text:
        return "send_email"

    return "agent"
