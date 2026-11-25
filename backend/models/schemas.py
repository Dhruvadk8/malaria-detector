from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime

class FAQItem(BaseModel):
    id: str
    category: str
    question: str
    answer: str
    keywords: List[str] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class FAQCreate(BaseModel):
    category: str
    question: str
    answer: str
    keywords: List[str] = []

class FAQUpdate(BaseModel):
    category: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    keywords: Optional[List[str]] = None

class ClarificationOption(BaseModel):
    id: str
    text: str
    sub_query: str

class SourceFAQ(BaseModel):
    id: str
    category: str
    question: str
    answer: str
    match_score: float

class MessageFeedback(BaseModel):
    message_id: str
    is_helpful: bool
    reason: Optional[str] = None
    comments: Optional[str] = None

class FeedbackRequest(BaseModel):
    message_id: str
    is_helpful: bool
    reason: Optional[str] = None
    comments: Optional[str] = None

class ChatMessage(BaseModel):
    id: str
    sender: Literal["user", "assistant", "system"]
    content: str
    timestamp: str
    confidence: Optional[float] = None
    confidence_level: Optional[Literal["HIGH", "MEDIUM", "LOW"]] = None
    source_faq: Optional[SourceFAQ] = None
    clarification_options: Optional[List[ClarificationOption]] = None
    requires_escalation: bool = False
    escalation_reason: Optional[str] = None
    feedback: Optional[MessageFeedback] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    conversation_id: str
    user_id: Optional[str] = "cust_demo_01"
    user_name: Optional[str] = "Alex Morgan"
    message: str
    selected_option: Optional[str] = None
    context_history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    conversation_id: str
    message: ChatMessage
    intent: Optional[str] = None
    status: Literal["answered", "clarification_needed", "escalation_offered", "escalated"]

class TicketCreate(BaseModel):
    conversation_id: str
    customer_name: str
    customer_email: str
    category: str
    issue_description: str
    priority: Literal["Low", "Medium", "High", "Urgent"] = "Medium"

class TicketResponse(BaseModel):
    id: str
    conversation_id: str
    customer_name: str
    customer_email: str
    category: str
    issue_description: str
    priority: Literal["Low", "Medium", "High", "Urgent"]
    status: Literal["Open", "In Progress", "Waiting for Customer", "Resolved", "Closed"]
    conversation_summary: Dict[str, Any]
    created_at: str
    assigned_agent: Optional[str] = "Unassigned"
    estimated_response_time: str = "15-30 minutes"
    notes: List[Dict[str, str]] = []

class TicketUpdate(BaseModel):
    status: Optional[Literal["Open", "In Progress", "Waiting for Customer", "Resolved", "Closed"]] = None
    priority: Optional[Literal["Low", "Medium", "High", "Urgent"]] = None
    assigned_agent: Optional[str] = None
    note: Optional[str] = None

class CSATRequest(BaseModel):
    conversation_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    category: Optional[str] = None

class AnalyticsOverview(BaseModel):
    today_conversations: int
    ai_resolution_rate: float
    escalated_tickets: int
    avg_response_time_min: float
    customer_satisfaction_score: float
    total_faqs: int
    confidence_breakdown: Dict[str, float]
    top_topics: List[Dict[str, Any]]
    daily_trends: List[Dict[str, Any]]
