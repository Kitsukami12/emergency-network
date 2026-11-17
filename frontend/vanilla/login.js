// login.js – prototype authentication

// Simple mock credentials (hard‑coded)
const MOCK_USER = {
  username: 'admin',
  password: 'password',
};

function showMessage(msg, isError = true) {
  const el = document.getElementById('login-message');
  el.textContent = msg;
  el.style.color = isError ? '#f87171' : '#34d399'; // red or green
}

document.getElementById('login-form').addEventListener('submit', e => {
  e.preventDefault();
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;
  if (username === MOCK_USER.username && password === MOCK_USER.password) {
    showMessage('Login successful – redirecting…', false);
    // simple client‑side redirect after short delay
    setTimeout(() => {
      window.location.href = 'command-center.html';
    }, 800);
  } else {
    showMessage('Invalid credentials. (Demo only – use admin/password)');
  }
});
