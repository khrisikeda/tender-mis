const API_BASE = window.localStorage.getItem('medtender_api_base') || 
  (window.location.port === '8000' || window.location.protocol.startsWith('http') ? window.location.origin : 'http://localhost:8000');

// ==========================================================================
// 1. Authentication Guard & Session Management
// ==========================================================================

const accessToken = window.localStorage.getItem('medtender_access_token');
const isDemoSession = window.localStorage.getItem('medtender_demo_session') === 'true';

if (!accessToken && !isDemoSession) {
  window.location.href = 'login.html';
}

function signOut() {
  window.localStorage.removeItem('medtender_access_token');
  window.localStorage.removeItem('medtender_refresh_token');
  window.localStorage.removeItem('medtender_demo_session');
  showToast('Signed out successfully.');
  setTimeout(() => {
    window.location.href = 'login.html';
  }, 400);
}

// User profile loading
async function loadUserProfile() {
  const userAvatar = document.querySelector('#userAvatar');
  const userName = document.querySelector('#userName');
  const userRole = document.querySelector('#userRole');
  const menuUserName = document.querySelector('#menuUserName');
  const menuUserEmail = document.querySelector('#menuUserEmail');
  const overviewHeading = document.querySelector('#overviewHeading');

  if (isDemoSession) {
    if (userName) userName.textContent = 'Chris Kalisa';
    if (userRole) userRole.textContent = 'Chief Medical Procurement';
    if (userAvatar) userAvatar.textContent = 'CK';
    if (menuUserName) menuUserName.textContent = 'Chris Kalisa';
    if (menuUserEmail) menuUserEmail.textContent = 'c.kalisa@medtender.rw';
    if (overviewHeading) overviewHeading.textContent = 'Good morning, Chris.';
    return;
  }

  if (accessToken) {
    try {
      const response = await fetch(`${API_BASE}/auth/me`, {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (!response.ok) throw new Error('Session expired.');
      const user = await response.json();

      const initials = (user.full_name || 'User')
        .split(' ')
        .map(n => n[0])
        .slice(0, 2)
        .join('')
        .toUpperCase();

      if (userAvatar) userAvatar.textContent = initials || 'CK';
      if (userName) userName.textContent = user.full_name;
      if (userRole) userRole.textContent = (user.role || 'Member').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
      if (menuUserName) menuUserName.textContent = user.full_name;
      if (menuUserEmail) menuUserEmail.textContent = user.email;
      if (overviewHeading) overviewHeading.textContent = `Good morning, ${user.full_name.split(' ')[0]}.`;
    } catch {
      // Fall back gracefully to demo profile
    }
  }
}

// Topbar profile dropdown
const profileChipBtn = document.querySelector('#profileChipBtn');
const profileDropdown = document.querySelector('#profileDropdown');

if (profileChipBtn && profileDropdown) {
  profileChipBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    const isExpanded = profileChipBtn.getAttribute('aria-expanded') === 'true';
    profileChipBtn.setAttribute('aria-expanded', String(!isExpanded));
    profileDropdown.classList.toggle('open', !isExpanded);
  });

  document.addEventListener('click', (e) => {
    if (!profileDropdown.contains(e.target) && !profileChipBtn.contains(e.target)) {
      profileDropdown.classList.remove('open');
      profileChipBtn.setAttribute('aria-expanded', 'false');
    }
  });
}

const signOutBtn = document.querySelector('#signOutBtn');
const sidebarSignOut = document.querySelector('#sidebarSignOut');
if (signOutBtn) signOutBtn.addEventListener('click', signOut);
if (sidebarSignOut) sidebarSignOut.addEventListener('click', signOut);

const menuSettings = document.querySelector('#menuSettings');
if (menuSettings) {
  menuSettings.addEventListener('click', () => {
    showToast('System preferences & API endpoints can be configured in .env and settings.');
    if (profileDropdown) profileDropdown.classList.remove('open');
  });
}

// ==========================================================================
// 2. Data Stores
// ==========================================================================

let tenders = [
  {
    id: 'tender-1',
    ref: '000004/G/NCB/2026/2027/RBC',
    title: 'Supply and installation of neonatal care equipment and incubators',
    procuring_entity: 'Rwanda Biomedical Centre (RBC)',
    category: 'Medical Equipment',
    tender_value: 4500000000,
    currency: 'RWF',
    deadline_at: '2026-08-28T16:00:00+02:00',
    relevance_score: 94,
    match: 92,
    technical: 87,
    suitability: 81,
    risk: 'Medium',
    security: 'RWF 4,500,000',
    authorization: 'Required',
    missing: 2,
    status: 'bid_preparation',
    recommendation: 'Recommended to bid',
    icon: 'NICU'
  },
  {
    id: 'tender-2',
    ref: '000012/G/ICB/2026/2027/CHUK',
    title: 'Automated clinical chemistry and hematology reagents framework',
    procuring_entity: 'University Teaching Hospital of Kigali (CHUK)',
    category: 'Laboratory',
    tender_value: 2800000000,
    currency: 'RWF',
    deadline_at: '2026-09-03T10:00:00+02:00',
    relevance_score: 88,
    match: 86,
    technical: 91,
    suitability: 90,
    risk: 'Low',
    security: 'Not required',
    authorization: 'Not required',
    missing: 1,
    status: 'interested',
    recommendation: 'Recommended to bid',
    icon: 'LAB'
  },
  {
    id: 'tender-3',
    ref: '000088/G/NCB/2026/2027/RMS',
    title: 'Framework agreement for essential surgical and medical consumables',
    procuring_entity: 'Rwanda Medical Supply Ltd (RMS)',
    category: 'Medical Consumables',
    tender_value: 5200000000,
    currency: 'RWF',
    deadline_at: '2026-09-07T15:00:00+02:00',
    relevance_score: 79,
    match: 81,
    technical: 76,
    suitability: 68,
    risk: 'Medium',
    security: 'RWF 2,000,000',
    authorization: 'Required',
    missing: 4,
    status: 'review',
    recommendation: 'Management review',
    icon: 'SUP'
  },
  {
    id: 'tender-4',
    ref: '000019/G/NCB/2026/2027/KDH',
    title: 'Procurement of modern dental units, autoclaves and imaging systems',
    procuring_entity: 'Kigali Dental Hospital',
    category: 'Dental',
    tender_value: 850000000,
    currency: 'RWF',
    deadline_at: '2026-09-18T12:00:00+02:00',
    relevance_score: 76,
    match: 74,
    technical: 83,
    suitability: 77,
    risk: 'Low',
    security: 'Not available',
    authorization: 'Required',
    missing: 0,
    status: 'bid_preparation',
    recommendation: 'Recommended to bid',
    icon: 'DEN'
  },
  {
    id: 'tender-5',
    ref: '000031/G/ICB/2026/2027/KFH',
    title: 'Supply, installation and commissioning of 128-Slice CT Scanner System',
    procuring_entity: 'King Faisal Hospital Rwanda',
    category: 'Imaging & Radiology',
    tender_value: 1450000000,
    currency: 'RWF',
    deadline_at: '2026-09-24T17:00:00+02:00',
    relevance_score: 91,
    match: 95,
    technical: 89,
    suitability: 88,
    risk: 'High',
    security: 'RWF 15,000,000',
    authorization: 'Required (Manufacturer OEM)',
    missing: 1,
    status: 'submitted',
    recommendation: 'High priority bid',
    icon: 'RAD'
  },
  {
    id: 'tender-6',
    ref: '000072/G/NCB/2026/2027/CHUB',
    title: 'Comprehensive hospital medical gas and oxygen plant maintenance',
    procuring_entity: 'University Teaching Hospital of Butare (CHUB)',
    category: 'Medical Equipment',
    tender_value: 620000000,
    currency: 'RWF',
    deadline_at: '2026-09-30T11:00:00+02:00',
    relevance_score: 72,
    match: 70,
    technical: 75,
    suitability: 65,
    risk: 'Medium',
    security: 'RWF 1,000,000',
    authorization: 'Not required',
    missing: 3,
    status: 'new',
    recommendation: 'Technical evaluation',
    icon: 'O2'
  }
];

