import React, { useState } from 'react';
import Sidebar from './Sidebar';
import { Sparkles } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

const EssayHelper = (props) => {
  const [mode, setMode] = useState('feedback');
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleEssayAction = async () => {
    const trimmed = text.trim();

    if (!trimmed) {
      setError('Please paste your essay or enter a topic first.');
      setResult(null);
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch(`${API_BASE}/tools/essay`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mode,
          level: 'college',
          text: trimmed,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Failed to process essay request.');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  const getPlaceholder = () => {
    if (mode === 'outline') {
      return 'Enter your essay topic, for example: The impact of social media on students';
    }

    if (mode === 'improve') {
      return 'Paste your draft here so the AI can improve it...';
    }

    return 'Paste your essay or writing here for feedback...';
  };

  const getButtonText = () => {
    if (loading) return 'Processing...';
    if (mode === 'outline') return 'Generate Outline';
    if (mode === 'improve') return 'Improve Writing';
    return 'Get Feedback';
  };

  const getEmptyText = () => {
    if (mode === 'outline') return 'AI-generated outline will appear here';
    if (mode === 'improve') return 'Improved version of your text will appear here';
    return 'AI writing feedback will appear here';
  };

  return (
    <div className="dashboard-layout">
      <Sidebar {...props} activeView="essay" />

      <main className="main-content">
        <div className="page-header-inline">
          <div
            className="tool-icon-frame"
            style={{ background: '#ffedd5', padding: '10px', borderRadius: '8px' }}
          >
            <Sparkles color="#f97316" size={20} />
          </div>
          <h2>Essay Writing Helper</h2>
        </div>

        <p className="page-subtitle">
          Get AI feedback, generate outlines, brainstorm ideas, or improve your writing.
        </p>

        <div className="summarizer-grid">
          <div className="input-box">
            <label htmlFor="essay-mode">Mode</label>
            <select
              id="essay-mode"
              className="essay-mode-select"
              value={mode}
              onChange={(e) => {
                setMode(e.target.value);
                setResult(null);
                setError('');
              }}
            >
              <option value="feedback">Get Feedback</option>
              <option value="outline">Generate Outline</option>
              <option value="improve">Improve Writing</option>
            </select>

            <label htmlFor="essay-text">
              {mode === 'outline' ? 'Enter your topic' : 'Paste your essay text'}
            </label>

            <textarea
              id="essay-text"
              placeholder={getPlaceholder()}
              value={text}
              onChange={(e) => setText(e.target.value)}
            />

            <div className="characters-count">{text.length} characters</div>
          </div>

          <div className="output-box">
            <label>AI Response</label>

            {loading ? (
              <div className="empty-output">
                <Sparkles size={40} color="#fdba74" />
                <p>Generating AI response...</p>
              </div>
            ) : error ? (
              <div className="empty-output">
                <p style={{ color: '#dc2626' }}>{error}</p>
              </div>
            ) : result ? (
              <div className="summary-result">
                <h3>{result.title || 'Result'}</h3>
                <p>{result.main_text}</p>

                {result.items?.length > 0 && (
                  <>
                    <h4>Suggestions</h4>
                    <ul>
                      {result.items.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
            ) : (
              <div className="empty-output">
                <Sparkles size={40} color="#e2e8f0" />
                <p>{getEmptyText()}</p>
              </div>
            )}
          </div>
        </div>

        <button
          className="action-btn-red"
          onClick={handleEssayAction}
          disabled={loading}
        >
          <Sparkles size={16} />
          {getButtonText()}
        </button>
      </main>
    </div>
  );
};

export default EssayHelper;