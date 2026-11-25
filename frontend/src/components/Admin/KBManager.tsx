import React, { useState, useEffect } from 'react';
import { BookOpen, Plus, Search, Edit2, Trash2, Save, X } from 'lucide-react';
import { fetchFAQs, createFAQ, updateFAQ, deleteFAQ } from '../../services/api';
import type { FAQItem } from '../../types';

interface KBManagerProps {
  onRefresh: () => void;
}

export const KBManager: React.FC<KBManagerProps> = ({ onRefresh }) => {
  const [faqs, setFaqs] = useState<FAQItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  // Add / Edit Modal State
  const [showModal, setShowModal] = useState(false);
  const [editingFaq, setEditingFaq] = useState<FAQItem | null>(null);

  const [formCategory, setFormCategory] = useState('Password Reset');
  const [formQuestion, setFormQuestion] = useState('');
  const [formAnswer, setFormAnswer] = useState('');
  const [formKeywords, setFormKeywords] = useState('');

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
      console.error('Failed to load FAQs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenAdd = () => {
    setEditingFaq(null);
    setFormCategory('Password Reset');
    setFormQuestion('');
    setFormAnswer('');
    setFormKeywords('');
    setShowModal(true);
  };

  const handleOpenEdit = (faq: FAQItem) => {
    setEditingFaq(faq);
    setFormCategory(faq.category);
    setFormQuestion(faq.question);
    setFormAnswer(faq.answer);
    setFormKeywords(faq.keywords ? faq.keywords.join(', ') : '');
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this FAQ entry from the Knowledge Base?')) {
      await deleteFAQ(id);
      loadFAQs();
      onRefresh();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formQuestion.trim() || !formAnswer.trim()) return;

    const kwArray = formKeywords
      .split(',')
      .map((k) => k.trim())
      .filter(Boolean);

    if (editingFaq) {
      await updateFAQ(editingFaq.id, {
        category: formCategory,
        question: formQuestion,
        answer: formAnswer,
        keywords: kwArray,
      });
    } else {
      await createFAQ({
        category: formCategory,
        question: formQuestion,
        answer: formAnswer,
        keywords: kwArray,
      });
    }

    setShowModal(false);
    loadFAQs();
    onRefresh();
  };

  return (
    <div className="space-y-4">
      
      {/* Header & Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-white border border-slate-200 p-4 rounded-2xl shadow-sm">
        <div className="flex items-center space-x-3">
          <BookOpen className="w-5 h-5 text-blue-600" />
          <span className="text-base font-bold text-slate-900">Knowledge Base Article Manager</span>
          <span className="px-2.5 py-0.5 bg-blue-50 text-blue-700 rounded-lg text-xs font-bold border border-blue-200">
            {faqs.length} FAQs
          </span>
        </div>

        <button
          onClick={handleOpenAdd}
          className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl transition flex items-center space-x-1.5 shadow-md shadow-blue-600/20"
        >
          <Plus className="w-4 h-4" />
          <span>Add New FAQ</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="relative sm:col-span-2">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search FAQs by question, answer, or keywords..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-blue-500 shadow-sm"
          />
        </div>

        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs font-semibold text-slate-800 focus:outline-none focus:border-blue-500 shadow-sm"
        >
          {categories.map((c) => (
            <option key={c} value={c}>
              Category: {c}
            </option>
          ))}
        </select>
      </div>

      {/* FAQ Table */}
      <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-600 font-bold uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="px-4 py-3.5">ID</th>
                <th className="px-4 py-3.5">Category</th>
                <th className="px-4 py-3.5">Question</th>
                <th className="px-4 py-3.5">Grounded Answer</th>
                <th className="px-4 py-3.5">Keywords</th>
                <th className="px-4 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate-400">Loading Knowledge Base...</td>
                </tr>
              ) : faqs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate-400">No FAQ articles found.</td>
                </tr>
              ) : (
                faqs.map((f) => (
                  <tr key={f.id} className="hover:bg-slate-50/80 transition">
                    <td className="px-4 py-3 font-mono font-bold text-blue-600">{f.id}</td>
                    <td className="px-4 py-3">
                      <span className="px-2.5 py-0.5 bg-blue-50 text-blue-700 border border-blue-200 rounded-md font-semibold text-[11px]">
                        {f.category}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-bold text-slate-900 max-w-xs">{f.question}</td>
                    <td className="px-4 py-3 max-w-sm truncate text-slate-600">{f.answer}</td>
                    <td className="px-4 py-3 max-w-xs truncate text-slate-400 font-mono text-[11px]">
                      {f.keywords ? f.keywords.join(', ') : ''}
                    </td>
                    <td className="px-4 py-3 text-right space-x-2">
                      <button
                        onClick={() => handleOpenEdit(f)}
                        className="p-1.5 text-slate-500 hover:text-blue-600 hover:bg-slate-100 rounded-lg transition"
                        title="Edit FAQ"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(f.id)}
                        className="p-1.5 text-slate-500 hover:text-rose-600 hover:bg-slate-100 rounded-lg transition"
                        title="Delete FAQ"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add / Edit FAQ Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white border border-slate-200 rounded-3xl max-w-lg w-full p-6 sm:p-8 shadow-2xl space-y-4">
            
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-lg font-bold text-slate-900">
                {editingFaq ? `Edit FAQ (${editingFaq.id})` : 'Add New FAQ Entry'}
              </h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4 text-xs">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Category</label>
                <select
                  value={formCategory}
                  onChange={(e) => setFormCategory(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:border-blue-500"
                >
                  {categories.filter((c) => c !== 'All').map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Question *</label>
                <input
                  type="text"
                  required
                  value={formQuestion}
                  onChange={(e) => setFormQuestion(e.target.value)}
                  placeholder="e.g. How do I reset my password?"
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Answer *</label>
                <textarea
                  rows={4}
                  required
                  value={formAnswer}
                  onChange={(e) => setFormAnswer(e.target.value)}
                  placeholder="Grounded company answer content..."
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Keywords (Comma separated)</label>
                <input
                  type="text"
                  value={formKeywords}
                  onChange={(e) => setFormKeywords(e.target.value)}
                  placeholder="e.g. password, reset, login, account"
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-slate-100 text-slate-700 font-semibold rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl flex items-center space-x-1.5 shadow-md shadow-blue-600/20"
                >
                  <Save className="w-4 h-4" />
                  <span>Save FAQ Entry</span>
                </button>
              </div>
            </form>

          </div>
        </div>
      )}

    </div>
  );
};
