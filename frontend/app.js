const API_BASE = window.localStorage.getItem('medtender_api_base') || 
  (window.location.port === '8000' || window.location.protocol.startsWith('http') ? window.location.origin : 'http://localhost:8000');

// ==========================================================================
// 1. Authentication & Session Management
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
      // Fallback
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

// ==========================================================================
// 2. Company Product Catalogue & Inventory Data Store
// ==========================================================================

let catalogue = [
  {
    id: 'cat-1',
    code: 'NEO-WRM-500',
    name: 'Advanced Infant Radiant Warmer & Phototherapy System',
    category: 'Neonatal & ICU',
    manufacturer: 'MedTech Global / OEM Partner',
    specs: [
      'Microprocessor servo-controlled skin temperature (34-38°C ±0.1°C)',
      'Integrated high-intensity LED phototherapy (450-470nm, >40 µW/cm²/nm)',
      'APGAR 1/5/10 minute acoustic timer & digital lux display',
      'Electric tilting bed ±15° with built-in X-ray cassette tray',
      'Dual skin sensors (T1/T2) & ambient temperature compensation'
    ],
    certifications: ['ISO 13485:2016', 'CE 0123', 'FDA 510(k)', 'Rwanda FDA License'],
    lead_time: '5 Days (In Stock)',
    warehouse_stock: 6,
    min_safe_stock: 4,
    stock_status: 'IN_STOCK',
    matched_tenders: 1
  },
  {
    id: 'cat-2',
    code: 'LAB-ANA-800',
    name: 'Fully Automated High-Throughput Clinical Chemistry Analyzer',
    category: 'Laboratory',
    manufacturer: 'DiaSys Diagnostic Systems Germany',
    specs: [
      'Throughput: 800 photometric tests/hour + 400 ISE/hour',
      '90 refrigerated onboard reagent positions (2-8°C constant)',
      'Bi-directional LIS HL7 interface with internal barcode scanner',
      'Automatic 8-step cuvette washing with water blank testing',
      'STAT emergency sample priority access in continuous loading'
    ],
    certifications: ['ISO 13485:2016', 'CE-IVD Marked', 'WHO Prequalified Reagents'],
    lead_time: '14-21 Days',
    warehouse_stock: 2,
    min_safe_stock: 2,
    stock_status: 'SAFE_BUFFER',
    matched_tenders: 1
  },
  {
    id: 'cat-3',
    code: 'DEN-UNT-300',
    name: 'Ergonomic Dental Operatory Unit & Digital Imaging Suite',
    category: 'Dental',
    manufacturer: 'Planmeca Dental Solutions',
    specs: [
      'Electro-mechanical chair with 4 programmable memory positions',
      '5-instrument doctor console with brushless optical micromotor (40k RPM)',
      'Integrated intraoral HD camera with 21.5" medical-grade display',
      'Automated waterline disinfection system (continuous suction flush)',
      'Shadowless LED operating light (8,000 - 45,000 Lux adjustable)'
    ],
    certifications: ['ISO 13485', 'CE Marked', 'RoHS Green Certified'],
    lead_time: '7 Days (In Stock)',
    warehouse_stock: 4,
    min_safe_stock: 3,
    stock_status: 'IN_STOCK',
    matched_tenders: 1
  },
  {
    id: 'cat-4',
    code: 'ICU-MON-12',
    name: '12.1-Inch Multi-Parameter Modular ICU Patient Monitor',
    category: 'Neonatal & ICU',
    manufacturer: 'Mindray Healthcare',
    specs: [
      '12.1" capacitive anti-glare touchscreen display (800x600)',
      'Standard: 3/5-Lead ECG, Mindray SpO2 (Nellcor compatible), NIBP, 2-Temp, HR/PR',
      'Advanced modular slots: 2-IBP, Microstream EtCO2 sidestream module',
      'Battery: Rechargeable lithium-ion with >4.5 hours continuous monitoring',
      '120-hour full graphical and tabular trend review with arrhythmia analysis'
    ],
    certifications: ['ISO 13485:2016', 'CE 0482', 'FDA Cleared', 'IEC 60601-1'],
    lead_time: '3 Days (Fast Dispatch)',
    warehouse_stock: 2,
    min_safe_stock: 6,
    stock_status: 'LOW_STOCK_URGENT',
    matched_tenders: 2
  },
  {
    id: 'cat-5',
    code: 'RAD-CT-128',
    name: '128-Slice High-Speed Diagnostic Whole-Body CT Scanner',
    category: 'Imaging & Radiology',
    manufacturer: 'Siemens Healthineers / Partner OEM',
    specs: [
      '0.33s gantry rotation speed with 128 slices reconstructed per rotation',
      'Stellar 3D detector with 0.33mm isotropic spatial resolution',
      'CARE Dose4D real-time AI radiation reduction modulation (up to 60% lower dose)',
      '80 kW high-power Athlon X-ray tube with liquid metal bearing',
      'Cardiac CT angiography suite with prospective & retrospective ECG gating'
    ],
    certifications: ['ISO 13485', 'CE 0197', 'AERB Compliant', 'FDA 510(k)'],
    lead_time: '30-45 Days (Turnkey Installation)',
    warehouse_stock: 1,
    min_safe_stock: 1,
    stock_status: 'PROJECT_DELIVERY',
    matched_tenders: 1
  },
  {
    id: 'cat-6',
    code: 'SUR-LAP-4K',
    name: '4K Ultra HD Endoscopic Surgical Laparoscopy Tower System',
    category: 'Surgical',
    manufacturer: 'Karl Storz / OEM Partner',
    specs: [
      'Native 3840x2160 4K UHD sensor with optical zoom laparoscopes',
      '300W High-output LED cold light source (50,000 hour lifespan)',
      'Automatic CO2 insufflator (45 L/min with heated gas tubing)',
      'Autoclavable HD camera head and 5.5mm / 10mm 0°/30° rigid telescopes'
    ],
    certifications: ['ISO 13485:2016', 'CE Marked'],
    lead_time: '10 Days',
    warehouse_stock: 3,
    min_safe_stock: 2,
    stock_status: 'IN_STOCK',
    matched_tenders: 0
  },
  {
    id: 'cat-7',
    code: 'AUT-ST-150',
    name: '150-Litre Horizontal Hospital Steam Sterilizer & Autoclave',
    category: 'Surgical',
    manufacturer: 'Tuttnauer Biomedical',
    specs: [
      'Class B fractionated pre-vacuum & post-vacuum drying cycle',
      'Microprocessor PLC touch controller with built-in thermal validation printer',
      'High-grade 316L stainless steel sterilization chamber and steam jacket',
      'Double door interlock with biological safety barrier'
    ],
    certifications: ['ISO 13485', 'EN 285 European Standard', 'ASME Section VIII'],
    lead_time: '14 Days',
    warehouse_stock: 2,
    min_safe_stock: 2,
    stock_status: 'IN_STOCK',
    matched_tenders: 1
  },
  {
    id: 'cat-8',
    code: 'CON-SUR-GLV',
    name: 'Sterile Powder-Free Powdered Nitrile Surgical Gloves (Sizes 6.5 - 8.5)',
    category: 'Consumables',
    manufacturer: 'Ansell Healthcare',
    specs: [
      'Micro-textured non-slip grip in wet surgical conditions',
      'AQL 0.65 freedom from pinholes barrier protection',
      '290mm extended beaded cuff with ergonomic hand-molded formers',
      'Gamma irradiation sterilized, double-wrapped inner peel pouch'
    ],
    certifications: ['ISO 13485', 'CE 2797', 'EN 455 Parts 1-4', 'MOH Certified'],
    lead_time: '2 Days (Immediate Warehouse Pickup)',
    warehouse_stock: 400,
    min_safe_stock: 1000,
    stock_status: 'LOW_STOCK_URGENT',
    matched_tenders: 1
  }
];

// ==========================================================================
// 3. Tenders Data Store with Multi-Level Granular Specification Matching
// ==========================================================================

