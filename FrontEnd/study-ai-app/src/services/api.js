const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
console.log('API_BASE_URL =', API_BASE_URL);

if (!API_BASE_URL) {
  throw new Error('VITE_API_BASE_URL is missing');
}

function getToken() {
  return localStorage.getItem('study_ai_token');
}

export function saveAuthData(data) {
  if (data?.access_token) {
    localStorage.setItem('study_ai_token', data.access_token);
  }
  if (data?.user) {
    localStorage.setItem('study_ai_user', JSON.stringify(data.user));
  }
}

export function clearAuthData() {
  localStorage.removeItem('study_ai_token');
  localStorage.removeItem('study_ai_user');
}

function getAuthHeaders(includeJson = false) {
  const headers = {};
  if (includeJson) headers['Content-Type'] = 'application/json';

  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  return headers;
}

async function readResponse(response) {
  const text = await response.text();
  let data = null;

  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = null;
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
      data?.message ||
      text ||
      `Request failed with status ${response.status}`
    );
  }

  return data;
}

export async function loginUser(email, password) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: getAuthHeaders(true),
    body: JSON.stringify({ email, password }),
  });

  const data = await readResponse(response);
  saveAuthData(data);
  return data;
}

export async function registerUser(email, password) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: getAuthHeaders(true),
    body: JSON.stringify({ email, password }),
  });

  const data = await readResponse(response);
  saveAuthData(data);
  return data;
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  return readResponse(response);
}

export async function sendChatMessage(message, sessionId = null) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: getAuthHeaders(true),
    body: JSON.stringify({ message, session_id: sessionId }),
  });
  return readResponse(response);
}

export async function uploadPdf(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData,
  });
  return readResponse(response);
}

export async function getChatSessions() {
  const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
    headers: getAuthHeaders(),
  });
  return readResponse(response);
}

export async function getSessionMessages(sessionId) {
  const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}/messages`, {
    headers: getAuthHeaders(),
  });
  return readResponse(response);
}

export async function deleteChatSession(sessionId) {
  const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  return readResponse(response);
}

export async function getFlashcardDecks() {
  const response = await fetch(`${API_BASE_URL}/tools/flashcards`, {
    headers: getAuthHeaders(),
  });
  return readResponse(response);
}

export async function createFlashcardDeck(payload) {
  const response = await fetch(`${API_BASE_URL}/tools/flashcards`, {
    method: 'POST',
    headers: getAuthHeaders(true),
    body: JSON.stringify(payload),
  });
  return readResponse(response);
}

export async function deleteFlashcardDeck(deckId) {
  const response = await fetch(`${API_BASE_URL}/tools/flashcards/${deckId}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  return readResponse(response);
}

export async function deleteFlashcardCard(deckId, cardId) {
  const response = await fetch(`${API_BASE_URL}/tools/flashcards/${deckId}/cards/${cardId}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  return readResponse(response);
}