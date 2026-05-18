// ============================================================
// app.js — спільні утиліти для всіх сторінок
// ============================================================

// ── Auth guard ────────────────────────────────────────────────
function guardRole(required) {
  // Захист сторінок на рівні UI. Остаточна перевірка все одно відбувається на backend.
  if (!Auth.isLoggedIn()) {
    location.href = 'index.html';
    return;
  }
  const user = Auth.getUser();
  if (user?.role !== required) {
    location.href = user?.role === 'teacher' ? 'teacher.html' : 'student.html';
  }
}

// ── Modal helpers ─────────────────────────────────────────────
function openModal(id) {
  document.getElementById(id).classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal(id) {
  document.getElementById(id).classList.remove('open');
  document.body.style.overflow = '';
}

// Закриття кліком на overlay
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
    document.body.style.overflow = '';
  }
});

// Закриття через Escape
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.open').forEach(m => {
      m.classList.remove('open');
      document.body.style.overflow = '';
    });
  }
});

// ── Toast notifications ───────────────────────────────────────
function toast(message, type = 'info', duration = 3500) {
  const container = document.getElementById('toasts');
  if (!container) return;

  const el = document.createElement('div');
  el.className = `toast ${type}`;

  const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
  // Не використовуємо innerHTML для тексту повідомлення, щоб не відкривати XSS.
  const icon = document.createElement('span');
  icon.style.marginRight = '.5rem';
  icon.textContent = icons[type] || 'ℹ️';
  el.append(icon, document.createTextNode(message));

  container.appendChild(el);
  setTimeout(() => {
    el.style.animation = 'toastIn .3s ease reverse';
    setTimeout(() => el.remove(), 280);
  }, duration);
}

// ── Sanitize HTML (захист від XSS) ───────────────────────────
function esc(str) {
  // Екрануємо користувацький текст перед вставкою в HTML-шаблони.
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