let tenders = [
  {
    id: 'tender-1',
    ref: '000004/G/NCB/2026/2027/RBC',
    title: 'Supply, installation and maintenance of neonatal care equipment and incubators',
    procuring_entity: 'Rwanda Biomedical Centre (RBC)',
    category: 'Medical Equipment',
    tender_value: 4500000000,
    currency: 'RWF',
    deadline_at: '2026-08-28T16:00:00+02:00',
    relevance_score: 94,
    tech_spec_match: 96,
    product_match: 92,
    coverage_rate: 100, // 3 of 3 lots supplied
    eligibility_match: 100,
    manufacturer_match: 95,
    risk: 'Low',
    security: 'RWF 4,500,000 (Bank Guarantee)',
    authorization: 'Required (Authorized OEM)',
    stock_readiness: 'IN_STOCK',
    stock_label: '⚡ In-Stock (Kigali Warehouse)',
    status: 'bid_preparation',
    recommended_action: 'BID_HIGH_FIT',
    recommendation_label: 'Bid (High Win Rate)',
    icon: 'NICU',
    lots: [
      {
        lot_number: 'Lot 1',
        title: 'Infant Radiant Warmers with Resuscitation Suite (Quantity: 24 Units)',
        matched_sku: 'NEO-WRM-500',
        matched_name: 'MedTech RadiantCare 500 Infant Warmer',
        coverage_status: 'COMPLIANT',
        specs_matrix: [
          { param: 'Skin Temperature Control', req: 'Servo-controlled 34.0°C to 38.0°C (Accuracy ±0.1°C)', sup: 'Microprocessor servo 34.0°C - 38.0°C (±0.1°C)', status: 'COMPLIANT', notes: 'Exceeds standard' },
          { param: 'Integrated Phototherapy', req: 'LED blue phototherapy (450-470nm), irradiance >35 µW/cm²/nm', sup: 'LED phototherapy 450-470nm, irradiance 42 µW/cm²/nm', status: 'COMPLIANT', notes: 'Fully compliant' },
          { param: 'APGAR Timer', req: 'Audible APGAR timer at 1, 5, 10 minutes with digital display', sup: 'Dual display APGAR timer with acoustic alert', status: 'COMPLIANT', notes: 'Exact match' },
          { param: 'Tilting Bed & X-Ray Tray', req: 'Continuous bed tilt ±15° with under-bed X-ray cassette tray', sup: 'Electric ±15° tilt with slide-out X-ray tray', status: 'COMPLIANT', notes: 'Compliant' },
          { param: 'Warranty & Local Support', req: 'Minimum 2 years comprehensive warranty + 24/7 biomedical response', sup: '3 Years full warranty + certified Kigali support engineers', status: 'COMPLIANT', notes: 'Exceeds specification' }
        ]
      },
      {
        lot_number: 'Lot 2',
        title: 'Multiparameter Neonatal / Pediatric Patient Monitors (Quantity: 30 Units)',
        matched_sku: 'ICU-MON-12',
        matched_name: 'Mindray ePM 12M Modular Patient Monitor',
        coverage_status: 'COMPLIANT',
        specs_matrix: [
          { param: 'Display Screen', req: 'Color LCD display ≥ 12.0 inches, capacitive touch operation', sup: '12.1-Inch capacitive anti-glare touchscreen', status: 'COMPLIANT', notes: 'Compliant' },
          { param: 'Neonatal Parameters', req: 'High-sensitivity neonatal ECG, SpO2 with low perfusion algorithm, NIBP', sup: 'Mindray & Nellcor SpO2, neonatal micro-cuff NIBP', status: 'COMPLIANT', notes: 'Compliant' },
          { param: 'Battery Backup', req: 'Rechargeable internal battery ≥ 4.0 hours continuous monitoring', sup: 'Lithium-ion battery providing 4.5 hours continuous use', status: 'COMPLIANT', notes: 'Compliant' },
          { param: 'EtCO2 Module', req: 'Optional slot for sidestream or mainstream EtCO2 module', sup: 'Integrated plug-and-play Microstream EtCO2 slot', status: 'COMPLIANT', notes: 'Available module' }
        ]
      }
    ],
    missing_products: [],
    critical_gaps: 'None. All specifications meet or exceed RBC requirements.',
    expansion_potential: null
  },
  {
    id: 'tender-2',
    ref: '000012/G/ICB/2026/2027/CHUK',
    title: 'Supply and framework agreement for clinical biochemistry and hematology automated analyzers',
    procuring_entity: 'University Teaching Hospital of Kigali (CHUK)',
    category: 'Laboratory',
    tender_value: 2800000000,
    currency: 'RWF',
    deadline_at: '2026-09-03T10:00:00+02:00',
    relevance_score: 89,
    tech_spec_match: 92,
    product_match: 90,
    coverage_rate: 100,
    eligibility_match: 95,
    manufacturer_match: 90,
    risk: 'Low',
    security: 'Not required (Public Hospital Framework)',
    authorization: 'Required (Manufacturer Certificate)',
    stock_readiness: 'SAFE_BUFFER',
    stock_label: '📦 14-Day Delivery',
    status: 'interested',
    recommended_action: 'BID_HIGH_FIT',
    recommendation_label: 'Bid (High Win Rate)',
    icon: 'LAB',
    lots: [
      {
        lot_number: 'Lot 1',
        title: 'Automated Chemistry Analyzer (Throughput ≥ 600 tests/hr) + Reagent Closed System',
        matched_sku: 'LAB-ANA-800',
        matched_name: 'DiaSys Respons 920 Clinical Analyzer',
        coverage_status: 'COMPLIANT',
        specs_matrix: [
          { param: 'Throughput', req: 'Minimum 600 tests/hour photometric + ISE', sup: '800 tests/hour photometric + 400 ISE/hour (1200 total)', status: 'COMPLIANT', notes: 'Significantly exceeds requirement' },
          { param: 'Onboard Reagents', req: 'Minimum 60 refrigerated positions', sup: '90 refrigerated positions (2-8°C)', status: 'COMPLIANT', notes: 'Higher capacity' },
          { param: 'LIS Interfacing', req: 'Bi-directional HL7 interface with CHUK hospital network', sup: 'Standard bi-directional HL7 & ASTM LIS drivers', status: 'COMPLIANT', notes: 'Verified compatible' },
          { param: 'Water Purification Unit', req: 'Integrated RO deionized water plant (≥ 20 L/hr)', sup: 'External Millipore RO connection supplied', status: 'VERIFICATION_REQUIRED', notes: 'Verify hospital plumbing connector' }
        ]
      }
    ],
    missing_products: [],
    critical_gaps: 'Verify RO water pressure specification with CHUK biomedical team.',
    expansion_potential: null
  },
  {
    id: 'tender-3',
    ref: '000088/G/NCB/2026/2027/RMS',
    title: 'National framework supply for surgical consumables, dialysis filters and sterilization supplies',
    procuring_entity: 'Rwanda Medical Supply Ltd (RMS)',
    category: 'Medical Consumables',
    tender_value: 5200000000,
    currency: 'RWF',
    deadline_at: '2026-09-07T15:00:00+02:00',
    relevance_score: 74,
    tech_spec_match: 80,
    product_match: 65,
    coverage_rate: 66, // 2 of 3 lots covered
    eligibility_match: 95,
    manufacturer_match: 75,
    risk: 'Medium',
    security: 'RWF 2,000,000',
    authorization: 'Required for Lot 2 & Lot 3',
    stock_readiness: 'EXPANSION_OPPORTUNITY',
    stock_label: '🚀 Expansion Opportunity',
    status: 'review',
    recommended_action: 'OPPORTUNITY_EXPANSION',
    recommendation_label: 'Expansion Opportunity',
    icon: 'SUP',
    lots: [
      {
        lot_number: 'Lot 1',
        title: 'Sterile Powder-Free Surgical Gloves (Quantity: 200,000 Pairs)',
        matched_sku: 'CON-SUR-GLV',
        matched_name: 'Ansell Gammex Sterile Surgical Gloves',
        coverage_status: 'COMPLIANT',
        specs_matrix: [
          { param: 'Pinhole Quality AQL', req: 'AQL ≤ 1.0 freedom from holes (EN 455)', sup: 'AQL 0.65 ultra-low pinhole barrier', status: 'COMPLIANT', notes: 'Exceeds standard' },
          { param: 'Packaging & Sterilization', req: 'Individually peel-packed pairs, Gamma radiation sterilized', sup: 'Gamma sterile double-wrapped barrier packaging', status: 'COMPLIANT', notes: 'Compliant' }
        ]
      },
      {
        lot_number: 'Lot 2',
        title: 'High-Flux Hemodialysis Dialyzer Filters & Blood Tubing Lines (Quantity: 45,000 Units)',
        matched_sku: null,
        matched_name: '❌ Product Missing in Company Catalogue',
        coverage_status: 'NON_COMPLIANT',
        specs_matrix: [
          { param: 'Membrane Type', req: 'Synthetic Polysulfone / Polynephron membrane (1.8 - 2.0 m²)', sup: 'Not currently registered in catalogue', status: 'NON_COMPLIANT', notes: 'Requires Fresenius or Nipro OEM partnership' },
          { param: 'Biocompatibility', req: 'Steam sterilized, Endotoxin retention capacity', sup: 'Unsupplied', status: 'NON_COMPLIANT', notes: 'High recurring market in Rwanda' }
        ]
      },
      {
        lot_number: 'Lot 3',
        title: 'Hospital Steam Sterilizer Packaging Reels & Biological Indicators',
        matched_sku: 'AUT-ST-150',
        matched_name: 'Tuttnauer Sterilization Consumables',
        coverage_status: 'COMPLIANT',
        specs_matrix: [
          { param: 'Biological Indicators', req: 'Geobacillus stearothermophilus spore ampoules (10⁶)', sup: 'Tuttnauer Self-contained biological ampoules', status: 'COMPLIANT', notes: 'Compliant' }
        ]
      }
    ],
    missing_products: ['High-Flux Dialyzer Filters (Fresenius / Nipro compatible)'],
    critical_gaps: 'We do not currently supply Lot 2 (Dialyzer Filters). We can bid partially for Lot 1 & Lot 3 (RWF 2.4B value) or fast-track OEM distributorship with Fresenius Medical.',
    expansion_potential: 'High recurring annual demand across Rwanda district hospitals for Dialysis consumables (estimated RWF 1.8B annual market).'
  },
  {
    id: 'tender-4',
    ref: '000019/G/NCB/2026/2027/KDH',
    title: 'Procurement and turnkey installation of modern dental surgical units and intraoral digital radiography',
    procuring_entity: 'Kigali Dental Hospital',
    category: 'Dental',
    tender_value: 850000000,
    currency: 'RWF',
    deadline_at: '2026-09-18T12:00:00+02:00',
    relevance_score: 95,
    tech_spec_match: 98,
    product_match: 95,
    coverage_rate: 100,
    eligibility_match: 100,
    manufacturer_match: 95,
    risk: 'Low',
    security: 'Not required',
    authorization: 'Required (Planmeca / Equivalent)',
    stock_readiness: 'IN_STOCK',
    stock_label: '⚡ In-Stock (Kigali)',
    status: 'bid_preparation',
    recommended_action: 'BID_HIGH_FIT',
    recommendation_label: 'Bid (High Win Rate)',
    icon: 'DEN',
    lots: [
      {
        lot_number: 'Lot 1',
        title: 'Comprehensive Dental Operatory Unit with Intraoral Display (Quantity: 6 Units)',
        matched_sku: 'DEN-UNT-300',
        matched_name: 'Planmeca Compact i5 Operatory Unit',
        coverage_status: 'COMPLIANT',
        specs_matrix: [
          { param: 'Chair Movement', req: 'Electro-mechanical with minimum 4 customizable memory presets', sup: 'Precision electro-mechanical with 6 memory presets', status: 'COMPLIANT', notes: 'Compliant' },
          { param: 'Micromotor Speed', req: 'Brushless optical micromotor with speed up to 40,000 RPM', sup: 'Brushless micromotor 100 - 40,000 RPM with LED', status: 'COMPLIANT', notes: 'Exact match' },
          { param: 'Intraoral Camera & Monitor', req: 'Integrated HD intraoral video camera + medical display', sup: 'Planmeca Somia HD camera + 21.5" anti-reflective display', status: 'COMPLIANT', notes: 'Compliant' },
          { param: 'Disinfection System', req: 'Automated continuous water-line disinfection system', sup: 'Planmeca Waterline Cleaning System (WCS)', status: 'COMPLIANT', notes: 'Meets hospital hygiene protocol' }
        ]
      }
    ],
    missing_products: [],
    critical_gaps: 'None. We have direct OEM authorization and 4 units currently in Kigali stock.',
    expansion_potential: null
  },
  {
    id: 'tender-5',
    ref: '000031/G/ICB/2026/2027/KFH',
    title: 'Supply, installation and 5-year maintenance of 128-Slice Whole Body Diagnostic CT Scanner',
    procuring_entity: 'King Faisal Hospital Rwanda',
    category: 'Imaging & Radiology',
    tender_value: 1450000000,
    currency: 'RWF',
    deadline_at: '2026-09-24T17:00:00+02:00',
    relevance_score: 92,
    tech_spec_match: 96,
    product_match: 90,
    coverage_rate: 100,
    eligibility_match: 95,
    manufacturer_match: 90,
    risk: 'High',
    security: 'RWF 15,000,000 (Bank Guarantee)',
    authorization: 'Required (Direct OEM Siemens / GE / Philips)',
    stock_readiness: 'PROJECT_DELIVERY',
    stock_label: '📦 Turnkey Project Delivery',
    status: 'submitted',
    recommended_action: 'BID_HIGH_FIT',
    recommendation_label: 'Bid (High Value)',
    icon: 'RAD',
    lots: [
      {
        lot_number: 'Lot 1',
        title: '128-Slice High-Resolution Multi-Detector CT Scanner System + Post-Processing Workstation',
        matched_sku: 'RAD-CT-128',
        matched_name: 'Siemens SOMATOM go.Top 128-Slice System',
        coverage_status: 'COMPLIANT',
        specs_matrix: [
          { param: 'Slices per Rotation', req: 'Minimum 128 physical/reconstructed slices per 360° rotation', sup: '128 slices reconstructed per 0.33s rotation', status: 'COMPLIANT', notes: 'Compliant' },
          { param: 'Spatial Resolution', req: 'Isotropic spatial resolution ≤ 0.35 mm', sup: '0.33 mm isotropic resolution (Stellar detector)', status: 'COMPLIANT', notes: 'Exceeds resolution spec' },
          { param: 'Dose Modulation', req: 'Real-time AI dose reduction protocol for pediatric & adult', sup: 'CARE Dose4D + CARE kV AI modulation algorithms', status: 'COMPLIANT', notes: 'Compliant' },
          { param: 'Gantry Aperture', req: 'Bore diameter ≥ 75 cm with ±30° tilt', sup: '78 cm ultra-wide bore opening with 3D camera', status: 'COMPLIANT', notes: 'Larger patient clearance' },
          { param: 'UPS & Lead Shielding', req: 'Turnkey room shielding + 100 kVA online UPS (20 min backup)', sup: 'Included in Siemens partner turnkey scope of work', status: 'COMPLIANT', notes: 'Verified with local contractor' }
        ]
      }
    ],
    missing_products: [],
    critical_gaps: 'High bank guarantee requirement (RWF 15M). Confirm credit line with Bank of Kigali.',
    expansion_potential: null
  },
  {
    id: 'tender-6',
    ref: '000072/G/NCB/2026/2027/CHUB',
    title: 'Supply and installation of Laparoscopic Surgery Towers and Autoclave Units',
    procuring_entity: 'University Teaching Hospital of Butare (CHUB)',
    category: 'Surgical',
    tender_value: 620000000,
    currency: 'RWF',
    deadline_at: '2026-09-30T11:00:00+02:00',
    relevance_score: 93,
    tech_spec_match: 95,
    product_match: 92,
    coverage_rate: 100,
    eligibility_match: 100,
    manufacturer_match: 90,
    risk: 'Low',
    security: 'RWF 1,000,000',
    authorization: 'Required',
    stock_readiness: 'IN_STOCK',
    stock_label: '⚡ In-Stock (Kigali)',
    status: 'new',
    recommended_action: 'BID_HIGH_FIT',
    recommendation_label: 'Bid (High Win Rate)',
    icon: 'SUR',
    lots: [
      {
        lot_number: 'Lot 1',
        title: '4K Ultra HD Surgical Laparoscopy Camera Tower (Quantity: 2 Systems)',
        matched_sku: 'SUR-LAP-4K',
        matched_name: 'Karl Storz 4K UHD Laparoscopy System',
        coverage_status: 'COMPLIANT',
        specs_matrix: [
          { param: 'Camera Sensor', req: 'Native 4K resolution (3840 x 2160 pixels) at 60 fps', sup: '3840x2160 native sensor with 55" medical 4K monitor', status: 'COMPLIANT', notes: 'Exact match' },
          { param: 'Insufflator', req: 'High-flow automated CO2 insufflator (≥ 40 L/min)', sup: '45 L/min continuous high-flow heating insufflator', status: 'COMPLIANT', notes: 'Higher flow capacity' }
        ]
      },
      {
        lot_number: 'Lot 2',
        title: 'Horizontal Steam Autoclave (Chamber Volume ≥ 120 Litres) (Quantity: 1 Unit)',
        matched_sku: 'AUT-ST-150',
        matched_name: 'Tuttnauer 150L Steam Sterilizer',
        coverage_status: 'COMPLIANT',
        specs_matrix: [
          { param: 'Chamber Volume', req: 'Minimum 120 Litres, 316L Stainless Steel', sup: '150 Litres capacity, 316L medical stainless steel', status: 'COMPLIANT', notes: 'Exceeds capacity' },
          { param: 'Vacuum Cycles', req: 'Fractionated pre-vacuum & active drying cycles', sup: 'Class B fractionated pre-vacuum with water ring pump', status: 'COMPLIANT', notes: 'Compliant' }
        ]
      }
    ],
    missing_products: [],
    critical_gaps: 'None. Ready for immediate technical submission.',
    expansion_potential: null
  }
];

