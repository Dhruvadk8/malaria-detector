import React, { useState } from 'react';
import { Filter, Send, X } from 'lucide-react';
import type { TicketResponse } from '../../types';
import { updateTicketStatus } from '../../services/api';

interface TicketManagerProps {
  tickets: TicketResponse[];
  onRefresh: () => void;
  isCompact?: boolean;
}

export const TicketManager: React.FC<TicketManagerProps> = ({ tickets, onRefresh, isCompact = false }) => {
  const [statusFilter, setStatusFilter] = useState<string>('All');
  const [priorityFilter, setPriorityFilter] = useState<string>('All');
  const [selectedTicket, setSelectedTicket] = useState<TicketResponse | null>(null);

  const [agentNote, setAgentNote] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const filteredTickets = tickets.filter((t) => {
    if (statusFilter !== 'All' && t.status !== statusFilter) return false;
    if (priorityFilter !== 'All' && t.priority !== priorityFilter) return false;
    return true;
  });

  const handleUpdateStatus = async (ticketId: string, status: string) => {
    await updateTicketStatus(ticketId, { status: status as any });
    onRefresh();
    if (selectedTicket && selectedTicket.id === ticketId) {
      setSelectedTicket((prev) => (prev ? { ...prev, status: status as any } : null));
    }
  };

  const handleAssignAgent = async (ticketId: string, agent: string) => {
    await updateTicketStatus(ticketId, { assigned_agent: agent });
    onRefresh();
    if (selectedTicket && selectedTicket.id === ticketId) {
      setSelectedTicket((prev) => (prev ? { ...prev, assigned_agent: agent } : null));
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!agentNote.trim() || !selectedTicket) return;

    setIsSaving(true);
    try {
      const updated = await updateTicketStatus(selectedTicket.id, {
        note: agentNote.trim(),
      });
      setSelectedTicket(updated);
      setAgentNote('');
      onRefresh();
    } catch (err) {
      console.error('Note add error:', err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      
      {/* Filters Bar */}
      {!isCompact && (
        <div className="flex flex-wrap items-center justify-between gap-3 bg-white border border-slate-200 p-4 rounded-2xl shadow-sm">
          <div className="flex flex-wrap items-center gap-3">
            <Filter className="w-4 h-4 text-blue-600" />
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Filter Tickets:</span>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-800 focus:outline-none focus:border-blue-500 shadow-sm"
            >
              <option value="All">All Statuses</option>
              <option value="Open">Open</option>
              <option value="In Progress">In Progress</option>
              <option value="Waiting for Customer">Waiting for Customer</option>
              <option value="Resolved">Resolved</option>
              <option value="Closed">Closed</option>
            </select>

            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-800 focus:outline-none focus:border-blue-500 shadow-sm"
            >
              <option value="All">All Priorities</option>
              <option value="Urgent">Urgent</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>

          <div className="text-xs text-slate-500 font-medium">
            Showing <strong className="text-slate-800">{filteredTickets.length}</strong> of {tickets.length} tickets
          </div>
        </div>
      )}

      {/* Ticket Table */}
      <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-600 font-bold uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="px-4 py-3.5">Ticket ID</th>
                <th className="px-4 py-3.5">Customer</th>
                <th className="px-4 py-3.5">Category</th>
                <th className="px-4 py-3.5">Issue Summary</th>
                <th className="px-4 py-3.5">Priority</th>
                <th className="px-4 py-3.5">Status</th>
                <th className="px-4 py-3.5">Assigned Agent</th>
                <th className="px-4 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredTickets.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-slate-400 font-medium">
                    No support tickets found matching the criteria.
                  </td>
                </tr>
              ) : (
                filteredTickets.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-50/80 transition">
                    <td className="px-4 py-3.5 font-mono font-bold text-blue-600">{t.id}</td>
                    <td className="px-4 py-3.5">
                      <div className="font-bold text-slate-900">{t.customer_name}</div>
                      <div className="text-[11px] text-slate-400 font-mono">{t.customer_email}</div>
                    </td>
                    <td className="px-4 py-3.5">
                      <span className="px-2.5 py-1 bg-slate-100 border border-slate-200 text-slate-700 rounded-lg text-[11px] font-semibold">
                        {t.category}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 max-w-xs truncate text-slate-600 font-normal">
                      {t.issue_description}
                    </td>
                    <td className="px-4 py-3.5">
                      <span className={`px-2.5 py-0.5 rounded-full font-bold text-[10px] ${
                        t.priority === 'Urgent' ? 'bg-rose-50 text-rose-700 border border-rose-200' :
                        t.priority === 'High' ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                        'bg-blue-50 text-blue-700 border border-blue-200'
                      }`}>
                        {t.priority}
                      </span>
                    </td>
                    <td className="px-4 py-3.5">
                      <select
                        value={t.status}
                        onChange={(e) => handleUpdateStatus(t.id, e.target.value)}
                        className="px-2.5 py-1 bg-white border border-slate-200 rounded-lg text-[11px] font-bold text-slate-800 focus:outline-none focus:border-blue-500 shadow-sm"
                      >
                        <option value="Open">Open</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Waiting for Customer">Waiting for Customer</option>
                        <option value="Resolved">Resolved</option>
                        <option value="Closed">Closed</option>
                      </select>
                    </td>
                    <td className="px-4 py-3.5">
                      <select
                        value={t.assigned_agent || 'Tier-1 Support Team'}
                        onChange={(e) => handleAssignAgent(t.id, e.target.value)}
                        className="px-2.5 py-1 bg-white border border-slate-200 rounded-lg text-[11px] text-slate-700 focus:outline-none focus:border-blue-500 shadow-sm"
                      >
                        <option value="Tier-1 Support Team">Tier-1 Support Team</option>
                        <option value="David Miller (Lead)">David Miller (Lead)</option>
                        <option value="Emma Watson">Emma Watson</option>
                        <option value="James Lee">James Lee</option>
                      </select>
                    </td>
                    <td className="px-4 py-3.5 text-right">
                      <button
                        onClick={() => setSelectedTicket(t)}
                        className="px-3 py-1.5 bg-blue-50 hover:bg-blue-100 border border-blue-200 text-blue-700 rounded-lg text-[11px] font-bold transition"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Ticket Detail Drawer Modal */}
      {selectedTicket && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white border border-slate-200 rounded-3xl max-w-2xl w-full p-6 sm:p-8 shadow-2xl space-y-6 max-h-[90vh] overflow-y-auto">
            
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <div>
                <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Ticket Details</span>
                <h3 className="text-2xl font-extrabold text-blue-600 font-mono">{selectedTicket.id}</h3>
              </div>
              <button
                onClick={() => setSelectedTicket(null)}
                className="p-1.5 text-slate-400 hover:text-slate-700 rounded-xl hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Customer Details */}
            <div className="grid grid-cols-2 gap-4 bg-slate-50 p-4 rounded-2xl border border-slate-200 text-xs">
              <div>
                <span className="text-slate-500 block mb-1 font-semibold">Customer Name</span>
                <span className="font-bold text-slate-900 text-sm">{selectedTicket.customer_name}</span>
              </div>
              <div>
                <span className="text-slate-500 block mb-1 font-semibold">Customer Email</span>
                <span className="font-bold text-blue-600 text-sm">{selectedTicket.customer_email}</span>
              </div>
            </div>

            {/* Issue Description */}
            <div className="space-y-1">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block">Customer Issue Description</span>
              <p className="text-sm text-slate-800 bg-slate-50 p-4 rounded-2xl border border-slate-200 leading-relaxed">
                {selectedTicket.issue_description}
              </p>
            </div>

            {/* Internal Agent Notes */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Support Agent Log Notes
              </h4>
              <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 space-y-2 max-h-40 overflow-y-auto text-xs">
                {selectedTicket.notes && selectedTicket.notes.length > 0 ? (
                  selectedTicket.notes.map((n, idx) => (
                    <div key={idx} className="border-b border-slate-200 pb-2 last:border-0 last:pb-0">
                      <div className="flex items-center justify-between text-blue-700 font-bold mb-0.5">
                        <span>{n.agent}</span>
                        <span className="text-[10px] text-slate-400 font-normal">{n.time}</span>
                      </div>
                      <p className="text-slate-700">{n.note}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-slate-400 italic text-[11px]">No internal notes logged yet.</p>
                )}
              </div>

              {/* Add Note Form */}
              <form onSubmit={handleAddNote} className="flex gap-2 pt-1">
                <input
                  type="text"
                  placeholder="Add internal agent note..."
                  value={agentNote}
                  onChange={(e) => setAgentNote(e.target.value)}
                  className="flex-1 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-blue-500"
                />
                <button
                  type="submit"
                  disabled={!agentNote.trim() || isSaving}
                  className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl transition flex items-center gap-1.5 shadow-md shadow-blue-600/20 disabled:opacity-50"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Add Note</span>
                </button>
              </form>
            </div>

            <div className="flex justify-end pt-2 border-t border-slate-100">
              <button
                onClick={() => setSelectedTicket(null)}
                className="px-6 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs rounded-xl transition"
              >
                Close Drawer
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};
