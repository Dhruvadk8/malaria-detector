import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Bot, UserCheck, HeartHandshake, RefreshCw } from 'lucide-react';
import { ChatMessage } from './ChatMessage';
import type { ChatMessage as ChatMessageType, SourceFAQ } from '../../types';
import { sendMessageToAI } from '../../services/api';
import { SourceModal } from './SourceModal';
import { CSATModal } from './CSATModal';

interface ChatInterfaceProps {
  conversationId: string;
  messages: ChatMessageType[];
  setMessages: React.Dispatch<React.SetStateAction<ChatMessageType[]>>;
  onOpenTicketPage: (initialQuery?: string) => void;
  externalPrompt?: string;
  onClearExternalPrompt?: () => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  conversationId,
  messages,
  setMessages,
  onOpenTicketPage,
  externalPrompt,
  onClearExternalPrompt,
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  
  // Modals state
  const [selectedSource, setSelectedSource] = useState<SourceFAQ | null>(null);
  const [showCSAT, setShowCSAT] = useState(false);
  const [fileToast, setFileToast] = useState(false);

  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    if (externalPrompt) {
      handleSend(externalPrompt);
      if (onClearExternalPrompt) onClearExternalPrompt();
    }
  }, [externalPrompt]);

  const handleSend = async (textToSend?: string, selectedOption?: string) => {
    const query = textToSend || inputMessage;
    if (!query.trim()) return;

    const userMsgId = `msg_${Math.random().toString(36).substring(2, 9)}`;
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const userMsg: ChatMessageType = {
      id: userMsgId,
      sender: 'user',
      content: query.trim(),
      timestamp,
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputMessage('');
    setIsTyping(true);

    try {
      const res = await sendMessageToAI(conversationId, query.trim(), selectedOption);
      setIsTyping(false);
      if (res && res.message) {
        setMessages((prev) => [...prev, res.message]);
      }
    } catch (err) {
      setIsTyping(false);
      console.error('Chat error:', err);
    }
  };

  const handleClarificationOption = (subQuery: string, optionText: string) => {
    handleSend(subQuery, optionText);
  };

  const handleResetChat = () => {
    setMessages([
      {
        id: `msg_welcome_${Date.now()}`,
        sender: 'assistant',
        content: 'Hello! I am SupportAI, your intelligent customer support assistant. How can I help you with your password, refunds, orders, shipping, or account today?',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        confidence: 1.0,
        confidence_level: 'HIGH',
      },
    ]);
  };

  const handleAttachFile = () => {
    setFileToast(true);
    setTimeout(() => setFileToast(false), 3000);
  };

  const sampleSuggestions = [
    'How can I reset my password?',
    'How can I get a refund?',
    'How do I contact support?',
    'What payment methods are accepted?',
    'Where is my order?',
    'How do I cancel my subscription?',
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-9rem)] min-h-[580px] bg-white border border-slate-200 rounded-3xl shadow-lg overflow-hidden animate-fadeIn">
      
      {/* Header */}
      <div className="bg-slate-50 border-b border-slate-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-2xl bg-blue-600 text-white flex items-center justify-center shadow-md shadow-blue-500/20">
              <Bot className="w-6 h-6" />
            </div>
            <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 border-2 border-white rounded-full"></span>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-bold text-slate-900">SupportAI Assistant</h2>
              <span className="px-2.5 py-0.5 text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span> Online
              </span>
            </div>
            <p className="text-xs text-slate-500">Grounded Knowledge Base Engine • IEEE Hackathon Demo</p>
          </div>
        </div>

        {/* Top Header Actions */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => onOpenTicketPage(messages.filter(m => m.sender === 'user').slice(-1)[0]?.content)}
            className="px-3.5 py-2 bg-amber-50 hover:bg-amber-100 border border-amber-200 text-amber-800 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shadow-sm"
          >
            <UserCheck className="w-4 h-4 text-amber-700" />
            <span className="hidden sm:inline">Contact</span> Human Support
          </button>

          <button
            onClick={handleResetChat}
            className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 rounded-xl transition"
            title="Reset Chat"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          
          <button
            onClick={() => setShowCSAT(true)}
            className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold transition flex items-center gap-1.5"
          >
            <HeartHandshake className="w-4 h-4 text-blue-600" />
            <span className="hidden md:inline">Rate Chat</span>
          </button>
        </div>
      </div>

      {/* File Upload Toast Notification */}
      {fileToast && (
        <div className="bg-blue-600 text-white text-xs px-4 py-2 text-center font-semibold shadow-md animate-fadeIn">
          📎 Simulated File Attachment (Images, Documents, Logs supported)
        </div>
      )}

      {/* Message Stream Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 bg-slate-50/50">
        {messages.map((msg) => (
          <ChatMessage
            key={msg.id}
            message={msg}
            onViewSource={(faq) => setSelectedSource(faq)}
            onSelectOption={handleClarificationOption}
            onOpenEscalation={() => onOpenTicketPage(msg.content)}
          />
        ))}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex items-center space-x-3 text-slate-500 text-xs animate-fadeIn">
            <div className="w-8 h-8 rounded-2xl bg-blue-600 text-white flex items-center justify-center shadow-sm">
              <Bot className="w-4 h-4" />
            </div>
            <div className="px-4 py-3 bg-white rounded-2xl rounded-tl-none border border-slate-200 flex items-center space-x-2 shadow-sm">
              <span className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></span>
              <span className="w-2 h-2 bg-blue-600 rounded-full animate-bounce [animation-delay:0.2s]"></span>
              <span className="w-2 h-2 bg-blue-600 rounded-full animate-bounce [animation-delay:0.4s]"></span>
              <span className="ml-2 font-medium text-slate-600">SupportAI is searching company FAQs...</span>
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Suggested Questions Pills */}
      <div className="px-4 sm:px-6 py-2.5 bg-white border-t border-slate-100">
        <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-xs no-scrollbar">
          <span className="text-slate-400 font-bold uppercase text-[10px] tracking-wider flex-shrink-0">
            Suggested:
          </span>
          {sampleSuggestions.map((promptText, i) => (
            <button
              key={i}
              onClick={() => handleSend(promptText)}
              className="px-3.5 py-1.5 bg-blue-50/80 hover:bg-blue-100 border border-blue-200/80 text-blue-700 hover:text-blue-900 font-medium rounded-full whitespace-nowrap transition flex-shrink-0 shadow-sm"
            >
              {promptText}
            </button>
          ))}
        </div>
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t border-slate-200">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center space-x-2"
        >
          <button
            type="button"
            onClick={handleAttachFile}
            className="p-3 text-slate-400 hover:text-blue-600 hover:bg-slate-100 rounded-2xl transition"
            title="Attach file"
          >
            <Paperclip className="w-5 h-5" />
          </button>

          <input
            type="text"
            placeholder="Type your question (e.g. password reset, refunds, shipping)..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            className="flex-1 px-4 py-3 bg-slate-50 border border-slate-200 focus:border-blue-500 focus:bg-white rounded-2xl text-sm text-slate-900 placeholder-slate-400 focus:outline-none transition-all shadow-inner"
          />

          <button
            type="submit"
            disabled={!inputMessage.trim()}
            className="px-5 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-2xl transition flex items-center space-x-2 shadow-md shadow-blue-600/20 disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline">Send</span>
          </button>
        </form>
      </div>

      {/* Source Modal */}
      <SourceModal sourceFaq={selectedSource} onClose={() => setSelectedSource(null)} />

      {/* CSAT Modal */}
      {showCSAT && (
        <CSATModal conversationId={conversationId} onClose={() => setShowCSAT(false)} />
      )}

    </div>
  );
};
