from typing import List, Dict, Any

def generate_conversation_summary(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Summarizes customer chat transcript into structured summary for human support agents.
    """
    user_msgs = [m["content"] for m in messages if m.get("sender") == "user"]
    if not user_msgs:
        return {
            "issue_summary": ["Customer requested support agent escalation."],
            "recommended_action": "Review customer account details and assist with query."
        }

    first_query = user_msgs[0]
    last_query = user_msgs[-1]
    msg_count = len(user_msgs)

    # Key issue extraction heuristic
    issue_bullet_1 = f"Customer initiated chat regarding: '{first_query}'."
    if msg_count > 1:
        issue_bullet_2 = f"Follow-up details provided: '{last_query}'."
    else:
        issue_bullet_2 = "Query could not be fully resolved using automated Knowledge Base."

    issue_bullet_3 = "Customer selected human support escalation handoff."

    # Recommended action
    query_lower = " ".join(user_msgs).lower()
    if any(k in query_lower for k in ["payment", "charge", "card", "declined"]):
        rec_action = "Inspect Stripe/Payment gateway logs, verify customer payment status, and offer manual checkout link."
    elif any(k in query_lower for k in ["refund", "return", "money back"]):
        rec_action = "Review customer order invoice timeline and verify 30-day money back eligibility."
    elif any(k in query_lower for k in ["password", "account", "login", "hacked"]):
        rec_action = "Verify customer account email identity and issue secure 2FA/Password override link."
    else:
        rec_action = "Contact customer via registered email to address specialized support inquiry."

    return {
        "issue_summary": [
            issue_bullet_1,
            issue_bullet_2,
            issue_bullet_3
        ],
        "recommended_action": rec_action
    }

def calculate_ticket_priority(category: str, user_query: str) -> str:
    """Calculates ticket priority based on issue sensitivity."""
    q = user_query.lower()
    if any(k in q for k in ["hacked", "security breach", "unauthorized", "500 error", "urgent", "system crash"]):
        return "Urgent"
    if any(k in q for k in ["payment declined", "charged twice", "double charge", "cannot pay", "fail"]):
        return "High"
    if any(k in q for k in ["refund", "cancel subscription", "billing"]):
        return "Medium"
    return "Low"
