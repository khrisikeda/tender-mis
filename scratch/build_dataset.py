import json
import os

print("Writing complete market builder...")

# Load template structure or define complete set of 52 tenders and 70 sources
tenders = [
  {
    "id": "tender-rms-apheresis-lab",
    "ref": "RMS/DAO/2026/G/018/LAB-EQ",
    "title": "Supply, Delivery, and Installation of Automated Clinical Electrophoresis, Apheresis, and Auto Stainer Systems",
    "procuring_entity": "Rwanda Medical Supply (RMS) Ltd",
    "category": "Laboratory",
    "tender_value": 384000000,
    "tender_security_amount": 12800000,
    "currency": "RWF",
    "deadline_at": "2026-09-24T10:00:00+02:00",
    "published_at": "2026-08-28T09:00:00+02:00",
    "relevance_score": 95,
    "tech_spec_match": 97,
    "product_match": 94,
    "coverage_rate": 100,
    "eligibility_match": 100,
    "manufacturer_match": 95,
    "risk": "Low",
    "security": "RWF 12,800,000 (Tender Security / Bank Guarantee)",
    "authorization": "Required (Authorized OEM / Distributor)",
    "stock_readiness": "IN_STOCK",
    "stock_label": "Ready for Delivery (RMS Central Warehouse)",
    "status": "bid_preparation",
    "recommended_action": "BID_HIGH_FIT",
    "recommendation_label": "Bid (High Win Rate - Job in Rwanda)",
    "icon": "Lab",
    "source_url": "https://www.jobinrwanda.com",
    "benchmarked_european_brand": "Sebia Capillarys 3 / Terumo BCT Spectra Optia",
    "chinese_stocked_model": "Biobase & Mindray Automated Clinical Electrophoresis & Cell Stainer",
    "european_market_price_rwf": 480000000,
    "chinese_bid_price_rwf": 268000000,
    "cost_advantage_pct": 44,
    "cost_savings_rwf": 212000000,
    "equivalence_score": 97,
    "tech_parity_score": 97,
    "clinical_parity_score": 96,
    "regulatory_parity_score": 100,
    "warranty_parity_score": 95,
    "sourcing_strategy": "BID_CHINESE_EQUIVALENT",
    "sourcing_strategy_label": "Bid Automated Diagnostic Suite (97% Parity)",
    "sourcing_strategy_desc": "Live RMS tender on Job in Rwanda. Turnkey supply across 3 laboratory lots with RWF 212M national budget savings.",
    "lots": [
      {"lot_no": 1, "name": "Automated Capillary Electrophoresis Analyzer", "security_rwf": 5200000, "place": "RMS Central Logistics", "delivery_days": 45, "coverage_status": "COMPLIANT"},
      {"lot_no": 2, "name": "Continuous Flow Apheresis Cell Separation System", "security_rwf": 5100000, "place": "National Blood Transfusion Centre", "delivery_days": 45, "coverage_status": "COMPLIANT"},
      {"lot_no": 3, "name": "Automated Slide Stainer for Hematology & Cytology", "security_rwf": 2500000, "place": "RMS Central Logistics", "delivery_days": 30, "coverage_status": "COMPLIANT"}
    ],
    "items": [
      {
        "lot_id": "Lot 1", "title": "Automated Capillary Electrophoresis Analyzer", "target_brand": "Sebia Capillarys 3",
        "our_product": "Biobase Auto-Electrophoresis System 800", "compliance": "Compliant", "compliance_class": "compliant",
        "specs_count": 10, "specs_matched": 10, "score": 97, "lot_tender_security_rwf": 5200000, "qty": 4,
        "notes": "Hemoglobin, serum protein, and immunofixation capillary testing. Bi-directional LIS HL7 interface.",
        "specs_matrix": [
          {"param": "Capillary Separation Channels", "req": "Minimum 8 silica capillaries with Peltier temperature control (35.5°C ±0.1°C)", "sup": "8-capillary array with Peltier precision thermal regulation", "status": "COMPLIANT", "notes": "Exact clinical diagnostic parity"},
          {"param": "Throughput & Sample Loading", "req": "Minimum 60 samples/hour for serum proteins", "sup": "72 samples/hour with continuous primary tube rack loader", "status": "COMPLIANT", "notes": "Exceeds required throughput"},
          {"param": "Photometric Detection Optical Range", "req": "Deuterium lamp with multi-wavelength absorbance (200-600nm)", "sup": "Solid-state deuterium optical system with 200-600nm CCD detection", "status": "COMPLIANT", "notes": "Full diagnostic spectrum"}
        ]
      }
    ],
    "brand_equivalence_matrix": [
      {
        "parameter": "Electrophoretic Resolution & Serum Protein Fractionation",
        "european_benchmark": "Sebia Capillarys: 8 capillaries, 300dpi optical resolution, automated barcoding",
        "chinese_supplied": "Biobase CE-800: 8 capillaries, 350dpi optical sensor, full LIS barcode tracking",
        "status": "EXACT_MATCH",
        "justification": "Full technical and clinical resolution parity. 100% compliant with ISO 15189 laboratory standards.",
        "standards_compliance": "ISO 13485, CE-IVD, IEC 61010"
      }
    ]
  },
  {
    "id": "tender-rsog-mch-warmers",
    "ref": "RSOG/G/2026/004/MCH-EQ",
    "title": "Supply and Delivery of Advanced Infant Radiant Warmers and Maternal Health Resuscitation Equipment",
    "procuring_entity": "Rwanda Society of Obstetricians and Gynecologists (RSOG)",
    "category": "Neonatal & ICU",
    "tender_value": 145000000,
    "tender_security_amount": 4500000,
    "currency": "RWF",
    "deadline_at": "2026-09-18T10:00:00+02:00",
    "published_at": "2026-08-25T11:00:00+02:00",
    "relevance_score": 98,
    "tech_spec_match": 98,
    "product_match": 98,
    "coverage_rate": 100,
    "eligibility_match": 100,
    "manufacturer_match": 100,
    "risk": "Low",
    "security": "RWF 4,500,000 (Tender Security / Bank Guarantee)",
    "authorization": "Required (Certified Distributor / Manufacturer)",
    "stock_readiness": "IN_STOCK",
    "stock_label": "Immediate Delivery (In Stock - Kigali)",
    "status": "bid_preparation",
    "recommended_action": "BID_HIGH_FIT",
    "recommendation_label": "Bid (100% Catalogue Match)",
    "icon": "ICU",
    "source_url": "https://www.jobinrwanda.com",
    "benchmarked_european_brand": "Dräger Babyroo TN300 / GE Giraffe OmniBed",
    "chinese_stocked_model": "MedTech NEO-WRM-500 Infant Radiant Warmer",
    "european_market_price_rwf": 178000000,
    "chinese_bid_price_rwf": 92000000,
    "cost_advantage_pct": 48,
    "cost_savings_rwf": 86000000,
    "equivalence_score": 98,
    "tech_parity_score": 98,
    "clinical_parity_score": 97,
    "regulatory_parity_score": 100,
    "warranty_parity_score": 100,
    "sourcing_strategy": "BID_CHINESE_EQUIVALENT",
    "sourcing_strategy_label": "Bid Stocked NEO-WRM-500 (48% Cost Edge)",
    "sourcing_strategy_desc": "In-stock warehouse inventory matches 100% of technical criteria. Turnkey warranty and delivery within 5 business days.",
    "lots": [
      {"lot_no": 1, "name": "Infant Radiant Warmers with T-Piece Resuscitation", "security_rwf": 3000000, "place": "RSOG Partner Maternity Clinics", "delivery_days": 14, "coverage_status": "COMPLIANT"},
      {"lot_no": 2, "name": "LED Phototherapy Units for Neonatal Jaundice", "security_rwf": 1500000, "place": "RSOG Partner Maternity Clinics", "delivery_days": 14, "coverage_status": "COMPLIANT"}
    ],
    "items": [
      {
        "lot_id": "Lot 1", "title": "Infant Radiant Warmer with Microprocessor Thermal Control", "target_brand": "Dräger Babyroo TN300",
        "our_product": "NEO-WRM-500 Advanced Infant Radiant Warmer", "compliance": "Compliant", "compliance_class": "compliant",
        "specs_count": 8, "specs_matched": 8, "score": 100, "lot_tender_security_rwf": 3000000, "qty": 8,
        "notes": "Full servo control, built-in Apgar timer, and integrated LED phototherapy module.",
        "specs_matrix": [
          {"param": "Thermal Regulation Modes", "req": "Pre-warm, manual, and baby skin servo-control (34.0°C to 38.0°C)", "sup": "Pre-warm, manual, servo-controlled skin sensor (34.0°C - 38.0°C, ±0.1°C)", "status": "COMPLIANT", "notes": "Exact clinical parity"},
          {"param": "Resuscitation Module", "req": "Integrated T-piece resuscitator with PIP and PEEP manometer valves", "sup": "Built-in Venturi suction and T-piece blender resuscitator with precision dial", "status": "COMPLIANT", "notes": "Full resuscitation compliance"}
        ]
      }
    ],
    "brand_equivalence_matrix": [
      {
        "parameter": "Infrared Radiant Heating Uniformity & Skin Thermal Precision",
        "european_benchmark": "Dräger Babyroo: Quartz heating element, dual thermistor skin probe, ±0.2°C uniformity",
        "chinese_supplied": "NEO-WRM-500: Micro-crystalline ceramic infrared emitter, dual YSI-400 thermistors, ±0.1°C accuracy",
        "status": "EXACT_MATCH",
        "justification": "Superior thermal efficiency with faster heating ramp-up time (<12 min to 37°C).",
        "standards_compliance": "IEC 60601-2-21, ISO 13485:2016, CE Marked"
      }
    ]
  },
  {
    "id": "tender-chuk-mri-15t",
    "ref": "000001/G/ICB/2026/2027/CHUK-RAD",
    "title": "Turnkey Supply, Civil Works, Shielding, and Installation of 1.5 Tesla Superconducting Whole-Body MRI System",
    "procuring_entity": "University Teaching Hospital of Kigali (CHUK)",
    "category": "Imaging & Radiology",
    "tender_value": 1850000000,
    "tender_security_amount": 37000000,
    "currency": "RWF",
    "deadline_at": "2026-10-15T10:00:00+02:00",
    "published_at": "2026-08-20T08:00:00+02:00",
    "relevance_score": 92,
    "tech_spec_match": 95,
    "product_match": 92,
    "coverage_rate": 100,
    "eligibility_match": 100,
    "manufacturer_match": 95,
    "risk": "Low",
    "security": "RWF 37,000,000 (Tender Security / Bank Guarantee)",
    "authorization": "Required (Authorized OEM Manufacturer)",
    "stock_readiness": "PROJECT_DELIVERY",
    "stock_label": "45-60 Days Turnkey Installation",
    "status": "bid_preparation",
    "recommended_action": "BID_HIGH_FIT",
    "recommendation_label": "Bid (High Value Flagship Project)",
    "icon": "DIAG",
    "source_url": "https://www.umucyo.gov.rw/eb/bav/selectAdvertisingDtlInfo.do?tendReferNo=000001/G/ICB/2026/2027/CHUK-RAD",
    "benchmarked_european_brand": "Siemens Magnetom Altea 1.5T / GE Signa Explorer",
    "chinese_stocked_model": "Neusoft NeuMR 1.5T Superconducting MRI Imaging Suite",
    "european_market_price_rwf": 2600000000,
    "chinese_bid_price_rwf": 1720000000,
    "cost_advantage_pct": 34,
    "cost_savings_rwf": 880000000,
    "equivalence_score": 95,
    "tech_parity_score": 96,
    "clinical_parity_score": 94,
    "regulatory_parity_score": 100,
    "warranty_parity_score": 95,
    "sourcing_strategy": "BID_CHINESE_EQUIVALENT",
    "sourcing_strategy_label": "Bid Neusoft NeuMR 1.5T (Save RWF 880M)",
    "sourcing_strategy_desc": "Flagship quaternary hospital imaging tender. Turnkey delivery with RF cabin, helium zero-boil-off magnet, and 5-Year local warranty.",
    "lots": [
      {"lot_no": 1, "name": "1.5T Superconducting MRI Scanner & RF Cage Shielding", "security_rwf": 30000000, "place": "CHUK Masaka Complex Radiology Wing", "delivery_days": 60, "coverage_status": "COMPLIANT"},
      {"lot_no": 2, "name": "MRI Compatible Patient Monitoring & Power Chiller", "security_rwf": 7000000, "place": "CHUK Masaka Complex Radiology Wing", "delivery_days": 45, "coverage_status": "COMPLIANT"}
    ],
    "items": [
      {
        "lot_id": "Lot 1", "title": "1.5T Superconducting Whole-Body MRI System", "target_brand": "Siemens Magnetom Altea",
        "our_product": "Neusoft NeuMR 1.5T MRI System", "compliance": "Compliant", "compliance_class": "compliant",
        "specs_count": 14, "specs_matched": 14, "score": 96, "lot_tender_security_rwf": 30000000, "qty": 1,
        "notes": "70cm wide bore, 45 mT/m gradient strength, 200 T/m/s slew rate, zero liquid helium boil-off.",
        "specs_matrix": [
          {"param": "Magnet Field Strength & Homogeneity", "req": "1.5 Tesla short bore superconducting magnet (<0.3 ppm VRMS at 45cm DSV)", "sup": "1.5 Tesla zero boil-off magnet (<0.2 ppm VRMS at 45cm DSV)", "status": "COMPLIANT", "notes": "Exceeds field homogeneity requirement"},
          {"param": "Gantry Bore Diameter", "req": "Minimum 70cm flared opening for claustrophobic & bariatric patients", "sup": "70cm wide-bore with ambient mood lighting and patient airflow", "status": "COMPLIANT", "notes": "Exact compliance"}
        ]
      }
    ],
    "brand_equivalence_matrix": [
      {
        "parameter": "Gradient Performance & Diffusion Neuro/Cardiac Protocols",
        "european_benchmark": "Siemens Altea: 45 mT/m amplitude, 200 T/m/s slew rate, Tim 4G RF architecture",
        "chinese_supplied": "NeuMR 1.5T: 45 mT/m amplitude, 200 T/m/s slew rate, 32-channel digital RF receiver",
        "status": "EXACT_MATCH",
        "justification": "Full neurological, musculoskeletal, and cardiac MRI pulse sequence parity. ISO 13485 and CE certified.",
        "standards_compliance": "ISO 13485, CE 0123, FDA 510(k)"
      }
    ]
  },
  {
    "id": "tender-kfh-hemodialysis",
    "ref": "KFH/G/2026/009/RENAL-CARE",
    "title": "Supply, Delivery, Installation, and Commissioning of 12-Station Hemodialysis Machines and Central RO Water Treatment Plant",
    "procuring_entity": "King Faisal Hospital Rwanda (KFH)",
    "category": "Renal & Dialysis",
    "tender_value": 460000000,
    "tender_security_amount": 9200000,
    "currency": "RWF",
    "deadline_at": "2026-09-30T10:00:00+02:00",
    "published_at": "2026-08-24T14:00:00+02:00",
    "relevance_score": 94,
    "tech_spec_match": 97,
    "product_match": 93,
    "coverage_rate": 100,
    "eligibility_match": 100,
    "manufacturer_match": 95,
    "risk": "Low",
    "security": "RWF 9,200,000 (Tender Security / Bank Guarantee)",
    "authorization": "Required (Authorized OEM Partner)",
    "stock_readiness": "ORDER_LEAD_TIME",
    "stock_label": "21 Days Factory Lead Time",
    "status": "bid_preparation",
    "recommended_action": "BID_HIGH_FIT",
    "recommendation_label": "Bid (High Win Rate - KFH Sourcing)",
    "icon": "DIAG",
    "source_url": "https://kfh.rw/tenders",
    "benchmarked_european_brand": "Fresenius 5008S CorDiax / Nikkiso DBB-06",
    "chinese_stocked_model": "WEGO DBB-06 & Double-Pass RO Water Treatment Plant (1500 L/h)",
    "european_market_price_rwf": 620000000,
    "chinese_bid_price_rwf": 385000000,
    "cost_advantage_pct": 38,
    "cost_savings_rwf": 235000000,
    "equivalence_score": 96,
    "tech_parity_score": 97,
    "clinical_parity_score": 95,
    "regulatory_parity_score": 100,
    "warranty_parity_score": 95,
    "sourcing_strategy": "BID_CHINESE_EQUIVALENT",
    "sourcing_strategy_label": "Bid WEGO Dialysis Suite (Save RWF 235M)",
    "sourcing_strategy_desc": "Turnkey renal expansion for KFH Dialysis Wing. Includes 12 touchscreen hemodiafiltration units and double-pass reverse osmosis plant.",
    "lots": [
      {"lot_no": 1, "name": "12 Online Hemodiafiltration (HDF) Dialysis Machines", "security_rwf": 7000000, "place": "King Faisal Hospital Dialysis Department", "delivery_days": 30, "coverage_status": "COMPLIANT"},
      {"lot_no": 2, "name": "Double-Pass Medical Reverse Osmosis (RO) Water Plant (1500L/h)", "security_rwf": 2200000, "place": "King Faisal Hospital Dialysis Department", "delivery_days": 30, "coverage_status": "COMPLIANT"}
    ],
    "items": [
      {
        "lot_id": "Lot 1", "title": "Online Hemodiafiltration (HDF) Dialysis Unit", "target_brand": "Fresenius 5008S CorDiax",
        "our_product": "WEGO Online HDF Hemodialysis System", "compliance": "Compliant", "compliance_class": "compliant",
        "specs_count": 12, "specs_matched": 12, "score": 97, "lot_tender_security_rwf": 7000000, "qty": 12,
        "notes": "Online post-dilution and pre-dilution HDF, automated blood volume monitoring (BVM), ultrafiltration profiling.",
        "specs_matrix": [
          {"param": "Dialysate Flow & Volumetric Balance", "req": "Flow rate 300 - 800 mL/min, volumetric balance chamber accuracy ±0.1%", "sup": "Flow rate 100 - 1000 mL/min, high-precision hydraulic balance chamber ±0.05%", "status": "COMPLIANT", "notes": "Exceeds flow precision"},
          {"param": "Online Substitution Fluid Filter", "req": "Dual endotoxin retentive ultrafilters for pyrogen-free substitution fluid", "sup": "Integrated dual-stage cascade pyrogen filters with automated integrity test", "status": "COMPLIANT", "notes": "Certified sterile infusate"}
        ]
      }
    ],
    "brand_equivalence_matrix": [
      {
        "parameter": "Hemodiafiltration Clearance (Kt/V) & Middle Molecule Removal",
        "european_benchmark": "Fresenius 5008S: AutoSub plus, Online clearance monitor (OCM), blood temperature monitor",
        "chinese_supplied": "WEGO DBB-06: Real-time Kt/V monitor, dynamic ultrafiltration profiling, automated disinfection",
        "status": "EXACT_MATCH",
        "justification": "Full clinical clearance parity. Approved in leading nephrology centers globally.",
        "standards_compliance": "ISO 13485, EN 60601-2-16, CE 0197"
      }
    ]
  },
  {
    "id": "tender-ruhengeri-oxygen-psa",
    "ref": "000005/G/NCB/2026/2027/1603000000",
    "title": "Turnkey Supply, Installation, and Commissioning of Medical Oxygen Generation PSA Plant (50 m3/h) with Dual Cylinder Filling Manifold",
    "procuring_entity": "Ruhengeri Referral Hospital (Northern Province)",
    "category": "Medical Gas & Infrastructure",
    "tender_value": 320000000,
    "tender_security_amount": 6400000,
    "currency": "RWF",
    "deadline_at": "2026-09-25T10:00:00+02:00",
    "published_at": "2026-08-27T08:30:00+02:00",
    "relevance_score": 96,
    "tech_spec_match": 98,
    "product_match": 95,
    "coverage_rate": 100,
    "eligibility_match": 100,
    "manufacturer_match": 95,
    "risk": "Low",
    "security": "RWF 6,400,000 (Tender Security / Bank Guarantee)",
    "authorization": "Required (Authorized Manufacturer / Engineering Contractor)",
    "stock_readiness": "PROJECT_DELIVERY",
    "stock_label": "30 Days Turnkey Plant Assembly",
    "status": "bid_preparation",
    "recommended_action": "BID_HIGH_FIT",
    "recommendation_label": "Bid (RPPA Compliant PSA Sourcing)",
    "icon": "OXY",
    "source_url": "https://www.umucyo.gov.rw/eb/bav/selectAdvertisingDtlInfo.do?tendReferNo=000005/G/NCB/2026/2027/1603000000",
    "benchmarked_european_brand": "Atlas Copco OGP 50 / Oxymat PSA Oxygen Generator",
    "chinese_stocked_model": "MedAir Tech PSA Medical Oxygen Plant (50 Nm3/h, 93±3% Purity)",
    "european_market_price_rwf": 460000000,
    "chinese_bid_price_rwf": 275000000,
    "cost_advantage_pct": 40,
    "cost_savings_rwf": 185000000,
    "equivalence_score": 97,
    "tech_parity_score": 98,
    "clinical_parity_score": 97,
    "regulatory_parity_score": 100,
    "warranty_parity_score": 95,
    "sourcing_strategy": "BID_CHINESE_EQUIVALENT",
    "sourcing_strategy_label": "Bid Medical PSA Oxygen Plant (Save RWF 185M)",
    "sourcing_strategy_desc": "High-priority national hospital oxygen self-reliance project. Turnkey delivery with oil-free air compressors, ZMS adsorption towers, and 40-cylinder filling ramp.",
    "lots": [
      {"lot_no": 1, "name": "50 Nm3/h Medical PSA Oxygen Generator & Air Treatment System", "security_rwf": 4800000, "place": "Ruhengeri Referral Hospital", "delivery_days": 45, "coverage_status": "COMPLIANT"},
      {"lot_no": 2, "name": "High-Pressure Booster Compressor & 2x20 Cylinder Filling Manifold", "security_rwf": 1600000, "place": "Ruhengeri Referral Hospital", "delivery_days": 30, "coverage_status": "COMPLIANT"}
    ],
    "items": [
      {
        "lot_id": "Lot 1", "title": "50 Nm3/h Medical Oxygen PSA Generator", "target_brand": "Atlas Copco OGP 50",
        "our_product": "MedAir Tech 50Nm3/h Medical PSA Oxygen System", "compliance": "Compliant", "compliance_class": "compliant",
        "specs_count": 10, "specs_matched": 10, "score": 98, "lot_tender_security_rwf": 4800000, "qty": 1,
        "notes": "Medical oxygen 93% ±3% purity compliant with European Pharmacopoeia and ISO 13485.",
        "specs_matrix": [
          {"param": "Oxygen Purity & Capacity", "req": "Flow rate minimum 50 Nm3/h with continuous purity 93% ±3% and ZrO2 analyzer", "sup": "50 Nm3/h output with dual zirconia continuous optical oxygen purity monitors", "status": "COMPLIANT", "notes": "Exact pharmacopoeial parity"},
          {"param": "Air Compressor & Desiccant Dryer", "req": "Heavy-duty rotary screw compressor (IE3 motor) with -40°C pressure dew point dryer", "sup": "High-efficiency rotary screw compressor with twin-tower desiccant air dryer", "status": "COMPLIANT", "notes": "Exceeds standard"}
        ]
      }
    ],
    "brand_equivalence_matrix": [
      {
        "parameter": "Adsorption Cycle Efficiency & Purity Stability",
        "european_benchmark": "Atlas Copco OGP: PLC controller, automatic purge vent on low purity, 93±3% standard",
        "chinese_supplied": "MedAir PSA-50: Siemens PLC touch control, automated divert valve (<90% purity), remote telemetry",
        "status": "EXACT_MATCH",
        "justification": "Delivers continuous hospital pipeline pressure (4.5 - 5.0 bar) with 100% adherence to European Pharmacopoeia.",
        "standards_compliance": "ISO 13485, ISO 7396-1, CE Medical Device"
      }
    ]
  }
]

print(f"Base flagship tenders ready: {len(tenders)}")
