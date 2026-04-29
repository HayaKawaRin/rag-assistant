import React, { useState } from 'react';
import { Mail, Lock, Eye, EyeOff, ArrowRight, GraduationCap, ChevronLeft, User } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const AuthCard = ({ setView, authMode, setAuthMode, onLogin }) => {
  const [showPassword, setShowPassword] = useState(false);
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const overlayStyle = {
    position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
    backgroundColor: '#ebf1f7', display: 'flex', justifyContent: 'center',
    alignItems: 'center', zIndex: 9999, fontFamily: 'sans-serif'
  };

  const cardStyle = {
    backgroundColor: '#323238', width: '440px', padding: '60px 45px',
    borderRadius: '40px', textAlign: 'center', color: 'white', boxSizing: 'border-box'
  };

  const inputContainer = {
    width: '100%', padding: '16px 45px', backgroundColor: 'rgba(255, 255, 255, 0.1)',
    border: '1px solid rgba(255, 255, 255, 0.2)', borderRadius: '15px',
    color: 'white', fontSize: '15px', outline: 'none', boxSizing: 'border-box'
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const endpoint = authMode === 'signup' ? '/auth/register' : '/auth/login';

      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Authentication failed');
      }

      onLogin(data);
    } catch (err) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={overlayStyle}>
      <div style={{ display: 'flex', flexDirection: 'column', width: '440px' }}>
        <button
          onClick={() => setView('landing')}
          style={{ background: 'none', border: 'none', color: '#8e9aaf', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', marginBottom: '20px', fontSize: '14px' }}
        >
          <ChevronLeft size={18} /> Back to Home
        </button>

        <div style={cardStyle}>
          <div style={{ width: '56px', height: '56px', backgroundColor: '#1d1b4b', borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 25px' }}>
            <GraduationCap size={30} color="white" />
          </div>

          <h2 style={{ fontSize: '28px', fontWeight: '700', margin: '0 0 10px' }}>
            {authMode === 'signin' ? 'Welcome Back' : 'Create Account'}
          </h2>

          <p style={{ color: '#8e9aaf', fontSize: '16px', marginBottom: '40px' }}>
            {authMode === 'signin' ? 'Sign in to continue' : 'Join our study community'}
          </p>

          <form onSubmit={handleSubmit}>
            {authMode === 'signup' && (
              <div style={{ position: 'relative', marginBottom: '15px' }}>
                <User size={20} style={{ position: 'absolute', left: '15px', top: '50%', transform: 'translateY(-50%)', color: '#8e9aaf' }} />
                <input
                  type="text"
                  placeholder="Full Name"
                  style={inputContainer}
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                />
              </div>
            )}

            <div style={{ position: 'relative', marginBottom: '15px' }}>
              <Mail size={20} style={{ position: 'absolute', left: '15px', top: '50%', transform: 'translateY(-50%)', color: '#8e9aaf' }} />
              <input
                type="email"
                placeholder="Email"
                style={inputContainer}
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div style={{ position: 'relative', marginBottom: '8px' }}>
              <Lock size={20} style={{ position: 'absolute', left: '15px', top: '50%', transform: 'translateY(-50%)', color: '#8e9aaf' }} />
              <input
                type={showPassword ? "text" : "password"}
                placeholder="Password"
                style={inputContainer}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{ position: 'absolute', right: '15px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: '#8e9aaf', cursor: 'pointer' }}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>

            {error && (
              <p style={{ color: '#ff8a8a', fontSize: '14px', marginBottom: '15px' }}>
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              style={{ width: '100%', padding: '18px', backgroundColor: '#9b6dff', color: 'white', border: 'none', borderRadius: '18px', fontWeight: '600', fontSize: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', cursor: 'pointer', marginTop: authMode === 'signup' ? '20px' : '0', opacity: loading ? 0.7 : 1 }}
            >
              {loading ? 'Please wait...' : (authMode === 'signin' ? 'Sign In' : 'Create Account')} <ArrowRight size={20} />
            </button>
          </form>

          <p style={{ marginTop: '35px', color: '#8e9aaf', fontSize: '15px' }}>
            {authMode === 'signin' ? "Don't have an account? " : "Already have an account? "}
            <span style={{ color: '#9b6dff', fontWeight: '700', cursor: 'pointer' }} onClick={() => setAuthMode(authMode === 'signin' ? 'signup' : 'signin')}>
              {authMode === 'signin' ? 'Sign Up' : 'Sign In'}
            </span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthCard;