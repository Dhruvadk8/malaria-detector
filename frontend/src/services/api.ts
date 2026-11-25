import type { FAQItem, TicketResponse, AnalyticsOverview, DemoScenario, ChatMessage } from '../types';

export const INITIAL_FAQS: FAQItem[] = [
  {
    id: 'FAQ-PWD-01',
    category: 'Password Reset',
    question: 'How can I reset my password?',
    answer: 'To reset your password:\n1. Click "Sign In" at the top right of SupportAI.\n2. Select "Forgot Password?".\n3. Enter your registered email address.\n4. Click the password reset link sent to your inbox (valid for 30 minutes).\n5. Enter your new password.',
    keywords: ['password', 'reset', 'forgot', 'login', 'account access', 'change password', 'credentials'],
    created_at: new Date().toISOString(),
  },
  {
    id: 'FAQ-REF-01',
    category: 'Refunds',
    question: 'How can I get a refund?',
    answer: 'We offer a full 30-day money-back guarantee for all subscription plans and products:\n1. Navigate to Account > Billing & Invoices.\n2. Locate your recent transaction and click "Request Refund".\n3. Select your reason for cancellation.\nApproved refunds are processed to your original payment method within 3–5 business days.',
    keywords: ['refund', 'money back', 'reimbursement', 'cancel order', 'return', 'guarantee', '30 days'],
    created_at: new Date().toISOString(),
  },
  {
    id: 'FAQ-PAY-01',
    category: 'Payments',
    question: 'What payment methods do you accept?',
    answer: 'SupportAI accepts all major credit and debit cards (Visa, Mastercard, American Express, Discover), PayPal, Apple Pay, and Google Pay. Enterprise plans can also pay via direct ACH bank transfer or wire invoice.',
    keywords: ['payment', 'pay', 'credit card', 'paypal', 'apple pay', 'billing', 'invoice', 'accepted payments'],
    created_at: new Date().toISOString(),
  },
  {
    id: 'FAQ-ORD-01',
    category: 'Orders',
    question: 'How can I track or check my order status?',
    answer: 'You can check your order status anytime by logging into your account and visiting the "Orders" page. Additionally, a tracking number and link are emailed to you as soon as your items ship.',
    keywords: ['order', 'track', 'status', 'package', 'where is my order', 'delivery status'],
    created_at: new Date().toISOString(),
  },
  {
    id: 'FAQ-SHP-01',
    category: 'Shipping',
    question: 'What are your shipping methods and delivery times?',
    answer: 'We offer standard and express shipping:\n• Standard Shipping (3–5 business days): Free on orders over $50, otherwise $4.99.\n• Express Shipping (1–2 business days): $12.99.\n• International Shipping (7–14 business days): Calculated at checkout.',
    keywords: ['shipping', 'delivery', 'express', 'standard shipping', 'dispatch', 'international shipping'],
    created_at: new Date().toISOString(),
  },
  {
    id: 'FAQ-ACC-01',
    category: 'Account Management',
    question: 'How do I update my profile or email address?',
    answer: 'To update your account information:\n1. Go to Account Settings > Profile.\n2. Edit your Name, Email, or Contact Details.\n3. Click "Save Changes". If changing your primary email, a verification link will be sent to the new address.',
    keywords: ['account', 'profile', 'email', 'change email', 'update info', 'settings', 'details'],
    created_at: new Date().toISOString(),
  },
  {
    id: 'FAQ-SUB-01',
    category: 'Subscription Cancellation',
    question: 'How do I cancel my subscription?',
    answer: 'You can cancel your auto-renewing subscription at any time:\n1. Go to Account Settings > Billing & Subscriptions.\n2. Click "Cancel Subscription".\n3. Confirm cancellation.\nYou will retain full access to all features until the end of your current billing cycle.',
    keywords: ['cancel subscription', 'unsubscribe', 'stop renewal', 'auto renew', 'end subscription', 'cancel plan'],
    created_at: new Date().toISOString(),
  },
];

