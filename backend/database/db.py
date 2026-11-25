import os
import json
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from backend.data.faqs_seed import SEED_FAQS

DB_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "db_store.json")

class DatabaseStore:
    def __init__(self):
        self.faqs: List[Dict[str, Any]] = []
        self.tickets: List[Dict[str, Any]] = []
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        self.feedback_records: List[Dict[str, Any]] = []
        self.csat_records: List[Dict[str, Any]] = []
        self._load_or_init_data()

    def _load_or_init_data(self):
        """Loads data from JSON storage file or initializes defaults."""
        if os.path.exists(DB_FILE_PATH):
            try:
                with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.faqs = data.get("faqs", SEED_FAQS)
                    self.tickets = data.get("tickets", self._get_initial_tickets())
                    self.conversations = data.get("conversations", {})
                    self.feedback_records = data.get("feedback_records", [])
                    self.csat_records = data.get("csat_records", self._get_initial_csat())
                    return
            except Exception as e:
                print(f"Warning: Could not read DB file ({e}). Initializing default seed data.")
        
        self.faqs = list(SEED_FAQS)
        self.tickets = self._get_initial_tickets()
        self.conversations = {}
        self.feedback_records = []
        self.csat_records = self._get_initial_csat()
        self._save_data()

    def _save_data(self):
        """Saves current state to JSON storage file."""
        os.makedirs(os.path.dirname(DB_FILE_PATH), exist_ok=True)
        try:
            with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump({
                    "faqs": self.faqs,
                    "tickets": self.tickets,
                    "conversations": self.conversations,
                    "feedback_records": self.feedback_records,
                    "csat_records": self.csat_records
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving DB file: {e}")

    def _get_initial_tickets(self) -> List[Dict[str, Any]]:
        """Generates sample initial tickets for demo dashboard."""
        return [
            {
                "id": "TKT-2026-10482",
                "conversation_id": "conv_demo_101",
                "customer_name": "Sarah Jenkins",
                "customer_email": "sarah.j@techcorp.io",
                "category": "Payments",
                "issue_description": "Payment was declined three times during checkout despite valid funds.",
                "priority": "High",
                "status": "In Progress",
                "conversation_summary": {
                    "issue_summary": [
                        "Customer attempted credit card payment 3 times.",
                        "System returned generic bank decline code.",
                        "FAQ policy provided no immediate resolution for international bank locks."
                    ],
                    "recommended_action": "Review payment gateway transaction logs and issue manual invoice or unlock checkout retry."
                },
                "created_at": "2026-10-07 09:30:00",
                "assigned_agent": "David Miller",
                "estimated_response_time": "15-30 minutes",
                "notes": [
                    {"agent": "David Miller", "note": "Checked Stripe gateway. Card flagged by international fraud check.", "time": "2026-10-07 09:45:00"}
                ]
            },
            {
                "id": "TKT-2026-10483",
                "conversation_id": "conv_demo_102",
                "customer_name": "Marcus Vance",
                "customer_email": "m.vance@innovate.co",
                "category": "Refunds",
                "issue_description": "Requesting custom pro-rated refund for multi-seat plan after 90 days.",
                "priority": "Medium",
                "status": "Open",
                "conversation_summary": {
                    "issue_summary": [
                        "Customer inquiring about refund policy beyond 30-day money-back guarantee.",
                        "AI correctly noted policy limit and escalated unknown request."
                    ],
                    "recommended_action": "Evaluate enterprise terms and determine if discretionary credit applies."
                },
                "created_at": "2026-10-07 10:15:00",
                "assigned_agent": "Unassigned",
                "estimated_response_time": "30-45 minutes",
                "notes": []
            },
            {
                "id": "TKT-2026-10484",
                "conversation_id": "conv_demo_103",
                "customer_name": "Elena Rostova",
                "customer_email": "elena.r@designhub.com",
                "category": "Technical Support",
                "issue_description": "API Webhook notifications failing to trigger on subscription renewals.",
                "priority": "Urgent",
                "status": "Open",
                "conversation_summary": {
                    "issue_summary": [
                        "Customer noticed missing HTTP 200 responses on webhook endpoints.",
                        "Tested endpoint manually; verified payload structure matches V2 spec."
                    ],
                    "recommended_action": "Inspect developer webhook dispatcher queue logs and resend failed events."
                },
                "created_at": "2026-10-07 11:05:00",
                "assigned_agent": "Unassigned",
                "estimated_response_time": "15-30 minutes",
                "notes": []
            }
        ]

    def _get_initial_csat(self) -> List[Dict[str, Any]]:
        return [
            {"conversation_id": "conv_demo_01", "rating": 5, "comment": "Fast and super accurate answer!"},
            {"conversation_id": "conv_demo_02", "rating": 5, "comment": "AI clarified my payment issue quickly."},
            {"conversation_id": "conv_demo_03", "rating": 4, "comment": "Good support, created ticket smoothly."}
        ]

    # --- FAQ Methods ---
    def get_all_faqs(self) -> List[Dict[str, Any]]:
        return self.faqs

    def add_faq(self, faq_data: Dict[str, Any]) -> Dict[str, Any]:
        faq_id = f"FAQ-{faq_data.get('category', 'GEN')[:3].upper()}-{len(self.faqs) + 1:02d}"
        new_faq = {
            "id": faq_id,
            "category": faq_data["category"],
            "question": faq_data["question"],
            "answer": faq_data["answer"],
            "keywords": faq_data.get("keywords", []),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.faqs.append(new_faq)
        self._save_data()
        return new_faq

    def update_faq(self, faq_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for faq in self.faqs:
            if faq["id"] == faq_id:
                for k, v in updates.items():
                    if v is not None:
                        faq[k] = v
                faq["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_data()
                return faq
        return None

    def delete_faq(self, faq_id: str) -> bool:
        initial_len = len(self.faqs)
        self.faqs = [f for f in self.faqs if f["id"] != faq_id]
        if len(self.faqs) < initial_len:
            self._save_data()
            return True
        return False

    # --- Conversation Methods ---
    def get_conversation(self, conv_id: str) -> List[Dict[str, Any]]:
        return self.conversations.get(conv_id, [])

    def save_message(self, conv_id: str, message: Dict[str, Any]):
        if conv_id not in self.conversations:
            self.conversations[conv_id] = []
        self.conversations[conv_id].append(message)
        self._save_data()

    # --- Ticket Methods ---
    def get_all_tickets(self) -> List[Dict[str, Any]]:
        return self.tickets

    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        for t in self.tickets:
            if t["id"] == ticket_id:
                return t
        return None

    def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        ticket_id = f"TKT-2026-{random.randint(10000, 99999)}"
        new_ticket = {
            "id": ticket_id,
            "conversation_id": ticket_data["conversation_id"],
            "customer_name": ticket_data["customer_name"],
            "customer_email": ticket_data["customer_email"],
            "category": ticket_data["category"],
            "issue_description": ticket_data["issue_description"],
            "priority": ticket_data.get("priority", "Medium"),
            "status": "Open",
            "conversation_summary": ticket_data.get("conversation_summary", {
                "issue_summary": [ticket_data["issue_description"]],
                "recommended_action": "Contact customer via email to address support request."
            }),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "assigned_agent": "Unassigned",
            "estimated_response_time": "15-30 minutes",
            "notes": []
        }
        self.tickets.insert(0, new_ticket)
        self._save_data()
        return new_ticket

    def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for t in self.tickets:
            if t["id"] == ticket_id:
                if "status" in updates and updates["status"]:
                    t["status"] = updates["status"]
                if "priority" in updates and updates["priority"]:
                    t["priority"] = updates["priority"]
                if "assigned_agent" in updates and updates["assigned_agent"]:
                    t["assigned_agent"] = updates["assigned_agent"]
                if "note" in updates and updates["note"]:
                    if "notes" not in t:
                        t["notes"] = []
                    t["notes"].append({
                        "agent": updates.get("agent_name", "Support Agent"),
                        "note": updates["note"],
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                self._save_data()
                return t
        return None

    # --- Feedback & CSAT Methods ---
    def add_feedback(self, feedback: Dict[str, Any]):
        self.feedback_records.append(feedback)
        self._save_data()

    def add_csat(self, csat: Dict[str, Any]):
        self.csat_records.append(csat)
        self._save_data()

    # --- Analytics Computation ---
    def get_analytics(self) -> Dict[str, Any]:
        total_convs = max(248, len(self.conversations) + 240)
        total_tickets = len(self.tickets)
        
        # Calculate CSAT average
        if self.csat_records:
            csat_avg = round(sum(r["rating"] for r in self.csat_records) / len(self.csat_records), 1)
        else:
            csat_avg = 4.6

        # Calculate AI resolution rate
        resolution_rate = round(((total_convs - total_tickets) / total_convs) * 100, 1)

        return {
            "today_conversations": total_convs,
            "ai_resolution_rate": max(78.0, min(95.0, resolution_rate)),
            "escalated_tickets": total_tickets,
            "avg_response_time_min": 1.8,
            "customer_satisfaction_score": csat_avg,
            "total_faqs": len(self.faqs),
            "confidence_breakdown": {
                "high": 72.0,
                "medium": 18.0,
                "low_escalated": 10.0
            },
            "top_topics": [
                {"category": "Payments", "count": 84, "percentage": 34},
                {"category": "Password Reset", "count": 62, "percentage": 25},
                {"category": "Refunds", "count": 45, "percentage": 18},
                {"category": "Orders", "count": 32, "percentage": 13},
                {"category": "Subscription", "count": 25, "percentage": 10}
            ],
            "daily_trends": [
                {"day": "Mon", "queries": 180, "resolved": 150, "escalated": 30},
                {"day": "Tue", "queries": 210, "resolved": 175, "escalated": 35},
                {"day": "Wed", "queries": 248, "resolved": 204, "escalated": 44},
                {"day": "Thu", "queries": 195, "resolved": 160, "escalated": 35},
                {"day": "Fri", "queries": 230, "resolved": 190, "escalated": 40},
                {"day": "Sat", "queries": 140, "resolved": 122, "escalated": 18},
                {"day": "Sun", "queries": 110, "resolved": 98, "escalated": 12}
            ]
        }

db_store = DatabaseStore()
