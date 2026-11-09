def conversation_markdown(messages):
    parts = ["# OmniBrain Conversation", ""]
    for m in messages:
        role = "You" if m["role"] == "user" else "OmniBrain"
        parts.extend([f"## {role}", "", m["content"], ""])
    return "\n".join(parts)