let sources = [
  {
    id: 'src-1',
    name: 'Rwanda Public Procurement Authority (RPPA)',
    organization: 'Umucyo e-Procurement System',
    website: 'https://umucyo.gov.rw',
    country: 'Rwanda',
    category: 'government_portal',
    collection_method: 'api',
    is_active: true,
    scan_frequency_hours: 6,
    robots_txt_allows_collection: true,
    requires_manual_import: false,
    last_scan_at: '14 min ago',
    last_successful_scan_at: '14 min ago',
    last_error: null,
    tenders_collected_count: 64
  },
  {
    id: 'src-2',
    name: 'Rwanda Biomedical Centre (RBC)',
    organization: 'Ministry of Health Implementing Agency',
    website: 'https://rbc.gov.rw/tenders',
    country: 'Rwanda',
    category: 'ministry',
    collection_method: 'webpage',
    is_active: true,
    scan_frequency_hours: 12,
    robots_txt_allows_collection: true,
    requires_manual_import: false,
    last_scan_at: '28 min ago',
    last_successful_scan_at: '28 min ago',
    last_error: null,
    tenders_collected_count: 28
  },
  {
    id: 'src-3',
    name: 'Rwanda Medical Supply Ltd (RMS)',
    organization: 'National Medical Supply & Distribution',
    website: 'https://rms.rw/procurement',
    country: 'Rwanda',
    category: 'government_portal',
    collection_method: 'api',
    is_active: true,
    scan_frequency_hours: 12,
    robots_txt_allows_collection: true,
    requires_manual_import: false,
    last_scan_at: '1 hour ago',
    last_successful_scan_at: '1 hour ago',
    last_error: null,
    tenders_collected_count: 22
  },
  {
    id: 'src-4',
    name: 'University Teaching Hospital of Kigali (CHUK)',
    organization: 'National Referral Teaching Hospital',
    website: 'https://chuk.rw/tenders',
    country: 'Rwanda',
    category: 'hospital',
    collection_method: 'webpage',
    is_active: true,
    scan_frequency_hours: 24,
    robots_txt_allows_collection: true,
    requires_manual_import: false,
    last_scan_at: '2 hours ago',
    last_successful_scan_at: '2 hours ago',
    last_error: null,
    tenders_collected_count: 14
  },
  {
    id: 'src-5',
    name: 'King Faisal Hospital Rwanda (KFH)',
    organization: 'Quaternary Referral Center',
    website: 'https://kfh.rw/tenders',
    country: 'Rwanda',
    category: 'hospital',
    collection_method: 'webpage',
    is_active: true,
    scan_frequency_hours: 24,
    robots_txt_allows_collection: true,
    requires_manual_import: false,
    last_scan_at: '3 hours ago',
    last_successful_scan_at: '3 hours ago',
    last_error: null,
    tenders_collected_count: 9
  },
  {
    id: 'src-6',
    name: 'University Teaching Hospital of Butare (CHUB)',
    organization: 'Southern Province Referral Hospital',
    website: 'https://chub.rw/tenders',
    country: 'Rwanda',
    category: 'hospital',
    collection_method: 'rss',
    is_active: true,
    scan_frequency_hours: 24,
    robots_txt_allows_collection: true,
    requires_manual_import: false,
    last_scan_at: '4 hours ago',
    last_successful_scan_at: '4 hours ago',
    last_error: null,
    tenders_collected_count: 5
  },
  {
    id: 'src-7',
    name: 'Ministry of Health Rwanda (MoH)',
    organization: 'Central Health Ministry',
    website: 'https://moh.gov.rw/opportunities',
    country: 'Rwanda',
    category: 'ministry',
    collection_method: 'webpage',
    is_active: true,
    scan_frequency_hours: 24,
    robots_txt_allows_collection: true,
    requires_manual_import: false,
    last_scan_at: '6 hours ago',
    last_successful_scan_at: '6 hours ago',
    last_error: null,
    tenders_collected_count: 8
  },
  {
    id: 'src-8',
    name: 'Partners In Health Rwanda (PIH / IMB)',
    organization: 'Inshuti Mu Buzima NGO',
    website: 'https://pih.org/rwanda/procurement',
    country: 'Rwanda',
    category: 'ngo',
    collection_method: 'manual_import',
    is_active: true,
    scan_frequency_hours: 72,
    robots_txt_allows_collection: true,
    requires_manual_import: true,
    last_scan_at: 'Yesterday',
    last_successful_scan_at: 'Yesterday',
    last_error: null,
    tenders_collected_count: 3
  }
];