export const INITIAL_TICKETS: TicketResponse[] = [
  {
    id: 'TICK-90412',
    conversation_id: 'conv_84920',
    customer_name: 'Sarah Jenkins',
    customer_email: 'sarah.j@example.com',
    category: 'Payments',
    issue_description: 'Charged twice for monthly subscription renewal on Oct 4.',
    priority: 'High',
    status: 'Open',
    created_at: '2026-10-06T14:22:00Z',
    assigned_agent: 'David Miller (Lead)',
    estimated_response_time: '< 15 mins',
    notes: [{ agent: 'System', note: 'Ticket initialized from AI chat escalation.', time: '14:22 PM' }],
  },
  {
    id: 'TICK-88391',
    conversation_id: 'conv_39102',
    customer_name: 'Alex Rivera',
    customer_email: 'arivera@techcorp.io',
    category: 'Account Management',
    issue_description: 'Unable to reset 2-Factor Authentication after phone replacement.',
    priority: 'Urgent',
    status: 'In Progress',
    created_at: '2026-10-06T18:45:00Z',
    assigned_agent: 'Emma Watson',
    estimated_response_time: '< 30 mins',
    notes: [{ agent: 'Emma Watson', note: 'Sent identity verification link via email.', time: '18:50 PM' }],
  },
  {
    id: 'TICK-74102',
    conversation_id: 'conv_12049',
    customer_name: 'Michael Chen',
    customer_email: 'm.chen@innovate.org',
    category: 'Shipping',
    issue_description: 'Express delivery delayed beyond 2 business days.',
    priority: 'Medium',
    status: 'Resolved',
    created_at: '2026-10-05T09:12:00Z',
    assigned_agent: 'James Lee',
    estimated_response_time: 'Resolved',
    notes: [{ agent: 'James Lee', note: 'Shipping fee refunded to customer.', time: '10:00 AM' }],
  },
  {
    id: 'TICK-61920',
    conversation_id: 'conv_90214',
    customer_name: 'Jessica Taylor',
    customer_email: 'jessica.t@gmail.com',
    category: 'Refunds',
    issue_description: 'Requesting refund confirmation for order #ORD-3819.',
    priority: 'Low',
    status: 'Closed',
    created_at: '2026-10-04T11:05:00Z',
    assigned_agent: 'Tier-1 Support Team',
    estimated_response_time: 'Closed',
    notes: [{ agent: 'System', note: 'Refund processed successfully.', time: '11:10 AM' }],
  },
];

const STORAGE_KEYS = {
  FAQS: 'supportai_faqs_v1',
  TICKETS: 'supportai_tickets_v1',
};

export function getStoredFAQs(): FAQItem[] {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.FAQS);
    return data ? JSON.parse(data) : INITIAL_FAQS;
  } catch {
    return INITIAL_FAQS;
  }
}

export function saveStoredFAQs(faqs: FAQItem[]) {
  try {
    localStorage.setItem(STORAGE_KEYS.FAQS, JSON.stringify(faqs));
  } catch (e) {
    console.error('Storage error:', e);
  }
}

export function getStoredTickets(): TicketResponse[] {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.TICKETS);
    return data ? JSON.parse(data) : INITIAL_TICKETS;
  } catch {
    return INITIAL_TICKETS;
  }
}

export function saveStoredTickets(tickets: TicketResponse[]) {
  try {
    localStorage.setItem(STORAGE_KEYS.TICKETS, JSON.stringify(tickets));
  } catch (e) {
    console.error('Storage error:', e);
  }
}

const API_BASE_URL = 'http://localhost:8000/api';

