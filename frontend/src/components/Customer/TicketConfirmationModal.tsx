import React from 'react';
import { CheckCircle2, Ticket, Clock, ShieldCheck, ArrowRight } from 'lucide-react';
import type { TicketResponse } from '../../types';

interface TicketConfirmationModalProps {
  ticket: TicketResponse;
  onClose: () => void;
  onViewTickets: () => void;
}

export const TicketConfirmationModal: React.FC<TicketConfirmationModalProps> = ({
  ticket,
  onClose,
  onViewTickets,
}) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-emerald-500/30 rounded-2xl max-w-lg w-full p-6 shadow-2xl shadow-emerald-500/10">
        
        {/* Header Success Icon */}
        <div className="text-center mb-5">
          <div className="w-14 h-14 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-lg shadow-emerald-500/20">
            <CheckCircle2 className="w-8 h-8" />
          </div>
          <h3 className="text-xl font-bold text-white">Ticket Submitted Successfully!</h3>
          <p className="text-xs text-slate-400 mt-1">
            Your request has been routed to our human support team.
          </p>
        </div>

        {/* Ticket Details */}
        <div className="space-y-4">
          
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Ticket ID</span>
              <span className="text-base font-mono font-bold text-indigo-400">{ticket.id}</span>
            </div>
            <div className="text-right">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Priority</span>
              <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-bold ${
                ticket.priority === 'Urgent' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                ticket.priority === 'High' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
              }`}>
                {ticket.priority}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="bg-slate-800/60 p-3 rounded-xl border border-slate-700/50">
              <span className="text-slate-400 block mb-1">Category</span>
              <span className="font-semibold text-slate-200">{ticket.category}</span>
            </div>
            <div className="bg-slate-800/60 p-3 rounded-xl border border-slate-700/50 flex items-center space-x-2">
              <Clock className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              <div>
                <span className="text-slate-400 block">Est. Response Time</span>
                <span className="font-semibold text-emerald-300">{ticket.estimated_response_time}</span>
              </div>
            </div>
          </div>

          {/* AI Conversation Summary Preview */}
          {ticket.conversation_summary && (
            <div className="bg-indigo-950/20 border border-indigo-500/20 p-3.5 rounded-xl space-y-2">
              <div className="flex items-center space-x-1.5 text-xs font-semibold text-indigo-300">
                <ShieldCheck className="w-4 h-4 text-indigo-400" />
                <span>AI Handoff Summary for Agent</span>
              </div>
              <ul className="text-xs text-slate-300 space-y-1 list-disc pl-4">
                {ticket.conversation_summary.issue_summary?.slice(0, 3).map((bullet, idx) => (
                  <li key={idx}>{bullet}</li>
                ))}
              </ul>
            </div>
          )}

        </div>

        {/* Footer Actions */}
        <div className="mt-6 flex flex-col sm:flex-row items-center gap-3">
          <button
            onClick={onViewTickets}
            className="w-full sm:w-1/2 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-sm rounded-xl transition flex items-center justify-center space-x-2"
          >
            <Ticket className="w-4 h-4" />
            <span>View My Tickets</span>
          </button>

          <button
            onClick={onClose}
            className="w-full sm:w-1/2 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm rounded-xl transition flex items-center justify-center space-x-2 shadow-lg shadow-indigo-600/20"
          >
            <span>Return to Chat</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

      </div>
    </div>
  );
};
