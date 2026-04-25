import React, { useState } from 'react';
import { LayoutGrid, MessageSquare, FileText, PenTool, Layers, LogOut } from 'lucide-react';

const Sidebar = ({ setView, onLogout, userInitial, activeView }) => {
  const [showLogout, setShowLogout] = useState(false);

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo-icon-wrap">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>
        </div>
        <span className="logo-text">StudyAI</span>
      </div>
      
      <nav className="sidebar-nav">
        <button onClick={() => setView('dashboard')} className={`nav-item ${activeView === 'dashboard' ? 'active' : ''}`}><LayoutGrid size={18} /> Dashboard</button>
        <button onClick={() => setView('chat')} className={`nav-item ${activeView === 'chat' ? 'active' : ''}`}><MessageSquare size={18} /> AI Chat</button>
        <button onClick={() => setView('summarizer')} className={`nav-item ${activeView === 'summarizer' ? 'active' : ''}`}><FileText size={18} /> Summarizer</button>
        <button onClick={() => setView('essay')} className={`nav-item ${activeView === 'essay' ? 'active' : ''}`}><PenTool size={18} /> Essay Helper</button>
        <button onClick={() => setView('flashcards')} className={`nav-item ${activeView === 'flashcards' ? 'active' : ''}`}><Layers size={18} /> Flashcards</button>
      </nav>

      <div className="sidebar-footer">
        {showLogout && (
          <div className="logout-popover">
            <button className="logout-btn" onClick={onLogout}>
              <LogOut size={16} /> Log out
            </button>
          </div>
        )}
        <div className="user-profile-layout" onClick={() => setShowLogout(!showLogout)}>
          <div className="user-avatar-circle">{userInitial}</div>
          <span className="user-name-text">Account</span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;