export async function sendMessageToAI(
  conversationId: string,
  message: string,
  selectedOption?: string
): Promise<{ conversation_id: string; message: ChatMessage; status: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        conversation_id: conversationId,
        message,
        selected_option: selectedOption,
      }),
    });
    if (!response.ok) throw new Error(`HTTP error ${response.status}`);
    return await response.json();
  } catch {
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const cleanQuery = message.toLowerCase().trim();
    const faqs = getStoredFAQs();

    if (
      cleanQuery.includes('human') ||
      cleanQuery.includes('agent') ||
      cleanQuery.includes('talk to someone') ||
      cleanQuery.includes('contact support') ||
      cleanQuery.includes('representative')
    ) {
      return {
        conversation_id: conversationId,
        message: {
          id: `msg_${Math.random().toString(36).substring(2, 9)}`,
          sender: 'assistant',
          content: 'I understand you would like to connect with a human support representative. I can immediately transfer your conversation and help you create a priority support ticket.',
          timestamp,
          confidence: 0.1,
          confidence_level: 'LOW',
          requires_escalation: true,
          escalation_reason: 'Explicit Customer Request for Human Handoff',
        },
        status: 'escalation_offered',
      };
    }

    if (cleanQuery === 'reset' || cleanQuery === 'cancel' || cleanQuery === 'payment' || cleanQuery === 'help') {
      let options = [];
      if (cleanQuery === 'reset') {
        options = [
          { id: 'opt-1', text: '🔑 Reset Password', sub_query: 'How can I reset my password?' },
          { id: 'opt-2', text: '🔒 Reset 2FA / Security', sub_query: 'How do I update my account 2FA?' },
        ];
      } else if (cleanQuery === 'cancel') {
        options = [
          { id: 'opt-3', text: '❌ Cancel Subscription', sub_query: 'How do I cancel my subscription?' },
          { id: 'opt-4', text: '📦 Cancel Recent Order', sub_query: 'How can I cancel my order?' },
        ];
      } else if (cleanQuery === 'payment') {
        options = [
          { id: 'opt-5', text: '💳 Payment Methods Accepted', sub_query: 'What payment methods do you accept?' },
          { id: 'opt-6', text: '💸 Request Refund', sub_query: 'How can I get a refund?' },
        ];
      } else {
        options = [
          { id: 'opt-7', text: '🔑 Password Reset', sub_query: 'How can I reset my password?' },
          { id: 'opt-8', text: '💸 Refund Request', sub_query: 'How can I get a refund?' },
          { id: 'opt-9', text: '👤 Human Support', sub_query: 'How do I contact human support?' },
        ];
      }

      return {
        conversation_id: conversationId,
        message: {
          id: `msg_${Math.random().toString(36).substring(2, 9)}`,
          sender: 'assistant',
          content: `Your query "${message}" could refer to a few different topics. Please select the option that best describes your request:`,
          timestamp,
          confidence: 0.55,
          confidence_level: 'MEDIUM',
          clarification_options: options,
        },
        status: 'clarification_needed',
      };
    }

    let bestMatch: FAQItem | null = null;
    let highestScore = 0;

    for (const faq of faqs) {
      let score = 0;
      for (const kw of faq.keywords) {
        if (cleanQuery.includes(kw.toLowerCase())) {
          score += 0.35;
        }
      }
      const qWords = faq.question.toLowerCase().split(' ');
      for (const qw of qWords) {
        if (qw.length > 3 && cleanQuery.includes(qw)) {
          score += 0.2;
        }
      }
      if (score > highestScore) {
        highestScore = score;
        bestMatch = faq;
      }
    }

    if (bestMatch && highestScore >= 0.3) {
      return {
        conversation_id: conversationId,
        message: {
          id: `msg_${Math.random().toString(36).substring(2, 9)}`,
          sender: 'assistant',
          content: bestMatch.answer,
          timestamp,
          confidence: Math.min(0.96, Math.max(0.82, highestScore + 0.5)),
          confidence_level: 'HIGH',
          source_faq: {
            id: bestMatch.id,
            category: bestMatch.category,
            question: bestMatch.question,
            answer: bestMatch.answer,
            match_score: Math.min(0.96, Math.max(0.82, highestScore + 0.5)),
          },
        },
        status: 'answered',
      };
    }

    return {
      conversation_id: conversationId,
      message: {
        id: `msg_${Math.random().toString(36).substring(2, 9)}`,
        sender: 'assistant',
        content: "I couldn't find a reliable answer for this question in our company knowledge base. To ensure you receive accurate assistance, please connect with our human support team below.",
        timestamp,
        confidence: 0.12,
        confidence_level: 'LOW',
        requires_escalation: true,
        escalation_reason: 'No grounded match in Knowledge Base',
      },
      status: 'unresolved',
    };
  }
}