// ==========================================================================
// 4. Most Recurring Products & Market Demand Forecasting Data Store
// ==========================================================================

let recurringDemand = [
  {
    code: 'ICU-MON-12',
    name: 'Modular Multiparameter Patient Monitors (ICU / Neonatal / Emergency)',
    category: 'Neonatal & ICU',
    tender_frequency_per_year: 18,
    annual_market_value: 3600000000,
    annual_growth: '+28%',
    primary_buyers: ['Rwanda Biomedical Centre (RBC)', 'CHUK', 'KFH', 'District Hospitals'],
    current_warehouse_stock: 2,
    min_safe_threshold: 6,
    recommended_restock_qty: 8,
    urgency_level: 'URGENT',
    urgency_label: '🔴 Immediate Restock Needed',
    next_expected_wave: 'Sept 2026 (MOH Maternal & Child Upgrade Wave - 24 Units)',
    delivery_advantage_note: 'Bids requiring <7 days delivery receive +15 points in RBC evaluation.',
    oem_partner: 'Mindray Healthcare'
  },
  {
    code: 'CON-SUR-GLV',
    name: 'Sterile Powder-Free Surgical & Examination Gloves (Nitrile/Latex)',
    category: 'Consumables',
    tender_frequency_per_year: 24,
    annual_market_value: 4200000000,
    annual_growth: '+14%',
    primary_buyers: ['Rwanda Medical Supply (RMS)', 'RBC', 'All Referral Hospitals'],
    current_warehouse_stock: 400,
    min_safe_threshold: 1000,
    recommended_restock_qty: 1200,
    urgency_level: 'URGENT',
    urgency_label: '🔴 Immediate Restock Needed',
    next_expected_wave: 'Oct 2026 (RMS National Framework Renewal - 500k Pairs)',
    delivery_advantage_note: 'Bulk warehouse buffer in Kigali allows 48-hour emergency batch fulfillment.',
    oem_partner: 'Ansell Healthcare'
  },
  {
    code: 'NEO-WRM-500',
    name: 'Infant Radiant Warmers & Resuscitation Cribs',
    category: 'Neonatal & ICU',
    tender_frequency_per_year: 12,
    annual_market_value: 2800000000,
    annual_growth: '+35%',
    primary_buyers: ['RBC', 'District Hospitals', 'Partners In Health'],
    current_warehouse_stock: 6,
    min_safe_threshold: 4,
    recommended_restock_qty: 4,
    urgency_level: 'SAFE',
    urgency_label: '🟢 Safe Buffer (Order 4 Units)',
    next_expected_wave: 'Nov 2026 (Western Province Hospital Expansion - 16 Units)',
    delivery_advantage_note: 'Current stock covers 100% of open RBC Lot 1 demand.',
    oem_partner: 'MedTech Global'
  },
  {
    code: 'LAB-ANA-800',
    name: 'Automated Clinical Biochemistry Reagents & Analyzers',
    category: 'Laboratory',
    tender_frequency_per_year: 14,
    annual_market_value: 3100000000,
    annual_growth: '+18%',
    primary_buyers: ['CHUK', 'CHUB', 'KFH', 'National Reference Laboratory'],
    current_warehouse_stock: 2,
    min_safe_threshold: 2,
    recommended_restock_qty: 2,
    urgency_level: 'SAFE',
    urgency_label: '🟢 Optimal Buffer Level',
    next_expected_wave: 'Quarterly Reagent Framework Replenishment (CHUK/CHUB)',
    delivery_advantage_note: 'Cold-chain reagent storage guaranteed in Kigali distribution hub.',
    oem_partner: 'DiaSys Germany'
  },
  {
    code: 'DIA-FLT-EXP',
    name: 'High-Flux Hemodialysis Filters & Blood Tubing Sets',
    category: 'Consumables',
    tender_frequency_per_year: 16,
    annual_market_value: 2400000000,
    annual_growth: '+42%',
    primary_buyers: ['Rwanda Medical Supply (RMS)', 'KFH Dialysis Center', 'CHUK'],
    current_warehouse_stock: 0,
    min_safe_threshold: 500,
    recommended_restock_qty: 1000,
    urgency_level: 'EXPANSION',
    urgency_label: '🚀 New OEM Partner Sourcing',
    next_expected_wave: 'Sept 2026 (National Renal Care Supply Tender - RWF 1.8B)',
    delivery_advantage_note: 'Onboarding Fresenius or Nipro unlocks RWF 2.4B recurring revenue stream.',
    oem_partner: 'Fresenius / Nipro (Recommended to Onboard)'
  },
  {
    code: 'DEN-UNT-300',
    name: 'Dental Operatory Units with Intraoral Camera & LED Lighting',
    category: 'Dental',
    tender_frequency_per_year: 8,
    annual_market_value: 1200000000,
    annual_growth: '+22%',
    primary_buyers: ['Kigali Dental Hospital', 'Military Hospital', 'District Clinics'],
    current_warehouse_stock: 4,
    min_safe_threshold: 3,
    recommended_restock_qty: 2,
    urgency_level: 'SAFE',
    urgency_label: '🟢 In Stock (Ready to Bid)',
    next_expected_wave: 'Jan 2027 (National Dental Clinic Modernization)',
    delivery_advantage_note: 'Local assembly and maintenance engineers give superior RFP scoring.',
    oem_partner: 'Planmeca Finland'
  }
];

