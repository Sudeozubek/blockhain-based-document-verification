/* ==========================================================
   BlockVerify — script.js
   Stack: Vanilla JavaScript
   All backend connection points are clearly marked.
   ========================================================== */

'use strict';

/* ── Role State ────────────────────────────────────────────
   Simulates role-based UI switching (Admin / User).
   Backend will connect here later — JWT payload or session
   will determine the actual role.
   ─────────────────────────────────────────────────────── */
const RoleManager = (() => {
  const ROLES = { ADMIN: 'admin', USER: 'user' };
  let currentRole = localStorage.getItem('bv_role') || ROLES.USER;

  function get() { return currentRole; }

  function set(role) {
    currentRole = role;
    localStorage.setItem('bv_role', role);
    applyRoleUI(role);
  }

  function applyRoleUI(role) {
    const isAdmin = role === ROLES.ADMIN;
    // Sidebar admin-only nav items
    document.querySelectorAll('[data-role="admin"]').forEach(el => {
      el.style.display = isAdmin ? '' : 'none';
    });
    // Role badge in topbar
    const badge = document.getElementById('roleBadge');
    if (badge) {
      badge.className = 'role-badge ' + role;
      badge.innerHTML = `<i class="bi bi-shield${isAdmin ? '-fill' : ''}"></i> ${isAdmin ? 'Admin' : 'User'}`;
    }
    // Sidebar user role label
    const sidebarRole = document.getElementById('sidebarUserRole');
    if (sidebarRole) sidebarRole.textContent = isAdmin ? 'Administrator' : 'Standard User';
    // Table view label
    const viewLabel = document.getElementById('viewLabel');
    if (viewLabel) viewLabel.textContent = isAdmin ? 'All Records' : 'My Records';
  }

  function init() { applyRoleUI(currentRole); }

  return { get, set, init, ROLES };
})();

/* ── Mock Data ─────────────────────────────────────────────
   Placeholder data that will be replaced by API responses.
   Backend will connect here later.
   ─────────────────────────────────────────────────────── */
const MockData = {
  stats: {
    totalContracts: 142,
    verified: 128,
    tamperAlerts: 7
  },
  recentActivity: [
    { type: 'verified', text: '<strong>NDA_Agreement_v3.pdf</strong> was verified successfully', time: '2 min ago', user: 'j.smith@corp.com' },
    { type: 'tamper',   text: '<strong>ServiceContract_2024.pdf</strong> hash mismatch detected', time: '15 min ago', user: 'a.jones@corp.com' },
    { type: 'upload',   text: '<strong>Employment_Contract_Q4.pdf</strong> uploaded and hashed', time: '1 hr ago', user: 'r.lee@corp.com' },
    { type: 'verified', text: '<strong>PartnerAgreement_Final.pdf</strong> integrity confirmed', time: '3 hrs ago', user: 'j.smith@corp.com' },
    { type: 'upload',   text: '<strong>Procurement_PO_8821.pdf</strong> uploaded and hashed', time: '5 hrs ago', user: 'm.chen@corp.com' },
  ],
  auditLog: [
    { id: 1, document: 'NDA_Agreement_v3.pdf',         uploader: 'j.smith@corp.com',   action: 'Verified',  timestamp: '2025-01-15 14:32:07', result: 'verified',  block: 4821 },
    { id: 2, document: 'ServiceContract_2024.pdf',     uploader: 'a.jones@corp.com',   action: 'Verified',  timestamp: '2025-01-15 13:18:44', result: 'tampered',  block: 4820 },
    { id: 3, document: 'Employment_Contract_Q4.pdf',   uploader: 'r.lee@corp.com',     action: 'Uploaded',  timestamp: '2025-01-15 12:05:31', result: 'uploaded',  block: 4819 },
    { id: 4, document: 'PartnerAgreement_Final.pdf',   uploader: 'j.smith@corp.com',   action: 'Verified',  timestamp: '2025-01-15 10:47:22', result: 'verified',  block: 4818 },
    { id: 5, document: 'Procurement_PO_8821.pdf',      uploader: 'm.chen@corp.com',    action: 'Uploaded',  timestamp: '2025-01-14 16:59:08', result: 'uploaded',  block: 4817 },
    { id: 6, document: 'LicenseAgreement_SAAS.pdf',    uploader: 'admin@corp.com',     action: 'Verified',  timestamp: '2025-01-14 15:30:50', result: 'verified',  block: 4816 },
    { id: 7, document: 'SupplierContract_HK.pdf',      uploader: 'a.jones@corp.com',   action: 'Uploaded',  timestamp: '2025-01-14 11:12:33', result: 'uploaded',  block: 4815 },
    { id: 8, document: 'Confidential_Board_Res.pdf',   uploader: 'admin@corp.com',     action: 'Verified',  timestamp: '2025-01-13 09:05:19', result: 'tampered',  block: 4814 },
    { id: 9, document: 'AnnualReport_Draft_v2.pdf',    uploader: 'r.lee@corp.com',     action: 'Uploaded',  timestamp: '2025-01-13 08:41:55', result: 'uploaded',  block: 4813 },
    { id:10, document: 'PurchaseOrder_2024_Q1.pdf',    uploader: 'm.chen@corp.com',    action: 'Verified',  timestamp: '2025-01-12 17:22:40', result: 'verified',  block: 4812 },
  ],
  hashes: {
    stored:   'a4f3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3',
    computed: 'a4f3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3', // same = verified
    tampered: '9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e7'
  }
};