export async function fetchFAQs(category?: string, search?: string): Promise<FAQItem[]> {
  try {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (search) params.append('search', search);

    const res = await fetch(`${API_BASE_URL}/faqs?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch FAQs');
    return await res.json();
  } catch {
    let faqs = getStoredFAQs();
    if (category && category !== 'All') {
      faqs = faqs.filter(f => f.category.toLowerCase() === category.toLowerCase());
    }
    if (search) {
      const q = search.toLowerCase();
      faqs = faqs.filter(f => 
        f.question.toLowerCase().includes(q) ||
        f.answer.toLowerCase().includes(q) ||
        f.category.toLowerCase().includes(q)
      );
    }
    return faqs;
  }
}

export async function createFAQ(faqData: Omit<FAQItem, 'id'>): Promise<FAQItem> {
  try {
    const res = await fetch(`${API_BASE_URL}/faqs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(faqData),
    });
    if (!res.ok) throw new Error('Failed to create FAQ');
    return await res.json();
  } catch {
    const newFaq: FAQItem = {
      ...faqData,
      id: `FAQ-CUSTOM-${Math.random().toString(36).substring(2, 7).toUpperCase()}`,
      created_at: new Date().toISOString(),
    };
    const faqs = getStoredFAQs();
    faqs.unshift(newFaq);
    saveStoredFAQs(faqs);
    return newFaq;
  }
}

export async function updateFAQ(faqId: string, updates: Partial<FAQItem>): Promise<FAQItem> {
  try {
    const res = await fetch(`${API_BASE_URL}/faqs/${faqId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    if (!res.ok) throw new Error('Failed to update FAQ');
    return await res.json();
  } catch {
    const faqs = getStoredFAQs();
    const idx = faqs.findIndex(f => f.id === faqId);
    if (idx !== -1) {
      faqs[idx] = { ...faqs[idx], ...updates, updated_at: new Date().toISOString() };
      saveStoredFAQs(faqs);
      return faqs[idx];
    }
    throw new Error('FAQ not found');
  }
}

export async function deleteFAQ(faqId: string) {
  try {
    const res = await fetch(`${API_BASE_URL}/faqs/${faqId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete FAQ');
    return await res.json();
  } catch {
    let faqs = getStoredFAQs();
    faqs = faqs.filter(f => f.id !== faqId);
    saveStoredFAQs(faqs);
    return { status: 'deleted', id: faqId };
  }
}

export async function createTicket(ticketData: {
  conversation_id?: string;
  customer_name: string;
  customer_email: string;
  category: string;
  issue_description: string;
  priority: 'Low' | 'Medium' | 'High' | 'Urgent';
}): Promise<TicketResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/tickets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(ticketData),
    });
    if (!res.ok) throw new Error('Failed to create support ticket');
    return await res.json();
  } catch {
    const newTicket: TicketResponse = {
      id: `TICK-${Math.floor(10000 + Math.random() * 90000)}`,
      conversation_id: ticketData.conversation_id || `conv_${Math.random().toString(36).substring(2, 9)}`,
      customer_name: ticketData.customer_name,
      customer_email: ticketData.customer_email,
      category: ticketData.category || 'General Inquiry',
      issue_description: ticketData.issue_description,
      priority: ticketData.priority || 'Medium',
      status: 'Open',
      created_at: new Date().toISOString(),
      assigned_agent: 'Tier-1 Support Team',
      estimated_response_time: '< 15 mins',
      notes: [{ agent: 'System', note: 'Support ticket submitted by customer.', time: 'Just now' }],
    };
    const tickets = getStoredTickets();
    tickets.unshift(newTicket);
    saveStoredTickets(tickets);
    return newTicket;
  }
}

