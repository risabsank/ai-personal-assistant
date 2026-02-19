# memory.py

conversation_history = []

def add_message(role, content):
    conversation_history.append({
        "role": role,
        "content": content
    })

def get_messages():
    # limit memory size
    return conversation_history[-30:]

def reset_memory():
    global conversation_history
    conversation_history = []
