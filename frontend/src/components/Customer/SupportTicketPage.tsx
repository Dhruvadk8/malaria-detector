import React, { useState } from 'react';
import { AlertCircle, UserCheck, Send, CheckCircle2, ArrowRight, ShieldAlert, Sparkles, Clock, Ticket } from 'lucide-react';
import { createTicket } from '../../services/api';
import type { TicketResponse } from '../../types';

interface SupportTicketPageProps {
  initialQuery?: string;
  isUnresolved?: boolean;
  onTicketSubmitted?: (ticket: TicketResponse) => void;
  onGoToChat?: () => void;
  onGoToAdmin?: () => void;
}

export const SupportTicketPage: React.FC<SupportTicketPageProps> = ({
  initialQuery = '',
  isUnresolved = false,
  onTicketSubmitted,
  onGoToChat,
  onGoToAdmin,
}) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [category, setCategory] = useState('General Inquiry');
  const [issue, setIssue] = useState(initialQuery);
  const [priority, setPriority] = useState<'Low' | 'Medium' | 'High' | 'Urgent'>('Medium');
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submittedTicket, setSubmittedTicket] = useState<TicketResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !email.trim() || !issue.trim()) {
      setError('Please provide your name, email address, and issue description.');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const ticket = await createTicket({
        customer_name: name.trim(),
        customer_email: email.trim(),
        category,
        issue_description: issue.trim(),
        priority,
      });

      setSubmittedTicket(ticket);
      if (onTicketSubmitted) onTicketSubmitted(ticket);
    } catch (err: any) {
      setError(err.message || 'Failed to submit support ticket. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12 animate-fadeIn">
      
      {/* Top Banner when coming from Unresolved AI Answer */}
      {isUnresolved && (
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-5 flex items-start space-x-4 shadow-sm">
          <div className="p-2.5 bg-amber-100 border border-amber-200 text-amber-700 rounded-xl flex-shrink-0">
            <AlertCircle className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <h3 className="text-base font-bold text-amber-900">
              "I couldn't find a reliable answer for this question."
            </h3>
            <p className="text-sm text-amber-800 leading-relaxed">
              Don't worry! Our human support team is ready to help. Please fill out the form below to submit a priority ticket, and an agent will contact you shortly.
            </p>
          </div>
        </div>
      )}

      {/* Main Container */}
      {!submittedTicket ? (
        <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-10 shadow-sm space-y-8">
          
          {/* Header */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-100 pb-6">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 rounded-2xl bg-blue-50 border border-blue-200 text-blue-600 flex items-center justify-center shadow-sm">
                <UserCheck className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900">Create Support Ticket</h1>
                <p className="text-sm text-slate-500">Connect with human support for specialized assistance</p>
              </div>
            </div>

            <div className="px-3.5 py-1.5 bg-blue-50 border border-blue-200 text-blue-700 rounded-full text-xs font-semibold flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-blue-600" />
              <span>Avg Response Time &lt; 15 mins</span>
            </div>
          </div>

          {error && (
            <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-2xl text-sm flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Ticket Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Full Name <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. Sarah Jenkins"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 text-sm focus:outline-none focus:border-blue-500 focus:bg-white transition-all shadow-sm"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Email Address <span className="text-rose-500">*</span>
                </label>
                <input
                  type="email"
                  placeholder="e.g. sarah.j@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 text-sm focus:outline-none focus:border-blue-500 focus:bg-white transition-all shadow-sm"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Category
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 text-sm focus:outline-none focus:border-blue-500 focus:bg-white transition-all shadow-sm"
                >
                  <option value="General Inquiry">General Inquiry</option>
                  <option value="Password Reset">Password Reset</option>
                  <option value="Refunds & Returns">Refunds & Returns</option>
                  <option value="Payments & Cards">Payments & Cards</option>
                  <option value="Orders & Tracking">Orders & Tracking</option>
                  <option value="Shipping & Delivery">Shipping & Delivery</option>
                  <option value="Account Management">Account Management</option>
                  <option value="Subscription Cancellation">Subscription Cancellation</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Priority Level
                </label>
                <div className="grid grid-cols-4 gap-2">
                  {(['Low', 'Medium', 'High', 'Urgent'] as const).map((p) => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => setPriority(p)}
                      className={`py-2.5 rounded-xl text-xs font-bold transition-all border ${
                        priority === p
                          ? p === 'Urgent'
                            ? 'bg-rose-600 text-white border-rose-600 shadow-sm'
                            : p === 'High'
                            ? 'bg-amber-600 text-white border-amber-600 shadow-sm'
                            : 'bg-blue-600 text-white border-blue-600 shadow-sm'
                          : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                Issue Details <span className="text-rose-500">*</span>
              </label>
              <textarea
                rows={4}
                placeholder="Describe your issue or request in detail..."
                value={issue}
                onChange={(e) => setIssue(e.target.value)}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 text-sm focus:outline-none focus:border-blue-500 focus:bg-white transition-all shadow-sm"
                required
              />
            </div>

            {/* AI Grounding summary badge */}
            <div className="p-4 bg-blue-50/60 border border-blue-200/80 rounded-2xl flex items-start space-x-3">
              <Sparkles className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="space-y-1 text-xs text-slate-600">
                <span className="font-bold text-slate-900 block">Automatic Ticket Handoff Context</span>
                <p>
                  Your ticket will automatically log your conversation history with SupportAI so human support agents can resolve your ticket without asking you to repeat yourself.
                </p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="pt-4 flex items-center justify-between">
              {onGoToChat && (
                <button
                  type="button"
                  onClick={onGoToChat}
                  className="px-5 py-3 text-slate-600 hover:text-slate-900 font-medium text-sm transition"
                >
                  ← Back to Customer Chat
                </button>
              )}

              <button
                type="submit"
                disabled={isSubmitting}
                className="ml-auto px-8 py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-2xl shadow-lg shadow-blue-600/25 hover:shadow-blue-600/40 transition-all flex items-center space-x-2 text-base disabled:opacity-50"
              >
                {isSubmitting ? (
                  <span>Generating Ticket ID...</span>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Submit Support Ticket</span>
                  </>
                )}
              </button>
            </div>

          </form>
        </div>
      ) : (
        /* SUCCESS CONFIRMATION VIEW WITH TICKET ID */
        <div className="bg-white border border-slate-200 rounded-3xl p-8 sm:p-12 shadow-md text-center space-y-6 animate-scaleUp">
          <div className="w-16 h-16 rounded-full bg-emerald-100 border border-emerald-200 text-emerald-600 mx-auto flex items-center justify-center shadow-sm">
            <CheckCircle2 className="w-8 h-8" />
          </div>

          <div className="space-y-2">
            <div className="inline-flex items-center space-x-2 px-3 py-1 bg-emerald-50 border border-emerald-200 rounded-full text-emerald-700 text-xs font-bold">
              <span>Status: Open Ticket Created</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900">Support Ticket Submitted!</h2>
            <p className="text-sm text-slate-500 max-w-md mx-auto">
              Your issue has been transferred to Tier-1 Human Support. Below is your official ticket tracking reference.
            </p>
          </div>

          {/* Ticket ID Box */}
          <div className="max-w-md mx-auto bg-slate-50 border border-slate-200 rounded-2xl p-6 text-left space-y-3 shadow-inner">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Generated Ticket ID</span>
              <span className="px-3 py-1 bg-blue-600 text-white text-sm font-extrabold rounded-lg font-mono tracking-wider shadow-sm">
                {submittedTicket.id}
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-500 font-medium">Customer:</span>
                <span className="font-bold text-slate-800">{submittedTicket.customer_name} ({submittedTicket.customer_email})</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-medium">Category:</span>
                <span className="font-semibold text-slate-800">{submittedTicket.category}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-medium">Priority:</span>
                <span className="font-bold text-amber-600">{submittedTicket.priority}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-medium">Estimated Response:</span>
                <span className="font-bold text-emerald-600">{submittedTicket.estimated_response_time}</span>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-200 text-xs text-slate-600">
              <strong className="text-slate-800">Issue Summary:</strong> {submittedTicket.issue_description}
            </div>
          </div>

          <div className="pt-4 flex flex-wrap items-center justify-center gap-4">
            <button
              onClick={() => {
                setSubmittedTicket(null);
                setIssue('');
              }}
              className="px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl text-sm transition"
            >
              Submit Another Ticket
            </button>

            {onGoToAdmin && (
              <button
                onClick={onGoToAdmin}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm shadow-md transition flex items-center space-x-2"
              >
                <Ticket className="w-4 h-4" />
                <span>View Ticket in Admin Dashboard</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      )}

    </div>
  );
};
