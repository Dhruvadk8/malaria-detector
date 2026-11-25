export type ConfidenceLevel = 'HIGH' | 'MEDIUM' | 'LOW';

export interface SourceFAQ {
  id: string;
  category: string;
  question: string;
  answer: string;
  match_score: number;
}

export interface ClarificationOption {
  id: string;
  text: string;
  sub_query: string;
}

export interface MessageFeedback {
  message_id: string;
  is_helpful: boolean;
  reason?: string;
  comments?: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  confidence?: number;
  confidence_level?: ConfidenceLevel;
  source_faq?: SourceFAQ | null;
  clarification_options?: ClarificationOption[] | null;
  requires_escalation?: boolean;
  escalation_reason?: string | null;
  feedback?: MessageFeedback | null;
  metadata?: Record<string, any>;
}

export interface FAQItem {
  id: string;
  category: string;
  question: string;
  answer: string;
  keywords: string[];
  created_at?: string;
  updated_at?: string;
}

export interface TicketSummary {
  issue_summary: string[];
  recommended_action: string;
}

export interface TicketNote {
  agent: string;
  note: string;
  time: string;
}

export interface TicketResponse {
  id: string;
  conversation_id: string;
  customer_name: string;
  customer_email: string;
  category: string;
  issue_description: string;
  priority: 'Low' | 'Medium' | 'High' | 'Urgent';
  status: 'Open' | 'In Progress' | 'Waiting for Customer' | 'Resolved' | 'Closed';
  conversation_summary?: TicketSummary;
  created_at: string;
  assigned_agent: string;
  estimated_response_time: string;
  notes?: TicketNote[];
}

export interface AnalyticsOverview {
  today_conversations: number;
  ai_resolution_rate: number;
  escalated_tickets: number;
  open_tickets?: number;
  avg_response_time_min: number;
  customer_satisfaction_score: number;
  total_faqs: number;
  confidence_breakdown: {
    high: number;
    medium: number;
    low_escalated: number;
  };
  top_topics: Array<{ category: string; count: number; percentage: number }>;
  daily_trends: Array<{ day: string; queries: number; resolved: number; escalated: number }>;
}

export interface DemoScenario {
  id: string;
  title: string;
  prompt: string;
  description: string;
}