/* ── Auth Page ─────────────────────────────────────────────
   Client-side validation only.
   Backend will connect here later — POST /api/auth/login
   Backend will connect here later — POST /api/auth/register
   ─────────────────────────────────────────────────────── */
function initAuthPage() {
  const loginTab    = document.getElementById('loginTab');
  const registerTab = document.getElementById('registerTab');
  const loginForm   = document.getElementById('loginForm');
  const regForm     = document.getElementById('registerForm');
  if (!loginTab) return;

  loginTab.addEventListener('click', () => {
    loginTab.classList.add('active'); registerTab.classList.remove('active');
    loginForm.style.display = ''; regForm.style.display = 'none';
  });
  registerTab.addEventListener('click', () => {
    registerTab.classList.add('active'); loginTab.classList.remove('active');
    regForm.style.display = ''; loginForm.style.display = 'none';
  });

  // Login validation
  loginForm && loginForm.addEventListener('submit', function(e) {
    e.preventDefault();
    clearErrors(this);
    const email    = document.getElementById('loginEmail');
    const password = document.getElementById('loginPassword');
    let valid = true;

    if (!email.value.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
      setError(email, 'Please enter a valid email address.'); valid = false;
    }
    if (!password.value || password.value.length < 6) {
      setError(password, 'Password must be at least 6 characters.'); valid = false;
    }
    if (valid) {
      // Backend will connect here later — POST /api/auth/login
      showFormSuccess('loginSuccess', 'Credentials validated. Redirecting to dashboard...');
      setTimeout(() => { window.location.href = 'dashboard.html'; }, 1200);
    }
  });

  // Register validation
  regForm && regForm.addEventListener('submit', function(e) {
    e.preventDefault();
    clearErrors(this);
    const fullname  = document.getElementById('regFullname');
    const email     = document.getElementById('regEmail');
    const password  = document.getElementById('regPassword');
    const confirm   = document.getElementById('regConfirm');
    let valid = true;

    if (!fullname.value.trim() || fullname.value.trim().length < 3) {
      setError(fullname, 'Full name must be at least 3 characters.'); valid = false;
    }
    if (!email.value.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
      setError(email, 'Please enter a valid email address.'); valid = false;
    }
    if (!password.value || password.value.length < 8) {
      setError(password, 'Password must be at least 8 characters.'); valid = false;
    }
    if (confirm.value !== password.value) {
      setError(confirm, 'Passwords do not match.'); valid = false;
    }
    if (valid) {
      // Backend will connect here later — POST /api/auth/register
      showFormSuccess('registerSuccess', 'Account created. Redirecting...');
      setTimeout(() => { window.location.href = 'dashboard.html'; }, 1200);
    }
  });

  // Password visibility toggle
  document.querySelectorAll('.toggle-pw').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = document.getElementById(btn.dataset.target);
      if (!input) return;
      const show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      btn.className = btn.className.replace(
        show ? 'bi-eye' : 'bi-eye-slash',
        show ? 'bi-eye-slash' : 'bi-eye'
      );
    });
  });
}

