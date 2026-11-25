import React, { useState, useEffect } from 'react';
import { Search, BookOpen, ChevronDown, ChevronUp } from 'lucide-react';
import { fetchFAQs } from '../../services/api';
import type { FAQItem } from '../../types';

export const CustomerKB: React.FC = () => {
  const [faqs, setFaqs] = useState<FAQItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [expandedFaqId, setExpandedFaqId] = useState<string | null>(null);

  const categories = [
    'All',
    'Account',
    'Billing',
    'Payments',
    'Orders',
    'Shipping',
    'Refunds',
    'Password',
    'Security',
    'Subscription',
    'Technical Support',
  ];

  useEffect(() => {
    loadFAQs();
  }, [selectedCategory, searchQuery]);

  const loadFAQs = async () => {
    setLoading(true);
    try {
      const data = await fetchFAQs(
        selectedCategory === 'All' ? undefined : selectedCategory,
        searchQuery ? searchQuery : undefined
      );
      setFaqs(data);
    } catch (err) {
      console.error('Error fetching FAQs:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fadeIn pb-12">
      
      {/* KB Hero Header */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 text-center space-y-4 shadow-xl">
        <div className="w-12 h-12 bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 rounded-2xl flex items-center justify-center mx-auto shadow-md">
          <BookOpen className="w-6 h-6" />
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          TechNova Support Knowledge Base
        </h1>
        <p className="text-sm text-slate-300 max-w-2xl mx-auto">
          Explore approved articles, guides, and policies used by SupportAI to deliver accurate, grounded answers.
        </p>

        {/* Search Bar */}
        <div className="max-w-xl mx-auto relative pt-2">
          <Search className="w-5 h-5 text-slate-400 absolute left-4 top-5" />
          <input
            type="text"
            placeholder="Search FAQs by keywords (e.g. password, refund, payment)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-11 pr-4 py-3 bg-slate-950 border border-slate-700 focus:border-indigo-500 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none shadow-lg"
          />
        </div>
      </div>

      {/* Category Filter Pills */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-2 no-scrollbar">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition border ${
              selectedCategory === cat
                ? 'bg-indigo-600 border-indigo-500 text-white shadow-md shadow-indigo-600/30'
                : 'bg-slate-800/80 border-slate-700/80 text-slate-300 hover:bg-slate-700 hover:text-white'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* FAQ Card Grid */}
      {loading ? (
        <div className="text-center py-12 text-slate-400 text-sm">
          Loading Knowledge Base articles...
        </div>
      ) : faqs.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center text-slate-400 text-sm">
          No Knowledge Base articles found matching your criteria.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {faqs.map((faq) => {
            const isExpanded = expandedFaqId === faq.id;
            return (
              <div
                key={faq.id}
                onClick={() => setExpandedFaqId(isExpanded ? null : faq.id)}
                className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-2xl p-5 cursor-pointer transition shadow-lg space-y-3"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center space-x-2">
                    <span className="px-2.5 py-0.5 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-md text-[11px] font-semibold">
                      {faq.category}
                    </span>
                    <span className="text-xs text-slate-500 font-mono">{faq.id}</span>
                  </div>
                  {isExpanded ? (
                    <ChevronUp className="w-4 h-4 text-slate-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-slate-400" />
                  )}
                </div>

                <h3 className="text-base font-bold text-white">{faq.question}</h3>

                <p className={`text-sm text-slate-300 leading-relaxed ${isExpanded ? '' : 'line-clamp-2'}`}>
                  {faq.answer}
                </p>

                {faq.keywords && faq.keywords.length > 0 && (
                  <div className="flex flex-wrap items-center gap-1.5 pt-2">
                    {faq.keywords.map((kw, idx) => (
                      <span key={idx} className="px-2 py-0.5 bg-slate-800 text-slate-400 rounded text-[10px]">
                        #{kw}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

    </div>
  );
};
