import os
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.models.schemas import (
    FAQItem, FAQCreate, FAQUpdate,
    ChatRequest, ChatResponse, ChatMessage,
    TicketCreate, TicketResponse, TicketUpdate,
    FeedbackRequest, CSATRequest, AnalyticsOverview
)
from backend.database.db import db_store
from backend.ai.ai_service import ai_service
from backend.ai.query_classifier import understand_query

app = FastAPI(
    title="SupportAI API",
    description="Intelligent Customer Support Assistant REST Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "SupportAI — Intelligent Customer Support Assistant",
        "tagline": "Answers When It Knows. Asks When It Doesn't. Escalates When You Need a Human.",
        "version": "1.0.0",
        "llm_configured": bool(os.getenv("OPENAI_API_KEY"))
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# --- CHAT & QUERY APIs ---
@app.post("/api/chat", response_model=ChatResponse)
def handle_chat(request: ChatRequest):
    """Processes customer query through the SupportAI grounded pipeline."""
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Chat message cannot be empty.")
    
    # Record user message in DB
    user_msg_id = f"msg_{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now().strftime("%I:%M %p")
    user_msg = {
        "id": user_msg_id,
        "sender": "user",
        "content": request.message.strip(),
        "timestamp": timestamp
    }
    db_store.save_message(request.conversation_id, user_msg)

    # Process AI pipeline
    result = ai_service.process_user_message(
        conversation_id=request.conversation_id,
        user_query=request.message.strip(),
        selected_option=request.selected_option
    )

    return result

@app.post("/api/analyze-query")
def analyze_query(payload: Dict[str, str] = Body(...)):
    """Analyzes a query intent and estimates grounding confidence prior to response."""
    query = payload.get("query", "")
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query text required.")
    
    understanding = understand_query(query)
    faqs = db_store.get_all_faqs()
    from backend.ai.knowledge_retriever import search_knowledge_base
    matched = search_knowledge_base(query, faqs)
    
    return {
        "query": query,
        "understanding": understanding,
        "matched_faq": matched,
        "estimated_confidence": matched.get("match_score", 0.0) if matched else 0.0
    }

# --- KNOWLEDGE BASE / FAQ APIs ---
@app.get("/api/faqs", response_model=List[FAQItem])
def get_faqs(category: Optional[str] = None, search: Optional[str] = None):
    """Retrieves all FAQs with optional category and search query filters."""
    faqs = db_store.get_all_faqs()
    if category and category.lower() != "all":
        faqs = [f for f in faqs if f["category"].lower() == category.lower()]
    if search:
        s = search.lower()
        faqs = [f for f in faqs if s in f["question"].lower() or s in f["answer"].lower() or any(s in k.lower() for k in f.get("keywords", []))]
    return faqs

@app.post("/api/faqs", response_model=FAQItem)
def create_faq(faq: FAQCreate):
    """Creates a new company FAQ in the Knowledge Base."""
    new_faq = db_store.add_faq(faq.model_dump())
    return new_faq

@app.put("/api/faqs/{faq_id}", response_model=FAQItem)
def update_faq(faq_id: str, updates: FAQUpdate):
    """Updates an existing FAQ entry."""
    updated = db_store.update_faq(faq_id, updates.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="FAQ not found.")
    return updated

@app.delete("/api/faqs/{faq_id}")
def delete_faq(faq_id: str):
    """Deletes an FAQ entry."""
    success = db_store.delete_faq(faq_id)
    if not success:
        raise HTTPException(status_code=404, detail="FAQ not found.")
    return {"message": "FAQ deleted successfully", "id": faq_id}

# --- TICKET MANAGEMENT APIs ---
@app.post("/api/tickets", response_model=TicketResponse)
def create_ticket(ticket_in: TicketCreate):
    """Creates a human support escalation ticket with AI-generated summary."""
    summary = ai_service.generate_summary(ticket_in.conversation_id)
    
    ticket_payload = {
        "conversation_id": ticket_in.conversation_id,
        "customer_name": ticket_in.customer_name,
        "customer_email": ticket_in.customer_email,
        "category": ticket_in.category,
        "issue_description": ticket_in.issue_description,
        "priority": ticket_in.priority,
        "conversation_summary": summary
    }
    created = db_store.create_ticket(ticket_payload)
    return created

@app.get("/api/tickets", response_model=List[TicketResponse])
def get_tickets(status: Optional[str] = None, priority: Optional[str] = None):
    """Retrieves all tickets for support agent dashboard."""
    tickets = db_store.get_all_tickets()
    if status and status.lower() != "all":
        tickets = [t for t in tickets if t["status"].lower() == status.lower()]
    if priority and priority.lower() != "all":
        tickets = [t for t in tickets if t["priority"].lower() == priority.lower()]
    return tickets

@app.patch("/api/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: str, updates: TicketUpdate):
    """Updates ticket status, priority, assigned agent, or adds agent notes."""
    updated = db_store.update_ticket(ticket_id, updates.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    return updated

# --- FEEDBACK & CSAT APIs ---
@app.post("/api/feedback")
def submit_feedback(payload: Dict[str, Any] = Body(...)):
    """Logs 👍 / 👎 feedback on individual AI responses."""
    db_store.add_feedback(payload)
    return {"status": "success", "message": "Feedback recorded."}

@app.post("/api/csat")
def submit_csat(csat: CSATRequest):
    """Submits customer satisfaction survey rating (1-5 stars) and comment."""
    db_store.add_csat(csat.model_dump())
    return {"status": "success", "message": "Thank you for your feedback!"}

# --- ANALYTICS API ---
@app.get("/api/analytics", response_model=AnalyticsOverview)
def get_analytics():
    """Returns AI resolution rate, escalation trends, and CSAT dashboard metrics."""
    return db_store.get_analytics()

# --- DEMO PRESETS API ---
@app.get("/api/demo-scenarios")
def get_demo_scenarios():
    """Returns pre-packaged demo conversation scenarios for hackathon presentations."""
    return [
        {
            "id": "demo-1",
            "title": "Demo 1 — FAQ Grounded Answer",
            "prompt": "How do I reset my password?",
            "description": "AI retrieves exact password reset FAQ with high confidence and displays source attribution badge."
        },
        {
            "id": "demo-2",
            "title": "Demo 2 — Smart Clarification",
            "prompt": "My payment isn't working.",
            "description": "AI detects query ambiguity and asks useful clarification pills (Declined, Pending, Incorrect Amount)."
        },
        {
            "id": "demo-3",
            "title": "Demo 3 — Unknown Query Safety",
            "prompt": "Can I get a refund for a product I purchased 2 years ago?",
            "description": "AI strictly avoids hallucinating company rules, states lack of KB info, and offers human handoff."
        },
        {
            "id": "demo-4",
            "title": "Demo 4 — Human Escalation & Ticket",
            "prompt": "I want to talk to a human.",
            "description": "AI immediately initiates human escalation, auto-summarizes conversation, and logs support ticket."
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