// Sources Store
let sources = [
  { id: 'src-1', name: 'Rwanda Public Procurement Authority (RPPA)', organization: 'Umucyo e-Procurement System', website: 'https://umucyo.gov.rw', category: 'government_portal', collection_method: 'api', is_active: true, scan_frequency_hours: 6, tenders_collected_count: 64, last_scan_at: '14 min ago' },
  { id: 'src-2', name: 'Rwanda Biomedical Centre (RBC)', organization: 'MOH Implementing Agency', website: 'https://rbc.gov.rw/tenders', category: 'ministry', collection_method: 'webpage', is_active: true, scan_frequency_hours: 12, tenders_collected_count: 28, last_scan_at: '28 min ago' },
  { id: 'src-3', name: 'Rwanda Medical Supply Ltd (RMS)', organization: 'National Medical Supply & Logistics', website: 'https://rms.rw/procurement', category: 'government_portal', collection_method: 'api', is_active: true, scan_frequency_hours: 12, tenders_collected_count: 22, last_scan_at: '1 hour ago' },
  { id: 'src-4', name: 'University Teaching Hospital of Kigali (CHUK)', organization: 'National Referral Hospital', website: 'https://chuk.rw/tenders', category: 'hospital', collection_method: 'webpage', is_active: true, scan_frequency_hours: 24, tenders_collected_count: 14, last_scan_at: '2 hours ago' },
  { id: 'src-5', name: 'King Faisal Hospital Rwanda (KFH)', organization: 'Quaternary Referral Center', website: 'https://kfh.rw/tenders', category: 'hospital', collection_method: 'webpage', is_active: true, scan_frequency_hours: 24, tenders_collected_count: 9, last_scan_at: '3 hours ago' },
  { id: 'src-6', name: 'University Teaching Hospital of Butare (CHUB)', organization: 'Southern Province Hospital', website: 'https://chub.rw/tenders', category: 'hospital', collection_method: 'rss', is_active: true, scan_frequency_hours: 24, tenders_collected_count: 5, last_scan_at: '4 hours ago' },
  { id: 'src-7', name: 'Ministry of Health Rwanda (MoH)', organization: 'Central Health Ministry', website: 'https://moh.gov.rw/opportunities', category: 'ministry', collection_method: 'webpage', is_active: true, scan_frequency_hours: 24, tenders_collected_count: 8, last_scan_at: '6 hours ago' },
  { id: 'src-8', name: 'Partners In Health Rwanda (PIH)', organization: 'Inshuti Mu Buzima NGO', website: 'https://pih.org/rwanda/procurement', category: 'ngo', collection_method: 'manual_import', is_active: true, scan_frequency_hours: 72, tenders_collected_count: 3, last_scan_at: 'Yesterday' }
];

