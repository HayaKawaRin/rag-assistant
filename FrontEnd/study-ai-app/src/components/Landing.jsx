import React from 'react';
import { GraduationCap, ArrowRight, Sparkles, Zap, Shield, MessageSquare, FileText, PenTool, Layers } from 'lucide-react';

// Импорт твоих изображений из папки assets
import brainImg from '../assets/my-brain-image.png';
import aiChatImg from '../assets/ai-chat.png';
import summarizerImg from '../assets/summarizer.png';
import essayImg from '../assets/essay-writing-helper.png';
import flashcardImg from '../assets/flashcard-generator.png';

const Landing = ({ setView, setAuthMode }) => {
  return (
    <div className="landing-container">
      <div className="bg-glow"></div>
      
      {/* 1. HEADER */}
      <header className="landing-header">
        <div className="logo" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ background: '#1e1b4b', padding: '8px', borderRadius: '10px', display: 'flex' }}>
            <GraduationCap size={20} color="#a855f7" />
          </div>
          <span style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>StudyAI</span>
        </div>
        <button className="btn-primary" onClick={() => { setView('auth'); setAuthMode('signin'); }}>
          Get Started <ArrowRight size={16} />
        </button>
      </header>

      {/* 2. HERO SECTION */}
      <main className="hero-section">
        <div className="badge">
          <Sparkles size={14} color="#a855f7" />
          <span>AI-Powered Academic Tools for University Students</span>
        </div>
        <h1 className="hero-title">
          Study Smarter, <br />
          <span className="text-gradient">Not Harder</span>
        </h1>
        <p className="hero-description">
          Your AI-powered study companion that helps you chat with an AI tutor, 
          summarize documents, write better essays, and create flashcards — all in one place.
        </p>
        
        <button 
          className="btn-primary" 
          onClick={() => { setView('auth'); setAuthMode('signup'); }} 
          style={{ padding: '16px 32px', fontSize: '1.1rem', marginTop: '40px' }}
        >
          Start Learning Free <ArrowRight size={20} />
        </button>

        {/* Главное изображение мозга из твоих assets */}
        <div className="brain-image-container">
            <img src={brainImg} alt="AI Brain Academic" />
        </div>

        {/* Статистика под главным фото */}
        <div className="stats-grid">
          <div className="stat-card"><h3>Multi</h3><p>AI Models</p></div>
          <div className="stat-card"><h3>&lt;3s</h3><p>Response Time</p></div>
          <div className="stat-card"><h3>4+</h3><p>Tools</p></div>
          <div className="stat-card"><h3>✓</h3><p>Free to Start</p></div>
        </div>
      </main>

      {/* 3. TOOLS SECTION (Everything You Need to Excel) */}
      <section className="section-container">
        <h2 className="section-title">Everything You Need to <span className="text-gradient-cyan">Excel</span></h2>
        <p style={{ textAlign: 'center', color: '#94a3b8', marginTop: '-40px', marginBottom: '60px' }}>
          Four powerful AI tools designed specifically for university students
        </p>
        
        <div className="features-grid">
          {/* AI Chat */}
          <div className="feature-card">
            <div className="icon-box purple"><MessageSquare size={20} /></div>
            <h3>AI Chat Assistant</h3>
            <p>Ask any academic question and get detailed, well-structured explanations powered by AI.</p>
            <img src={aiChatImg} alt="AI Chat Preview" className="feature-preview-img" />
          </div>

          {/* Summarizer */}
          <div className="feature-card">
            <div className="icon-box green"><FileText size={20} /></div>
            <h3>Document Summarizer</h3>
            <p>Paste lengthy articles, textbook chapters, or research papers and get concise summaries.</p>
            <img src={summarizerImg} alt="Summarizer Preview" className="feature-preview-img" />
          </div>

          {/* Essay Helper */}
          <div className="feature-card">
            <div className="icon-box orange"><PenTool size={20} /></div>
            <h3>Essay Writing Helper</h3>
            <p>Get AI-powered feedback on your essays, brainstorm ideas, and generate outlines.</p>
            <img src={essayImg} alt="Essay Helper Preview" className="feature-preview-img" />
          </div>

          {/* Flashcards */}
          <div className="feature-card">
            <div className="icon-box pink"><Layers size={20} /></div>
            <h3>Flashcard Generator</h3>
            <p>Transform study material into interactive flashcards automatically for better memory.</p>
            <img src={flashcardImg} alt="Flashcards Preview" className="feature-preview-img" />
          </div>
        </div>
      </section>

      {/* 4. WHY US SECTION */}
<section className="section-container">
  <h2 className="section-title" style={{ marginBottom: '20px' }}>
    Why Students <span className="text-gradient-purple">Love</span> StudyAI
  </h2>
  
  <div className="why-us-grid">
    <div className="stat-card-simple">
      <div className="icon-box purple"><Zap size={20} /></div>
      <h4>Instant Answers</h4>
      <p>Get detailed explanations in seconds, not hours.</p>
    </div>

    <div className="stat-card-simple">
      <div className="icon-box green"><Sparkles size={20} /></div>
      <h4>AI-Powered</h4>
      <p>Leveraging cutting-edge models for accuracy.</p>
    </div>

    <div className="stat-card-simple">
      <div className="icon-box pink"><Shield size={20} /></div>
      <h4>Private & Secure</h4>
      <p>Your study data is always encrypted and private.</p>
    </div>
  </div>
</section>

      {/* 5. CALL TO ACTION (Исправлено центрирование) */}
      <section className="section-container" style={{ display: 'flex', justifyContent: 'center' }}>
        <div className="cta-box">
          <h2 style={{ fontSize: '2.5rem', fontWeight: '800', marginBottom: '20px', color: 'white' }}>
            Ready to Ace Your Studies?
          </h2>
          <p style={{ color: '#94a3b8', fontSize: '1.1rem', marginBottom: '40px', maxWidth: '600px' }}>
            Join thousands of students already using AI to study more effectively.
          </p>
          <button 
            className="btn-primary" 
            onClick={() => setView('auth')} 
            style={{ padding: '14px 40px', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '10px' }}
          >
            Get Started for Free <ArrowRight size={18} />
          </button>
        </div>
      </section>

      {/* 6. FOOTER */}
      <footer className="footer-simple">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <GraduationCap size={18} /> StudyAI 2026
        </div>
        <div>AI-Powered Academic Assistant</div>
      </footer>
    </div>
  );
};

export default Landing;