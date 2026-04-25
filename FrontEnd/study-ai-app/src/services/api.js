const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function getToken() {
  return localStorage.getItem('study_ai_token');
}

function getAuthHeaders(includeJson = false) {
  const headers = {};

  if (includeJson) {
    headers['Content-Type'] = 'application/json';
  }

  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
}

async function parseError(response, fallbackMessage) {
  const text = await response.text().catch(() => '');
  throw new Error(text || fallbackMessage);
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error("Health check failed");
  }
  return response.json();
}

export async function sendChatMessage(message, sessionId = null) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: getAuthHeaders(true),
    body: JSON.stringify({
      message,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    await parseError(response, `Failed to send message: ${response.status}`);
  }

  return response.json();
}

export async function uploadPdf(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData,
  });

  if (!response.ok) {
    await parseError(response, 'Upload failed');
  }

  return response.json();
}

export async function getChatSessions() {
  const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    await parseError(response, `Failed to load sessions: ${response.status}`);
  }

  return response.json();
}

export async function getSessionMessages(sessionId) {
  const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}/messages`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    await parseError(response, `Failed to load messages: ${response.status}`);
  }

  return response.json();
}

export async function deleteChatSession(sessionId) {
  const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    await parseError(response, `Failed to delete session: ${response.status}`);
  }

  return response.json();
}