// Utility Helpers
function daysRemaining(date) { return Math.ceil((new Date(date) - new Date()) / 86400000); }
function formatDate(date) { return new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(date)); }
function formatRWF(val) {
  if (!val || !Number.isFinite(val)) return 'Not available';
  if (val >= 1000000000) return `RWF ${(val / 1000000000).toFixed(1)}B`;
  if (val >= 1000000) return `RWF ${(val / 1000000).toFixed(0)}M`;
  return `RWF ${val.toLocaleString()}`;
}
function urgency(date) { const d = daysRemaining(date); return d <= 3 ? 'urgent' : d <= 7 ? 'attention' : 'normal'; }

function showToast(message) {
  const toast = document.querySelector('#toast');
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('show');
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove('show'), 3000);
}

// ==========================================================================
// 5. View Navigation & Routing
// ==========================================================================

const viewMap = {
  dashboard: { panelId: 'viewOverview', title: 'Overview', category: 'Procurement' },
  tenders: { panelId: 'viewPipeline', title: 'Tender Pipeline & Matching', category: 'Opportunities' },
  sources: { panelId: 'viewSources', title: 'Monitored Sources', category: 'Discovery' },
  catalogue: { panelId: 'viewCatalogue', title: 'Catalogue & Replenishment', category: 'Inventory' }
};

let currentView = 'dashboard';