/* ── Dashboard Page ────────────────────────────────────────
   Loads mock stats and activity feed.
   Backend will connect here later — GET /api/dashboard/stats
   Backend will connect here later — GET /api/activity/recent
   ─────────────────────────────────────────────────────── */
function initDashboard() {
  const totalEl    = document.getElementById('statTotal');
  const verifiedEl = document.getElementById('statVerified');
  const tamperEl   = document.getElementById('statTamper');
  if (!totalEl) return;

  // Backend will connect here later — replace MockData.stats with real API
  animateCounter(totalEl,    0, MockData.stats.totalContracts, 900);
  animateCounter(verifiedEl, 0, MockData.stats.verified,       900);
  animateCounter(tamperEl,   0, MockData.stats.tamperAlerts,   900);

  // Render activity feed
  // Backend will connect here later — GET /api/activity/recent
  const feed = document.getElementById('activityFeed');
  if (feed) {
    feed.innerHTML = MockData.recentActivity.map(item => `
      <div class="activity-item">
        <span class="activity-dot dot-${item.type}"></span>
        <div class="activity-text">
          <span>${item.text}</span><br>
          <small class="text-muted-app">${item.user}</small>
        </div>
        <span class="activity-time">${item.time}</span>
      </div>
    `).join('');
  }
}

/* ── Upload Page ───────────────────────────────────────────
   Handles drag-and-drop, file selection, and form UI.
   Backend will connect here later — POST /api/contracts/upload
   ─────────────────────────────────────────────────────── */
function initUploadPage() {
  const dropzone  = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const selectedEl = document.getElementById('fileSelected');
  const clearBtn  = document.getElementById('clearFile');
  const uploadForm = document.getElementById('uploadForm');
  if (!dropzone) return;

  let selectedFile = null;

  function showFile(file) {
    selectedFile = file;
    document.getElementById('selectedName').textContent = file.name;
    document.getElementById('selectedSize').textContent = formatBytes(file.size);
    selectedEl.style.display = 'flex';
    // SHA-256 placeholder — Backend will connect here later — real hash computed server-side
    const shaVal = document.getElementById('shaValue');
    if (shaVal) {
      shaVal.innerHTML = '<span class="sha-pending">Hash will be computed server-side on upload...</span>';
    }
  }

  function clearFile() {
    selectedFile = null;
    fileInput.value = '';
    selectedEl.style.display = 'none';
    const shaVal = document.getElementById('shaValue');
    if (shaVal) shaVal.innerHTML = '<span class="sha-pending">No file selected</span>';
  }

  // Drag events
  ['dragenter','dragover'].forEach(ev => {
    dropzone.addEventListener(ev, e => { e.preventDefault(); dropzone.classList.add('dragover'); });
  });
  ['dragleave','drop'].forEach(ev => {
    dropzone.addEventListener(ev, e => { e.preventDefault(); dropzone.classList.remove('dragover'); });
  });
  dropzone.addEventListener('drop', e => {
    const file = e.dataTransfer.files[0];
    if (file) { validateAndShowFile(file); }
  });
  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) { validateAndShowFile(fileInput.files[0]); }
  });
  clearBtn && clearBtn.addEventListener('click', clearFile);

  function validateAndShowFile(file) {
    if (file.type !== 'application/pdf') {
      showUploadAlert('danger', '<i class="bi bi-x-circle-fill me-2"></i>Only PDF files are supported.'); return;
    }
    if (file.size > 20 * 1024 * 1024) {
      showUploadAlert('danger', '<i class="bi bi-x-circle-fill me-2"></i>File exceeds maximum size of 20 MB.'); return;
    }
    hideUploadAlert();
    showFile(file);
  }

  uploadForm && uploadForm.addEventListener('submit', function(e) {
    e.preventDefault();
    if (!selectedFile) {
      showUploadAlert('danger', '<i class="bi bi-x-circle-fill me-2"></i>Please select a PDF file first.'); return;
    }
    // Backend will connect here later — POST /api/contracts/upload (multipart/form-data)
    showUploadAlert('info', '<i class="bi bi-arrow-repeat me-2"></i>Uploading and hashing document...');
    setTimeout(() => {
      showUploadAlert('success',
        '<i class="bi bi-check-circle-fill me-2"></i><strong>Upload successful.</strong> ' +
        'The document has been hashed and recorded on the ledger.'
      );
      clearFile();
    }, 1800);
  });
}

