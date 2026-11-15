from backend.chat_history import (
    init_db,
    create_conversation,
    save_message,
    get_chat_history,
    conversation_exists
)

session_id = "test-session-001"

init_db()
create_conversation(session_id)

save_message(session_id, "user", "Summarise this document.")
save_message(session_id, "assistant", "The document discusses leadership principles.")

print("Conversation exists:", conversation_exists(session_id))
print("Chat history:", get_chat_history(session_id))