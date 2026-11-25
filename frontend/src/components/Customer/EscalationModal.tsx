import React, { useState } from 'react';
import { X, UserCheck, Send, Sparkles } from 'lucide-react';
import { createTicket } from '../../services/api';
import type { TicketResponse } from '../../types';

interface EscalationModalProps {
  conversationId: string;
  initialQuery?: string;
  onClose: () => void;
  onTicketCreated: (ticket: TicketResponse) => void;
}

export const EscalationModal: React.FC<EscalationModalProps> = ({
  conversationId,
  initialQuery = '',
  onClose,
  onTicketCreated,
}) => {
  const [name, setName] = useState('Alex Morgan');
  const [email, setEmail] = useState('alex.m@technova-user.io');
  const [category, setCategory] = useState('General');
  const [description, setDescription] = useState(initialQuery || 'I require human agent assistance for my query.');
  const [priority, setPriority] = useState<'Low' | 'Medium' | 'High' | 'Urgent'>('Medium');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !email.trim() || !description.trim()) {
      setError('Please fill in all required fields.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      const ticket = await createTicket({
        conversation_id: conversationId,
        customer_name: name,
        customer_email: email,
        category,
        issue_description: description,
        priority,
      });
      onTicketCreated(ticket);
    } catch (err: any) {
      setError(err.message || 'Failed to submit ticket. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl max-w-lg w-full p-6 shadow-2xl shadow-indigo-500/10">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
          <div className="flex items-center space-x-2.5">
            <div className="p-2.5 bg-amber-500/10 border border-amber-500/20 rounded-xl text-amber-400">
              <UserCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Escalate to Human Support</h3>
              <p className="text-xs text-slate-400">Submit a support ticket for agent review</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-rose-500/10 border border-rose-500/30 text-rose-400 rounded-xl text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Your Name *</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500"
                required
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Email Address *</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Issue Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500"
              >
                <option value="General">General Inquiry</option>
                <option value="Payments">Payments & Billing</option>
                <option value="Account">Account Access & Password</option>
                <option value="Orders">Orders & Shipping</option>
                <option value="Refunds">Refunds & Returns</option>
                <option value="Subscription">Subscription</option>
                <option value="Technical Support">Technical Support</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Priority</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value as any)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500"
              >
                <option value="Low">Low Priority</option>
                <option value="Medium">Medium Priority</option>
                <option value="High">High Priority</option>
                <option value="Urgent">Urgent</option>
              </select>
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Issue Description *</label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500"
              required
            />
          </div>

          <div className="p-3 bg-indigo-950/30 border border-indigo-500/20 rounded-xl">
            <div className="flex items-center space-x-2 text-xs font-semibold text-indigo-300 mb-1">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              <span>AI Conversation Handoff Included</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              SupportAI will automatically generate a bullet-point summary and recommended action for the support agent so you don't have to repeat yourself.
            </p>
          </div>

          <div className="flex items-center justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium rounded-xl transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 bg-gradient-to-r from-amber-500 to-indigo-600 hover:from-amber-600 hover:to-indigo-700 text-slate-950 font-semibold text-sm rounded-xl transition shadow-lg shadow-indigo-500/20 flex items-center space-x-2 disabled:opacity-50"
            >
              {isSubmitting ? (
                <span>Submitting...</span>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Create Support Ticket</span>
                </>
              )}
            </button>
          </div>

        </form>
      </div>
    </div>
  );
};
