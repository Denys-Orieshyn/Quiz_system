// ============================================================
// api.js — усі запити до Backend FastAPI
// ============================================================

const API = 'http://localhost:8000';

// ── Базовий запит ─────────────────────────────────────────────
async function request(method, path, body = null, auth = true) {
    const headers = { 'Content-Type': 'application/json' };

    if (auth) {
        const token = Auth.getToken();
        if (!token) { Auth.logout(); return null; }
        headers['Authorization'] = `Bearer ${token}`;
    }

    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);

    const res = await fetch(`${API}${path}`, opts);

    if (res.status === 401) { Auth.logout(); return null; }

    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Помилка ${res.status}`);
    }

    if (res.status === 204) return null;
    return res.json();
}

// ── Логін (OAuth2 form-data) ──────────────────────────────────
async function apiLogin(email, password) {
    const form = new URLSearchParams();
    form.append('username', email);
    form.append('password', password);

    const res = await fetch(`${API}/users/login`, {
        method: 'POST',
        body: form,
    });

    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Невірний email або пароль');
    }
    return res.json();
}

// ── Auth ──────────────────────────────────────────────────────
const api = {
    register: (data)  => request('POST', '/users/register', data, false),
    login:    apiLogin,
    getMe:    ()      => request('GET',  '/users/me'),

    // Tests (загальне)
    getTests: (search = '') => request('GET', `/tests/?search=${encodeURIComponent(search)}`),
    getTest:  (id)          => request('GET', `/tests/${id}`),

    // Tests (викладач)
    getMyTests:  ()          => request('GET',    '/tests/my'),
    createTest:  (data)      => request('POST',   '/tests/',      data),
    updateTest:  (id, data)  => request('PUT',    `/tests/${id}`, data),
    deleteTest:  (id)        => request('DELETE', `/tests/${id}`),
    toggleTest:  (id)        => request('PATCH',  `/tests/${id}/toggle`),

    // Questions
    getQuestions:   (testId)    => request('GET',    `/tests/${testId}/questions`),
    addQuestion:    (testId, d) => request('POST',   `/tests/${testId}/questions`, d),
    deleteQuestion: (qId)       => request('DELETE', `/tests/questions/${qId}`),

    // Statistics
    getStatistics: (testId) => request('GET', `/tests/${testId}/statistics`),

    // Testing (студент)
    startTest:  (testId)         => request('GET',  `/testing/start/${testId}`),
    submitTest: (testId, answers) => request('POST', `/testing/submit/${testId}`, { answers }),
};
