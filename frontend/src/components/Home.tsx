import React, { useState, useEffect } from 'react';
import { Bot, BookOpen, HelpCircle, UserCheck, ArrowRight, Sparkles, Search, ShieldCheck, CheckCircle2, MessageSquare, Ticket, ChevronRight, Zap } from 'lucide-react';
import type { FAQItem } from '../types';
import { fetchFAQs } from '../services/api';

interface HomeProps {
  onStartChat: (initialPrompt?: string) => void;
  onNavigateToTicket: () => void;
  onNavigateToAdmin: () => void;
}

export const Home: React.FC<HomeProps> = ({
  onStartChat,
  onNavigateToTicket,
  onNavigateToAdmin,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [faqs, setFaqs] = useState<FAQItem[]>([]);
  const [expandedFaq, setExpandedFaq] = useState<string | null>(null);

  useEffect(() => {
    loadFaqs();
  }, [selectedCategory, searchQuery]);

  const loadFaqs = async () => {
    const data = await fetchFAQs(selectedCategory === 'All' ? undefined : selectedCategory, searchQuery);
    setFaqs(data);
  };

  const categories = [
    'All',
    'Password Reset',
    'Refunds',
    'Payments',
    'Orders',
    'Shipping',
    'Account Management',
    'Subscription Cancellation',
  ];

  const demoSteps = [
    { step: 1, label: 'Customer Question', detail: 'User enters query in chat' },
    { step: 2, label: 'AI Answer', detail: 'Matches grounded FAQ' },
    { step: 3, label: 'Unclear Query', detail: 'Detects ambiguous phrasing' },
    { step: 4, label: 'Clarification', detail: 'Offers interactive choice pills' },
    { step: 5, label: 'Unresolved Query', detail: 'Strict zero-hallucination policy' },
    { step: 6, label: 'Human Support', detail: 'Offers handoff button' },
    { step: 7, label: 'Support Ticket', detail: 'Creates ticket with unique ID' },
  ];

  return (
    <div className="space-y-12 pb-12 animate-fadeIn">
      
      {/* 1. HERO SECTION */}
      <section className="relative overflow-hidden bg-gradient-to-b from-blue-50/80 via-white to-slate-50 border border-blue-100 rounded-3xl p-8 sm:p-12 md:p-16 shadow-xl shadow-blue-500/5">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-blue-400/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 -mb-12 -ml-12 w-80 h-80 bg-indigo-400/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="relative max-w-3xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 bg-blue-50 border border-blue-200 rounded-full text-blue-700 text-xs font-semibold shadow-sm">
            <Sparkles className="w-3.5 h-3.5 text-blue-600 animate-pulse" />
            <span>IEEE Hackathon Demonstration Project</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight">
            SupportAI – Intelligent Customer Support
          </h1>

          <p className="text-lg sm:text-xl text-slate-600 font-normal max-w-2xl mx-auto leading-relaxed">
            Get instant answers, smart assistance, and seamless human support.
          </p>

          <div className="pt-4 flex flex-wrap items-center justify-center gap-4">
            <button
              onClick={() => onStartChat()}
              className="px-6 py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-2xl shadow-lg shadow-blue-600/25 hover:shadow-blue-600/40 transition-all flex items-center space-x-2 group text-base"
            >
              <Bot className="w-5 h-5" />
              <span>Start Chat</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>

            <button
              onClick={onNavigateToTicket}
              className="px-6 py-3.5 bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 font-semibold rounded-2xl shadow-sm transition-all flex items-center space-x-2 text-base"
            >
              <Ticket className="w-5 h-5 text-blue-600" />
              <span>Contact Support Ticket</span>
            </button>

            <button
              onClick={onNavigateToAdmin}
              className="px-6 py-3.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold rounded-2xl shadow-md transition-all flex items-center space-x-2 text-base"
            >
              <Zap className="w-5 h-5 text-amber-400" />
              <span>Admin Dashboard</span>
            </button>
          </div>

          {/* Value Badges */}
          <div className="pt-6 border-t border-slate-200/80 flex flex-wrap items-center justify-center gap-6 text-xs font-medium text-slate-500">
            <div className="flex items-center space-x-1.5 text-slate-700">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Grounded Knowledge Base</span>
            </div>
            <div className="flex items-center space-x-1.5 text-slate-700">
              <CheckCircle2 className="w-4 h-4 text-blue-600" />
              <span>Zero Hallucinations</span>
            </div>
            <div className="flex items-center space-x-1.5 text-slate-700">
              <MessageSquare className="w-4 h-4 text-indigo-600" />
              <span>Smart Clarifications</span>
            </div>
          </div>
        </div>
      </section>

      {/* 2. FEATURE CARDS */}
      <section className="space-y-6">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold text-slate-900">Key Features</h2>
          <p className="text-sm text-slate-500">Designed for enterprise accuracy and effortless customer satisfaction</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          
          {/* Card 1 */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md hover:border-blue-300 transition-all space-y-4 group">
            <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-200 text-blue-600 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Bot className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <h3 className="font-bold text-slate-900 text-lg">AI-Powered Answers</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Instant, accurate responses powered by grounded AI search algorithms that match customer questions with company policies.
              </p>
            </div>
          </div>

          {/* Card 2 */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md hover:border-blue-300 transition-all space-y-4 group">
            <div className="w-12 h-12 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-600 flex items-center justify-center group-hover:scale-110 transition-transform">
              <BookOpen className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <h3 className="font-bold text-slate-900 text-lg">FAQ-Based Support</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Retrieves answer snippets strictly from verified company FAQs covering accounts, billing, shipping, and refunds.
              </p>
            </div>
          </div>

          {/* Card 3 */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md hover:border-blue-300 transition-all space-y-4 group">
            <div className="w-12 h-12 rounded-xl bg-amber-50 border border-amber-200 text-amber-600 flex items-center justify-center group-hover:scale-110 transition-transform">
              <HelpCircle className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <h3 className="font-bold text-slate-900 text-lg">Smart Clarification</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                When customer queries are brief or ambiguous, SupportAI automatically presents interactive options to pinpoint exact intent.
              </p>
            </div>
          </div>

          {/* Card 4 */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md hover:border-blue-300 transition-all space-y-4 group">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-600 flex items-center justify-center group-hover:scale-110 transition-transform">
              <UserCheck className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <h3 className="font-bold text-slate-900 text-lg">Human Handoff</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                If an answer is unavailable or requested, SupportAI smoothly transfers the issue to human agents via an automated ticket ID.
              </p>
            </div>
          </div>

        </div>
      </section>

      {/* 3. IEEE DEMO FLOW WORKFLOW */}
      <section className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 text-xs font-bold bg-blue-100 text-blue-700 rounded-md uppercase tracking-wider">
                Hackathon Architecture
              </span>
              <h2 className="text-xl font-bold text-slate-900">Main Demo Pipeline</h2>
            </div>
            <p className="text-sm text-slate-500">Live operational flow verified during IEEE project presentation</p>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => onStartChat('How can I reset my password?')}
              className="px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg text-xs font-semibold transition"
            >
              Test FAQ Match →
            </button>
            <button
              onClick={() => onStartChat('reset')}
              className="px-3 py-1.5 bg-amber-50 hover:bg-amber-100 text-amber-700 rounded-lg text-xs font-semibold transition"
            >
              Test Clarification →
            </button>
            <button
              onClick={() => onStartChat('Can I return an item bought 3 years ago?')}
              className="px-3 py-1.5 bg-rose-50 hover:bg-rose-100 text-rose-700 rounded-lg text-xs font-semibold transition"
            >
              Test Unresolved Handoff →
            </button>
          </div>
        </div>

        {/* Horizontal Flow Steps */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3 pt-2">
          {demoSteps.map((stepItem, idx) => (
            <div
              key={idx}
              className="relative bg-slate-50 border border-slate-200 rounded-xl p-3.5 space-y-2 text-center hover:border-blue-300 transition-colors"
            >
              <div className="w-6 h-6 rounded-full bg-blue-600 text-white font-bold text-xs mx-auto flex items-center justify-center">
                {stepItem.step}
              </div>
              <div className="font-bold text-xs text-slate-900">{stepItem.label}</div>
              <div className="text-[11px] text-slate-500 leading-tight">{stepItem.detail}</div>

              {idx < demoSteps.length - 1 && (
                <div className="hidden lg:block absolute -right-3 top-1/2 -translate-y-1/2 z-10 text-slate-400">
                  <ChevronRight className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* 4. SEARCHABLE FAQ KNOWLEDGE BASE PREVIEW */}
      <section className="space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Explore Company Knowledge Base</h2>
            <p className="text-sm text-slate-500">Verified official answers for common customer questions</p>
          </div>

          {/* Search bar */}
          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search FAQs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-blue-500 shadow-sm"
            />
          </div>
        </div>

        {/* Category Pills */}
        <div className="flex items-center space-x-2 overflow-x-auto pb-2 no-scrollbar">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap transition-all ${
                selectedCategory === cat
                  ? 'bg-blue-600 text-white shadow-sm shadow-blue-600/20'
                  : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* FAQ Accordion List */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {faqs.map((faq) => (
            <div
              key={faq.id}
              className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-2 hover:border-blue-200 transition-all cursor-pointer"
              onClick={() => setExpandedFaq(expandedFaq === faq.id ? null : faq.id)}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="px-2.5 py-0.5 text-[11px] font-semibold bg-blue-50 text-blue-600 border border-blue-200/60 rounded-md">
                  {faq.category}
                </span>
                <span className="text-xs text-blue-600 font-medium hover:underline flex items-center gap-1">
                  Ask AI <ArrowRight className="w-3 h-3" />
                </span>
              </div>

              <h3 className="font-bold text-slate-900 text-base">{faq.question}</h3>
              
              <p className={`text-sm text-slate-600 leading-relaxed whitespace-pre-line ${expandedFaq === faq.id ? '' : 'line-clamp-2'}`}>
                {faq.answer}
              </p>

              <div className="pt-2 flex items-center justify-between text-xs text-slate-400">
                <span>Keywords: {faq.keywords.slice(0, 3).join(', ')}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onStartChat(faq.question);
                  }}
                  className="px-2.5 py-1 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
                >
                  Test in Chat
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

    </div>
  );
};