/* ── Verify Page ───────────────────────────────────────────
   Simulates verification flow with mock hash comparison.
   Backend will connect here later — POST /api/contracts/verify
   ─────────────────────────────────────────────────────── */
function initVerifyPage() {
  const verifyForm = document.getElementById('verifyForm');
  const verifyInput = document.getElementById('verifyFileInput');
  const verifyDrop  = document.getElementById('verifyDropzone');
  if (!verifyForm) return;

  let verifyFile = null;

  // Drag-and-drop
  ['dragenter','dragover'].forEach(ev => {
    verifyDrop.addEventListener(ev, e => { e.preventDefault(); verifyDrop.classList.add('dragover'); });
  });
  ['dragleave','drop'].forEach(ev => {
    verifyDrop.addEventListener(ev, e => { e.preventDefault(); verifyDrop.classList.remove('dragover'); });
  });
  verifyDrop.addEventListener('drop', e => {
    const file = e.dataTransfer.files[0];
    if (file) setVerifyFile(file);
  });
  verifyInput.addEventListener('change', () => {
    if (verifyInput.files[0]) setVerifyFile(verifyInput.files[0]);
  });

  function setVerifyFile(file) {
    verifyFile = file;
    document.getElementById('verifyFileName').textContent = file.name;
    document.getElementById('verifyFileSize').textContent = formatBytes(file.size);
    document.getElementById('verifyFileSelected').style.display = 'flex';
  }

  const clearVerify = document.getElementById('clearVerifyFile');
  clearVerify && clearVerify.addEventListener('click', () => {
    verifyFile = null;
    verifyInput.value = '';
    document.getElementById('verifyFileSelected').style.display = 'none';
    resetVerifyResult();
  });

  verifyForm.addEventListener('submit', function(e) {
    e.preventDefault();
    if (!verifyFile) {
      setVerifyStatus('not-found', 'No File Selected', 'Please upload a PDF to verify.', null); return;
    }

    // Simulate loading state
    setVerifyStatus('idle', 'Verifying...', 'Computing hash and querying the ledger. Please wait.', null);

    // Backend will connect here later — POST /api/contracts/verify (multipart/form-data)
    setTimeout(() => {
      // Cycle through mock results for demonstration: verified → tampered → not-found
      const cycle = ['verified', 'tampered', 'not-found'];
      const state = window._verifyState = cycle[(((window._verifyState || -1) === 'verified' ? 0 :
        (window._verifyState === 'tampered' ? 1 : 2)) + 1) % 3];

      const ts = new Date().toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'medium' });

      if (state === 'verified') {
        renderHashes(MockData.hashes.stored, MockData.hashes.stored, true);
        setVerifyStatus('verified',
          'Document Verified',
          'The document hash matches the stored record. Integrity confirmed.',
          ts
        );
      } else if (state === 'tampered') {
        renderHashes(MockData.hashes.stored, MockData.hashes.tampered, false);
        setVerifyStatus('tampered',
          'Tamper Detected!',
          'The computed hash does not match the stored record. This document may have been altered.',
          ts
        );
      } else {
        renderHashes('—', '—', null);
        setVerifyStatus('not-found',
          'Document Not Found',
          'No record was found for this document on the ledger. It may not have been registered.',
          ts
        );
      }
    }, 1600);
  });
}

