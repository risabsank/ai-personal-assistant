from googleapiclient.discovery import build
from typing import List, Dict, Optional

# ----------------------
# Gmail service
# ----------------------
def get_gmail_service(creds):
    """Return Gmail service object from credentials."""
    return build("gmail", "v1", credentials=creds)

# ----------------------
# Read emails
# ----------------------
def list_messages(creds, query: Optional[str] = None, max_results: int = 50) -> List[Dict]:
    """List message IDs matching a query."""
    service = get_gmail_service(creds)
    response = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    return response.get("messages", [])

def get_message(creds, msg_id: str) -> Dict:
    """Retrieve full message by ID."""
    service = get_gmail_service(creds)
    message = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    return message

def get_unread_from_sender(creds, sender_email: str, max_results: int = 10) -> List[Dict]:
    """Get unread emails from a specific sender."""
    query = f"from:{sender_email} is:unread"
    messages = list_messages(creds, query=query, max_results=max_results)
    return [get_message(creds, m["id"]) for m in messages]

def has_responded(creds, thread_id: str) -> bool:
    """
    Check if a thread has any messages from others (i.e., a reply exists).
    """
    service = get_gmail_service(creds)
    thread = service.users().threads().get(userId="me", id=thread_id).execute()
    messages = thread.get("messages", [])
    for m in messages:
        headers = {h["name"]: h["value"] for h in m["payload"]["headers"]}
        if headers.get("From") != "me":
            return True
    return False

# ----------------------
# Send email (write)
# ----------------------
def send_email(creds, to: str, subject: str, body: str):
    """
    Send an email using Gmail API.
    Requires 'https://www.googleapis.com/auth/gmail.send' scope.
    """
    import base64
    from email.mime.text import MIMEText

    service = get_gmail_service(creds)

    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return sent.get("id")
