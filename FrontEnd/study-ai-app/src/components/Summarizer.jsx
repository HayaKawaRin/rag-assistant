import React, { useState } from 'react';
import Sidebar from './Sidebar';
import { FileText, Sparkles } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const Summarizer = (props) => {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSummarize = async () => {
    const trimmed = text.trim();

    if (!trimmed) {
      setError('Please paste some text first.');
      setResult(null);
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch(`${API_BASE}/tools/summarize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: trimmed,
          length: 'medium',
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Failed to summarize text.');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-layout">
      <Sidebar {...props} activeView="summarizer" />

      <main className="main-content">
        <div className="page-header-inline">
          <FileText color="#10b981" />
          <h2>Document Summarizer</h2>
        </div>

        <p className="page-subtitle">
          Paste any text and get an instant AI summary.
        </p>

        <div className="summarizer-grid">
          <div className="input-box">
            <label htmlFor="summary-input">Paste your text here</label>
            <textarea
              id="summary-input"
              placeholder="Paste an article, textbook chapter..."
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
          </div>

          <div className="output-box">
            <label>AI Summary</label>

            {loading ? (
              <div className="empty-output">
                <FileText size={40} color="#94a3b8" />
                <p>Generating summary...</p>
              </div>
            ) : error ? (
              <div className="empty-output">
                <FileText size={40} color="#fca5a5" />
                <p style={{ color: '#dc2626' }}>{error}</p>
              </div>
            ) : result ? (
              <div className="summary-result">
                <h3>Summary</h3>
                <p>{result.summary}</p>

                {result.key_points?.length > 0 && (
                  <>
                    <h4>Key points</h4>
                    <ul>
                      {result.key_points.map((point, index) => (
                        <li key={index}>{point}</li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
            ) : (
              <div className="empty-output">
                <FileText size={40} color="#e2e8f0" />
                <p>Your AI-generated summary will appear here</p>
              </div>
            )}
          </div>
        </div>

        <button
          className="action-btn-green"
          onClick={handleSummarize}
          disabled={loading}
        >
          <Sparkles size={16} />
          {loading ? ' Summarizing...' : ' Summarize'}
        </button>
      </main>
    </div>
  );
};

export default Summarizer;