function renderHashes(stored, computed, match) {
  const storedEl   = document.getElementById('storedHash');
  const computedEl = document.getElementById('computedHash');
  const storedBox  = document.getElementById('storedHashBox');
  const computedBox = document.getElementById('computedHashBox');
  if (!storedEl) return;
  storedEl.textContent   = stored;
  computedEl.textContent = computed;
  if (match === null) {
    storedBox.className   = 'hash-box';
    computedBox.className = 'hash-box';
  } else if (match) {
    storedBox.className   = 'hash-box hash-match';
    computedBox.className = 'hash-box hash-match';
  } else {
    storedBox.className   = 'hash-box';
    computedBox.className = 'hash-box hash-mismatch';
  }
}

function setVerifyStatus(state, title, desc, timestamp) {
  const banner  = document.getElementById('resultBanner');
  const icon    = document.getElementById('resultIcon');
  const titleEl = document.getElementById('resultTitle');
  const descEl  = document.getElementById('resultDesc');
  const tsEl    = document.getElementById('resultTimestamp');
  if (!banner) return;

  const icons = { verified: 'bi-patch-check-fill', tampered: 'bi-shield-exclamation',
                  'not-found': 'bi-question-circle-fill', idle: 'bi-hourglass-split' };
  banner.className = `result-banner ${state}`;
  icon.className   = `result-icon`;
  icon.innerHTML   = `<i class="bi ${icons[state] || 'bi-hourglass-split'}"></i>`;
  titleEl.textContent = title;
  descEl.textContent  = desc;
  if (tsEl) {
    tsEl.style.display = timestamp ? 'flex' : 'none';
    if (timestamp) tsEl.querySelector('.ts-value').textContent = timestamp;
  }
  document.getElementById('verifyResult').style.display = '';
}

function resetVerifyResult() {
  const el = document.getElementById('verifyResult');
  if (el) el.style.display = 'none';
}

/* ── Audit Log / History Page ──────────────────────────────
   Renders filterable mock audit table.
   Backend will connect here later — GET /api/audit-log
   ─────────────────────────────────────────────────────── */
function initHistoryPage() {
  const tableBody = document.getElementById('auditTableBody');
  if (!tableBody) return;

  // Backend will connect here later — GET /api/audit-log?role=...&user=...
  let data = [...MockData.auditLog];
  const isAdmin = RoleManager.get() === RoleManager.ROLES.ADMIN;

  // User sees only own records (mock: first 5)
  if (!isAdmin) data = data.slice(0, 5);

  renderTable(data);

  // Search
  const searchInput  = document.getElementById('searchInput');
  const filterResult = document.getElementById('filterResult');
  const filterAction = document.getElementById('filterAction');

  function applyFilters() {
    const q      = (searchInput?.value || '').toLowerCase();
    const result = (filterResult?.value || '');
    const action = (filterAction?.value || '');
    let filtered = isAdmin ? [...MockData.auditLog] : MockData.auditLog.slice(0, 5);
    if (q)      filtered = filtered.filter(r => r.document.toLowerCase().includes(q) || r.uploader.toLowerCase().includes(q));
    if (result) filtered = filtered.filter(r => r.result === result);
    if (action) filtered = filtered.filter(r => r.action.toLowerCase() === action.toLowerCase());
    renderTable(filtered);
    const countEl = document.getElementById('recordCount');
    if (countEl) countEl.textContent = `${filtered.length} record${filtered.length !== 1 ? 's' : ''}`;
  }

  searchInput  && searchInput.addEventListener('input', applyFilters);
  filterResult && filterResult.addEventListener('change', applyFilters);
  filterAction && filterAction.addEventListener('change', applyFilters);

  const clearBtn = document.getElementById('clearFilters');
  clearBtn && clearBtn.addEventListener('click', () => {
    if (searchInput)  searchInput.value  = '';
    if (filterResult) filterResult.value = '';
    if (filterAction) filterAction.value = '';
    applyFilters();
  });

  // Export placeholder
  const exportBtn = document.getElementById('exportBtn');
  exportBtn && exportBtn.addEventListener('click', () => {
    // Backend will connect here later — GET /api/audit-log/export
    alert('Export functionality will be available once the backend is connected.');
  });
}

