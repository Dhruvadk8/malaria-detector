import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.ai.query_classifier import understand_query
from backend.ai.knowledge_retriever import search_knowledge_base
from backend.ai.confidence_detector import detect_uncertainty
from backend.ai.clarification_engine import generate_clarification
from backend.ai.response_generator import generate_grounded_answer
from backend.ai.escalation_engine import generate_conversation_summary, calculate_ticket_priority
from backend.database.db import db_store

class AIService:
    def process_user_message(self, conversation_id: str, user_query: str, selected_option: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes the full SupportAI pipeline:
        Query -> Intent -> KB Search -> Confidence -> Clarify / Answer / Escalate.
        """
        timestamp = datetime.now().strftime("%I:%M %p")
        msg_id = f"msg_{uuid.uuid4().hex[:8]}"

        # 1. Understand query intent
        understanding = understand_query(user_query)
        intent = understanding["intent"]
        is_human_requested = understanding["is_human_requested"]
        is_ambiguous = understanding["is_ambiguous"]

        # If user explicitly selected a clarification option, clear ambiguity
        if selected_option:
            is_ambiguous = False

        # 2. Search Knowledge Base
        faqs = db_store.get_all_faqs()
        matched_faq = search_knowledge_base(user_query, faqs)
        match_score = matched_faq.get("match_score", 0.0) if matched_faq else 0.0

        # 3. Detect Confidence Level
        confidence_pct, confidence_level = detect_uncertainty(match_score, is_ambiguous, is_human_requested)

        # 4. Handle Explicit Human Agent Request
        if is_human_requested:
            res_msg = {
                "id": msg_id,
                "sender": "assistant",
                "content": "I understand you'd like to speak with a human support agent. I'd be glad to connect you. Please click below to create a support ticket, and one of our team members will get back to you shortly.",
                "timestamp": timestamp,
                "confidence": confidence_pct,
                "confidence_level": confidence_level,
                "source_faq": None,
                "clarification_options": None,
                "requires_escalation": True,
                "escalation_reason": "Explicit Customer Request"
            }
            db_store.save_message(conversation_id, res_msg)
            return {
                "conversation_id": conversation_id,
                "message": res_msg,
                "intent": intent,
                "status": "escalation_offered"
            }

        # 5. Handle Smart Clarification for Ambiguous Queries
        if is_ambiguous and confidence_level == "LOW":
            clarification_data = generate_clarification(user_query, intent)
            res_msg = {
                "id": msg_id,
                "sender": "assistant",
                "content": clarification_data["question"],
                "timestamp": timestamp,
                "confidence": confidence_pct,
                "confidence_level": "LOW",
                "source_faq": None,
                "clarification_options": clarification_data["options"],
                "requires_escalation": False
            }
            db_store.save_message(conversation_id, res_msg)
            return {
                "conversation_id": conversation_id,
                "message": res_msg,
                "intent": intent,
                "status": "clarification_needed"
            }

        # 6. Generate Grounded AI Answer
        grounded_result = generate_grounded_answer(user_query, matched_faq, confidence_level)
        
        res_msg = {
            "id": msg_id,
            "sender": "assistant",
            "content": grounded_result["answer"],
            "timestamp": timestamp,
            "confidence": confidence_pct,
            "confidence_level": confidence_level,
            "source_faq": grounded_result.get("source_faq"),
            "clarification_options": None,
            "requires_escalation": grounded_result.get("requires_escalation", False),
            "escalation_reason": grounded_result.get("escalation_reason")
        }

        db_store.save_message(conversation_id, res_msg)

        status_type = "answered"
        if grounded_result.get("requires_escalation"):
            status_type = "escalation_offered"

        return {
            "conversation_id": conversation_id,
            "message": res_msg,
            "intent": intent,
            "status": status_type
        }

    def generate_summary(self, conversation_id: str) -> Dict[str, Any]:
        history = db_store.get_conversation(conversation_id)
        return generate_conversation_summary(history)

ai_service = AIService()
