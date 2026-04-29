import React, { useEffect, useState } from 'react';
import Sidebar from './Sidebar';
import {
  MessageSquare,
  FileText,
  PenTool,
  Layers,
  ChevronRight,
  Clock,
  Sparkles,
  Trash2,
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL;

const getAuthHeaders = (includeJson = false) => {
  const token = localStorage.getItem('study_ai_token');
  const headers = {};

  if (includeJson) {
    headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
};

const Dashboard = ({ setView, onLogout, userInitial }) => {
  const [recentDecks, setRecentDecks] = useState([]);
  const [loadingDecks, setLoadingDecks] = useState(true);
  const [deckError, setDeckError] = useState('');

  const [recentChats, setRecentChats] = useState([]);
  const [loadingChats, setLoadingChats] = useState(true);
  const [chatError, setChatError] = useState('');

  const tools = [
    {
      id: 'chat',
      title: 'AI Chat Assistant',
      desc: 'Ask questions, get explanations, and learn interactively',
      icon: <MessageSquare size={20} color="#a855f7" />,
      bg: '#f3e8ff',
    },
    {
      id: 'summarizer',
      title: 'Document Summarizer',
      desc: 'Condense articles and papers into key takeaways',
      icon: <FileText size={20} color="#10b981" />,
      bg: '#d1fae5',
    },
    {
      id: 'essay',
      title: 'Essay Writing Helper',
      desc: 'Get feedback, outlines, and writing suggestions',
      icon: <PenTool size={20} color="#f97316" />,
      bg: '#ffedd5',
    },
    {
      id: 'flashcards',
      title: 'Flashcard Generator',
      desc: 'Auto-generate flashcards from your study material',
      icon: <Layers size={20} color="#ec4899" />,
      bg: '#fce7f3',
    },
  ];

  useEffect(() => {
  fetchRecentChats();
  fetchRecentDecks();
}, []);

const fetchRecentChats = async () => {
  try {
    setLoadingChats(true);
    setChatError('');

    const response = await fetch(`${API_BASE}/chat/sessions`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to load recent conversations.');
    }

    const data = await response.json();
    const sessions = Array.isArray(data) ? data : [];

    setRecentChats(sessions.slice(0, 5));
  } catch (err) {
    setChatError(err.message || 'Failed to load conversations.');
  } finally {
    setLoadingChats(false);
  }
};

const fetchRecentDecks = async () => {
  try {
    setLoadingDecks(true);
    setDeckError('');

    const response = await fetch(`${API_BASE}/tools/flashcards`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      throw new Error('Failed to load flashcard decks.');
    }

    const data = await response.json();
    const decks = Array.isArray(data.decks) ? data.decks : [];

    setRecentDecks(decks.slice(0, 5));
  } catch (err) {
    setDeckError(err.message || 'Failed to load flashcard decks.');
  } finally {
    setLoadingDecks(false);
  }
};

  const handleDeleteDeck = async (deckId) => {
    try {
      const response = await fetch(`${API_BASE}/tools/flashcards/${deckId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Failed to delete deck.');
      }

      setRecentDecks((prev) => prev.filter((deck) => deck.id !== deckId));
    } catch (err) {
      setDeckError(err.message || 'Failed to delete deck.');
    }
  };

  return (
    <div className="dashboard-layout">
      <Sidebar
        setView={setView}
        onLogout={onLogout}
        userInitial={userInitial}
        activeView="dashboard"
      />

      <main className="main-content">
        <header className="main-header">
          <h1>Welcome back! 👋</h1>
          <p>Choose a tool to start studying smarter.</p>
        </header>

        <div className="tools-grid">
          {tools.map((tool) => (
            <div
              key={tool.id}
              className="tool-card-ui"
              onClick={() => setView(tool.id)}
            >
              <div className="tool-icon-frame" style={{ background: tool.bg }}>
                {tool.icon}
              </div>
              <h3>{tool.title}</h3>
              <p>{tool.desc}</p>
              <div className="open-tool-link">
                Open <ChevronRight size={14} style={{ marginLeft: '2px' }} />
              </div>
            </div>
          ))}
        </div>

        <div className="activity-grid">
          
          <div className="activity-column">
            <div className="col-head"><Clock size={16} /> Recent Conversations</div>

            {loadingChats ? (
              <div className="empty-state-card">
                <MessageSquare size={32} color="#e2e8f0" style={{ marginBottom: '12px' }} />
                <p>Loading conversations...</p>
              </div>
            ) : recentChats.length === 0 ? (
              <div className="empty-state-card">
                <MessageSquare size={32} color="#e2e8f0" style={{ marginBottom: '12px' }} />
                <p>No conversations yet. Start a chat!</p>
              </div>
            ) : (
              <div className="dashboard-conversations-list">
                {recentChats.map((chat) => (
                  <div
                    key={chat.id}
                    className="dashboard-conversation-card"
                    onClick={() => setView('chat')}
                  >
                    <div className="dashboard-conversation-icon">
                      <MessageSquare size={16} />
                    </div>

                    <div className="dashboard-conversation-content">
                      <h4>{chat.title || `Conversation #${chat.id}`}</h4>
                      <p>
                        {chat.updated_at
                          ? `Updated: ${new Date(chat.updated_at).toLocaleString()}`
                          : `Session ID: ${chat.id}`}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {chatError && <p className="flashcard-error bottom-error">{chatError}</p>}
          </div>

          <div className="activity-column">
            <div className="col-head">
              <Layers size={16} /> Recent Flashcard Decks
            </div>

            {loadingDecks ? (
              <div className="empty-state-card">
                <Sparkles
                  size={32}
                  color="#e2e8f0"
                  style={{ marginBottom: '12px' }}
                />
                <p>Loading decks...</p>
              </div>
            ) : recentDecks.length === 0 ? (
              <div className="empty-state-card">
                <Sparkles
                  size={32}
                  color="#e2e8f0"
                  style={{ marginBottom: '12px' }}
                />
                <p>No flashcard decks yet. Create one!</p>
              </div>
            ) : (
              <div className="dashboard-decks-list">
                {recentDecks.map((deck) => (
                  <div key={deck.id} className="dashboard-deck-card">
                    <div
                      className="dashboard-deck-main"
                      onClick={() => setView('flashcards')}
                    >
                      <h4>{deck.deck_title}</h4>
                      <div className="dashboard-deck-meta">
                        <span className="deck-language-badge">{deck.language}</span>
                        <span className="deck-count-badge">
                          {deck.cards.length} cards
                        </span>
                      </div>
                    </div>

                    <button
                      className="dashboard-deck-delete"
                      onClick={() => handleDeleteDeck(deck.id)}
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {deckError && <p className="flashcard-error bottom-error">{deckError}</p>}
          </div>
        
        </div>
      </main>
    </div>
  );
};

export default Dashboard;