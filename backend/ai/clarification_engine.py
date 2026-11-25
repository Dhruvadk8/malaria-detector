from typing import Dict, Any, List

CLARIFICATION_PRESETS = {
    "ambiguous_payment": {
        "question": "I can help with your payment query. Could you specify what issue you're experiencing?",
        "options": [
            {"id": "opt_pay_declined", "text": "Payment Declined", "sub_query": "Why was my payment declined?"},
            {"id": "opt_pay_pending", "text": "Payment Pending / Double Charge", "sub_query": "Why was I charged twice or payment pending?"},
            {"id": "opt_pay_methods", "text": "Supported Payment Methods", "sub_query": "What payment methods are supported?"},
            {"id": "opt_pay_human", "text": "Connect with Agent", "sub_query": "I want to talk to a human support agent about my payment."}
        ]
    },
    "ambiguous_account": {
        "question": "I'd be happy to assist with your account. What action are you looking to perform?",
        "options": [
            {"id": "opt_acc_pwd", "text": "Reset Password", "sub_query": "How can I reset my password?"},
            {"id": "opt_acc_profile", "text": "Update Profile Info", "sub_query": "How can I update my profile details?"},
            {"id": "opt_acc_2fa", "text": "Enable 2FA / Security", "sub_query": "How do I enable Two-Factor Authentication?"},
            {"id": "opt_acc_del", "text": "Delete / Close Account", "sub_query": "How do I delete or deactivate my account?"}
        ]
    },
    "ambiguous_order": {
        "question": "I can assist with your order details. Which of these fits your situation best?",
        "options": [
            {"id": "opt_ord_track", "text": "Track Order Delivery", "sub_query": "Where is my order and how can I track it?"},
            {"id": "opt_ord_modify", "text": "Cancel / Modify Order", "sub_query": "Can I modify or cancel my order after placing it?"},
            {"id": "opt_ord_shipping", "text": "Shipping Times & Options", "sub_query": "What shipping options and delivery timelines are available?"},
            {"id": "opt_ord_human", "text": "Speak to Support Team", "sub_query": "Connect me to a human agent regarding my order."}
        ]
    }
}

def generate_clarification(user_query: str, intent: str) -> Dict[str, Any]:
    """Generates clarifying question text and structured option buttons."""
    if intent in CLARIFICATION_PRESETS:
        return CLARIFICATION_PRESETS[intent]

    # Default fallback clarification for general ambiguous queries
    return {
        "question": f"I want to make sure I give you the exact right information regarding '{user_query}'. Which of the following best describes your request?",
        "options": [
            {"id": "opt_gen_pwd", "text": "Password & Account Access", "sub_query": "How can I reset my password?"},
            {"id": "opt_gen_billing", "text": "Billing & Subscription", "sub_query": "How can I cancel my subscription or view invoices?"},
            {"id": "opt_gen_refund", "text": "Refund & Returns Policy", "sub_query": "What is TechNova's refund policy?"},
            {"id": "opt_gen_agent", "text": "Connect with Human Support", "sub_query": "I want to talk to a human support agent."}
        ]
    }
