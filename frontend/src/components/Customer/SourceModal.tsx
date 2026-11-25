import React from 'react';
import { X, BookOpen, CheckCircle, ShieldCheck, Tag } from 'lucide-react';
import type { SourceFAQ } from '../../types';

interface SourceModalProps {
  sourceFaq: SourceFAQ | null;
  onClose: () => void;
}

export const SourceModal: React.FC<SourceModalProps> = ({ sourceFaq, onClose }) => {
  if (!sourceFaq) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl max-w-lg w-full p-6 shadow-2xl shadow-indigo-500/10">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 rounded-xl text-indigo-400">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                Explainable AI Grounding Source
              </h3>
              <p className="text-xs text-slate-400">Verification of knowledge base backing</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* FAQ Content Details */}
        <div className="space-y-4">
          
          <div className="flex items-center justify-between text-xs bg-slate-800/60 p-3 rounded-xl border border-slate-700/50">
            <div className="flex items-center space-x-2 text-indigo-300 font-semibold">
              <Tag className="w-3.5 h-3.5" />
              <span>Reference ID: {sourceFaq.id}</span>
            </div>
            <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold flex items-center gap-1">
              <ShieldCheck className="w-3 h-3" /> Grounded ({Math.round(sourceFaq.match_score * 100)}% Match)
            </span>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Category
            </label>
            <span className="inline-block px-2.5 py-1 bg-slate-800 text-slate-200 rounded-md text-xs font-medium border border-slate-700">
              {sourceFaq.category}
            </span>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Knowledge Base Question
            </label>
            <p className="text-sm font-semibold text-slate-100 bg-slate-950 p-3 rounded-xl border border-slate-800">
              "{sourceFaq.question}"
            </p>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Approved Company Answer
            </label>
            <div className="text-sm text-slate-300 bg-indigo-950/20 border border-indigo-500/20 p-3.5 rounded-xl leading-relaxed">
              {sourceFaq.answer}
            </div>
          </div>

          <div className="pt-2 text-xs text-slate-400 flex items-center gap-1.5 bg-slate-950/50 p-2.5 rounded-lg">
            <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>This answer was generated using verified TechNova internal documentation.</span>
          </div>

        </div>

        {/* Footer */}
        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-xl text-sm transition"
          >
            Got It
          </button>
        </div>

      </div>
    </div>
  );
};