let catalogue = [
  {
    id: 'cat-1',
    code: 'NEO-WRM-500',
    name: 'Advanced Infant Radiant Warmer & Phototherapy Unit',
    category: 'Neonatal & ICU',
    manufacturer: 'MedTech Global Biomedical',
    specs: ['Servo-controlled skin temperature', 'Integrated LED phototherapy', 'APGAR timer', 'Tilting bassinet'],
    certifications: ['ISO 13485', 'CE 0123', 'FDA 510(k)'],
    lead_time: '7-14 Days',
    stock_status: 'In Stock (Kigali)',
    matched_tenders: 1
  },
  {
    id: 'cat-2',
    code: 'LAB-ANA-800',
    name: 'Fully Automated Clinical Chemistry & ISE Analyzer',
    category: 'Laboratory',
    manufacturer: 'DiaSys Diagnostic Systems',
    specs: ['800 tests/hour throughput', 'Refrigerated reagent disk', 'Automated cuvette wash', 'LIS bidirectional'],
    certifications: ['ISO 13485', 'CE-IVD', 'Rwanda FDA Approved'],
    lead_time: '14-21 Days',
    stock_status: 'Available to Order',
    matched_tenders: 1
  },
  {
    id: 'cat-3',
    code: 'DEN-UNT-300',
    name: 'Ergonomic Dental Chair Unit with Intraoral Camera & LED Light',
    category: 'Dental',
    manufacturer: 'Planmeca Dental Solutions',
    specs: ['Programmable chair positions', 'Fiber optic high-speed handpiece', 'Integrated ultrasonic scaler', 'Disinfection system'],
    certifications: ['ISO 13485', 'CE Marked', 'RoHS'],
    lead_time: '10 Days',
    stock_status: 'In Stock (Kigali)',
    matched_tenders: 1
  },
  {
    id: 'cat-4',
    code: 'ICU-MON-12',
    name: '12.1-Inch Multi-Parameter Modular Patient Monitor',
    category: 'Neonatal & ICU',
    manufacturer: 'Mindray Healthcare',
    specs: ['ECG, SpO2, NIBP, 2-Temp, 2-IBP, EtCO2', '120-hour graphic trend', 'Defibrillator sync', 'Central station wireless'],
    certifications: ['ISO 13485', 'CE 0482', 'FDA Cleared'],
    lead_time: '5 Days',
    stock_status: 'In Stock (Kigali)',
    matched_tenders: 1
  },
  {
    id: 'cat-5',
    code: 'RAD-CT-128',
    name: '128-Slice Ultra-Low Dose Diagnostic CT Scanner',
    category: 'Imaging & Radiology',
    manufacturer: 'Siemens Healthineers / OEM Partner',
    specs: ['0.28s rotation speed', '0.33mm isotropic resolution', 'CARE Dose4D AI reduction', 'Cardiac imaging suite'],
    certifications: ['ISO 13485', 'CE 0197', 'AERB Compliant'],
    lead_time: '30-45 Days',
    stock_status: 'Project Delivery',
    matched_tenders: 1
  },
  {
    id: 'cat-6',
    code: 'SUR-LAP-4K',
    name: 'Full Ultra HD 4K Surgical Laparoscopy Tower System',
    category: 'Surgical',
    manufacturer: 'Karl Storz / OEM Medical',
    specs: ['3840x2160 native sensor', 'Autoclavable laparoscopes', 'LED cold light source', '4K recording & documentation'],
    certifications: ['ISO 13485', 'CE Marked'],
    lead_time: '14 Days',
    stock_status: 'In Stock (Kigali)',
    matched_tenders: 0
  },
  {
    id: 'cat-7',
    code: 'AUT-ST-150',
    name: 'Horizontal Hospital Steam Sterilizer & Autoclave (150L)',
    category: 'Surgical',
    manufacturer: 'Tuttnauer Biomedical',
    specs: ['Class B pre/post vacuum', 'Microprocessor touch screen', 'Built-in thermal printer', 'Dual chamber pressure vessels'],
    certifications: ['ISO 13485', 'EN 285', 'ASME Stamped'],
    lead_time: '14-21 Days',
    stock_status: 'Available to Order',
    matched_tenders: 1
  },
  {
    id: 'cat-8',
    code: 'CON-SUR-GLV',
    name: 'Sterile Powder-Free Nitrile & Latex Surgical Gloves',
    category: 'Consumables',
    manufacturer: 'Ansell Healthcare',
    specs: ['Micro-textured finish', 'AQL 0.65 pinhole barrier', 'Beaded cuff 290mm', 'EN 455 Medical Grade'],
    certifications: ['ISO 13485', 'CE 2797', 'MOH Certified'],
    lead_time: '3 Days',
    stock_status: 'In Stock (Warehouse)',
    matched_tenders: 1
  }
];

// Helpers
function daysRemaining(date) {
  return Math.ceil((new Date(date) - new Date()) / 86400000);
}

function formatDate(date) {
  return new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(date));
}

function formatRWF(val) {
  if (!val || !Number.isFinite(val)) return 'Not available';
  if (val >= 1000000000) return `RWF ${(val / 1000000000).toFixed(1)}B`;
  if (val >= 1000000) return `RWF ${(val / 1000000).toFixed(0)}M`;
  return `RWF ${val.toLocaleString()}`;
}

function urgency(date) {
  const days = daysRemaining(date);
  return days <= 3 ? 'urgent' : days <= 7 ? 'attention' : 'normal';
}

function suitabilityClass(score) {
  return score >= 80 ? 'green' : score >= 60 ? 'yellow' : 'red';
}

function showToast(message) {
  const toast = document.querySelector('#toast');
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('show');
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove('show'), 2800);
}

// ==========================================================================
// 3. View Navigation & Routing
// ==========================================================================

const viewMap = {
  dashboard: { panelId: 'viewOverview', title: 'Overview', category: 'Procurement' },
  tenders: { panelId: 'viewPipeline', title: 'Tender Pipeline', category: 'Opportunities' },
  sources: { panelId: 'viewSources', title: 'Monitored Sources', category: 'Discovery' },
  catalogue: { panelId: 'viewCatalogue', title: 'Product Catalogue', category: 'Capabilities' }
};

let currentView = 'dashboard';

