import React, { useState, useEffect } from 'react';
import { Ticket, RefreshCw, ShieldCheck } from 'lucide-react';
import { fetchTickets } from '../../services/api';
import type { TicketResponse } from '../../types';

export const MyTickets: React.FC = () => {
  const [tickets, setTickets] = useState<TicketResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadTickets();
  }, []);

  const loadTickets = async () => {
    setLoading(true);
    try {
      const data = await fetchTickets();
      setTickets(data);
    } catch (err) {
      console.error('Error fetching tickets:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-fadeIn pb-12">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Ticket className="w-6 h-6 text-indigo-400" /> My Support Tickets
          </h1>
          <p className="text-xs text-slate-400">Track and monitor your human support requests</p>
        </div>
        <button
          onClick={loadTickets}
          className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition flex items-center gap-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400 text-sm">Loading your tickets...</div>
      ) : tickets.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center text-slate-400 text-sm">
          No support tickets created yet.
        </div>
      ) : (
        <div className="space-y-4">
          {tickets.map((t) => (
            <div key={t.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
              
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
                <div className="flex items-center space-x-3">
                  <span className="text-base font-mono font-bold text-indigo-400">{t.id}</span>
                  <span className="px-2.5 py-0.5 bg-slate-800 text-slate-300 border border-slate-700 rounded-md text-xs font-semibold">
                    {t.category}
                  </span>
                </div>

                <div className="flex items-center space-x-2">
                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                    t.status === 'Resolved' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                    t.status === 'In Progress' ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' :
                    'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  }`}>
                    {t.status}
                  </span>

                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                    t.priority === 'Urgent' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                    t.priority === 'High' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                    'bg-slate-800 text-slate-400 border border-slate-700'
                  }`}>
                    {t.priority}
                  </span>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-slate-200 block mb-1">Issue Description</h3>
                <p className="text-sm text-slate-300 bg-slate-950 p-3 rounded-xl border border-slate-800">
                  {t.issue_description}
                </p>
              </div>

              {t.conversation_summary && (
                <div className="bg-indigo-950/20 border border-indigo-500/20 p-3.5 rounded-xl space-y-2 text-xs">
                  <div className="flex items-center space-x-1.5 font-semibold text-indigo-300">
                    <ShieldCheck className="w-4 h-4 text-indigo-400" />
                    <span>AI Conversation Summary Prepared for Agent</span>
                  </div>
                  <ul className="list-disc pl-4 text-slate-300 space-y-1">
                    {t.conversation_summary.issue_summary?.map((b, idx) => (
                      <li key={idx}>{b}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="flex flex-wrap items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/60">
                <span>Created: {t.created_at}</span>
                <span>Assigned Agent: {t.assigned_agent}</span>
                <span className="text-emerald-400 font-medium">Est. Response: {t.estimated_response_time}</span>
              </div>

            </div>
          ))}
        </div>
      )}

    </div>
  );
};
