import React from 'react';
import { CheckCircle2, UserX, Clock, Star, Activity, PieChart } from 'lucide-react';
import type { AnalyticsOverview } from '../../types';

interface AnalyticsViewProps {
  analytics: AnalyticsOverview | null;
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({ analytics }) => {
  const data = analytics || {
    today_conversations: 1420,
    ai_resolution_rate: 83.1,
    escalated_tickets: 240,
    open_tickets: 18,
    avg_response_time_min: 1.5,
    customer_satisfaction_score: 4.8,
    total_faqs: 28,
    confidence_breakdown: { high: 75.0, medium: 17.0, low_escalated: 8.0 },
    top_topics: [
      { category: 'Password Reset', count: 480, percentage: 34 },
      { category: 'Refunds & Money Back', count: 320, percentage: 23 },
      { category: 'Payments & Cards', count: 260, percentage: 18 },
      { category: 'Orders & Tracking', count: 210, percentage: 15 },
      { category: 'Subscriptions', count: 150, percentage: 10 },
    ],
    daily_trends: [
      { day: 'Mon', queries: 210, resolved: 180, escalated: 30 },
      { day: 'Tue', queries: 240, resolved: 205, escalated: 35 },
      { day: 'Wed', queries: 280, resolved: 235, escalated: 45 },
      { day: 'Thu', queries: 260, resolved: 218, escalated: 42 },
      { day: 'Fri', queries: 290, resolved: 242, escalated: 48 },
      { day: 'Sat', queries: 160, resolved: 140, escalated: 20 },
      { day: 'Sun', queries: 120, resolved: 105, escalated: 15 },
    ],
  };

  const humanEscalationRate = Math.round((100 - data.ai_resolution_rate) * 10) / 10;

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Metrics Banner Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs font-bold text-slate-500 uppercase tracking-wider">
            <span>AI Resolution Rate</span>
            <div className="p-2 bg-emerald-50 text-emerald-600 rounded-xl">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-emerald-600">
            {data.ai_resolution_rate}%
          </div>
          <p className="text-xs text-slate-500">Resolved instantly via FAQ matching</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs font-bold text-slate-500 uppercase tracking-wider">
            <span>Human Handoff Rate</span>
            <div className="p-2 bg-amber-50 text-amber-600 rounded-xl">
              <UserX className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-amber-600">
            {humanEscalationRate}%
          </div>
          <p className="text-xs text-slate-500">Transferred to Support Ticket</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs font-bold text-slate-500 uppercase tracking-wider">
            <span>Avg Response Time</span>
            <div className="p-2 bg-blue-50 text-blue-600 rounded-xl">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-slate-900">
            {data.avg_response_time_min} <span className="text-sm font-normal text-slate-400">min</span>
          </div>
          <p className="text-xs text-emerald-600 font-semibold">Instant AI search response</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs font-bold text-slate-500 uppercase tracking-wider">
            <span>CSAT Score</span>
            <div className="p-2 bg-amber-50 text-amber-500 rounded-xl">
              <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-amber-500 flex items-baseline gap-1">
            {data.customer_satisfaction_score} <span className="text-sm font-normal text-slate-400">/ 5.0</span>
          </div>
          <p className="text-xs text-slate-500">Based on user ratings</p>
        </div>

      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Weekly Volume Trends */}
        <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-600" /> Weekly Conversation Volume Trends
          </h3>

          <div className="space-y-4 pt-2">
            {data.daily_trends.map((item) => {
              const maxVal = 300;
              const resWidth = (item.resolved / maxVal) * 100;
              const escWidth = (item.escalated / maxVal) * 100;

              return (
                <div key={item.day} className="space-y-1">
                  <div className="flex justify-between text-xs font-semibold text-slate-700">
                    <span>{item.day}</span>
                    <span className="text-slate-500">
                      Total: {item.queries} (Resolved: <strong className="text-emerald-600">{item.resolved}</strong> | Escalated: <strong className="text-amber-600">{item.escalated}</strong>)
                    </span>
                  </div>
                  <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden flex">
                    <div className="h-full bg-emerald-500" style={{ width: `${resWidth}%` }}></div>
                    <div className="h-full bg-amber-500" style={{ width: `${escWidth}%` }}></div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="flex items-center justify-center space-x-6 text-xs text-slate-500 pt-2 border-t border-slate-100">
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 bg-emerald-500 rounded-full"></span>
              <span>AI Grounded Resolutions</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 bg-amber-500 rounded-full"></span>
              <span>Human Ticket Escalations</span>
            </div>
          </div>
        </div>

        {/* Confidence Distribution */}
        <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <PieChart className="w-5 h-5 text-indigo-600" /> AI Grounding Confidence & Safety Distribution
          </h3>

          <div className="space-y-4 pt-2">
            <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 space-y-2">
              <div className="flex justify-between text-xs font-bold text-emerald-700">
                <span>High Confidence Match (80-100%)</span>
                <span>{data.confidence_breakdown.high}%</span>
              </div>
              <p className="text-xs text-slate-600">Direct grounded answer retrieved from verified company FAQs.</p>
            </div>

            <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 space-y-2">
              <div className="flex justify-between text-xs font-bold text-amber-700">
                <span>Medium Confidence (50-79%)</span>
                <span>{data.confidence_breakdown.medium}%</span>
              </div>
              <p className="text-xs text-slate-600">Ambiguous query triggering interactive clarification choice pills.</p>
            </div>

            <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 space-y-2">
              <div className="flex justify-between text-xs font-bold text-rose-700">
                <span>Low Confidence / Out-of-Bounds (&lt;50%)</span>
                <span>{data.confidence_breakdown.low_escalated}%</span>
              </div>
              <p className="text-xs text-slate-600">Zero-hallucination guardrail active. AI offers direct human support ticket handoff.</p>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
};
