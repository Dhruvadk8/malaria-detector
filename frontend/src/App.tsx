import { useState, useEffect } from 'react';
import { Navbar, type NavTab } from './components/Navbar';
import { DemoLauncherBar } from './components/DemoLauncherBar';
import { Home } from './components/Home';
import { ChatInterface } from './components/Customer/ChatInterface';
import { SupportTicketPage } from './components/Customer/SupportTicketPage';
import { AdminDashboard } from './components/Admin/AdminDashboard';
import type { ChatMessage, TicketResponse } from './types';
import { fetchTickets } from './services/api';
import { Sparkles, ShieldCheck } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<NavTab>('home');
  const [conversationId] = useState<string>(`conv_${Math.random().toString(36).substring(2, 9)}`);
  
  // Initial messages state
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'msg_welcome',
      sender: 'assistant',
      content: 'Hello! I am SupportAI, your intelligent customer support assistant. How can I help you with password reset, refunds, orders, shipping, payments, or your account today?',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      confidence: 1.0,
      confidence_level: 'HIGH',
    },
  ]);

  const [openTicketsCount, setOpenTicketsCount] = useState<number>(18);
  const [demoPrompt, setDemoPrompt] = useState<string | undefined>(undefined);
  const [ticketPageQuery, setTicketPageQuery] = useState<string>('');
  const [isTicketUnresolved, setIsTicketUnresolved] = useState<boolean>(false);

  useEffect(() => {
    loadTicketCount();
  }, [activeTab]);

  const loadTicketCount = async () => {
    try {
      const tickets = await fetchTickets();
      const openCount = tickets.filter((t: TicketResponse) => t.status === 'Open' || t.status === 'In Progress').length;
      setOpenTicketsCount(openCount);
    } catch (e) {
      console.warn('Ticket count load offline:', e);
    }
  };

  const handleRunDemo = (promptText: string) => {
    setActiveTab('chat');
    setDemoPrompt(promptText);
  };

  const handleOpenTicketWithQuery = (initialQuery?: string, unresolved: boolean = false) => {
    if (initialQuery) setTicketPageQuery(initialQuery);
    setIsTicketUnresolved(unresolved);
    setActiveTab('ticket');
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      
      {/* Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        openTicketsCount={openTicketsCount}
      />

      {/* Demo Launcher Quick Toolbar */}
      <DemoLauncherBar onRunDemo={handleRunDemo} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        
        {/* Banner shown on Chat view */}
        {activeTab === 'chat' && (
          <div className="mb-4 bg-gradient-to-r from-blue-900 via-blue-950 to-indigo-950 border border-blue-800 text-white rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-md">
            <div className="space-y-1 text-center sm:text-left">
              <h2 className="text-base sm:text-lg font-bold tracking-tight flex items-center gap-2 justify-center sm:justify-start">
                <Sparkles className="w-5 h-5 text-blue-400 animate-pulse" />
                SupportAI Grounded Workflow Demo
              </h2>
              <p className="text-xs text-blue-200">
                Customer Question → AI Answer → Unclear Query → Clarification → Unresolved Query → Human Support → Support Ticket
              </p>
            </div>

            <div className="flex items-center space-x-3 text-xs flex-shrink-0">
              <div className="flex items-center space-x-1.5 px-3 py-1.5 bg-blue-900/80 border border-blue-700/80 rounded-xl text-blue-200 font-semibold">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Zero Hallucinations Policy</span>
              </div>
            </div>
          </div>
        )}

        {/* Tab Route Views */}
        {activeTab === 'home' && (
          <Home
            onStartChat={(prompt) => {
              setActiveTab('chat');
              if (prompt) setDemoPrompt(prompt);
            }}
            onNavigateToTicket={() => handleOpenTicketWithQuery()}
            onNavigateToAdmin={() => setActiveTab('admin')}
          />
        )}

        {activeTab === 'chat' && (
          <ChatInterface
            conversationId={conversationId}
            messages={messages}
            setMessages={setMessages}
            onOpenTicketPage={(query) => handleOpenTicketWithQuery(query, true)}
            externalPrompt={demoPrompt}
            onClearExternalPrompt={() => setDemoPrompt(undefined)}
          />
        )}

        {activeTab === 'ticket' && (
          <SupportTicketPage
            initialQuery={ticketPageQuery}
            isUnresolved={isTicketUnresolved}
            onTicketSubmitted={() => loadTicketCount()}
            onGoToChat={() => setActiveTab('chat')}
            onGoToAdmin={() => setActiveTab('admin')}
          />
        )}

        {activeTab === 'admin' && <AdminDashboard />}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-5 text-center text-xs text-slate-500 space-y-1">
        <p className="font-semibold text-slate-700">SupportAI – AI-Powered Customer Support Chatbot</p>
        <p>Built for IEEE Hackathon Project Demonstration • Grounded FAQ Intelligence & Seamless Human Handoff</p>
      </footer>

    </div>
  );
}

export default App;
