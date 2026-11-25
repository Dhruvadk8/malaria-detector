import re
from typing import Dict, Any, List

HUMAN_REQUEST_KEYWORDS = [
    "human", "agent", "talk to human", "real person", "representative", 
    "speak to a person", "connect me to human", "support team", "customer care agent",
    "operator", "live agent"
]

AMBIGUOUS_PATTERNS = {
    "payment": ["payment isn't working", "payment failed", "payment error", "can't pay", "problem with payment", "my payment isn't working"],
    "account": ["account issue", "can't login", "account problem", "access issue"],
    "order": ["where is my order", "order issue", "problem with order", "order delayed"]
}

def understand_query(user_query: str) -> Dict[str, Any]:
    """Analyzes user intent, checks for human escalation requests and ambiguity."""
    query_lower = user_query.lower().strip()
    
    # 1. Check for explicit human agent request
    if any(k in query_lower for k in HUMAN_REQUEST_KEYWORDS):
        return {
            "intent": "explicit_human_request",
            "is_human_requested": True,
            "is_ambiguous": False,
            "category": "General Support"
        }
    
    # 2. Check for known ambiguous patterns
    for category, patterns in AMBIGUOUS_PATTERNS.items():
        if any(p in query_lower for p in patterns):
            return {
                "intent": f"ambiguous_{category}",
                "is_human_requested": False,
                "is_ambiguous": True,
                "category": category.capitalize()
            }
            
    # 3. Standard classification heuristics
    if any(k in query_lower for k in ["password", "reset", "forgot password"]):
        intent = "password_reset"
        category = "Password"
    elif any(k in query_lower for k in ["refund", "return money", "money back"]):
        intent = "refund_request"
        category = "Refunds"
    elif any(k in query_lower for k in ["payment", "credit card", "debit", "upi", "pay"]):
        intent = "payment_inquiry"
        category = "Payments"
    elif any(k in query_lower for k in ["cancel subscription", "unsubscribe", "stop plan"]):
        intent = "cancel_subscription"
        category = "Subscription"
    elif any(k in query_lower for k in ["invoice", "receipt", "billing"]):
        intent = "billing_inquiry"
        category = "Billing"
    elif any(k in query_lower for k in ["track", "order status", "shipping"]):
        intent = "order_tracking"
        category = "Orders"
    else:
        intent = "general_inquiry"
        category = "General"

    return {
        "intent": intent,
        "is_human_requested": False,
        "is_ambiguous": False,
        "category": category
    }
