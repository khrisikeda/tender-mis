const API_BASE = window.localStorage.getItem('medtender_api_base') || 
  (window.location.port === '8000' || window.location.protocol.startsWith('http') ? window.location.origin : 'http://localhost:8000');

const feedback = document.querySelector('#authFeedback');
const loginForm = document.querySelector('#loginForm');
const signupForm = document.querySelector('#signupForm');
const demoLogin = document.querySelector('#demoLogin');
const forgotPasswordBtn = document.querySelector('#forgotPasswordBtn');

function setFeedback(message, type = 'error') {
  if (!feedback) return;
  feedback.className = `auth-feedback ${type}`;
  feedback.textContent = message;
}

function clearFeedback() {
  if (!feedback) return;
  feedback.className = 'auth-feedback';
  feedback.textContent = '';
}

function enterWorkspaceAsDemo() {
  window.localStorage.setItem('medtender_demo_session', 'true');
  window.localStorage.removeItem('medtender_access_token');
  window.localStorage.removeItem('medtender_refresh_token');
  setFeedback('Loading demo workspace...', 'info');
  setTimeout(() => {
    window.location.href = 'index.html';
  }, 300);
}

// Login Page Handlers
if (loginForm) {
  loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearFeedback();

    const emailInput = document.querySelector('#loginEmail');
    const passwordInput = document.querySelector('#loginPassword');
    const email = emailInput ? emailInput.value.trim() : '';
    const password = passwordInput ? passwordInput.value : '';

    if (!email || !password) {
      setFeedback('Please enter both your email address and password.', 'error');
      return;
    }

    setFeedback('Authenticating...', 'info');
    const body = new URLSearchParams({ username: email, password: password });

    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Incorrect email or password.');
      }

      const session = await response.json();
      window.localStorage.setItem('medtender_access_token', session.access_token);
      window.localStorage.setItem('medtender_refresh_token', session.refresh_token);
      window.localStorage.removeItem('medtender_demo_session');

      setFeedback('Sign in successful! Redirecting to workspace...', 'success');
      setTimeout(() => {
        window.location.href = 'index.html';
      }, 400);
    } catch (error) {
      setFeedback(`${error.message} Click "Explore with demo data" below to test the interface.`, 'error');
    }
  });

  if (demoLogin) {
    demoLogin.addEventListener('click', enterWorkspaceAsDemo);
  }

  if (forgotPasswordBtn) {
    forgotPasswordBtn.addEventListener('click', () => {
      setFeedback('Password resets must be processed by your organization administrator.', 'info');
    });
  }

  // Check if session exists and offer quick link
  const existingToken = window.localStorage.getItem('medtender_access_token');
  const isDemo = window.localStorage.getItem('medtender_demo_session') === 'true';
  if (existingToken || isDemo) {
    setFeedback('You have an active session. You can continue directly to your workspace.', 'info');
    const switchLink = document.querySelector('.auth-switch');
    if (switchLink) {
      const resumeLink = document.createElement('p');
      resumeLink.className = 'auth-switch';
      resumeLink.style.marginTop = '10px';
      resumeLink.innerHTML = `<a href="index.html"><strong>Open Dashboard Workspace →</strong></a>`;
      switchLink.insertAdjacentElement('afterend', resumeLink);
    }
  }
}

// Signup / Request Access Handlers
if (signupForm) {
  signupForm.addEventListener('submit', (event) => {
    event.preventDefault();
    clearFeedback();

    const nameInput = document.querySelector('#signupName');
    const emailInput = document.querySelector('#signupEmail');
    const companyInput = document.querySelector('#signupCompany');
    const roleInput = document.querySelector('#signupRole');

    if (!nameInput.value.trim() || !emailInput.value.trim() || !companyInput.value.trim()) {
      setFeedback('Please fill out all required fields.', 'error');
      return;
    }

    setFeedback(`Thank you, ${nameInput.value.trim()}. Your access request has been recorded. An administrator will review your account.`, 'success');
    signupForm.reset();
  });
}