function renderTable(data) {
  const tbody = document.getElementById('auditTableBody');
  const empty = document.getElementById('emptyState');
  if (!tbody) return;

  if (!data.length) {
    tbody.innerHTML = '';
    if (empty) empty.style.display = '';
    return;
  }
  if (empty) empty.style.display = 'none';

  tbody.innerHTML = data.map(row => {
    const badgeMap = {
      verified: '<span class="badge-status badge-verified">Verified</span>',
      tampered: '<span class="badge-status badge-tampered">Tampered</span>',
      uploaded: '<span class="badge-status badge-uploaded">Uploaded</span>',
      pending:  '<span class="badge-status badge-pending">Pending</span>',
    };
    return `
      <tr>
        <td>
          <div class="d-flex align-items-center gap-2">
            <i class="bi bi-file-earmark-pdf text-danger-app"></i>
            <span class="fw-500">${escHtml(row.document)}</span>
          </div>
        </td>
        <td class="text-secondary-app">${escHtml(row.uploader)}</td>
        <td>${escHtml(row.action)}</td>
        <td class="mono text-muted-app">${escHtml(row.timestamp)}</td>
        <td>${badgeMap[row.result] || row.result}</td>
        <td class="mono text-muted-app">#${row.block}</td>
      </tr>
    `;
  }).join('');
}

/* ── Role Switch (Topbar) ──────────────────────────────────
   Allows demo switching between Admin and User views.
   ─────────────────────────────────────────────────────── */
function initRoleSwitch() {
  const switcher = document.getElementById('roleSwitcher');
  if (!switcher) return;
  // Set initial value
  switcher.value = RoleManager.get();
  switcher.addEventListener('change', () => {
    RoleManager.set(switcher.value);
    // Refresh page to re-apply all role-dependent content
    setTimeout(() => location.reload(), 200);
  });
}

/* ── Sidebar Mobile Toggle ──────────────────────────────── */
function initSidebarToggle() {
  const toggle  = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  if (!toggle || !sidebar) return;
  toggle.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    if (overlay) overlay.style.display = sidebar.classList.contains('open') ? 'block' : 'none';
  });
  overlay && overlay.addEventListener('click', () => {
    sidebar.classList.remove('open');
    overlay.style.display = 'none';
  });
}

/* ── Logout ──────────────────────────────────────────────── */
function initLogout() {
  document.querySelectorAll('.logout-btn').forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      // Backend will connect here later — POST /api/auth/logout (clear session/cookie)
      localStorage.removeItem('bv_role');
      window.location.href = 'index.html';
    });
  });
}

/* ── Helpers ─────────────────────────────────────────────── */
function setError(input, msg) {
  input.classList.add('is-invalid');
  let fb = input.nextElementSibling;
  if (!fb || !fb.classList.contains('invalid-feedback')) {
    fb = document.createElement('div');
    fb.className = 'invalid-feedback';
    input.parentNode.insertBefore(fb, input.nextSibling);
  }
  fb.textContent = msg;
}

function clearErrors(form) {
  form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
  form.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
}

function showFormSuccess(id, msg) {
  const el = document.getElementById(id);
  if (!el) return;
  el.style.display = '';
  el.innerHTML = `<i class="bi bi-check-circle-fill me-2"></i>${msg}`;
}

function showUploadAlert(type, html) {
  const el = document.getElementById('uploadAlert');
  if (!el) return;
  el.style.display = '';
  el.className = `alert alert-${type} mb-0`;
  el.innerHTML = html;
}

function hideUploadAlert() {
  const el = document.getElementById('uploadAlert');
  if (el) el.style.display = 'none';
}

function animateCounter(el, from, to, duration) {
  if (!el) return;
  const start = performance.now();
  function step(now) {
    const progress = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(from + (to - from) * ease);
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function formatBytes(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/* ── Init ─────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  RoleManager.init();
  initRoleSwitch();
  initSidebarToggle();
  initLogout();
  initAuthPage();
  initDashboard();
  initUploadPage();
  initVerifyPage();
  initHistoryPage();
});