export async function fetchTickets(status?: string, priority?: string): Promise<TicketResponse[]> {
  try {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (priority) params.append('priority', priority);

    const res = await fetch(`${API_BASE_URL}/tickets?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch tickets');
    return await res.json();
  } catch {
    let tickets = getStoredTickets();
    if (status && status !== 'All') {
      tickets = tickets.filter(t => t.status.toLowerCase() === status.toLowerCase());
    }
    if (priority && priority !== 'All') {
      tickets = tickets.filter(t => t.priority.toLowerCase() === priority.toLowerCase());
    }
    return tickets;
  }
}

export async function updateTicketStatus(
  ticketId: string,
  updates: {
    status?: 'Open' | 'In Progress' | 'Waiting for Customer' | 'Resolved' | 'Closed';
    priority?: 'Low' | 'Medium' | 'High' | 'Urgent';
    assigned_agent?: string;
    note?: string;
  }
): Promise<TicketResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    if (!res.ok) throw new Error('Failed to update ticket');
    return await res.json();
  } catch {
    const tickets = getStoredTickets();
    const idx = tickets.findIndex(t => t.id === ticketId);
    if (idx !== -1) {
      const current = tickets[idx];
      const newNotes = current.notes ? [...current.notes] : [];
      if (updates.note) {
        newNotes.push({
          agent: updates.assigned_agent || 'Support Agent',
          note: updates.note,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        });
      }
      tickets[idx] = {
        ...current,
        status: updates.status || current.status,
        priority: updates.priority || current.priority,
        assigned_agent: updates.assigned_agent || current.assigned_agent,
        notes: newNotes,
      };
      saveStoredTickets(tickets);
      return tickets[idx];
    }
    throw new Error('Ticket not found');
  }
}

export async function sendFeedback(messageId: string, isHelpful: boolean, reason?: string, comments?: string) {
  try {
    await fetch(`${API_BASE_URL}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message_id: messageId, is_helpful: isHelpful, reason, comments }),
    });
  } catch (e) {
    console.info('Feedback recorded locally:', messageId, isHelpful, reason, comments, e);
  }
}

export async function sendCSAT(conversationId: string, rating: number, comment?: string) {
  try {
    await fetch(`${API_BASE_URL}/csat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ conversation_id: conversationId, rating, comment }),
    });
  } catch (e) {
    console.info('CSAT recorded locally:', conversationId, rating, comment, e);
  }
}

export async function fetchAnalytics(): Promise<AnalyticsOverview> {
  try {
    const res = await fetch(`${API_BASE_URL}/analytics`);
    if (!res.ok) throw new Error('Failed to fetch analytics');
    return await res.json();
  } catch {
    const tickets = getStoredTickets();
    const openCount = tickets.filter(t => t.status === 'Open' || t.status === 'In Progress').length;
    return {
      today_conversations: 1420,
      ai_resolution_rate: 83.1,
      escalated_tickets: 240,
      open_tickets: openCount || 18,
      avg_response_time_min: 1.5,
      customer_satisfaction_score: 4.8,
      total_faqs: getStoredFAQs().length,
      confidence_breakdown: { high: 75.0, medium: 17.0, low_escalated: 8.0 },
      top_topics: [
        { category: 'Password Reset', count: 480, percentage: 34 },
        { category: 'Refunds & Money Back', count: 320, percentage: 23 },
        { category: 'Payments & Cards', count: 260, percentage: 18 },
        { category: 'Orders & Tracking', count: 210, percentage: 15 },
        { category: 'Subscriptions', count: 150, percentage: 10 },
      ],
      daily_trends: [
        { day: 'Mon', queries: 210, resolved: 180, escalated: 30 },
        { day: 'Tue', queries: 240, resolved: 205, escalated: 35 },
        { day: 'Wed', queries: 280, resolved: 235, escalated: 45 },
        { day: 'Thu', queries: 260, resolved: 218, escalated: 42 },
        { day: 'Fri', queries: 290, resolved: 242, escalated: 48 },
        { day: 'Sat', queries: 160, resolved: 140, escalated: 20 },
        { day: 'Sun', queries: 120, resolved: 105, escalated: 15 },
      ],
    };
  }
}

export async function fetchDemoScenarios(): Promise<DemoScenario[]> {
  return [
    {
      id: 'demo-1',
      title: '1. AI Answer (FAQ)',
      prompt: 'How can I reset my password?',
      description: 'AI matches company FAQ with high confidence and gives step-by-step instructions.',
    },
    {
      id: 'demo-2',
      title: '2. Smart Clarification',
      prompt: 'reset',
      description: 'Query is short/ambiguous. AI asks a clarification question with quick choices.',
    },
    {
      id: 'demo-3',
      title: '3. Unresolved & Ticket',
      prompt: 'Can I get a refund for a product purchased 5 years ago?',
      description: 'AI avoids inventing policy rules and offers human support with a ticket button.',
    },
    {
      id: 'demo-4',
      title: '4. Direct Escalation',
      prompt: 'I want to talk to a human agent.',
      description: 'AI detects request for human assistance and opens the support ticket workflow.',
    },
  ];
}