function switchView(viewKey) {
  if (!viewMap[viewKey]) viewKey = 'dashboard';
  currentView = viewKey;

  // Update sidebar active buttons
  document.querySelectorAll('.nav-item[data-view]').forEach(btn => {
    const isActive = btn.dataset.view === viewKey;
    btn.classList.toggle('active', isActive);
    if (isActive) {
      btn.setAttribute('aria-current', 'page');
    } else {
      btn.removeAttribute('aria-current');
    }
  });

  // Update view panel visibility
  document.querySelectorAll('.view-panel').forEach(panel => {
    panel.classList.remove('active');
  });

  const activePanel = document.querySelector(`#${viewMap[viewKey].panelId}`);
  if (activePanel) activePanel.classList.add('active');

  // Update breadcrumbs & title
  const breadcrumbCat = document.querySelector('#breadcrumbCategory');
  const breadcrumbView = document.querySelector('#breadcrumbView');
  if (breadcrumbCat) breadcrumbCat.textContent = viewMap[viewKey].category;
  if (breadcrumbView) breadcrumbView.textContent = viewMap[viewKey].title;
  document.title = `${viewMap[viewKey].title} | MedTender Intelligence`;

  // Trigger render for that specific view
  if (viewKey === 'dashboard') renderOverview();
  else if (viewKey === 'tenders') renderPipeline();
  else if (viewKey === 'sources') renderSources();
  else if (viewKey === 'catalogue') renderCatalogue();

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Handle all view navigation triggers
document.querySelectorAll('[data-view]').forEach(btn => {
  btn.addEventListener('click', () => {
    const targetView = btn.dataset.view;
    window.location.hash = targetView;
    switchView(targetView);
  });
});

// Deep linking via hash
window.addEventListener('hashchange', () => {
  const hash = window.location.hash.replace('#', '');
  if (viewMap[hash]) switchView(hash);
});

// ==========================================================================
// 4. View 1: Overview Dashboard Controller
// ==========================================================================

function renderOverview() {
  const open = tenders.filter(t => !['cancelled', 'lost', 'awarded'].includes(t.status)).length;
  const relevant = tenders.filter(t => Number(t.relevance_score || t.match || 0) >= 75).length;
  const closing = tenders.filter(t => {
    const d = daysRemaining(t.deadline_at);
    return d >= 0 && d <= 7;
  }).length;
  const urgent = tenders.filter(t => {
    const d = daysRemaining(t.deadline_at);
    return d >= 0 && d <= 3;
  }).length;

  const values = tenders.map(t => Number(t.tender_value)).filter(Number.isFinite);
  const pipelineTotal = values.reduce((sum, v) => sum + v, 0);

  const openCountEl = document.querySelector('#openCount');
  const relevantCountEl = document.querySelector('#relevantCount');
  const closingCountEl = document.querySelector('#closingCount');
  const sourceSummaryEl = document.querySelector('#sourceSummary');
  const urgentSummaryEl = document.querySelector('#urgentSummary');
  const pipelineValueEl = document.querySelector('#pipelineValue');
  const pipelineSummaryEl = document.querySelector('#pipelineSummary');
  const relevantBar = document.querySelector('#relevantBar');
  const closingBar = document.querySelector('#closingBar');
  const pipelineBar = document.querySelector('#pipelineBar');

  if (openCountEl) openCountEl.textContent = open;
  if (relevantCountEl) relevantCountEl.textContent = relevant;
  if (closingCountEl) closingCountEl.textContent = closing;
  if (sourceSummaryEl) sourceSummaryEl.textContent = `${tenders.length} opportunities monitored`;
  if (urgentSummaryEl) urgentSummaryEl.textContent = `${urgent} require action within 3 days`;
  if (pipelineValueEl) pipelineValueEl.textContent = formatRWF(pipelineTotal);
  if (pipelineSummaryEl) pipelineSummaryEl.textContent = `${values.length} published values included`;

  if (relevantBar) relevantBar.style.width = `${open ? Math.round((relevant / open) * 100) : 0}%`;
  if (closingBar) closingBar.style.width = `${open ? Math.min(100, Math.round((closing / open) * 100)) : 0}%`;
  if (pipelineBar) pipelineBar.style.width = values.length ? '82%' : '0%';

  // Overview Table
  const rows = document.querySelector('#tenderRows');
  const emptyState = document.querySelector('#emptyState');
  const searchInput = document.querySelector('#searchInput');
  const categoryFilter = document.querySelector('#categoryFilter');

  if (!rows) return;

  const term = searchInput ? searchInput.value.toLowerCase().trim() : '';
  const category = categoryFilter ? categoryFilter.value : '';

  const filtered = tenders.filter(tender => {
    const matchesCat = !category || tender.category === category;
    const matchesTerm = !term || `${tender.title} ${tender.procuring_entity} ${tender.category}`.toLowerCase().includes(term);
    return matchesCat && matchesTerm;
  });

  if (filtered.length === 0) {
    rows.innerHTML = '';
    if (emptyState) emptyState.hidden = false;
    return;
  }

  if (emptyState) emptyState.hidden = true;

  rows.innerHTML = filtered.map(tender => {
    const days = daysRemaining(tender.deadline_at);
    const urgencyLabel = days <= 3 ? `${days} days left` : days <= 7 ? `${days} days left` : `${days} days remaining`;

    return `
      <tr>
        <td>
          <div class="tender-name">
            <span class="tender-icon" aria-hidden="true">${tender.icon}</span>
            <div>
              <strong>${tender.title}</strong>
              <small>${tender.procuring_entity}</small>
            </div>
          </div>
        </td>
        <td>
          <div class="deadline">
            <strong>${formatDate(tender.deadline_at)}</strong>
            <small class="${urgency(tender.deadline_at)}">${urgencyLabel}</small>
          </div>
        </td>
        <td>
          <strong class="match-value">${tender.match}%</strong>
          <span class="match-label">${tender.category}</span>
        </td>
        <td>
          <span class="suitability ${suitabilityClass(tender.suitability)}">
            ${tender.suitability}% · ${tender.risk}
          </span>
        </td>
        <td>
          <button class="row-action" data-open-drawer="${tender.id}" aria-label="Open details for ${tender.title}">
            →
          </button>
        </td>
      </tr>
    `;
  }).join('');

  rows.querySelectorAll('[data-open-drawer]').forEach(btn => {
    btn.addEventListener('click', () => openTenderDrawer(btn.dataset.openDrawer));
  });
}

// Overview search & reset
const overviewSearchInput = document.querySelector('#searchInput');
const overviewCategoryFilter = document.querySelector('#categoryFilter');
const overviewFilterBtn = document.querySelector('#filterButton');

if (overviewSearchInput) overviewSearchInput.addEventListener('input', renderOverview);
if (overviewCategoryFilter) overviewCategoryFilter.addEventListener('change', renderOverview);
if (overviewFilterBtn) {
  overviewFilterBtn.addEventListener('click', () => {
    if (overviewSearchInput) overviewSearchInput.value = '';
    if (overviewCategoryFilter) overviewCategoryFilter.value = '';
    renderOverview();
    showToast('Overview filters reset.');
  });
}

// ==========================================================================
// 5. View 2: Tender Pipeline Controller
// ==========================================================================

let pipelineSelectedStage = '';

function renderPipeline() {
  const pipelineRows = document.querySelector('#pipelineTableRows');
  const pipelineEmptyState = document.querySelector('#pipelineEmptyState');
  const searchInput = document.querySelector('#pipelineSearchInput');
  const categoryFilter = document.querySelector('#pipelineCategoryFilter');
  const riskFilter = document.querySelector('#pipelineRiskFilter');
  const sortBy = document.querySelector('#pipelineSortBy');

  // Update stage counts
  const stageCounts = {
    all: tenders.length,
    new: tenders.filter(t => ['new', 'review'].includes(t.status)).length,
    interested: tenders.filter(t => t.status === 'interested').length,
    bid_preparation: tenders.filter(t => t.status === 'bid_preparation').length,
    submitted: tenders.filter(t => t.status === 'submitted').length,
    awarded: tenders.filter(t => t.status === 'awarded').length
  };

  const cAll = document.querySelector('#countStageAll');
  const cNew = document.querySelector('#countStageNew');
  const cInt = document.querySelector('#countStageInterested');
  const cPrep = document.querySelector('#countStagePrep');
  const cSub = document.querySelector('#countStageSubmitted');
  const cAwd = document.querySelector('#countStageAwarded');

  if (cAll) cAll.textContent = stageCounts.all;
  if (cNew) cNew.textContent = stageCounts.new;
  if (cInt) cInt.textContent = stageCounts.interested;
  if (cPrep) cPrep.textContent = stageCounts.bid_preparation;
  if (cSub) cSub.textContent = stageCounts.submitted;
  if (cAwd) cAwd.textContent = stageCounts.awarded;

  // Pipeline summary metrics
  const activeTenders = tenders.filter(t => !['cancelled', 'lost'].includes(t.status));
  const totalPipelineVal = activeTenders.reduce((sum, t) => sum + (t.tender_value || 0), 0);
  const prepTenders = tenders.filter(t => t.status === 'bid_preparation').length;
  const avgSuit = Math.round(tenders.reduce((sum, t) => sum + (t.suitability || 0), 0) / (tenders.length || 1));

  const pTotalVal = document.querySelector('#pipelineTotalValue');
  const pActiveCount = document.querySelector('#pipelineActiveCount');
  const pPrepCount = document.querySelector('#pipelinePrepCount');
  const pAvgMatch = document.querySelector('#pipelineAvgMatch');

  if (pTotalVal) pTotalVal.textContent = formatRWF(totalPipelineVal);
  if (pActiveCount) pActiveCount.textContent = `${activeTenders.length} active opportunities`;
  if (pPrepCount) pPrepCount.textContent = prepTenders;
  if (pAvgMatch) pAvgMatch.textContent = `${avgSuit}%`;

  // Sidebar badge sync
  const sbPipeCount = document.querySelector('#sidebarPipelineCount');
  if (sbPipeCount) sbPipeCount.textContent = tenders.length;

  if (!pipelineRows) return;

  const term = searchInput ? searchInput.value.toLowerCase().trim() : '';
  const cat = categoryFilter ? categoryFilter.value : '';
  const risk = riskFilter ? riskFilter.value : '';
  const sort = sortBy ? sortBy.value : 'deadline';

  let filtered = tenders.filter(t => {
    // Stage check
    if (pipelineSelectedStage === 'new' && !['new', 'review'].includes(t.status)) return false;
    if (pipelineSelectedStage && pipelineSelectedStage !== 'new' && t.status !== pipelineSelectedStage) return false;

    // Filters check
    if (cat && t.category !== cat) return false;
    if (risk && t.risk !== risk) return false;
    if (term && !`${t.ref} ${t.title} ${t.procuring_entity} ${t.category}`.toLowerCase().includes(term)) return false;

    return true;
  });

  // Sorting
  filtered.sort((a, b) => {
    if (sort === 'deadline') return new Date(a.deadline_at) - new Date(b.deadline_at);
    if (sort === 'relevance') return (b.suitability || 0) - (a.suitability || 0);
    if (sort === 'value') return (b.tender_value || 0) - (a.tender_value || 0);
    return 0;
  });

  if (filtered.length === 0) {
    pipelineRows.innerHTML = '';
    if (pipelineEmptyState) pipelineEmptyState.hidden = false;
    return;
  }

  if (pipelineEmptyState) pipelineEmptyState.hidden = true;

  pipelineRows.innerHTML = filtered.map(t => {
    const days = daysRemaining(t.deadline_at);
    const urgencyLabel = days <= 3 ? `${days} days left` : days <= 7 ? `${days} days left` : `${days} days left`;
    const stageClass = t.status === 'bid_preparation' ? 'prep' : t.status;
    const stageLabels = {
      new: 'New Discovery',
      review: 'Under Review',
      interested: 'Qualified',
      bid_preparation: 'In Bid Prep',
      submitted: 'Submitted',
      awarded: 'Awarded'
    };

    return `
      <tr>
        <td>
          <div class="tender-name">
            <span class="tender-icon" aria-hidden="true">${t.icon}</span>
            <div>
              <strong>${t.title}</strong>
              <small style="font-family:'DM Mono',monospace;color:var(--teal)">${t.ref || 'REF: PENDING'}</small>
            </div>
          </div>
        </td>
        <td>
          <strong>${t.procuring_entity}</strong>
          <small class="match-label">${t.category}</small>
        </td>
        <td>
          <strong>${formatRWF(t.tender_value)}</strong>
        </td>
        <td>
          <div class="deadline">
            <strong>${formatDate(t.deadline_at)}</strong>
            <small class="${urgency(t.deadline_at)}">${urgencyLabel}</small>
          </div>
        </td>
        <td>
          <strong class="match-value">${t.match}%</strong>
        </td>
        <td>
          <span class="suitability ${suitabilityClass(t.suitability)}">${t.suitability}% · ${t.risk}</span>
        </td>
        <td>
          <select class="stage-select" data-update-stage="${t.id}" aria-label="Change stage for ${t.title}">
            <option value="new" ${t.status === 'new' ? 'selected' : ''}>New Discovery</option>
            <option value="review" ${t.status === 'review' ? 'selected' : ''}>Under Review</option>
            <option value="interested" ${t.status === 'interested' ? 'selected' : ''}>Qualified</option>
            <option value="bid_preparation" ${t.status === 'bid_preparation' ? 'selected' : ''}>In Bid Prep</option>
            <option value="submitted" ${t.status === 'submitted' ? 'selected' : ''}>Submitted</option>
            <option value="awarded" ${t.status === 'awarded' ? 'selected' : ''}>Won / Awarded</option>
          </select>
        </td>
        <td>
          <button class="row-action" data-open-drawer="${t.id}" aria-label="View tender decision facts">
            →
          </button>
        </td>
      </tr>
    `;
  }).join('');

  // Attach stage changer listeners
  pipelineRows.querySelectorAll('[data-update-stage]').forEach(selectEl => {
    selectEl.addEventListener('change', (e) => {
      const id = selectEl.dataset.updateStage;
      const newStage = e.target.value;
      const targetTender = tenders.find(t => t.id === id);
      if (targetTender) {
        targetTender.status = newStage;
        showToast(`Tender stage updated to: ${newStage.replace(/_/g, ' ').toUpperCase()}`);
        renderPipeline();
        renderOverview();
      }
    });
  });

  pipelineRows.querySelectorAll('[data-open-drawer]').forEach(btn => {
    btn.addEventListener('click', () => openTenderDrawer(btn.dataset.openDrawer));
  });
}

// Stage pills click handler
document.querySelectorAll('.stage-pill').forEach(pill => {
  pill.addEventListener('click', () => {
    document.querySelectorAll('.stage-pill').forEach(p => {
      p.classList.remove('active');
      p.setAttribute('aria-selected', 'false');
    });
    pill.classList.add('active');
    pill.setAttribute('aria-selected', 'true');
    pipelineSelectedStage = pill.dataset.stage;
    renderPipeline();
  });
});

const pipeSearch = document.querySelector('#pipelineSearchInput');
const pipeCat = document.querySelector('#pipelineCategoryFilter');
const pipeRisk = document.querySelector('#pipelineRiskFilter');
const pipeSort = document.querySelector('#pipelineSortBy');

if (pipeSearch) pipeSearch.addEventListener('input', renderPipeline);
if (pipeCat) pipeCat.addEventListener('change', renderPipeline);
if (pipeRisk) pipeRisk.addEventListener('change', renderPipeline);
if (pipeSort) pipeSort.addEventListener('change', renderPipeline);

const pipelineExportBtn = document.querySelector('#pipelineExportBtn');
if (pipelineExportBtn) {
  pipelineExportBtn.addEventListener('click', () => {
    const csvRows = [
      ['Reference', 'Title', 'Entity', 'Category', 'Value (RWF)', 'Deadline', 'Product Match %', 'Suitability %', 'Stage'],
      ...tenders.map(t => [t.ref, `"${t.title.replace(/"/g, '""')}"`, `"${t.procuring_entity}"`, t.category, t.tender_value || '', t.deadline_at, t.match, t.suitability, t.status])
    ];
    const csvContent = "data:text/csv;charset=utf-8," + csvRows.map(e => e.join(",")).join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `medtender_pipeline_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast('Tender pipeline exported to CSV.');
  });
}

// ==========================================================================
// 6. View 3: Tender Sources Controller
// ==========================================================================

function renderSources() {
  const container = document.querySelector('#sourcesGridContainer');
  const emptyState = document.querySelector('#sourcesEmptyState');
  const searchInput = document.querySelector('#sourceSearchInput');
  const categoryFilter = document.querySelector('#sourceCategoryFilter');
  const methodFilter = document.querySelector('#sourceMethodFilter');
  const statusFilter = document.querySelector('#sourceStatusFilter');

  // Summary counts
  const totalCount = sources.length;
  const activeCount = sources.filter(s => s.is_active).length;
  const totalTendersDiscovered = sources.reduce((sum, s) => sum + (s.tenders_collected_count || 0), 0);

  const sTotalEl = document.querySelector('#sourcesTotalCount');
  const sActiveEl = document.querySelector('#sourcesActiveCount');
  const sTendersEl = document.querySelector('#sourcesTotalTenders');
  const sbSourcesCount = document.querySelector('#sidebarSourcesCount');
  const sidebarScanStatus = document.querySelector('#sidebarScanStatus');

  if (sTotalEl) sTotalEl.textContent = totalCount;
  if (sActiveEl) sActiveEl.textContent = `${activeCount} online & active`;
  if (sTendersEl) sTendersEl.textContent = totalTendersDiscovered;
  if (sbSourcesCount) sbSourcesCount.textContent = totalCount;
  if (sidebarScanStatus) sidebarScanStatus.textContent = `Monitoring ${activeCount} sources`;

  if (!container) return;

  const term = searchInput ? searchInput.value.toLowerCase().trim() : '';
  const cat = categoryFilter ? categoryFilter.value : '';
  const method = methodFilter ? methodFilter.value : '';
  const stat = statusFilter ? statusFilter.value : '';

  const filtered = sources.filter(s => {
    if (cat && s.category !== cat) return false;
    if (method && s.collection_method !== method) return false;
    if (stat === 'active' && !s.is_active) return false;
    if (stat === 'inactive' && s.is_active) return false;
    if (term && !`${s.name} ${s.organization} ${s.website}`.toLowerCase().includes(term)) return false;
    return true;
  });

  if (filtered.length === 0) {
    container.innerHTML = '';
    if (emptyState) emptyState.hidden = false;
    return;
  }

  if (emptyState) emptyState.hidden = true;

  container.innerHTML = filtered.map(s => {
    const categoryBadgeClass = s.category === 'government_portal' ? 'gov' : s.category === 'hospital' ? 'hospital' : 'ngo';
    const methodBadgeClass = s.collection_method === 'api' ? 'api' : s.collection_method === 'manual_import' ? 'manual' : 'scraper';
    const methodLabel = s.collection_method === 'api' ? 'REST API' : s.collection_method === 'manual_import' ? 'Manual Import' : s.collection_method === 'rss' ? 'RSS Feed' : 'Web Scraper';

    return `
      <article class="source-card" data-source-id="${s.id}">
        <div>
          <div class="source-header">
            <div>
              <h3>${s.name}</h3>
              <a href="${s.website}" target="_blank" rel="noopener noreferrer">${s.website} ↗</a>
            </div>
            <span class="status-tag ${s.is_active ? 'active' : 'inactive'}">
              <span class="status-dot" style="${s.is_active ? '' : 'background:#9aa6a5;box-shadow:none'}"></span>
              ${s.is_active ? 'Active' : 'Deactivated'}
            </span>
          </div>

          <div class="source-badges" style="margin-top: 10px;">
            <span class="badge ${categoryBadgeClass}">${s.category.replace(/_/g, ' ').toUpperCase()}</span>
            <span class="badge ${methodBadgeClass}">${methodLabel}</span>
            <span class="badge" style="background:#edf3f2;color:#4f6161">Every ${s.scan_frequency_hours}h</span>
          </div>
        </div>

        <div class="source-meta">
          <div>
            <small>Last successful scan</small>
            <strong>${s.last_scan_at}</strong>
          </div>
          <div>
            <small>Tenders collected</small>
            <strong style="color:var(--teal)">${s.tenders_collected_count} discovered</strong>
          </div>
          <div>
            <small>Compliance status</small>
            <strong style="color:var(--green)">✓ Robots.txt Allowed</strong>
          </div>
          <div>
            <small>Organization</small>
            <strong>${s.organization || 'Public Agency'}</strong>
          </div>
        </div>

        <div class="source-actions">
          <button class="primary-button" data-scan-source="${s.id}" ${s.is_active ? '' : 'disabled'}>
            ↻ Scan Source
          </button>
          <button class="outline-button" data-toggle-source="${s.id}">
            ${s.is_active ? 'Deactivate' : 'Reactivate'}
          </button>
        </div>
      </article>
    `;
  }).join('');

  // Attach action handlers
  container.querySelectorAll('[data-scan-source]').forEach(btn => {
    btn.addEventListener('click', () => {
      const srcId = btn.dataset.scanSource;
      const src = sources.find(s => s.id === srcId);
      if (src) {
        btn.textContent = 'Scanning...';
        btn.disabled = true;
        setTimeout(() => {
          src.last_scan_at = 'Just now';
          src.tenders_collected_count += Math.floor(Math.random() * 3);
          renderSources();
          showToast(`Completed compliant scan for: ${src.name}`);
        }, 600);
      }
    });
  });

  container.querySelectorAll('[data-toggle-source]').forEach(btn => {
    btn.addEventListener('click', () => {
      const srcId = btn.dataset.toggleSource;
      const src = sources.find(s => s.id === srcId);
      if (src) {
        src.is_active = !src.is_active;
        showToast(`Source "${src.name}" ${src.is_active ? 'reactivated' : 'deactivated'}.`);
        renderSources();
      }
    });
  });
}

const sourceSearch = document.querySelector('#sourceSearchInput');
const sourceCat = document.querySelector('#sourceCategoryFilter');
const sourceMethod = document.querySelector('#sourceMethodFilter');
const sourceStatus = document.querySelector('#sourceStatusFilter');

if (sourceSearch) sourceSearch.addEventListener('input', renderSources);
if (sourceCat) sourceCat.addEventListener('change', renderSources);
if (sourceMethod) sourceMethod.addEventListener('change', renderSources);
if (sourceStatus) sourceStatus.addEventListener('change', renderSources);

const scanAllSourcesBtn = document.querySelector('#scanAllSourcesBtn');
if (scanAllSourcesBtn) {
  scanAllSourcesBtn.addEventListener('click', () => {
    showToast('Executing automated discovery scan across all 8 Rwanda procurement portals...');
    setTimeout(() => {
      sources.forEach(s => {
        if (s.is_active) s.last_scan_at = 'Just now';
      });
      renderSources();
      showToast('All sources synchronized. 0 compliance violations.');
    }, 800);
  });
}

// ==========================================================================
// 7. View 4: Product Catalogue Controller
// ==========================================================================

function renderCatalogue() {
  const container = document.querySelector('#catalogueGridContainer');
  const emptyState = document.querySelector('#catalogueEmptyState');
  const searchInput = document.querySelector('#catalogueSearchInput');
  const categoryFilter = document.querySelector('#catalogueCategoryFilter');

  const catTotalEl = document.querySelector('#catalogueTotalCount');
  const catMatchedEl = document.querySelector('#catalogueMatchedCount');
  const sbCatCount = document.querySelector('#sidebarCatalogueCount');

  const matchedItems = catalogue.filter(c => c.matched_tenders > 0).length;
  if (catTotalEl) catTotalEl.textContent = catalogue.length;
  if (catMatchedEl) catMatchedEl.textContent = matchedItems;
  if (sbCatCount) sbCatCount.textContent = catalogue.length;

  if (!container) return;

  const term = searchInput ? searchInput.value.toLowerCase().trim() : '';
  const cat = categoryFilter ? categoryFilter.value : '';

  const filtered = catalogue.filter(p => {
    if (cat && p.category !== cat) return false;
    if (term && !`${p.code} ${p.name} ${p.manufacturer} ${p.specs.join(' ')}`.toLowerCase().includes(term)) return false;
    return true;
  });

  if (filtered.length === 0) {
    container.innerHTML = '';
    if (emptyState) emptyState.hidden = false;
    return;
  }

  if (emptyState) emptyState.hidden = true;

  container.innerHTML = filtered.map(p => {
    return `
      <article class="product-card">
        <div>
          <div class="product-card-top">
            <span class="product-code">${p.code}</span>
            <span class="badge" style="background:#e3f1ed;color:var(--teal-dark)">${p.category}</span>
          </div>

          <h3>${p.name}</h3>
          <small style="color:var(--muted);display:block;margin-bottom:10px;">OEM: ${p.manufacturer}</small>

          <div class="product-specs">
            ${p.specs.map(s => `<span class="spec-tag">${s}</span>`).join('')}
          </div>
        </div>

        <div>
          <div style="margin: 12px 0 8px; display: flex; gap: 5px; flex-wrap: wrap;">
            ${p.certifications.map(c => `<span class="cert-tag">✓ ${c}</span>`).join('')}
          </div>

          <div class="product-footer">
            <div>
              <small style="color:var(--muted)">Lead time:</small>
              <strong>${p.lead_time}</strong>
            </div>
            <div>
              <span class="badge" style="${p.matched_tenders ? 'background:var(--mint);color:var(--teal-dark)' : 'background:#edf3f2;color:var(--muted)'}">
                ${p.matched_tenders ? `${p.matched_tenders} Linked Tender` : 'No Active Bid'}
              </span>
            </div>
          </div>
        </div>
      </article>
    `;
  }).join('');
}

const catSearch = document.querySelector('#catalogueSearchInput');
const catCat = document.querySelector('#catalogueCategoryFilter');

if (catSearch) catSearch.addEventListener('input', renderCatalogue);
if (catCat) catCat.addEventListener('change', renderCatalogue);

// ==========================================================================
// 8. Modals & Drawer Management
// ==========================================================================

const drawer = document.querySelector('#tenderDrawer');
const drawerBackdrop = document.querySelector('#drawerBackdrop');
const closeDrawerBtn = document.querySelector('#closeDrawer');

function openTenderDrawer(id) {
  const tender = tenders.find(item => item.id === id);
  if (!tender || !drawer) return;

  const days = daysRemaining(tender.deadline_at);
  const drawerContent = document.querySelector('#drawerContent');

  if (drawerContent) {
    drawerContent.innerHTML = `
      <h2 class="drawer-title" id="drawerTitle">${tender.title}</h2>
      <p class="drawer-entity">${tender.procuring_entity} · ${tender.category}</p>

      <div class="drawer-score-grid" aria-label="Evaluation scores">
        <div class="drawer-score">
          <strong>${tender.match}%</strong>
          <small>Product match</small>
        </div>
        <div class="drawer-score">
          <strong>${tender.technical}%</strong>
          <small>Technical match</small>
        </div>
        <div class="drawer-score">
          <strong>${tender.suitability}%</strong>
          <small>Bid suitability</small>
        </div>
      </div>

      <section class="drawer-section">
        <h3>Official Decision Facts</h3>
        <div class="drawer-facts">
          <div><small>Reference number</small><strong>${tender.ref}</strong></div>
          <div><small>Estimated value</small><strong>${formatRWF(tender.tender_value)}</strong></div>
          <div><small>Submission deadline</small><strong>${formatDate(tender.deadline_at)}</strong></div>
          <div><small>Time remaining</small><strong class="${urgency(tender.deadline_at)}">${days} days</strong></div>
          <div><small>Financial risk level</small><strong>${tender.risk}</strong></div>
          <div><small>Bid security required</small><strong>${tender.security}</strong></div>
          <div><small>Manufacturer OEM authorization</small><strong>${tender.authorization}</strong></div>
          <div><small>Missing compliance documents</small><strong>${tender.missing}</strong></div>
        </div>
      </section>

      <section class="drawer-section">
        <h3>Intelligence Recommendation</h3>
        <div class="drawer-recommendation">
          <strong>${tender.recommendation}</strong>
          Specification extraction and qualification matrix verified. Ensure ISO 13485 certificates and local supplier registration are attached before bid submission.
        </div>
        <div class="drawer-actions">
          <button class="outline-button" data-drawer-action="review">Save to Watchlist</button>
          <button class="primary-button" data-drawer-action="advance">Advance to Bid Prep</button>
        </div>
      </section>
    `;
  }

  drawer.classList.add('open');
  drawer.setAttribute('aria-hidden', 'false');
  if (drawerBackdrop) drawerBackdrop.hidden = false;
  if (closeDrawerBtn) closeDrawerBtn.focus();

  document.querySelectorAll('[data-drawer-action]').forEach(btn => {
    btn.addEventListener('click', () => {
      const action = btn.dataset.drawerAction;
      if (action === 'advance') {
        tender.status = 'bid_preparation';
        renderPipeline();
        renderOverview();
        showToast(`Tender advanced to Bid Preparation workspace.`);
      } else {
        showToast('Tender saved to watchlist.');
      }
      closeTenderDrawer();
    });
  });
}

function closeTenderDrawer() {
  if (!drawer) return;
  drawer.classList.remove('open');
  drawer.setAttribute('aria-hidden', 'true');
  if (drawerBackdrop) drawerBackdrop.hidden = true;
}

if (closeDrawerBtn) closeDrawerBtn.addEventListener('click', closeTenderDrawer);
if (drawerBackdrop) drawerBackdrop.addEventListener('click', closeTenderDrawer);

// Add Source Modal
const openAddSourceBtn = document.querySelector('#openAddSourceBtn');
const addSourceModalBackdrop = document.querySelector('#addSourceModalBackdrop');
const closeAddSourceModal = document.querySelector('#closeAddSourceModal');
const cancelAddSourceBtn = document.querySelector('#cancelAddSourceBtn');
const addSourceForm = document.querySelector('#addSourceForm');

function toggleAddSourceModal(show) {
  if (addSourceModalBackdrop) addSourceModalBackdrop.hidden = !show;
  if (show && document.querySelector('#newSourceName')) {
    document.querySelector('#newSourceName').focus();
  }
}

if (openAddSourceBtn) openAddSourceBtn.addEventListener('click', () => toggleAddSourceModal(true));
if (closeAddSourceModal) closeAddSourceModal.addEventListener('click', () => toggleAddSourceModal(false));
if (cancelAddSourceBtn) cancelAddSourceBtn.addEventListener('click', () => toggleAddSourceModal(false));

if (addSourceForm) {
  addSourceForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const name = document.querySelector('#newSourceName').value.trim();
    const website = document.querySelector('#newSourceWebsite').value.trim();
    const org = document.querySelector('#newSourceOrganization').value.trim();
    const category = document.querySelector('#newSourceCategory').value;
    const method = document.querySelector('#newSourceMethod').value;
    const frequency = parseInt(document.querySelector('#newSourceFrequency').value, 10) || 24;
    const manual = document.querySelector('#newSourceManual').checked;

    if (!name || !website) {
      showToast('Please provide both Source Name and Website URL.');
      return;
    }

    const newSource = {
      id: `src-${Date.now()}`,
      name,
      website,
      organization: org || name,
      category,
      collection_method: method,
      is_active: true,
      scan_frequency_hours: frequency,
      robots_txt_allows_collection: true,
      requires_manual_import: manual,
      last_scan_at: 'Just registered',
      last_successful_scan_at: 'Pending initial scan',
      last_error: null,
      tenders_collected_count: 0
    };

    sources.unshift(newSource);
    toggleAddSourceModal(false);
    addSourceForm.reset();
    renderSources();
    showToast(`Monitored source "${name}" registered successfully.`);
  });
}

// Add Tender Modal
const openAddTenderBtn = document.querySelector('#openAddTenderBtn');
const addTenderModalBackdrop = document.querySelector('#addTenderModalBackdrop');
const closeAddTenderModal = document.querySelector('#closeAddTenderModal');
const cancelAddTenderBtn = document.querySelector('#cancelAddTenderBtn');
const addTenderForm = document.querySelector('#addTenderForm');

function toggleAddTenderModal(show) {
  if (addTenderModalBackdrop) addTenderModalBackdrop.hidden = !show;
  if (show && document.querySelector('#newTenderTitle')) {
    document.querySelector('#newTenderTitle').focus();
  }
}

if (openAddTenderBtn) openAddTenderBtn.addEventListener('click', () => toggleAddTenderModal(true));
if (closeAddTenderModal) closeAddTenderModal.addEventListener('click', () => toggleAddTenderModal(false));
if (cancelAddTenderBtn) cancelAddTenderBtn.addEventListener('click', () => toggleAddTenderModal(false));

if (addTenderForm) {
  addTenderForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const title = document.querySelector('#newTenderTitle').value.trim();
    const ref = document.querySelector('#newTenderRef').value.trim();
    const entity = document.querySelector('#newTenderEntity').value.trim();
    const category = document.querySelector('#newTenderCategory').value;
    const deadline = document.querySelector('#newTenderDeadline').value;
    const val = parseFloat(document.querySelector('#newTenderValue').value) || 0;
    const risk = document.querySelector('#newTenderRisk').value;

    if (!title || !ref || !entity) {
      showToast('Please fill out all required tender fields.');
      return;
    }

    const newTender = {
      id: `tender-${Date.now()}`,
      ref,
      title,
      procuring_entity: entity,
      category,
      tender_value: val,
      currency: 'RWF',
      deadline_at: deadline || new Date(Date.now() + 14 * 86400000).toISOString(),
      relevance_score: 85,
      match: 88,
      technical: 85,
      suitability: 82,
      risk,
      security: val ? `RWF ${(val * 0.02).toLocaleString()}` : 'Not required',
      authorization: 'Required',
      missing: 1,
      status: 'new',
      recommendation: 'New opportunity registered',
      icon: (category.slice(0, 3)).toUpperCase()
    };

    tenders.unshift(newTender);
    toggleAddTenderModal(false);
    addTenderForm.reset();
    renderPipeline();
    renderOverview();
    showToast(`Tender opportunity "${ref}" added to pipeline.`);
  });
}

// Help Centre Modal
const helpCentreBtn = document.querySelector('#helpCentreBtn');
const helpCentreModalBackdrop = document.querySelector('#helpCentreModalBackdrop');
const closeHelpCentreModal = document.querySelector('#closeHelpCentreModal');
const dismissHelpBtn = document.querySelector('#dismissHelpBtn');

function toggleHelpModal(show) {
  if (helpCentreModalBackdrop) helpCentreModalBackdrop.hidden = !show;
}

if (helpCentreBtn) helpCentreBtn.addEventListener('click', () => toggleHelpModal(true));
if (closeHelpCentreModal) closeHelpCentreModal.addEventListener('click', () => toggleHelpModal(false));
if (dismissHelpBtn) dismissHelpBtn.addEventListener('click', () => toggleHelpModal(false));

const openAddProductBtn = document.querySelector('#openAddProductBtn');
if (openAddProductBtn) {
  openAddProductBtn.addEventListener('click', () => {
    showToast('Add new medical equipment/consumable: specify OEM specs and ISO certificates.');
  });
}

const readinessReportBtn = document.querySelector('#readinessReportBtn');
if (readinessReportBtn) {
  readinessReportBtn.addEventListener('click', () => {
    showToast('Bid readiness audit report generated. Technical capacity: 82%, Document availability: 68%.');
  });
}

const scanButton = document.querySelector('#scanButton');
if (scanButton) {
  scanButton.addEventListener('click', () => {
    showToast('Scanning all Rwanda procurement portals for medical opportunities...');
    setTimeout(() => {
      renderOverview();
      showToast('Scan complete. Current opportunity queue updated.');
    }, 600);
  });
}

const notificationButton = document.querySelector('#notificationButton');
if (notificationButton) {
  notificationButton.addEventListener('click', () => {
    showToast('3 priority alerts: 1 new tender matched at RBC, 1 deadline in 48h at CHUK, 1 ISO certificate verified.');
  });
}

// Global Keyboard handlers (Escape key)
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeTenderDrawer();
    toggleAddSourceModal(false);
    toggleAddTenderModal(false);
    toggleHelpModal(false);
    if (profileDropdown && profileDropdown.classList.contains('open')) {
      profileDropdown.classList.remove('open');
      if (profileChipBtn) profileChipBtn.setAttribute('aria-expanded', 'false');
    }
  }
});

// Format dynamic header date
const currentDateEl = document.querySelector('#currentDate');
if (currentDateEl) {
  const now = new Date();
  const dateOptions = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
  currentDateEl.textContent = new Intl.DateTimeFormat('en-GB', dateOptions).format(now);
}

// Initial initialization
loadUserProfile();
const initialHash = window.location.hash.replace('#', '');
switchView(initialHash && viewMap[initialHash] ? initialHash : 'dashboard');
