const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

export class ApiError extends Error {
  constructor({ status, code, message, details }) {
    super(message || 'Request failed');
    this.name = 'ApiError';
    this.status = status;
    this.code = code || 'UNKNOWN_ERROR';
    this.details = details;
  }
}

async function parseResponse(response) {
  const contentType = response.headers.get('content-type') || '';
  const isJson = contentType.includes('application/json');
  const body = isJson ? await response.json().catch(() => null) : await response.text();

  if (!response.ok) {
    throw new ApiError({
      status: response.status,
      code: body?.code,
      message: body?.message || response.statusText || 'Request failed',
      details: body?.details,
    });
  }

  return body;
}

async function request(path, options) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  return parseResponse(response);
}

export const apiClient = {
  getEntries: () => request('/entries'),
  getStats: () => request('/stats'),
  getGoal: () => request('/goal'),
  createEntry: (payload) =>
    request('/entries', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
  updateEntry: (id, payload) =>
    request(`/entries/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
  deleteEntry: (id) =>
    request(`/entries/${id}`, {
      method: 'DELETE',
    }),
  updateGoal: (payload) =>
    request('/goal', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
  exportCsv: () => request('/entries/export.csv'),
};
