import React from 'react';
import { Play, HelpCircle, ShieldAlert, MessageSquarePlus, UserCheck } from 'lucide-react';

interface DemoLauncherBarProps {
  onRunDemo: (prompt: string, selectedOption?: string) => void;
}

export const DemoLauncherBar: React.FC<DemoLauncherBarProps> = ({ onRunDemo }) => {
  return (
    <div className="bg-blue-50/70 border-b border-blue-100 py-2.5 px-4 sm:px-6">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
        
        {/* Label */}
        <div className="flex items-center space-x-2 text-xs font-extrabold text-blue-900">
          <Play className="w-3.5 h-3.5 text-blue-600 fill-blue-600" />
          <span className="uppercase tracking-wider">IEEE Demo Presets:</span>
        </div>

        {/* Demo Quick Action Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          
          <button
            onClick={() => onRunDemo("How can I reset my password?")}
            className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-white hover:bg-blue-100 text-blue-700 border border-blue-200 transition-all flex items-center gap-1.5 shadow-sm"
            title="Demonstrates grounded FAQ answer with high confidence"
          >
            <HelpCircle className="w-3.5 h-3.5 text-blue-600" />
            <span>1. Grounded FAQ Answer</span>
          </button>

          <button
            onClick={() => onRunDemo("reset")}
            className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-white hover:bg-amber-100 text-amber-800 border border-amber-200 transition-all flex items-center gap-1.5 shadow-sm"
            title="Demonstrates AI asking clarifying question with quick option buttons"
          >
            <MessageSquarePlus className="w-3.5 h-3.5 text-amber-600" />
            <span>2. Smart Clarification</span>
          </button>

          <button
            onClick={() => onRunDemo("Can I get a refund for a product purchased 5 years ago?")}
            className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-white hover:bg-rose-100 text-rose-800 border border-rose-200 transition-all flex items-center gap-1.5 shadow-sm"
            title="Demonstrates zero-hallucination guardrail on ungrounded query"
          >
            <ShieldAlert className="w-3.5 h-3.5 text-rose-600" />
            <span>3. Unresolved Query Handoff</span>
          </button>

          <button
            onClick={() => onRunDemo("I want to talk to a human.")}
            className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-white hover:bg-emerald-100 text-emerald-800 border border-emerald-200 transition-all flex items-center gap-1.5 shadow-sm"
            title="Demonstrates human escalation and ticket creation"
          >
            <UserCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>4. Direct Support Ticket</span>
          </button>

        </div>

      </div>
    </div>
  );
};
