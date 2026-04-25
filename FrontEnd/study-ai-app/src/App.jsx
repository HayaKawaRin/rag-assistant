import React, { useState, useEffect } from 'react';
import Landing from './components/Landing';
import AuthCard from './components/AuthCard';
import Dashboard from './components/Dashboard';
import AIChat from './components/AIChat';
import Summarizer from './components/Summarizer';
import EssayHelper from './components/EssayHelper';
import Flashcards from './components/Flashcards';
import './index.css';

function App() {
  const [view, setView] = useState(() => localStorage.getItem('study_ai_view') || 'landing');
  const [token, setToken] = useState(() => localStorage.getItem('study_ai_token') || '');
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem('study_ai_user');
    return raw ? JSON.parse(raw) : null;
  });
  const [authMode, setAuthMode] = useState('signin');

  useEffect(() => {
    localStorage.setItem('study_ai_view', view);
  }, [view]);

  useEffect(() => {
    if (token) {
      localStorage.setItem('study_ai_token', token);
    } else {
      localStorage.removeItem('study_ai_token');
    }

    if (user) {
      localStorage.setItem('study_ai_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('study_ai_user');
    }
  }, [token, user]);

  const handleLogin = (authData) => {
    setToken(authData.access_token);
    setUser(authData.user);
    setView('dashboard');
  };

  const handleLogout = () => {
    localStorage.removeItem('study_ai_token');
    localStorage.removeItem('study_ai_user');
    localStorage.removeItem('study_ai_view');
    setToken('');
    setUser(null);
    setView('landing');
  };

  const commonProps = {
    setView,
    onLogout: handleLogout,
    token,
    currentUser: user,
    userInitial: user?.email?.charAt(0).toUpperCase() || 'S',
  };

  const renderView = () => {
    switch (view) {
      case 'landing':
        return <Landing setView={setView} setAuthMode={setAuthMode} />;

      case 'auth':
        return (
          <AuthCard
            setView={setView}
            authMode={authMode}
            setAuthMode={setAuthMode}
            onLogin={handleLogin}
          />
        );

      case 'dashboard':
        return <Dashboard {...commonProps} />;
      case 'chat':
        return <AIChat {...commonProps} />;
      case 'summarizer':
        return <Summarizer {...commonProps} />;
      case 'essay':
        return <EssayHelper {...commonProps} />;
      case 'flashcards':
        return <Flashcards {...commonProps} />;
      default:
        return <Landing setView={setView} setAuthMode={setAuthMode} />;
    }
  };

  return <div className="app-root">{renderView()}</div>;
}

export default App;