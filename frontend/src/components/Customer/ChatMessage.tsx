import React, { useState } from 'react';
import { Bot, User, ThumbsUp, ThumbsDown, BookOpen, AlertCircle, ShieldCheck, UserCheck, Check } from 'lucide-react';
import type { ChatMessage as ChatMessageType, SourceFAQ } from '../../types';
import { sendFeedback } from '../../services/api';

interface ChatMessageProps {
  message: ChatMessageType;
  onViewSource: (faq: SourceFAQ) => void;
  onSelectOption: (subQuery: string, optionText: string) => void;
  onOpenEscalation: () => void;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  onViewSource,
  onSelectOption,
  onOpenEscalation,
}) => {
  const isUser = message.sender === 'user';
  const isAssistant = message.sender === 'assistant';

  const [feedbackState, setFeedbackState] = useState<'none' | 'helpful' | 'unhelpful'>('none');
  const [showFeedbackReason, setShowFeedbackReason] = useState(false);

  const handleFeedback = (isHelpful: boolean) => {
    if (isHelpful) {
      setFeedbackState('helpful');
      setShowFeedbackReason(false);
      sendFeedback(message.id, true);
    } else {
      setFeedbackState('unhelpful');
      setShowFeedbackReason(true);
    }
  };

  const submitUnhelpfulReason = (reason: string) => {
    setShowFeedbackReason(false);
    sendFeedback(message.id, false, reason);
    if (reason === 'Need human support') {
      onOpenEscalation();
    }
  };

  return (
    <div className={`flex w-full mb-5 ${isUser ? 'justify-end' : 'justify-start'} animate-fadeIn`}>
      <div className={`flex items-start max-w-2xl gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        
        {/* Avatar */}
        <div className={`w-9 h-9 rounded-2xl flex items-center justify-center flex-shrink-0 text-xs font-bold shadow-sm ${
          isUser
            ? 'bg-blue-100 text-blue-700 border border-blue-200'
            : 'bg-blue-600 text-white shadow-blue-500/20'
        }`}>
          {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
        </div>

        {/* Bubble & Details */}
        <div className="space-y-2 max-w-xl">
          
          {/* Main Bubble */}
          <div className={`p-4 sm:p-5 rounded-2xl text-sm leading-relaxed shadow-sm ${
            isUser
              ? 'bg-blue-600 text-white rounded-tr-none'
              : 'bg-white text-slate-800 border border-slate-200 rounded-tl-none'
          }`}>
            
            {/* Confidence & Source Badge for AI Message */}
            {isAssistant && message.confidence !== undefined && (
              <div className="flex flex-wrap items-center justify-between gap-2 mb-3 pb-2.5 border-b border-slate-100 text-xs">
                <div className="flex items-center space-x-1.5 font-semibold">
                  <ShieldCheck className="w-4 h-4 text-blue-600" />
                  <span className="text-slate-600">Confidence:</span>
                  <span className={`px-2 py-0.5 rounded-full text-[11px] font-bold ${
                    message.confidence_level === 'HIGH'
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : message.confidence_level === 'MEDIUM'
                      ? 'bg-amber-50 text-amber-700 border border-amber-200'
                      : 'bg-rose-50 text-rose-700 border border-rose-200'
                  }`}>
                    {Math.round(message.confidence * 100)}% ({message.confidence_level})
                  </span>
                </div>

                {message.source_faq && (
                  <button
                    onClick={() => onViewSource(message.source_faq!)}
                    className="flex items-center space-x-1 px-2.5 py-1 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg text-xs font-semibold text-blue-700 transition"
                  >
                    <BookOpen className="w-3.5 h-3.5 text-blue-600" />
                    <span>FAQ Source</span>
                  </button>
                )}
              </div>
            )}

            {/* Content Text */}
            <div className="whitespace-pre-wrap font-normal">{message.content}</div>

            {/* Clarification Options Pills */}
            {isAssistant && message.clarification_options && message.clarification_options.length > 0 && (
              <div className="mt-4 pt-3 border-t border-slate-100 space-y-2">
                <p className="text-xs font-bold text-amber-800 flex items-center gap-1.5">
                  <AlertCircle className="w-4 h-4 text-amber-600" /> Did you mean one of these topics?
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {message.clarification_options.map((opt) => (
                    <button
                      key={opt.id}
                      onClick={() => onSelectOption(opt.sub_query, opt.text)}
                      className="text-left px-3.5 py-2.5 bg-slate-50 hover:bg-blue-50 border border-slate-200 hover:border-blue-300 rounded-xl text-xs font-semibold text-slate-700 hover:text-blue-700 transition flex items-center justify-between group shadow-sm"
                    >
                      <span>{opt.text}</span>
                      <Check className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 text-blue-600 transition" />
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Escalation Offer Box */}
            {isAssistant && message.requires_escalation && (
              <div className="mt-4 pt-3 border-t border-slate-100 bg-amber-50/80 p-4 rounded-2xl border border-amber-200 space-y-3">
                <div className="flex items-center space-x-2 text-xs font-bold text-amber-900">
                  <UserCheck className="w-4 h-4 text-amber-700" />
                  <span>Human Support Assistance</span>
                </div>
                <p className="text-xs text-amber-800 leading-relaxed">
                  "I couldn't find a reliable answer for this question." Would you like to submit a support ticket for a human customer specialist to resolve this?
                </p>
                <button
                  onClick={onOpenEscalation}
                  className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-xl transition shadow-md shadow-blue-600/20 flex items-center justify-center space-x-2"
                >
                  <UserCheck className="w-4 h-4" />
                  <span>Contact Human Support / Create Support Ticket</span>
                </button>
              </div>
            )}

          </div>

          {/* AI Message Footer: Timestamp & Feedback */}
          {isAssistant && (
            <div className="flex items-center justify-between text-xs text-slate-400 px-1">
              <span className="text-[11px] text-slate-400">{message.timestamp}</span>

              {/* Feedback System */}
              <div className="flex items-center space-x-1.5">
                <button
                  onClick={() => handleFeedback(true)}
                  className={`p-1 rounded-lg hover:bg-slate-100 transition ${
                    feedbackState === 'helpful' ? 'text-emerald-600 bg-emerald-50' : 'text-slate-400 hover:text-slate-600'
                  }`}
                  title="Helpful"
                >
                  <ThumbsUp className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => handleFeedback(false)}
                  className={`p-1 rounded-lg hover:bg-slate-100 transition ${
                    feedbackState === 'unhelpful' ? 'text-rose-600 bg-rose-50' : 'text-slate-400 hover:text-slate-600'
                  }`}
                  title="Not Helpful"
                >
                  <ThumbsDown className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}

          {/* Feedback Reason Popover */}
          {showFeedbackReason && (
            <div className="bg-white border border-slate-200 p-3 rounded-2xl text-xs space-y-2 shadow-md animate-fadeIn">
              <p className="font-semibold text-slate-700">What went wrong?</p>
              <div className="flex flex-wrap gap-1.5">
                {['Incorrect answer', "Didn't understand", 'Not relevant', 'Need human support'].map((r) => (
                  <button
                    key={r}
                    onClick={() => submitUnhelpfulReason(r)}
                    className="px-3 py-1 bg-slate-50 hover:bg-blue-50 border border-slate-200 text-slate-600 hover:text-blue-700 rounded-lg transition text-[11px] font-medium"
                  >
                    {r}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* User message timestamp */}
          {isUser && (
            <div className="text-[11px] text-slate-400 text-right px-1">
              {message.timestamp}
            </div>
          )}

        </div>
      </div>
    </div>
  );
};