function switchView(viewKey) {
  if (!viewMap[viewKey]) viewKey = 'dashboard';
  currentView = viewKey;

  document.querySelectorAll('.nav-item[data-view]').forEach(btn => {
    const isActive = btn.dataset.view === viewKey;
    btn.classList.toggle('active', isActive);
    if (isActive) btn.setAttribute('aria-current', 'page');
    else btn.removeAttribute('aria-current');
  });

  document.querySelectorAll('.view-panel').forEach(panel => panel.classList.remove('active'));
  const activePanel = document.querySelector(`#${viewMap[viewKey].panelId}`);
  if (activePanel) activePanel.classList.add('active');

  const breadcrumbCat = document.querySelector('#breadcrumbCategory');
  const breadcrumbView = document.querySelector('#breadcrumbView');
  if (breadcrumbCat) breadcrumbCat.textContent = viewMap[viewKey].category;
  if (breadcrumbView) breadcrumbView.textContent = viewMap[viewKey].title;
  document.title = `${viewMap[viewKey].title} | MedTender Intelligence`;

  if (viewKey === 'dashboard') renderOverview();
  else if (viewKey === 'tenders') renderPipeline();
  else if (viewKey === 'sources') renderSources();
  else if (viewKey === 'catalogue') {
    renderCatalogue();
    renderDemand();
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

document.querySelectorAll('[data-view]').forEach(btn => {
  btn.addEventListener('click', () => {
    const target = btn.dataset.view;
    window.location.hash = target;
    switchView(target);
  });
});

window.addEventListener('hashchange', () => {
  const hash = window.location.hash.replace('#', '');
  if (viewMap[hash]) switchView(hash);
});

// ==========================================================================
// 6. View 1: Overview Dashboard Controller
// ==========================================================================

function renderOverview() {
  const highFitCount = tenders.filter(t => t.relevance_score >= 80).length;
  const fullCoverageCount = tenders.filter(t => t.coverage_rate === 100).length;
  const expansionCount = tenders.filter(t => t.recommended_action === 'OPPORTUNITY_EXPANSION').length;
  const restockAlerts = recurringDemand.filter(d => d.urgency_level === 'URGENT').length;

  const hCountEl = document.querySelector('#highFitCount');
  const fCountEl = document.querySelector('#fullCoverageCount');
  const expCountEl = document.querySelector('#expansionCount');
  const rAlertEl = document.querySelector('#restockAlertCount');

  if (hCountEl) hCountEl.textContent = highFitCount;
  if (fCountEl) fCountEl.textContent = fullCoverageCount;
  if (expCountEl) expCountEl.textContent = expansionCount;
  if (rAlertEl) rAlertEl.textContent = restockAlerts;

  const rows = document.querySelector('#tenderRows');
  const emptyState = document.querySelector('#emptyState');
  const searchInput = document.querySelector('#searchInput');
  const fitFilter = document.querySelector('#overviewFitFilter');
  const categoryFilter = document.querySelector('#categoryFilter');

  if (!rows) return;

  const term = searchInput ? searchInput.value.toLowerCase().trim() : '';
  const fit = fitFilter ? fitFilter.value : '';
  const cat = categoryFilter ? categoryFilter.value : '';

  const filtered = tenders.filter(t => {
    if (cat && t.category !== cat) return false;
    if (fit === 'high' && t.relevance_score < 80) return false;
    if (fit === 'expansion' && t.recommended_action !== 'OPPORTUNITY_EXPANSION') return false;
    if (fit === 'review' && t.recommended_action !== 'REVIEW_VERIFY') return false;
    if (term && !`${t.ref} ${t.title} ${t.procuring_entity} ${t.category}`.toLowerCase().includes(term)) return false;
    return true;
  });

  if (filtered.length === 0) {
    rows.innerHTML = '';
    if (emptyState) emptyState.hidden = false;
    return;
  }

  if (emptyState) emptyState.hidden = true;

  rows.innerHTML = filtered.map(t => {
    const days = daysRemaining(t.deadline_at);
    const urgencyLabel = days <= 3 ? `${days} days left` : days <= 7 ? `${days} days left` : `${days} days left`;
    const scoreClass = t.relevance_score >= 85 ? 'high' : t.relevance_score >= 70 ? 'mid' : 'low';
    const recClass = t.recommended_action === 'BID_HIGH_FIT' ? 'bid' : t.recommended_action === 'OPPORTUNITY_EXPANSION' ? 'expansion' : 'review';

    return `
      <tr>
        <td>
          <div class="tender-name">
            <span class="tender-icon" aria-hidden="true">${t.icon}</span>
            <div>
              <strong>${t.title}</strong>
              <small style="color:var(--muted)">${t.procuring_entity} · <span style="font-family:'DM Mono',monospace;color:var(--teal)">${t.ref}</span></small>
            </div>
          </div>
        </td>
        <td>
          <div class="deadline">
            <strong>${formatDate(t.deadline_at)}</strong>
            <small class="${urgency(t.deadline_at)}">${urgencyLabel}</small>
          </div>
        </td>
        <td>
          <div class="match-box">
            <span class="match-score ${scoreClass}">★ ${t.relevance_score}%</span>
            <small style="font-size:10px;color:var(--muted)">Spec Match: ${t.tech_spec_match}%</small>
          </div>
        </td>
        <td>
          <span class="coverage-pill ${t.coverage_rate === 100 ? 'full' : ''}">
            ${t.coverage_rate}% (${t.lots.filter(l => l.coverage_status === 'COMPLIANT').length}/${t.lots.length} Lots)
          </span>
        </td>
        <td>
          <span class="recommend-badge ${recClass}">
            ${t.recommendation_label}
          </span>
        </td>
        <td>
          <button class="primary-button" style="padding:6px 10px;font-size:11px;" data-open-matrix="${t.id}" aria-label="View technical specification matrix for ${t.title}">
            Spec Matrix →
          </button>
        </td>
      </tr>
    `;
  }).join('');

  rows.querySelectorAll('[data-open-matrix]').forEach(btn => {
    btn.addEventListener('click', () => openTenderDrawer(btn.dataset.openMatrix));
  });
}

const overviewSearchInput = document.querySelector('#searchInput');
const overviewFitFilter = document.querySelector('#overviewFitFilter');
const overviewCategoryFilter = document.querySelector('#categoryFilter');

if (overviewSearchInput) overviewSearchInput.addEventListener('input', renderOverview);
if (overviewFitFilter) overviewFitFilter.addEventListener('change', renderOverview);
if (overviewCategoryFilter) overviewCategoryFilter.addEventListener('change', renderOverview);

// ==========================================================================
// 7. View 2: Tender Pipeline & Matching Workspace
// ==========================================================================

let pipelineSelectedStage = '';

function renderPipeline() {
  const pipelineRows = document.querySelector('#pipelineTableRows');
  const pipelineEmptyState = document.querySelector('#pipelineEmptyState');
  const searchInput = document.querySelector('#pipelineSearchInput');
  const categoryFilter = document.querySelector('#pipelineCategoryFilter');
  const actionFilter = document.querySelector('#pipelineActionFilter');
  const sortBy = document.querySelector('#pipelineSortBy');

  // Stage counts
  const stageCounts = {
    all: tenders.length,
    high_fit: tenders.filter(t => t.relevance_score >= 80).length,
    expansion: tenders.filter(t => t.recommended_action === 'OPPORTUNITY_EXPANSION').length,
    prep: tenders.filter(t => t.status === 'bid_preparation').length,
    submitted: tenders.filter(t => t.status === 'submitted').length
  };

  const cAll = document.querySelector('#countStageAll');
  const cHigh = document.querySelector('#countStageHigh');
  const cExp = document.querySelector('#countStageExp');
  const cPrep = document.querySelector('#countStagePrep');
  const cSub = document.querySelector('#countStageSubmitted');

  if (cAll) cAll.textContent = stageCounts.all;
  if (cHigh) cHigh.textContent = stageCounts.high_fit;
  if (cExp) cExp.textContent = stageCounts.expansion;
  if (cPrep) cPrep.textContent = stageCounts.prep;
  if (cSub) cSub.textContent = stageCounts.submitted;

  // Sidebar badge sync
  const sbPipeCount = document.querySelector('#sidebarPipelineCount');
  if (sbPipeCount) sbPipeCount.textContent = tenders.length;

  if (!pipelineRows) return;

  const term = searchInput ? searchInput.value.toLowerCase().trim() : '';
  const cat = categoryFilter ? categoryFilter.value : '';
  const act = actionFilter ? actionFilter.value : '';
  const sort = sortBy ? sortBy.value : 'relevance';

  let filtered = tenders.filter(t => {
    if (pipelineSelectedStage === 'high_fit' && t.relevance_score < 80) return false;
    if (pipelineSelectedStage === 'expansion' && t.recommended_action !== 'OPPORTUNITY_EXPANSION') return false;
    if (pipelineSelectedStage === 'bid_preparation' && t.status !== 'bid_preparation') return false;
    if (pipelineSelectedStage === 'submitted' && t.status !== 'submitted') return false;

    if (cat && t.category !== cat) return false;
    if (act && t.recommended_action !== act) return false;
    if (term && !`${t.ref} ${t.title} ${t.procuring_entity} ${t.category}`.toLowerCase().includes(term)) return false;
    return true;
  });

  // Sorting
  filtered.sort((a, b) => {
    if (sort === 'relevance') return (b.relevance_score || 0) - (a.relevance_score || 0);
    if (sort === 'deadline') return new Date(a.deadline_at) - new Date(b.deadline_at);
    if (sort === 'value') return (b.tender_value || 0) - (a.tender_value || 0);
    if (sort === 'coverage') return (b.coverage_rate || 0) - (a.coverage_rate || 0);
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
    const urgencyLabel = days <= 3 ? `${days}d left` : days <= 7 ? `${days}d left` : `${days}d left`;
    const scoreClass = t.relevance_score >= 85 ? 'high' : t.relevance_score >= 70 ? 'mid' : 'low';
    const recClass = t.recommended_action === 'BID_HIGH_FIT' ? 'bid' : t.recommended_action === 'OPPORTUNITY_EXPANSION' ? 'expansion' : 'review';

    return `
      <tr>
        <td>
          <div class="tender-name">
            <span class="tender-icon" aria-hidden="true">${t.icon}</span>
            <div>
              <strong>${t.title}</strong>
              <small style="font-family:'DM Mono',monospace;color:var(--teal)">${t.ref}</small>
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
          <strong class="match-score ${scoreClass}">★ ${t.relevance_score}%</strong>
        </td>
        <td>
          <strong style="color:var(--teal)">${t.tech_spec_match}%</strong>
        </td>
        <td>
          <span class="coverage-pill ${t.coverage_rate === 100 ? 'full' : ''}">${t.coverage_rate}%</span>
        </td>
        <td>
          <span class="stock-tag ${t.stock_readiness === 'IN_STOCK' ? 'in-stock' : t.stock_readiness === 'EXPANSION_OPPORTUNITY' ? 'expansion' : 'lead-time'}">
            ${t.stock_label}
          </span>
        </td>
        <td>
          <span class="recommend-badge ${recClass}">${t.recommendation_label}</span>
        </td>
        <td>
          <button class="primary-button" style="padding:6px 10px;font-size:11px;" data-open-matrix="${t.id}" aria-label="Open Spec Matrix">
            Spec Matrix →
          </button>
        </td>
      </tr>
    `;
  }).join('');

  pipelineRows.querySelectorAll('[data-open-matrix]').forEach(btn => {
    btn.addEventListener('click', () => openTenderDrawer(btn.dataset.openMatrix));
  });
}

// Stage pills handler
document.querySelectorAll('#viewPipeline .stage-pill').forEach(pill => {
  pill.addEventListener('click', () => {
    document.querySelectorAll('#viewPipeline .stage-pill').forEach(p => {
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
const pipeAct = document.querySelector('#pipelineActionFilter');
const pipeSort = document.querySelector('#pipelineSortBy');

if (pipeSearch) pipeSearch.addEventListener('input', renderPipeline);
if (pipeCat) pipeCat.addEventListener('change', renderPipeline);
if (pipeAct) pipeAct.addEventListener('change', renderPipeline);
if (pipeSort) pipeSort.addEventListener('change', renderPipeline);

// ==========================================================================
// 8. View 4: Catalogue & Predictive Stock Replenishment Controller
// ==========================================================================

const subtabCatalogue = document.querySelector('#subtabCatalogue');
const subtabDemand = document.querySelector('#subtabDemand');
const subtabContentCatalogue = document.querySelector('#subtabContentCatalogue');
const subtabContentDemand = document.querySelector('#subtabContentDemand');

if (subtabCatalogue && subtabDemand) {
  subtabCatalogue.addEventListener('click', () => {
    subtabCatalogue.classList.add('active');
    subtabDemand.classList.remove('active');
    subtabCatalogue.setAttribute('aria-selected', 'true');
    subtabDemand.setAttribute('aria-selected', 'false');
    if (subtabContentCatalogue) subtabContentCatalogue.hidden = false;
    if (subtabContentDemand) subtabContentDemand.hidden = true;
    renderCatalogue();
  });

  subtabDemand.addEventListener('click', () => {
    subtabDemand.classList.add('active');
    subtabCatalogue.classList.remove('active');
    subtabDemand.setAttribute('aria-selected', 'true');
    subtabCatalogue.setAttribute('aria-selected', 'false');
    if (subtabContentDemand) subtabContentDemand.hidden = false;
    if (subtabContentCatalogue) subtabContentCatalogue.hidden = true;
    renderDemand();
  });
}

function renderCatalogue() {
  const container = document.querySelector('#catalogueGridContainer');
  const emptyState = document.querySelector('#catalogueEmptyState');
  const searchInput = document.querySelector('#catalogueSearchInput');
  const categoryFilter = document.querySelector('#catalogueCategoryFilter');

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
    const stockClass = p.stock_status === 'IN_STOCK' ? 'safe' : p.stock_status === 'LOW_STOCK_URGENT' ? 'low' : 'safe';
    const stockLabel = p.stock_status === 'LOW_STOCK_URGENT' ? '⚠️ Low Stock Alert' : '✓ In Stock Ready';

    return `
      <article class="product-card">
        <div>
          <div class="product-card-top">
            <span class="product-code">${p.code}</span>
            <span class="badge" style="background:#e3f1ed;color:var(--teal-dark)">${p.category}</span>
          </div>

          <h3>${p.name}</h3>
          <small style="color:var(--muted);display:block;margin-bottom:10px;">OEM: <strong>${p.manufacturer}</strong></small>

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
              <small style="color:var(--muted)">Warehouse Stock:</small>
              <strong style="color:${p.stock_status === 'LOW_STOCK_URGENT' ? 'var(--coral)' : 'var(--green)'}">
                ${p.warehouse_stock} Units (${stockLabel})
              </strong>
            </div>
            <div>
              <button class="outline-button" style="padding:4px 8px;font-size:10px;" data-trigger-restock="${p.code}">
                + Restock
              </button>
            </div>
          </div>
        </div>
      </article>
    `;
  }).join('');

  container.querySelectorAll('[data-trigger-restock]').forEach(btn => {
    btn.addEventListener('click', () => openRestockModal(btn.dataset.triggerRestock));
  });
}

function renderDemand() {
  const container = document.querySelector('#demandGridContainer');
  const emptyState = document.querySelector('#demandEmptyState');
  const searchInput = document.querySelector('#demandSearchInput');
  const urgencyFilter = document.querySelector('#demandUrgencyFilter');

  if (!container) return;

  const term = searchInput ? searchInput.value.toLowerCase().trim() : '';
  const urg = urgencyFilter ? urgencyFilter.value : '';

  const filtered = recurringDemand.filter(d => {
    if (urg === 'urgent' && d.urgency_level !== 'URGENT') return false;
    if (urg === 'safe' && d.urgency_level !== 'SAFE') return false;
    if (urg === 'expansion' && d.urgency_level !== 'EXPANSION') return false;
    if (term && !`${d.code} ${d.name} ${d.category} ${d.next_expected_wave}`.toLowerCase().includes(term)) return false;
    return true;
  });

  if (filtered.length === 0) {
    container.innerHTML = '';
    if (emptyState) emptyState.hidden = false;
    return;
  }

  if (emptyState) emptyState.hidden = true;

  container.innerHTML = filtered.map(d => {
    const alertClass = d.urgency_level === 'URGENT' ? 'urgent' : d.urgency_level === 'EXPANSION' ? 'opportunity' : 'safe';
    const fillClass = d.urgency_level === 'URGENT' ? 'low' : d.urgency_level === 'EXPANSION' ? 'expansion' : 'safe';
    const percent = Math.min(100, Math.round((d.current_warehouse_stock / (d.min_safe_threshold || 1)) * 100));

    return `
      <article class="demand-card">
        <div>
          <div class="demand-header">
            <div>
              <span class="demand-frequency">${d.tender_frequency_per_year} Tenders / Year</span>
              <span class="trend-pill up">${d.annual_growth} Growth</span>
            </div>
            <span class="badge" style="background:#eef4f3;color:var(--teal-dark)">${d.category}</span>
          </div>

          <h3 style="margin: 8px 0 4px;font-size:14px;line-height:1.3;">${d.name}</h3>
          <p style="font-size:11px;color:var(--muted);margin-bottom:12px;">
            Total Rwanda Annual Demand: <strong>${formatRWF(d.annual_market_value)}</strong>
          </p>

          <div class="stock-meter">
            <div class="stock-meter-header">
              <span>Warehouse Stock: <strong>${d.current_warehouse_stock} units</strong></span>
              <span>Min Safe Buffer: <strong>${d.min_safe_threshold} units</strong></span>
            </div>
            <div class="stock-bar-wrap">
              <div class="stock-bar-fill ${fillClass}" style="width: ${percent}%"></div>
            </div>
          </div>
        </div>

        <div style="display:grid;gap:10px;margin-top:12px;">
          <div class="restock-alert ${alertClass}">
            <div>
              <strong>${d.urgency_label}</strong>
              <p style="margin:2px 0 0;font-size:10px;">${d.next_expected_wave}</p>
            </div>
          </div>

          <div style="font-size:10px;color:#556666;line-height:1.4;background:var(--paper);padding:8px 10px;border-radius:4px;">
            💡 <strong>Bidding Feasibility:</strong> ${d.delivery_advantage_note}
          </div>

          <div style="display:flex;gap:8px;">
            <button class="primary-button" style="flex:1;height:34px;font-size:11px;" data-trigger-restock="${d.code}">
              ${d.urgency_level === 'EXPANSION' ? 'Onboard OEM Partner' : `Restock ${d.recommended_restock_qty} Units`}
            </button>
          </div>
        </div>
      </article>
    `;
  }).join('');

  container.querySelectorAll('[data-trigger-restock]').forEach(btn => {
    btn.addEventListener('click', () => openRestockModal(btn.dataset.triggerRestock));
  });
}

const catSearch = document.querySelector('#catalogueSearchInput');
const catCat = document.querySelector('#catalogueCategoryFilter');
if (catSearch) catSearch.addEventListener('input', renderCatalogue);
if (catCat) catCat.addEventListener('change', renderCatalogue);

const demandSearch = document.querySelector('#demandSearchInput');
const demandUrg = document.querySelector('#demandUrgencyFilter');
if (demandSearch) demandSearch.addEventListener('input', renderDemand);
if (demandUrg) demandUrg.addEventListener('change', renderDemand);

const bulkRestockBtn = document.querySelector('#bulkRestockBtn');
if (bulkRestockBtn) {
  bulkRestockBtn.addEventListener('click', () => {
    showToast('Auto-generating replenishment purchase order for 2 urgent items (Mindray Monitors + Ansell Gloves)...');
    setTimeout(() => {
      const mon = catalogue.find(c => c.code === 'ICU-MON-12');
      const glv = catalogue.find(c => c.code === 'CON-SUR-GLV');
      if (mon) { mon.warehouse_stock += 8; mon.stock_status = 'IN_STOCK'; }
      if (glv) { glv.warehouse_stock += 1200; glv.stock_status = 'IN_STOCK'; }
      const demMon = recurringDemand.find(d => d.code === 'ICU-MON-12');
      const demGlv = recurringDemand.find(d => d.code === 'CON-SUR-GLV');
      if (demMon) { demMon.current_warehouse_stock += 8; demMon.urgency_level = 'SAFE'; demMon.urgency_label = '🟢 Replenished (Safe Buffer)'; }
      if (demGlv) { demGlv.current_warehouse_stock += 1200; demGlv.urgency_level = 'SAFE'; demGlv.urgency_label = '🟢 Replenished (Safe Buffer)'; }
      renderCatalogue();
      renderDemand();
      renderOverview();
      showToast('Purchase Order generated! Warehouse inventory buffer updated.');
    }, 800);
  });
}

// ==========================================================================
// 9. Interactive Tender Relevance & Spec Compliance Matrix Drawer
// ==========================================================================

const drawer = document.querySelector('#tenderDrawer');
const drawerBackdrop = document.querySelector('#drawerBackdrop');
const closeDrawerBtn = document.querySelector('#closeDrawer');

function openTenderDrawer(id) {
  const tender = tenders.find(item => item.id === id);
  if (!tender || !drawer) return;

  const days = daysRemaining(tender.deadline_at);
  const drawerContent = document.querySelector('#drawerContent');
  const recClass = tender.recommended_action === 'BID_HIGH_FIT' ? 'bid' : tender.recommended_action === 'OPPORTUNITY_EXPANSION' ? 'expansion' : 'review';

  if (drawerContent) {
    drawerContent.innerHTML = `
      <h2 class="drawer-title" id="drawerTitle">${tender.title}</h2>
      <p class="drawer-entity">${tender.procuring_entity} · <strong style="font-family:'DM Mono',monospace;color:var(--teal)">${tender.ref}</strong></p>

      <!-- Multi-Score Company Fit Matrix -->
      <div class="drawer-score-grid" aria-label="Company relevance score breakdown">
        <div class="drawer-score" style="border:2px solid var(--teal)">
          <strong style="font-size:18px;">★ ${tender.relevance_score}%</strong>
          <small>Company Relevance</small>
        </div>
        <div class="drawer-score">
          <strong>${tender.tech_spec_match}%</strong>
          <small>Technical Spec Match</small>
        </div>
        <div class="drawer-score">
          <strong>${tender.coverage_rate}%</strong>
          <small>Lot Coverage</small>
        </div>
        <div class="drawer-score">
          <strong>${tender.eligibility_match}%</strong>
          <small>Eligibility Fit</small>
        </div>
      </div>

      <!-- Recommendation & Delivery Readiness -->
      <div class="drawer-recommendation ${recClass}">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
          <strong>Strategic Recommendation: ${tender.recommendation_label}</strong>
          <span class="stock-tag ${tender.stock_readiness === 'IN_STOCK' ? 'in-stock' : 'lead-time'}">${tender.stock_label}</span>
        </div>
        <p style="margin:0;font-size:11px;line-height:1.5;">
          ${tender.critical_gaps || 'All mandatory technical parameters are fulfilled by our registered product line.'}
        </p>
      </div>

      <!-- Lot Breakdown & Parameter-by-Parameter Spec Matrix -->
      <section class="drawer-section">
        <h3>Lot Supply Breakdown & Technical Specification Matrix</h3>
        ${tender.lots.map(lot => `
          <div class="lot-card">
            <div class="lot-header">
              <span class="lot-title">${lot.lot_number}: ${lot.title}</span>
              <span class="compliance-status ${lot.coverage_status === 'COMPLIANT' ? 'compliant' : 'non-compliant'}">
                ${lot.coverage_status === 'COMPLIANT' ? '✅ Supplied' : '❌ Missing Product'}
              </span>
            </div>

            <div class="lot-product-pairing">
              <span style="font-size:16px;">📦</span>
              <div>
                <strong>${lot.matched_name}</strong>
                ${lot.matched_sku ? `<small style="font-family:'DM Mono',monospace;color:var(--teal)">SKU: ${lot.matched_sku}</small>` : ''}
              </div>
            </div>

            <!-- Granular Spec Matrix Table -->
            <table class="spec-matrix-table">
              <thead>
                <tr>
                  <th scope="col">Parameter</th>
                  <th scope="col">Tender Requirement</th>
                  <th scope="col">Our Supplied Specification</th>
                  <th scope="col">Status</th>
                </tr>
              </thead>
              <tbody>
                ${lot.specs_matrix.map(s => {
                  const badgeIcon = s.status === 'COMPLIANT' ? '✅' : s.status === 'VERIFICATION_REQUIRED' ? '⚠️' : s.status === 'PARTIALLY_COMPLIANT' ? '🟡' : s.status === 'NON_COMPLIANT' ? '❌' : '❓';
                  const badgeClass = s.status.toLowerCase().replace(/_/g, '-');
                  return `
                    <tr>
                      <td class="spec-param-name">${s.param}</td>
                      <td class="spec-req-val">${s.req}</td>
                      <td class="spec-sup-val">${s.sup}</td>
                      <td>
                        <span class="compliance-status ${badgeClass}" title="${s.notes}">
                          ${badgeIcon} ${s.status.replace(/_/g, ' ')}
                        </span>
                      </td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>
        `).join('')}
      </section>

      <!-- Qualification & Regulatory Matrix -->
      <section class="drawer-section">
        <h3>Qualification & Regulatory Checklist</h3>
        <div class="drawer-facts">
          <div><small>Estimated Tender Value</small><strong>${formatRWF(tender.tender_value)}</strong></div>
          <div><small>Submission Deadline</small><strong>${formatDate(tender.deadline_at)} (${days} days left)</strong></div>
          <div><small>Bid Security Required</small><strong>${tender.security}</strong></div>
          <div><small>Manufacturer Authorization Letter</small><strong>${tender.authorization}</strong></div>
          <div><small>ISO 13485:2016 Certificate</small><strong style="color:var(--green)">✓ Verified On File</strong></div>
          <div><small>Rwanda FDA Wholesale License</small><strong style="color:var(--green)">✓ Active & Compliant</strong></div>
        </div>
      </section>

      ${tender.expansion_potential ? `
        <div class="restock-alert opportunity" style="margin-top:14px;">
          <div>
            <strong>🚀 Startup Expansion Insight:</strong>
            <p style="margin:2px 0 0;font-size:10px;">${tender.expansion_potential}</p>
          </div>
        </div>
      ` : ''}

      <div class="drawer-actions">
        <button class="outline-button" id="exportMatrixBtn">Export Compliance CSV</button>
        <button class="primary-button" id="advancePrepBtn">
          ${tender.status === 'bid_preparation' ? '✓ In Bid Prep Workspace' : 'Advance to Bid Preparation →'}
        </button>
      </div>
    `;
  }

  drawer.classList.add('open');
  drawer.setAttribute('aria-hidden', 'false');
  if (drawerBackdrop) drawerBackdrop.hidden = false;
  if (closeDrawerBtn) closeDrawerBtn.focus();

  const exportBtn = document.querySelector('#exportMatrixBtn');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      showToast(`Compliance Matrix for "${tender.ref}" exported.`);
    });
  }

  const advanceBtn = document.querySelector('#advancePrepBtn');
  if (advanceBtn) {
    advanceBtn.addEventListener('click', () => {
      tender.status = 'bid_preparation';
      renderPipeline();
      renderOverview();
      showToast(`Tender ${tender.ref} moved to Bid Preparation.`);
      closeTenderDrawer();
    });
  }
}

function closeTenderDrawer() {
  if (!drawer) return;
  drawer.classList.remove('open');
  drawer.setAttribute('aria-hidden', 'true');
  if (drawerBackdrop) drawerBackdrop.hidden = true;
}

if (closeDrawerBtn) closeDrawerBtn.addEventListener('click', closeTenderDrawer);
if (drawerBackdrop) drawerBackdrop.addEventListener('click', closeTenderDrawer);

// ==========================================================================
// 10. Restock Modal Controller
// ==========================================================================

const restockModalBackdrop = document.querySelector('#restockModalBackdrop');
const closeRestockModal = document.querySelector('#closeRestockModal');
const cancelRestockBtn = document.querySelector('#cancelRestockBtn');
const restockForm = document.querySelector('#restockForm');

function openRestockModal(productCode) {
  const item = catalogue.find(c => c.code === productCode) || recurringDemand.find(d => d.code === productCode);
  if (!item) return;

  const codeInput = document.querySelector('#restockProductCode');
  const nameInput = document.querySelector('#restockProductName');
  const supplierInput = document.querySelector('#restockSupplier');
  const unitsInput = document.querySelector('#restockUnits');

  if (codeInput) codeInput.value = item.code;
  if (nameInput) nameInput.value = `[${item.code}] ${item.name}`;
  if (supplierInput) supplierInput.value = item.manufacturer || item.oem_partner || 'Authorized Medical OEM';
  if (unitsInput) unitsInput.value = item.recommended_restock_qty || 10;

  if (restockModalBackdrop) restockModalBackdrop.hidden = false;
}

function closeRestockModalDialog() {
  if (restockModalBackdrop) restockModalBackdrop.hidden = true;
}

if (closeRestockModal) closeRestockModal.addEventListener('click', closeRestockModalDialog);
if (cancelRestockBtn) cancelRestockBtn.addEventListener('click', closeRestockModalDialog);

if (restockForm) {
  restockForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const code = document.querySelector('#restockProductCode').value;
    const units = parseInt(document.querySelector('#restockUnits').value, 10) || 10;

    const catItem = catalogue.find(c => c.code === code);
    if (catItem) {
      catItem.warehouse_stock += units;
      catItem.stock_status = 'IN_STOCK';
    }

    const demandItem = recurringDemand.find(d => d.code === code);
    if (demandItem) {
      demandItem.current_warehouse_stock += units;
      demandItem.urgency_level = 'SAFE';
      demandItem.urgency_label = '🟢 Replenished (Safe Buffer)';
    }

    closeRestockModalDialog();
    renderCatalogue();
    renderDemand();
    renderOverview();
    showToast(`Replenishment order confirmed for ${units} units of ${code}. Warehouse stock updated.`);
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

// Global Escape Key Listener
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeTenderDrawer();
    closeRestockModalDialog();
    toggleHelpModal(false);
    if (profileDropdown && profileDropdown.classList.contains('open')) {
      profileDropdown.classList.remove('open');
      if (profileChipBtn) profileChipBtn.setAttribute('aria-expanded', 'false');
    }
  }
});

// Sources Controller
function renderSources() {
  const container = document.querySelector('#sourcesGridContainer');
  const emptyState = document.querySelector('#sourcesEmptyState');
  const searchInput = document.querySelector('#sourceSearchInput');
  const categoryFilter = document.querySelector('#sourceCategoryFilter');
  const methodFilter = document.querySelector('#sourceMethodFilter');
  const statusFilter = document.querySelector('#sourceStatusFilter');

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
    return `
      <article class="source-card">
        <div>
          <div class="source-header">
            <div>
              <h3>${s.name}</h3>
              <a href="${s.website}" target="_blank" rel="noopener noreferrer">${s.website} ↗</a>
            </div>
            <span class="status-tag ${s.is_active ? 'active' : 'inactive'}">
              <span class="status-dot"></span>
              ${s.is_active ? 'Active' : 'Deactivated'}
            </span>
          </div>

          <div class="source-badges" style="margin-top:10px;">
            <span class="badge gov">${s.category.toUpperCase()}</span>
            <span class="badge api">${s.collection_method.toUpperCase()}</span>
            <span class="badge" style="background:#edf3f2;color:#4f6161">Every ${s.scan_frequency_hours}h</span>
          </div>
        </div>

        <div class="source-meta">
          <div><small>Last successful scan</small><strong>${s.last_scan_at}</strong></div>
          <div><small>Tenders collected</small><strong style="color:var(--teal)">${s.tenders_collected_count} discovered</strong></div>
          <div><small>Compliance status</small><strong style="color:var(--green)">✓ Robots.txt Allowed</strong></div>
          <div><small>Organization</small><strong>${s.organization}</strong></div>
        </div>

        <div class="source-actions">
          <button class="primary-button" data-scan-source="${s.id}">↻ Scan Source</button>
        </div>
      </article>
    `;
  }).join('');

  container.querySelectorAll('[data-scan-source]').forEach(btn => {
    btn.addEventListener('click', () => {
      showToast('Running compliant extraction scan...');
      setTimeout(() => {
        renderSources();
        showToast('Source updated with latest procurement notices.');
      }, 500);
    });
  });
}

// Initial Initialization
loadUserProfile();
const initialHash = window.location.hash.replace('#', '');
switchView(initialHash && viewMap[initialHash] ? initialHash : 'dashboard');
