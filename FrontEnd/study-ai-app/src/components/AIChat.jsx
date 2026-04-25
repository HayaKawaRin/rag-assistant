import React, { useEffect, useRef, useState } from 'react';

import Sidebar from './Sidebar';
import { Plus, BotMessageSquare, SendHorizonal, Menu } from 'lucide-react';
import {
  sendChatMessage,
  uploadPdf,
  getChatSessions,
  getSessionMessages,
  deleteChatSession,
} from '../services/api';

const defaultAssistantMessage = {
  role: 'assistant',
  text: 'Hello! Ask me any academic question.',
  sources: [],
};

const AIChat = ({ setView, onLogout, userInitial }) => {
  const [messages, setMessages] = useState([defaultAssistantMessage]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploadInfo, setUploadInfo] = useState(null);
  const [uploading, setUploading] = useState(false);

  const [sessionId, setSessionId] = useState(null);
  const [chatSessions, setChatSessions] = useState([]);
  const [sessionsLoading, setSessionsLoading] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const exampleQuestions = [
    'Explain quantum entanglement simply',
    'Help me understand Big O notation',
    'What caused the French Revolution?',
    'Explain the Krebs cycle step by step',
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]); // useRef + useEffect autoscroll is a common React chat pattern. [web:772][web:786]

  const loadSessions = async () => {
    try {
      setSessionsLoading(true);
      const sessions = await getChatSessions();
      setChatSessions(sessions);
    } catch (error) {
      console.error('Failed to load chat sessions:', error);
    } finally {
      setSessionsLoading(false);
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessionById = async (selectedSessionId) => {
    try {
      setLoading(true);
      const sessionMessages = await getSessionMessages(selectedSessionId);

      if (!sessionMessages || sessionMessages.length === 0) {
        setMessages([defaultAssistantMessage]);
        setSessionId(selectedSessionId);
        return;
      }

      const mappedMessages = sessionMessages.map((msg) => ({
        role: msg.role,
        text: msg.content,
        sources: [],
      }));

      setMessages(mappedMessages);
      setSessionId(selectedSessionId);
    } catch (error) {
      console.error('Failed to load session messages:', error);
      setMessages([
        defaultAssistantMessage,
        {
          role: 'assistant',
          text: 'Error: could not load previous chat history.',
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async (rawText) => {
    const text = rawText.trim();
    if (!text || loading) return;

    setMessages((prev) => [
      ...prev,
      {
        role: 'user',
        text,
        sources: [],
      },
    ]);

    setInput('');
    setLoading(true);

    try {
      const data = await sendChatMessage(text, sessionId);

      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      const assistantText = data.answer || 'No answer returned from backend.';

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: assistantText,
          sources: data.sources || [],
        },
      ]);

      await loadSessions();
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: `Error: ${error.message || 'could not connect to backend.'}`,
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadInfo(null);

    try {
      const data = await uploadPdf(file);
      setUploadInfo(data);

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: `PDF uploaded successfully: ${data.filename}. Pages: ${data.page_count}, text length: ${data.text_length}, chunks: ${data.chunk_count}`,
          sources: [],
        },
      ]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: `Error: ${error.message || 'PDF upload failed.'}`,
          sources: [],
        },
      ]);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const resetChat = () => {
    setMessages([defaultAssistantMessage]);
    setUploadInfo(null);
    setInput('');
    setSessionId(null);
  };

  const formatSessionTitle = (title) => {
    if (!title) return 'New Chat';
    return title.length > 32 ? `${title.slice(0, 32)}...` : title;
  };

  const formatDateTime = (isoString) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    if (Number.isNaN(date.getTime())) return isoString;
    return date.toLocaleString();
  };

  return (
    <div className="dashboard-layout chat-view-layout">
      <Sidebar
        setView={setView}
        onLogout={onLogout}
        userInitial={userInitial}
        activeView="chat"
      />

      <>
        <div
          onClick={() => setHistoryOpen(false)}
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.35)',
            opacity: historyOpen ? 1 : 0,
            pointerEvents: historyOpen ? 'auto' : 'none',
            transition: 'opacity 0.28s ease',
            zIndex: 40,
          }}
        />

        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '320px',
            height: '100vh',
            background: '#ffffff',
            borderRight: '1px solid #e5e7eb',
            padding: '16px',
            zIndex: 50,
            overflowY: 'auto',
            boxShadow: '0 10px 30px rgba(0,0,0,0.12)',
            transform: historyOpen ? 'translateX(0)' : 'translateX(-100%)',
            opacity: historyOpen ? 1 : 0,
            pointerEvents: historyOpen ? 'auto' : 'none',
            transition: 'transform 0.32s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.24s ease',
          }}
        >
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '14px',
            }}
          >
            <h3 style={{ margin: 0, color: '#111827' }}>Chat History</h3>

            <button
              onClick={() => setHistoryOpen(false)}
              style={{
                border: '1px solid #e5e7eb',
                background: '#fff',
                borderRadius: '10px',
                padding: '8px 10px',
                cursor: 'pointer',
                transition: 'background 0.2s ease, transform 0.2s ease',
                color: '#dc2626',
              }}
            >
              ✕
            </button>
          </div>

          <button
            onClick={() => {
              resetChat();
              setHistoryOpen(false);
            }}
            style={{
              width: '100%',
              marginBottom: '12px',
              border: 'none',
              background: '#ede9fe',
              color: '#4c1d95',
              padding: '10px 12px',
              borderRadius: '10px',
              cursor: 'pointer',
              fontWeight: 600,
            }}
          >
            + New Chat
          </button>

          {sessionsLoading ? (
            <p style={{ color: '#6b7280' }}>Loading sessions...</p>
          ) : chatSessions.length === 0 ? (
            <p style={{ color: '#6b7280' }}>No saved chats yet.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {chatSessions.map((session) => (
                <div
                  key={session.id}
                  style={{ display: 'flex', gap: '8px', alignItems: 'stretch' }}
                >
                  <button
                    onClick={() => {
                      loadSessionById(session.id);
                      setHistoryOpen(false);
                    }}
                    style={{
                      flex: 1,
                      textAlign: 'left',
                      padding: '10px 12px',
                      borderRadius: '10px',
                      border: sessionId === session.id ? '1px solid #8b5cf6' : '1px solid #e5e7eb',
                      background: sessionId === session.id ? '#f5f3ff' : '#fff',
                      cursor: 'pointer',
                    }}
                  >
                    <div
                      style={{
                        fontWeight: 600,
                        marginBottom: '4px',
                        color: '#111827',
                      }}
                    >
                      {formatSessionTitle(session.title)}
                    </div>
                    <div style={{ fontSize: '12px', color: '#6b7280' }}>
                      {formatDateTime(session.created_at)}
                    </div>
                  </button>

                  <button
                    onClick={async () => {
                      try {
                        await deleteChatSession(session.id);
                        if (sessionId === session.id) {
                          resetChat();
                        }
                        await loadSessions();
                      } catch (error) {
                        console.error(error);
                        alert(error.message);
                      }
                    }}
                    style={{
                      border: '1px solid #e5e7eb',
                      background: '#fff',
                      color: '#dc2626',
                      borderRadius: '10px',
                      width: '40px',
                      cursor: 'pointer',
                      fontWeight: 700,
                    }}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </>

      <main className="main-content chat-page-content">
        <div
          style={{
            width: '100%',
            maxWidth: '1200px',
            margin: '0 auto',
          }}
        >
          <section>
            <div
              className="chat-top-actions"
              style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginBottom: '16px' }}
            >
              <button className="new-chat-action-btn" onClick={resetChat}>
                <Plus size={18} /> New Chat
              </button>

              <button
                className="new-chat-action-btn"
                onClick={() => setHistoryOpen(true)}
              >
                <Menu size={18} /> History
              </button>

              <label className="new-chat-action-btn" style={{ cursor: 'pointer' }}>
                Upload PDF
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="application/pdf"
                  style={{ display: 'none' }}
                  onChange={handleFileChange}
                />
              </label>
            </div>

            <div className="chat-welcome-container">
              <div className="bot-welcome-frame">
                <div className="bot-icon-large-frame">
                  <BotMessageSquare size={48} color="white" />
                </div>
                <h2>AI Chat Assistant</h2>
                <p>Ask any academic question — from calculus to chemistry, history to programming.</p>
              </div>

              <div className="example-questions-grid">
                {exampleQuestions.map((question, index) => (
                  <button
                    key={index}
                    className="example-question-card"
                    onClick={() => handleSend(question)}
                    disabled={loading}
                  >
                    {question}
                  </button>
                ))}
              </div>

              {uploading && (
                <div
                  style={{
                    width: '100%',
                    maxWidth: '900px',
                    margin: '20px auto',
                    padding: '14px 16px',
                    background: '#f8fafc',
                    border: '1px solid #e5e7eb',
                    borderRadius: '14px',
                    textAlign: 'left',
                  }}
                >
                  Uploading PDF...
                </div>
              )}

              {uploadInfo && (
                <div
                  style={{
                    width: '100%',
                    maxWidth: '900px',
                    margin: '20px auto',
                    padding: '16px',
                    background: '#f8fafc',
                    border: '1px solid #e5e7eb',
                    borderRadius: '14px',
                    textAlign: 'left',
                  }}
                >
                  <h3 style={{ marginBottom: '8px' }}>Uploaded document</h3>
                  <p><strong>File:</strong> {uploadInfo.filename}</p>
                  <p><strong>Pages:</strong> {uploadInfo.page_count}</p>
                  <p><strong>Text length:</strong> {uploadInfo.text_length}</p>
                  {uploadInfo.chunk_count !== undefined && (
                    <p><strong>Chunks:</strong> {uploadInfo.chunk_count}</p>
                  )}
                  <p><strong>Preview:</strong> {uploadInfo.preview || 'No text extracted'}</p>
                </div>
              )}

              <div style={{ width: '100%', maxWidth: '900px', margin: '24px auto' }}>
                {messages.map((msg, index) => (
                  <div
                    key={index}
                    style={{
                      marginBottom: '12px',
                      padding: '14px 16px',
                      borderRadius: '14px',
                      background: msg.role === 'user' ? '#ede9fe' : '#f8fafc',
                      border: '1px solid #e5e7eb',
                      textAlign: 'left',
                      whiteSpace: 'pre-wrap',
                    }}
                  >
                    <strong>{msg.role === 'user' ? 'You' : 'Assistant'}:</strong> {msg.text}
                  </div>
                ))}

                {loading && (
                  <div
                    style={{
                      marginBottom: '12px',
                      padding: '14px 16px',
                      borderRadius: '14px',
                      background: '#f8fafc',
                      border: '1px solid #e5e7eb',
                      textAlign: 'left',
                    }}
                  >
                    <strong>Assistant:</strong> Thinking...
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            </div>

            <div className="chat-input-sticky-bottom">
              <div className="chat-input-wrapper-frame">
                <input
                  type="text"
                  placeholder="Ask any academic question..."
                  className="chat-input-field"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleSend(input);
                    }
                  }}
                  disabled={loading}
                />
                <button
                  className="chat-send-action-btn"
                  onClick={() => handleSend(input)}
                  disabled={loading}
                >
                  <SendHorizonal size={20} color="white" />
                </button>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default AIChat;