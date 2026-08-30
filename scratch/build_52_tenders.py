import json

tenders_list = []

# List of 52 detailed realistic tenders across Rwanda
dataset_specs = [
  # 1. RMS Electrophoresis
  ("tender-rms-apheresis-lab", "RMS/DAO/2026/G/018/LAB-EQ", "Supply, Delivery, and Installation of Automated Clinical Electrophoresis, Apheresis, and Auto Stainer Systems", "Rwanda Medical Supply (RMS) Ltd", "Laboratory", 384000000, 12800000, "2026-09-24T10:00:00+02:00", "2026-08-28T09:00:00+02:00", 95, 97, "Lab", "Sebia Capillarys 3 / Terumo BCT Spectra Optia", "Biobase & Mindray Automated Clinical Electrophoresis & Cell Stainer", 480000000, 268000000,
   ["Automated Capillary Electrophoresis Analyzer", "Continuous Flow Apheresis Cell Separation System", "Automated Slide Stainer for Hematology"],
   [("Capillary Separation Channels", "Minimum 8 silica capillaries with Peltier thermal control (35.5°C ±0.1°C)", "8-capillary array with Peltier precision thermal regulation", "Exact clinical diagnostic parity"),
    ("Throughput & Sample Loading", "Minimum 60 samples/hour for serum proteins", "72 samples/hour with continuous primary tube rack loader", "Exceeds throughput requirement"),
    ("Photometric Detection Optical Range", "Deuterium lamp with multi-wavelength absorbance (200-600nm)", "Solid-state deuterium optical system with 200-600nm CCD detection", "Full diagnostic spectrum")]),

  # 2. RSOG Radiant Warmers
  ("tender-rsog-mch-warmers", "RSOG/G/2026/004/MCH-EQ", "Supply and Delivery of Advanced Infant Radiant Warmers and Maternal Health Resuscitation Equipment", "Rwanda Society of Obstetricians and Gynecologists (RSOG)", "Neonatal & ICU", 145000000, 4500000, "2026-09-18T10:00:00+02:00", "2026-08-25T11:00:00+02:00", 98, 98, "ICU", "Dräger Babyroo TN300 / GE Giraffe OmniBed", "MedTech NEO-WRM-500 Infant Radiant Warmer", 178000000, 92000000,
   ["Infant Radiant Warmers with T-Piece Resuscitation", "LED Phototherapy Units for Neonatal Jaundice"],
   [("Thermal Regulation Modes", "Pre-warm, manual, and baby skin servo-control (34.0°C to 38.0°C)", "Pre-warm, manual, servo-controlled skin sensor (34.0°C - 38.0°C, ±0.1°C)", "Exact clinical parity"),
    ("Resuscitation Module", "Integrated T-piece resuscitator with PIP and PEEP manometer valves", "Built-in Venturi suction and T-piece blender resuscitator with precision dial", "Full resuscitation compliance")]),

  # 3. CHUK 1.5T MRI
  ("tender-chuk-mri-15t", "000001/G/ICB/2026/2027/CHUK-RAD", "Turnkey Supply, Civil Works, Shielding, and Installation of 1.5 Tesla Superconducting Whole-Body MRI System", "University Teaching Hospital of Kigali (CHUK)", "Imaging & Radiology", 1850000000, 37000000, "2026-10-15T10:00:00+02:00", "2026-08-20T08:00:00+02:00", 92, 95, "DIAG", "Siemens Magnetom Altea 1.5T / GE Signa Explorer", "Neusoft NeuMR 1.5T Superconducting MRI Imaging Suite", 2600000000, 1720000000,
   ["1.5T Superconducting MRI Scanner & RF Cage Shielding", "MRI Compatible Patient Monitoring & Power Chiller"],
   [("Magnet Field Strength & Homogeneity", "1.5 Tesla short bore superconducting magnet (<0.3 ppm VRMS at 45cm DSV)", "1.5 Tesla zero boil-off magnet (<0.2 ppm VRMS at 45cm DSV)", "Exceeds field homogeneity requirement"),
    ("Gantry Bore Diameter", "Minimum 70cm flared opening for claustrophobic & bariatric patients", "70cm wide-bore with ambient mood lighting and patient airflow", "Exact compliance")]),

  # 4. KFH Hemodialysis
  ("tender-kfh-hemodialysis", "KFH/G/2026/009/RENAL-CARE", "Supply, Delivery, Installation, and Commissioning of 12-Station Hemodialysis Machines and Central RO Water Treatment Plant", "King Faisal Hospital Rwanda (KFH)", "Renal & Dialysis", 460000000, 9200000, "2026-09-30T10:00:00+02:00", "2026-08-24T14:00:00+02:00", 94, 97, "DIAG", "Fresenius 5008S CorDiax / Nikkiso DBB-06", "WEGO DBB-06 & Double-Pass RO Water Treatment Plant (1500 L/h)", 620000000, 385000000,
   ["12 Online Hemodiafiltration (HDF) Dialysis Machines", "Double-Pass Medical Reverse Osmosis (RO) Water Plant (1500L/h)"],
   [("Dialysate Flow & Volumetric Balance", "Flow rate 300 - 800 mL/min, volumetric balance chamber accuracy ±0.1%", "Flow rate 100 - 1000 mL/min, high-precision hydraulic balance chamber ±0.05%", "Exceeds flow precision"),
    ("Online Substitution Fluid Filter", "Dual endotoxin retentive ultrafilters for pyrogen-free substitution fluid", "Integrated dual-stage cascade pyrogen filters with automated integrity test", "Certified sterile infusate")]),

  # 5. Ruhengeri PSA Oxygen Plant
  ("tender-ruhengeri-oxygen-psa", "000005/G/NCB/2026/2027/1603000000", "Turnkey Supply, Installation, and Commissioning of Medical Oxygen Generation PSA Plant (50 m3/h) with Dual Cylinder Filling Manifold", "Ruhengeri Referral Hospital", "Medical Gas & Infrastructure", 320000000, 6400000, "2026-09-25T10:00:00+02:00", "2026-08-27T08:30:00+02:00", 96, 98, "OXY", "Atlas Copco OGP 50 / Oxymat PSA Oxygen Generator", "MedAir Tech PSA Medical Oxygen Plant (50 Nm3/h, 93±3% Purity)", 460000000, 275000000,
   ["50 Nm3/h Medical PSA Oxygen Generator & Air Treatment System", "High-Pressure Booster Compressor & 2x20 Cylinder Filling Manifold"],
   [("Oxygen Purity & Capacity", "Flow rate minimum 50 Nm3/h with continuous purity 93% ±3% and ZrO2 analyzer", "50 Nm3/h output with dual zirconia continuous optical oxygen purity monitors", "Exact pharmacopoeial parity"),
    ("Air Compressor & Desiccant Dryer", "Heavy-duty rotary screw compressor (IE3 motor) with -40°C pressure dew point dryer", "High-efficiency rotary screw compressor with twin-tower desiccant air dryer", "Exceeds standard")]),

  # 6. CHUB 4K Laparoscopy Tower
  ("tender-chub-laparoscopy-4k", "000002/G/NCB/2026/2027/CHUB-SURG", "Supply and Installation of 4K Ultra HD Endoscopic Surgical Laparoscopy Tower System with Dual Monitor Arm", "University Teaching Hospital of Butare (CHUB)", "Surgical", 185000000, 3700000, "2026-09-22T10:00:00+02:00", "2026-08-26T09:15:00+02:00", 97, 98, "DIAG", "Karl Storz Image1 S 4K / Olympus Visera Elite II", "Mindray HyPixel R1 4K UHD Laparoscopy Suite", 240000000, 148000000,
   ["4K UHD Camera Control Unit & 300W LED Light Source", "Electronic CO2 Insufflator 45L/min & Autoclavable Telescopes (0°/30°)"],
   [("Image Sensor & Video Output", "Native 3840x2160 pixels at 60fps with HDR color enhancement", "Ultra HD 4K 1/1.8-inch CMOS with 12G-SDI / HDMI 2.0 zero-latency output", "Full 4K surgical resolution"),
    ("Insufflation Flow Rate", "High-flow 45 L/min with active gas heating and automatic venting", "45 L/min micro-controlled heating insufflator with smoke evacuation channel", "Exceeds safety criteria")]),

  # 7. RMH Kanombe 128-Slice CT Scanner
  ("tender-rmh-ct-128", "000004/G/ICB/2026/2027/RMH-RAD", "Turnkey Supply, Installation, and Commissioning of 128-Slice Diagnostic Whole-Body CT Scanner for Trauma & Cardiac Imaging", "Rwanda Military Hospital (RMH Kanombe)", "Imaging & Radiology", 1150000000, 23000000, "2026-10-08T10:00:00+02:00", "2026-08-22T10:00:00+02:00", 93, 96, "DIAG", "Siemens SOMATOM go.Top / GE Revolution EVO", "Neusoft NeuViz 128-Slice Diagnostic Whole-Body CT", 1650000000, 1080000000,
   ["128-Slice CT Gantry, X-Ray Tube & Generator System", "Cardiac CTA Post-Processing Server & Dual-Head Contrast Injector"],
   [("Gantry Rotation & Slice Count", "0.33s gantry rotation speed with 128 physical slices per rotation", "0.33s rotation with 128 true anatomical slices reconstructed per cycle", "Exact clinical rotation speed"),
    ("AI Dose Modulation & Radiation Safety", "Iterative reconstruction algorithm reducing radiation dose by >50%", "ClearView deep-learning iterative dose reduction up to 60% lower dose", "Full ALARA radiation protection")]),

  # 8. Masaka Referral Hospital Digital DR X-Ray
  ("tender-masaka-dr-xray", "000001/G/NCB/2026/2027/MASAKA-RAD", "Supply, Delivery, Installation, and Civil Shielding of Ceiling-Suspended Digital Radiography (DR) Dual Detector X-Ray System", "Masaka Referral Teaching Hospital", "Imaging & Radiology", 240000000, 4800000, "2026-09-28T10:00:00+02:00", "2026-08-25T14:30:00+02:00", 96, 97, "DIAG", "Philips DigitalDiagnost C90 / Canon CXDI", "Angell Dynamic Ceiling-Suspended Digital DR X-Ray", 340000000, 210000000,
   ["Ceiling Suspended X-Ray Tube Stand & Motorized Elevating Table", "Dual Wireless Cesium Iodide (CsI) Flat Panel Detectors (43x43cm)"],
   [("Detector Quantum Efficiency (DQE)", "Direct-deposit CsI flat panel detector with minimum 70% DQE at 0 lp/mm", "Wireless 140-micron CsI detector with 75% DQE and auto-exposure detection (AED)", "Exceeds image sharpness"),
    ("High-Voltage Generator Output", "Minimum 65 kW high-frequency generator (up to 150 kV, 800 mA)", "80 kW ultra-high frequency multi-pulse generator with anatomical programming", "Superior penetration power")]),

  # 9. National Reference Lab 5-Part Hematology & Biochemistry
  ("tender-nrl-hematology-biochem", "000003/G/NCB/2026/2027/RBC-NRL", "Supply, Delivery, and Reagent Rental of High-Throughput 5-Part Differential Hematology and Fully Automated Biochemistry Analyzers", "National Reference Laboratory (NRL)", "Laboratory", 295000000, 5900000, "2026-09-29T10:00:00+02:00", "2026-08-24T16:00:00+02:00", 97, 98, "Lab", "Sysmex XN-1000 / Roche Cobas c501", "Biobase BK-6190 5-Part Hematology & BK-800 Biochemistry Suite", 410000000, 245000000,
   ["Automated 5-Part Differential Hematology Analyzer (110 tests/hour)", "Floor-Standing Clinical Chemistry Analyzer (800 photometric tests/hour)"],
   [("Hematology Measurement Technology", "Semiconductor laser scatter combined with chemical dye flow cytometry", "Tri-angle laser scatter flow cytometry with fluorescent dye technology", "Identical white blood cell classification"),
    ("Chemistry Photometric Throughput", "Minimum 800 tests/hour with ISE module (Na/K/Cl/Li)", "800 photometric + 400 ISE tests/hour with refrigerated 160-position reagent carousel", "Exceeds daily laboratory demand")]),

  # 10. King Faisal Hospital CSSD 300L Steam Autoclave
  ("tender-kfh-cssd-autoclave", "KFH/G/2026/012/CSSD-STERIL", "Supply, Installation, and Validation of 300-Litre Horizontal Double-Door Pass-Through Steam Sterilizers for Central Sterile Department", "King Faisal Hospital Rwanda (KFH)", "Surgical", 165000000, 3300000, "2026-10-02T10:00:00+02:00", "2026-08-23T11:00:00+02:00", 95, 96, "DIAG", "Belimed MST-V 600 / Tuttnauer 3870", "Tuttnauer Biomedical / OEM 300L Double-Door Pass-Through Autoclave", 220000000, 138000000,
   ["300L Class B Pass-Through Horizontal Steam Sterilizer", "Integrated Clean Steam Generator with Reverse Osmosis Feed"],
   [("Chamber Material & Safety Certification", "Solid 316L stainless steel chamber with ASME / EN 285 pressure vessel standard", "AISI 316L mirror-polished chamber, pneumatic double-door bio-barrier seal", "Full hospital CSSD standard compliance"),
    ("Vacuum & Drying Performance", "High-efficiency liquid-ring vacuum pump with fractionated pre-vacuum cycles", "Heavy-duty water-ring vacuum pump achieving residual moisture <0.2%", "Meets international sterilisation norms")]),

  # 11. Kabgayi Hospital Ophthalmic Phaco & Slit Lamps
  ("tender-kabgayi-eye-phaco", "000008/G/NCB/2026/2027/KABGAYI-EYE", "Supply and Delivery of Ophthalmic Cataract Phacoemulsification Systems, Surgical Operating Microscopes, and Digital Slit Lamps", "Kabgayi District Hospital & Eye Unit", "Ophthalmology", 135000000, 2700000, "2026-09-20T10:00:00+02:00", "2026-08-26T10:00:00+02:00", 96, 97, "EYE", "Alcon Centurion Vision System / Haag-Streit BM 900", "Appasamy & Biobase Phacoemulsification Cataract System Pro", 195000000, 118000000,
   ["High-Frequency Ultrasound Phacoemulsification Cataract Unit", "Ophthalmic Surgical Operating Microscope with XY Coupling", "Digital Slit Lamp with Integrated HD Anterior Segment Camera"],
   [("Ultrasound Handpiece & Vacuum", "Elliptical / torsional ultrasound vibration with peristaltic & Venturi dual pump", "40 kHz high-efficiency piezoelectric handpiece with dual-pump dynamic fluidics", "Full anterior segment surgical precision"),
    ("Optical Clarity & Illumination", "Apochromatic optics with stereo coaxial illumination and red reflex", "German optical glass multi-layer coating with red reflex coaxial LED light", "Exact surgical visualization")]),

  # 12. UR-HG Physical Therapy & Multi-Station Gym
  ("tender-urhg-gym-rehab", "URHG/G/2026/001/REHAB-GYM", "Supply, Delivery, and Installation of Biomechanical Physical Therapy, Multi-Station Strength Conditioning, and Rehabilitation Gym Equipment", "University of Rwanda Holding Group (UR-HG Ltd)", "Physical Therapy & Gym", 88000000, 1760000, "2026-09-17T10:00:00+02:00", "2026-08-26T12:00:00+02:00", 98, 98, "GYM", "Technogym Biostrength / Matrix Fitness Rehab Series", "Commercial Grade ISO 20957 Biomechanical Gym & Rehab Station", 130000000, 72000000,
   ["Multi-User 5-Station Biomechanical Cable & Pulley Rehabilitation Tower", "Commercial Heavy-Duty Motorized Treadmills with Cardiac Telemetry", "Ergometric Recumbent Rehabilitation Bikes with Biofeedback"],
   [("Chassis Structural Integrity", "Heavy-gauge 3mm Q235 structural steel tube with electrostatically powder coated finish", "Heavy-gauge 3.2mm structural steel with dual corrosion-resistant baked powder coat", "Exceeds mechanical strength requirement"),
    ("Rehabilitation Biofeedback", "Integrated Polar telemetry heart rate monitoring and customizable resistance steps", "ANT+ and Bluetooth 5.0 cardiac monitoring with clinical low-speed 0.1 km/h start", "Full physiotherapeutic compliance")]),

  # 13. RMS Bulk Nitrile Surgical Gloves Framework (1.5M Pairs)
  ("tender-rms-gloves-framework", "RMS/DAO/2026/G/021/GLV-FRM", "Framework Contract for Supply and Delivery of Sterile Powder-Free Surgical and Examination Nitrile Gloves (1.5 Million Pairs)", "Rwanda Medical Supply (RMS) Ltd", "Consumables", 520000000, 10400000, "2026-09-27T10:00:00+02:00", "2026-08-27T11:00:00+02:00", 99, 99, "Consumables", "Ansell Gammex / Molnlycke Biogel", "MedTender Sterile Powder-Free Nitrile Surgical Gloves (Sizes 6.5 - 8.5)", 750000000, 420000000,
   ["Sterile Nitrile Surgical Gloves (Sizes 6.5, 7.0, 7.5, 8.0, 8.5)", "Non-Sterile Nitrile Medical Examination Gloves (Sizes S, M, L)"],
   [("Barrier Protection & Pinholes", "AQL 0.65 freedom from pinholes for surgical and AQL 1.5 for examination", "AQL 0.65 certified gamma-irradiated surgical barrier, 100% batch tested", "Superior barrier safety"),
    ("Tensile Strength & Elongation", "Minimum 18 MPa tensile strength, 650% elongation at break before aging", "21 MPa tensile strength, 700% elongation, micro-textured non-slip wet grip", "Meets EN 455 Parts 1-4 and ASTM D6978")]),

  # 14. RBC National PCR Viral Load Analyzers
  ("tender-rbc-viral-pcr", "000006/G/NCB/2026/2027/RBC-MOH", "Supply and Installation of Automated Real-Time Quantitative RT-PCR Analyzers for Viral Load and Infectious Disease Surveillance", "Rwanda Biomedical Centre (RBC)", "Laboratory", 260000000, 5200000, "2026-10-05T10:00:00+02:00", "2026-08-25T15:00:00+02:00", 94, 96, "Lab", "Applied Biosystems QuantStudio 5 / Bio-Rad CFX96", "Biobase LineGene 9600 Plus Real-Time PCR Detection System", 360000000, 215000000,
   ["96-Well Real-Time Quantitative PCR Detection Systems (6 Optical Channels)", "Automated Magnetic Bead Nucleic Acid Extraction Workstations"],
   [("Optical Detection Channels", "Minimum 6 optical detection channels covering FAM/VIC/ROX/CY5/CY5.5", "6-channel high-sensitivity cold CCD with long-life maintenance-free LED excitation", "Full fluorescent multiplex capability"),
    ("Thermal Uniformity & Ramp Rate", "Peltier heating/cooling with maximum ramp rate ≥5.0°C/sec, uniformity ±0.2°C", "Solid-state Peltier elements with 5.5°C/sec ramp rate and ±0.15°C thermal precision", "Exceeds diagnostic standard")]),

  # 15. RMH Multi-Gas Anaesthesia Workstations
  ("tender-rmh-anaesthesia-workstation", "000007/G/NCB/2026/2027/RMH-OR", "Supply, Delivery, and Installation of Advanced Multi-Gas Anaesthesia Delivery Workstations with Patient Vital Monitoring", "Rwanda Military Hospital (RMH Kanombe)", "Surgical", 210000000, 4200000, "2026-10-01T10:00:00+02:00", "2026-08-26T11:30:00+02:00", 96, 97, "ICU", "Dräger Perseus A500 / Mindray WATO EX-65", "MedTech WATO Advance Multi-Gas Anaesthesia Station", 290000000, 185000000,
   ["Anaesthesia Delivery Workstation with Integrated ICU-Grade Ventilator", "Paramagnetic O2 & Multi-Gas Halogenated Agent Vaporizer (Isoflurane/Sevoflurane)"],
   [("Ventilation Modes & Tidal Volume", "PCV, VCV, SIMV, PSV, PRVC with tidal volume range 20 - 1500 mL (Neonate to Adult)", "Comprehensive ventilation (VCV, PCV, SIMV-V/P, PSV, PRVC) tidal volume 10 - 1500 mL", "Covers neonatal to bariatric patients"),
    ("Gas Delivery & Flowmeter", "Electronic gas mixer with virtual digital flowmeter tubes and hypoxic guard", "Electronic multi-gas mixer with active minimum 25% O2 anti-hypoxic safety interlock", "Full clinical safety assurance")]),

  # 16. CHUK Masaka PACS & 5MP Diagnostic Displays
  ("tender-umucyo-chuk-workstations", "000002/G/ICB/2026/2027/RBC", "Supply and Installation of IT, PACS Servers, and Diagnostic Workstation Equipment for CHUK Masaka", "Rwanda Biomedical Centre (RBC)", "Digital Health & Telemedicine", 15099425, 301988, "2026-09-28T10:00:00+02:00", "2026-08-26T12:00:00+02:00", 90, 93, "DIAG", "Barco Coronis / HP Z-Series Medical Workstation", "Beacon Medical 5MP DICOM Grayscale/Color Displays & PACS Servers", 25000000, 14200000,
   ["5MP High-Resolution Diagnostic Radiology Displays & Workstations", "Enterprise PACS Archive Server with HL7 / DICOM 3.0 Bridge"],
   [("Display Resolution & Calibration", "Minimum 5MP (2560x2048) resolution with hardware DICOM Part 14 calibration", "5MP IPS medical panel, 1000 cd/m2 brightness, built-in front sensor calibration", "Exceeds calibration requirement"),
    ("Diagnostic Luminance Precision", "14-bit grayscale lookup table with ambient light compensation", "14-bit LUT with dynamic luminance stabilization QA software suite", "FDA 510(k) cleared for digital mammography")]),

  # 17. SAMU Advanced Emergency Ambulances
  ("tender-samu-ambulances-typeb", "SAMU/G/2026/001/AMB-4WD", "Supply and Delivery of 10 Fully Equipped Type B Emergency Advanced Life Support Ambulances with 4WD Reinforced Chassis", "SAMU Emergency Medical Services Rwanda", "Emergency & Ambulance", 750000000, 15000000, "2026-10-12T10:00:00+02:00", "2026-08-24T09:00:00+02:00", 92, 95, "Consumables", "Mercedes-Benz Sprinter 4x4 / Toyota Land Cruiser Emergency", "Foton & Toyota 4WD High-Roof Advanced Life Support Ambulance", 1050000000, 680000000,
   ["4WD High-Roof Emergency Ambulance Vehicle with Heavy-Duty Suspension", "Integrated Onboard Medical Equipment: Transport Defibrillator, Ventilator, Suction, Oxygen"],
   [("Chassis & Powertrain", "Diesel turbo 4-cylinder engine, minimum 130 kW, selectable 4WD with high ground clearance", "Heavy-duty 2.8L Turbo Diesel 130 kW, reinforced 4WD chassis with rough-terrain skid plates", "Built for Rwanda rural and hilly terrain"),
    ("Onboard Life Support Fitout", "Seamless antibacterial ABS interior wall lining with certified roll-over crash cage", "EN 1789 certified medical compartment, dual medical oxygen cylinders (2x10L), 220V inverter", "Full SAMU emergency medical compliance")]),

  # 18. Ngarama Hospital Medical Air Compressor
  ("tender-ngarama-air-compressor", "000004/G/NCB/2026/2027/6300003001", "Supply and Installation of Medical Air Compressor and Central Medical Vacuum System for ICU and Neonatology", "Ngarama District Hospital", "Medical Gas & Infrastructure", 65000000, 1300000, "2026-09-24T10:00:00+02:00", "2026-08-26T14:00:00+02:00", 96, 97, "AIR", "Atlas Copco Medical Air / BeaconMedaes", "MedAir ISO 7396 Duplex Medical Air & Vacuum Package", 95000000, 58000000,
   ["Duplex Oil-Free Scroll Medical Air Compressor (4.0 bar, 600 L/min)", "Duplex Rotary Vane Medical Vacuum System with Bacterial Filter Array"],
   [("Air Quality Standard", "ISO 8573-1 Class 1.2.1 oil-free medical breathing air (<0.01 mg/m3 residual oil)", "100% oil-free scroll pump with desiccant dryers delivering -40°C pressure dew point", "Meets European Pharmacopoeia air standards"),
    ("Emergency Redundancy (Duplex)", "100% duplex backup operation with automated PLC changeover in case of single failure", "Dual independent compressor pumps with Siemens PLC auto-alternation and telemetry", "Guarantees zero interruption to neonatology")]),

  # 19. Nyamata Emergency Diagnostic Ultrasound
  ("tender-nyamata-ultrasound", "000002/G/NCB/2026/2027/6500003002", "Supply and Delivery of High-Resolution Color Doppler Diagnostic Ultrasound Systems for Emergency and Obstetrics", "Nyamata District Hospital", "Imaging & Radiology", 72000000, 1440000, "2026-09-23T10:00:00+02:00", "2026-08-27T10:00:00+02:00", 97, 98, "DIAG", "GE Voluson E8 / Mindray DC-70", "Mindray & Sonoscape High-Resolution Color Doppler Ultrasound Suite", 110000000, 66000000,
   ["Shared Service Color Doppler Ultrasound System with 21.5-inch LED Monitor", "Broadband Convex, Linear, and Endocavitary Transducer Array"],
   [("Imaging Modes & Transducers", "B, M, Color Doppler, Power Doppler, Pulsed Wave (PW), Continuous Wave (CW), 3D/4D", "Full clinical multi-modality suite with single-crystal high-density probe technology", "Full maternal and emergency imaging"),
    ("Automated Biometry Tools", "AI-assisted automated fetal biometry calculation (BPD, HC, AC, FL) and cardiac EF", "Smart OB auto-measurement with DICOM 3.0 direct PACS networking", "Exceeds district diagnostic workflow")]),

  # 20. Butaro Cancer Centre Digital Mammography
  ("tender-butaro-mammography", "000009/G/NCB/2026/2027/BUTARO-ONCO", "Supply, Civil Shielding, and Commissioning of Full-Field Digital Mammography System with 3D Tomosynthesis", "Butaro Cancer Centre of Excellence Hospital", "Imaging & Radiology", 340000000, 6800000, "2026-10-10T10:00:00+02:00", "2026-08-25T13:00:00+02:00", 93, 95, "DIAG", "Hologic Selenia Dimensions / GE Senographe Pristina", "Anke & Neusoft Digital Breast Tomosynthesis Mammography Suite", 480000000, 310000000,
   ["Full-Field Digital Mammography System with Iso-Centric Motorized C-Arm", "High-Resolution Acquisition Workstation with 5MP Review Monitors"],
   [("Detector Technology & Tomosynthesis", "Direct conversion Amorphous Selenium (a-Se) detector with 15° or wider tomosynthesis sweep", "Direct-deposit a-Se detector with 25° high-angular tomosynthesis acquisition", "Superior lesion detection"),
    ("Patient Comfort & Compression", "Smart motorized compression with curved comfort paddle and automatic decompression", "Intelligent smooth pressure sensing paddle with soft-touch ergonomic breast support", "Reduces patient discomfort")]),

  # 21. Gisenyi Hospital Blood Gas & Electrolyte Analyzers
  ("tender-gisenyi-blood-gas", "000010/G/NCB/2026/2027/GISENYI-EMERG", "Supply, Delivery, and Maintenance of Point-of-Care Blood Gas, Electrolyte, and Lactate Critical Care Analyzers", "Gisenyi Referral Hospital", "Laboratory", 48000000, 960000, "2026-09-22T10:00:00+02:00", "2026-08-27T14:00:00+02:00", 98, 98, "Lab", "Radiometer ABL90 FLEX / Instrumentation Laboratory GEM 4000", "Edan i15 Critical Care Point-of-Care Blood Gas & Electrolyte System", 68000000, 42000000,
   ["Cartridge-Based Point-of-Care Blood Gas & Co-Oximetry Analyzers", "Reagent Cartridge Starter Packs with Integrated Calibration QC"],
   [("Sample Volume & Analysis Speed", "Maximum 70 microliters whole blood, results in <60 seconds", "Micro-sample 65 uL whole blood with comprehensive results ready in 45 seconds", "Fast clinical decision in emergency"),
    ("Measured Parameter Profile", "pH, pCO2, pO2, Na+, K+, Cl-, Ca++, Glu, Lac, Hct, sO2, CO-Oximetry fractions", "Full 15-parameter critical panel with auto-calibration and zero maintenance", "Exact emergency care parity")]),

  # 22. Kibagabaga Modular ICU Patient Monitors
  ("tender-kibagabaga-icu-monitors", "000011/G/NCB/2026/2027/KIBAGABAGA-ICU", "Supply, Delivery, and Central Station Networking of Modular 12.1-inch Multiparameter ICU Patient Monitors", "Kibagabaga District Hospital", "Neonatal & ICU", 92000000, 1840000, "2026-09-26T10:00:00+02:00", "2026-08-26T16:00:00+02:00", 98, 99, "ICU", "Mindray BeneVision N12 / Philips IntelliVue MX450", "MedTech ICU-MON-12 Modular Multiparameter Monitoring Station", 135000000, 84000000,
   ["12.1-inch Multi-Touch ICU Patient Monitors (ECG, SpO2, NIBP, Dual Temp, Dual IBP, EtCO2)", "Central Nursing Station with Dual 24-inch Diagnostic Displays & Remote Alarm Routing"],
   [("Arrhythmia Detection & ST Analysis", "23 arrhythmia classifications with multi-lead ST segment and QT/QTc interval analysis", "26 arrhythmia types, automated Glasgow ECG algorithm, continuous ST vector mapping", "Exceeds cardiac monitoring criteria"),
    ("Defibrillator & ESU Protection", "Full electrosurgical unit (ESU) interference suppression and 5000V defibrillation protection", "Certified 5kV anti-defibrillation isolation with active electrosurgical noise filtering", "Complies with IEC 60601-2-27")]),

  # 23. Muhima Transport Neonatal Incubators
  ("tender-muhima-transport-incubator", "000012/G/NCB/2026/2027/MUHIMA-MAT", "Supply and Delivery of Advanced Transport Neonatal Incubators with Integrated Ventilator and O2 Monitoring", "Muhima District Hospital", "Neonatal & ICU", 85000000, 1700000, "2026-09-21T10:00:00+02:00", "2026-08-25T11:00:00+02:00", 97, 98, "ICU", "Dräger TI500 Globe-Trotter / Atom Infant Transport", "MedTech Transport Neonatal Incubator Pro with Collapsible Ambulance Trolley", 120000000, 78000000,
   ["Mobile Transport Infant Incubator with Battery & 12V/220V Power System", "Integrated Transport Infant CPAP / T-Piece Resuscitator and Pulse Oximeter"],
   [("Battery Autonomy & Thermal Stability", "Minimum 3 hours continuous heating operation on internal rechargeable battery", "4.5 hours continuous lithium-ion heating battery with dual ambulance 12V/24V input", "Safe inter-hospital transfer across Kigali"),
    ("Vibration Dampening & Trolley", "Shock-absorbing ambulance stretcher trolley with secure vehicle latch lock", "EN 1789 certified crash-tested 10G locking trolley with pneumatic suspension", "Guarantees neonatal safety")]),

  # 24. Rwamagana Low-Temp Plasma Sterilizer
  ("tender-rwamagana-plasma-sterilizer", "000013/G/NCB/2026/2027/RWAMAGANA-CSSD", "Supply and Installation of Fast-Cycle Hydrogen Peroxide Low-Temperature Gas Plasma Sterilizer for Sensitive Optics", "Rwamagana Provincial Hospital", "Surgical", 78000000, 1560000, "2026-09-27T10:00:00+02:00", "2026-08-26T15:00:00+02:00", 96, 97, "DIAG", "STERRAD 100NX / Steris V-PRO maX", "Biobase Plasma Hydrogen Peroxide Low-Temp Sterilizer (100L)", 115000000, 71000000,
   ["100-Litre Hydrogen Peroxide Gas Plasma Sterilization Chamber", "Biological Indicators, Chemical Strips, and Tyvek Sterilization Pouch Starter Kit"],
   [("Cycle Time & Lumen Penetration", "Standard cycle ≤45 min, flexible endoscope lumen cycle ≤30 min without residue", "Fast cycle 28 min with RF plasma breakdown into harmless water vapor and oxygen", "Rapid instrument turnaround"),
    ("Temperature Control Precision", "Chamber operating temperature strictly ≤55°C to protect delicate laparoscopes", "Microprocessor controlled temperature at 45°C - 50°C with digital pressure sensors", "Preserves endoscopic camera seals")]),

  # 25. Nyagatare Motorized Floor Digital X-Ray
  ("tender-nyagatare-floor-xray", "000014/G/NCB/2026/2027/NYAGATARE-RAD", "Supply, Civil Works, Shielding, and Installation of Motorized Floor-Mounted Digital Radiography (DR) X-Ray System", "Nyagatare District Hospital", "Imaging & Radiology", 145000000, 2900000, "2026-09-30T10:00:00+02:00", "2026-08-27T12:00:00+02:00", 97, 98, "DIAG", "Siemens Multix Impact / Shimadzu RADspeed", "Angell Floor-Mounted Motorized Digital Radiography Suite", 210000000, 132000000,
   ["Floor-Mounted Tubestand with Elevating 4-Way Floating Top Table", "Wireless High-Resolution Cesium Iodide (CsI) Flat Panel Detector"],
   [("Generator Power & Tube Load", "Minimum 50 kW high frequency generator with 300 kHU thermal capacity tube", "55 kW high frequency generator with 350 kHU rotating anode X-ray tube", "Heavy daily patient capacity"),
    ("Image Processing Engine", "Advanced multi-frequency image enhancement and grid suppression software", "AI-driven edge enhancement with automated stitching for full spine/long leg", "Superior diagnostic clarity")]),

  # 26. Nyanza Electro-Hydraulic Operating Table
  ("tender-nyanza-or-tables", "000015/G/NCB/2026/2027/NYANZA-SURG", "Supply and Delivery of Electro-Hydraulic Universal Operating Theatre Tables and Dual-Head LED Surgical Lights", "Nyanza District Hospital", "Surgical", 68000000, 1360000, "2026-09-23T10:00:00+02:00", "2026-08-25T16:30:00+02:00", 98, 98, "DIAG", "Maquet Alphamaquet / Getinge Meera", "Mindray & MedTech Electro-Hydraulic Universal Surgical Table Suite", 98000000, 61000000,
   ["Electro-Hydraulic Universal Surgical Tables with Radiolucent Kidney Bridge", "Dual-Head Ceiling Suspended Surgical LED Lights (160,000 / 120,000 Lux)"],
   [("Weight Capacity & Articulation", "Minimum 250 kg safe patient working load with Trendelenburg ±30° and lateral tilt ±20°", "300 kg safe working load with Trendelenburg ±32°, lateral tilt ±22°, flex/reflex", "Exceeds bariatric surgery load"),
    ("C-Arm Compatibility & Imaging", "Full-length radiolucent carbon fiber table top with >300mm longitudinal shift", "350mm longitudinal sliding top allowing 100% full-body C-arm imaging clearance", "Optimal intraoperative fluoroscopy")]),

  # 27. Byumba 6-Bed Hemodialysis Package
  ("tender-byumba-dialysis-package", "000016/G/NCB/2026/2027/BYUMBA-DIAL", "Turnkey Supply, Installation, and Commissioning of 6-Station Hemodialysis Clinic Package with RO Water Treatment", "Byumba District Hospital", "Renal & Dialysis", 230000000, 4600000, "2026-10-04T10:00:00+02:00", "2026-08-27T15:00:00+02:00", 95, 96, "DIAG", "Fresenius 4008S NG / B. Braun Dialog+", "WEGO 6-Station Hemodialysis System with Single-Pass RO Water Plant (800L/h)", 320000000, 205000000,
   ["6 Modern Hemodialysis Treatment Stations with Motorized Dialysis Chairs", "Medical Reverse Osmosis Water Purification System (800 L/h)"],
   [("Dialysis Precision & UF Control", "Volumetric ultrafiltration control accuracy ±30 mL/h with sodium profiling", "Closed-loop volumetric balance control with customizable profiling and blood leak detector", "High patient comfort and safety"),
    ("Water Purification Microbial Standard", "Medical RO water compliant with ISO 23500 (Endotoxin <0.25 EU/mL)", "Dual-stage pre-filtration with RO membrane producing ultrapure water <0.03 EU/mL", "Meets national nephrology standards")]),

  # 28. Kibuye Bulk Cryogenic Liquid Oxygen VIE
  ("tender-kibuye-liquid-oxygen", "000017/G/NCB/2026/2027/KIBUYE-OXY", "Civil Foundations, Supply, and Commissioning of 5,000-Litre Cryogenic Liquid Medical Oxygen Vacuum Insulated Tank (VIE)", "Kibuye Referral Hospital", "Medical Gas & Infrastructure", 195000000, 3900000, "2026-10-06T10:00:00+02:00", "2026-08-26T17:00:00+02:00", 94, 96, "OXY", "Chart Industries VIE Tank / Air Liquide", "CryoTech 5000L Vacuum Insulated Medical Oxygen Evaporator Tank Package", 280000000, 175000000,
   ["5,000-Litre Cryogenic Vertical Liquid Oxygen Pressure Vessel (16 bar)", "Ambient Air Vaporizers (100 Nm3/h) and Dual Pressure Regulating Manifold"],
   [("Thermal Insulation & Boil-Off Rate", "High-vacuum perlite insulation with daily natural boil-off rate <0.35%", "High-grade cryogenic multi-layer vacuum insulation with daily evaporation <0.28%", "Minimal oxygen loss in tropical climate"),
    ("Safety Relief & Telemetry", "Dual ASME certified safety pressure relief valves with digital remote telemetry gauge", "Dual safety burst discs, automated pressure economizer, and GSM remote tank level telemetry", "Safe continuous hospital supply")]),

  # 29. Kirehe Coagulation & Urine Sediment
  ("tender-kirehe-lab-coag-urine", "000018/G/NCB/2026/2027/KIREHE-LAB", "Supply and Delivery of Automated Blood Coagulation Analyzers and Digital Urine Sediment Flow Cytometers", "Kirehe District Hospital", "Laboratory", 42000000, 840000, "2026-09-25T10:00:00+02:00", "2026-08-28T08:00:00+02:00", 97, 98, "Lab", "Stago Compact Max / Sysmex UF-500i", "Biobase Automated Optical Coagulation & Urine Sediment Suite", 62000000, 38000000,
   ["Automated 4-Channel Optical Coagulation Analyzer (PT, APTT, FIB, TT, D-Dimer)", "Automated Urine Chemistry & Formed Element Microscopic Imaging System"],
   [("Coagulation Methodology", "Magnetic bead clotting combined with chromogenic and immunoturbidimetric assays", "Dual magnetic sensor and optical LED detection avoiding lipemic/icteric interference", "Accurate bleeding disorder testing"),
    ("Urine Sediment Recognition", "Automated digital flow morphology identification of RBC, WBC, casts, crystals", "High-speed planar flow microscopy with deep-learning image particle classification", "Eliminates manual microscopy errors")]),

  # 30. Bushenge Neonatal Bubble CPAP
  ("tender-bushenge-bubble-cpap", "000019/G/NCB/2026/2027/BUSHENGE-MCH", "Supply and Delivery of Continuous Positive Airway Pressure (Bubble CPAP) Systems and Infant Phototherapy for Neonatology", "Bushenge Provincial Hospital", "Neonatal & ICU", 36000000, 720000, "2026-09-22T10:00:00+02:00", "2026-08-25T17:00:00+02:00", 98, 99, "ICU", "Fisher & Paykel Healthcare Bubble CPAP / Diamedica", "MedTech Neonatal Bubble CPAP with Integrated Heated Humidifier & Blender", 52000000, 31000000,
   ["Neonatal Bubble CPAP Systems with Air/Oxygen Precision Blender", "Servo-Controlled Heated Humidification Chambers and Reusable Silicone Prongs"],
   [("Air/Oxygen Blender Precision", "FiO2 adjustment range 21% to 100% with flow meter 0 - 15 L/min", "Precision mechanical gas blender (21-100% ±3%) with continuous ultrasonic O2 sensor", "Protects preterm infants from retinopathy"),
    ("Pressure Generation & Bubbler", "Clear bubbler bottle with calibrated submersion depth 1 - 10 cm H2O and pop-off safety", "Calibrated auto-filling bubbler reservoir with 0-10 cm H2O scale and 15 cm H2O safety relief", "Gentle neonatal lung recruitment")]),

  # 31. Ruli Hospital Dental Operatory Chair
  ("tender-ruli-dental-chair", "000020/G/NCB/2026/2027/RULI-DENT", "Supply, Delivery, and Installation of Compact Dental Operatory Unit with Oil-Free Air Compressor and LED Curing Light", "Ruli District Hospital", "Dental", 28000000, 560000, "2026-09-28T10:00:00+02:00", "2026-08-28T10:30:00+02:00", 98, 99, "Consumables", "Planmeca Compact i / A-dec 300", "MedTech DEN-UNT-300 Ergonomic Dental Operatory Suite", 42000000, 24000000,
   ["Dental Treatment Chair with 5-Hole Delivery Instrument Tray", "Oil-Free Ultra-Quiet Dental Air Compressor (50L Tank) & Autoclavable Handpieces"],
   [("Electromechanical Chair Movement", "Silent low-voltage DC motors with Trendelenburg synchronization and memory presets", "Smooth hydraulic/DC actuators, seamless antibacterial upholstery, 3 programmable memories", "Comfortable patient positioning"),
    ("Water & Suction System", "Self-contained distilled water bottle system with high-volume surgical aspirator", "Dual clean water switch, built-in saliva ejector, and multi-stage ceramic spittoon filter", "Strict infection control standard")]),

  # 32. PIH Wireless Point-of-Care Ultrasound
  ("tender-pih-poc-ultrasound", "PIH-RW-2026-POC-US", "Supply and Delivery of 20 Handheld Dual-Probe Wireless Point-of-Care Ultrasound (POCUS) Scanners for Rural Health Centers", "Partners In Health / Inshuti Mu Buzima (PIH)", "Imaging & Radiology", 64000000, 1280000, "2026-09-20T10:00:00+02:00", "2026-08-26T18:00:00+02:00", 96, 98, "DIAG", "Butterfly iQ+ / GE Vscan Air", "SonoWireless Dual-Head (Curved + Linear) Handheld Ultrasound Scanner", 95000000, 54000000,
   ["20 Handheld Dual-Probe Wireless Pocket Ultrasound Scanners", "20 Ruggedized Android Medical Tablets with Pre-Installed Diagnostic Software"],
   [("Transducer Architecture", "Dual-headed probe with phased/curved (deep) and linear (superficial) arrays", "Integrated single-housing Convex (2.5-5.0 MHz) + Linear (7.5-10.0 MHz) waterproof probe", "Complete rural triage scanning"),
    ("Wireless Transmission & Battery", "Wi-Fi 5GHz / Bluetooth connection with minimum 2.5 hours continuous scan time", "Direct Wi-Fi point-to-point transmission to iOS/Android, wireless induction charging", "Ideal for off-grid rural clinics")]),

  # 33. Global Fund Flow Cytometry CD4
  ("tender-globalfund-cd4", "GLOBALFUND-RW-2026-CD4", "Supply and Delivery of Benchtop Multi-Color Flow Cytometers and Reagents for National CD4/CD8 Monitoring", "Global Fund to Fight AIDS, TB & Malaria (Rwanda)", "Laboratory", 175000000, 3500000, "2026-10-09T10:00:00+02:00", "2026-08-25T18:30:00+02:00", 94, 96, "Lab", "BD FACSLyric / Beckman Coulter CytoFLEX", "Biobase FlowMaster 4-Laser Multi-Color Benchtop Flow Cytometer", 245000000, 155000000,
   ["Benchtop 3-Laser 10-Color Clinical Flow Cytometry System", "Automated No-Wash CD4/CD8 Reagent Kits and QC Calibration Beads"],
   [("Lasers & Detectors", "Minimum 3 solid-state lasers (488nm, 638nm, 405nm) with 10 fluorescent channels", "Blue (488nm), Red (638nm), Violet (405nm) lasers with avalanche photodiode detectors", "Precise immunophenotyping"),
    ("Volumetric Absolute Counting", "Direct volumetric absolute cell counting without reference beads", "Micro-syringe direct absolute volume measurement (accuracy >98%)", "Fast turnaround for antiretroviral therapy")]),

  # 34. Enabel Solar Vaccine Refrigerators
  ("tender-enabel-solar-refrigerators", "ENABEL-RW-2026-SOLAR-MCH", "Supply, Delivery, and Installation of Solar Direct Drive (SDD) Vaccine & Biological Reagent Refrigerators for 30 Health Centers", "Enabel Rwanda - Belgian Development Agency", "Medical Gas & Infrastructure", 110000000, 2200000, "2026-09-26T10:00:00+02:00", "2026-08-27T16:00:00+02:00", 98, 99, "Consumables", "Dometic TCW 2000 SDD / B Medical Systems TCW40SDD", "Biobase WHO PQS Certified Solar Direct Drive Vaccine Refrigerator Package", 155000000, 95000000,
   ["30 WHO-PQS Certified Solar Direct Drive (SDD) Vaccine Refrigerators (80L Net)", "30 Rooftop Solar Photovoltaic Panels with Heavy-Duty Mounting & Surge Arrestors"],
   [("WHO PQS Certification Standard", "Strict WHO/PQS E003/050 certification with freeze-free ice-lining technology", "WHO PQS certified (PQS code E003/088), holdover time >72 hours at +43°C ambient", "Zero risk of vaccine freezing"),
    ("Battery-Free Direct Drive", "100% battery-free solar direct drive compressor utilizing phase change materials", "CFC-free R600a refrigerant, maintenance-free phase change thermal storage", "Reliable 10-year field lifespan")]),

  # 35. WHO Genomic Sequencing Surveillance
  ("tender-who-genomic-sequencer", "WHO-RW-2026-GENOM-SEQ", "Supply, Delivery, Commissioning, and Reagents for Benchtop Next-Generation Targeted Genomic Sequencing Platform", "WHO Country Office Rwanda", "Laboratory", 390000000, 7800000, "2026-10-14T10:00:00+02:00", "2026-08-26T19:00:00+02:00", 91, 94, "Lab", "Illumina NextSeq 550 / Oxford Nanopore PromethION", "MGI Tech DNBSEQ-G99 Fast High-Throughput Genomic Sequencer", 540000000, 360000000,
   ["Benchtop Fast High-Throughput Genomic Sequencing Instrument", "Multiplex Viral Pathogen & Antimicrobial Resistance Library Preparation Kits"],
   [("Sequencing Chemistry & Output", "Sequencing-by-synthesis or DNB technology producing >50 Gb data per run in <24h", "DNBSEQ patterned array technology generating 8 - 96 Gb per 12-hour sequencing run", "Rapid pathogen outbreak identification"),
    ("Base Calling Accuracy (Q30)", "Minimum 85% of bases with quality score Q30 or higher (accuracy 99.9%)", "Q30 score >90% for standard 2x150bp paired-end sequencing protocol", "Meets international surveillance standards")]),

  # 36. UNICEF Newborn Resuscitation Kits (500 Sets)
  ("tender-unicef-resus-kits", "UNICEF-RW-2026-RESUS-KITS", "Supply and Delivery of 500 Sets of Reusable Neonatal Bag-Valve-Mask Manual Resuscitation Kits and Foot-Operated Suction Units", "UNICEF Rwanda Child Health Programme", "Consumables", 58000000, 1160000, "2026-09-19T10:00:00+02:00", "2026-08-25T19:00:00+02:00", 99, 100, "Consumables", "Laerdal Neonatal Resuscitator / Ambu Baby", "MedTender Autoclavable Silicone Neonatal Bag-Valve-Mask Resuscitator 500-Pack", 82000000, 49000000,
   ["500 Reusable 100% Liquid Silicone Neonatal Manual Resuscitation Bags (250mL)", "500 Sets of Transparent Neonatal Face Masks (Sizes 00, 0, 1) and Foot Suction Pumps"],
   [("Material & Autoclavability", "100% medical-grade silicone autoclavable up to 134°C (minimum 50 cycles)", "High-transparency liquid silicone rubber fully autoclavable up to 134°C", "Long-term reusable durability"),
    ("Pressure Relief Valve", "Integrated 40 cm H2O pressure limiting pop-off valve with override lock", "40 cm H2O automatic safety blow-off valve with audible click and override clip", "Prevents neonatal barotrauma")]),

  # 37. USAID Ultra-Low -86C Freezers
  ("tender-usaid-ult-freezers", "USAID-PSM-2026-COLD-CHAIN", "Supply and Delivery of 15 Ultra-Low Temperature (-86°C) Dual-Compressor Biomedical Freezers for Vaccine Hubs", "USAID / GHSC-PSM Global Health Supply Chain", "Medical Gas & Infrastructure", 125000000, 2500000, "2026-09-29T10:00:00+02:00", "2026-08-27T17:30:00+02:00", 96, 97, "Consumables", "Thermo Scientific TSX / PHCbi VIP ECO", "Haier Biomedical / Biobase -86°C TwinGuard Dual Independent Cooling Freezer (500L)", 180000000, 112000000,
   ["15 Dual-Refrigeration Ultra-Low -86°C Freezers (500-Litre Storage)", "CO2 Backup Emergency Injection System and 24/7 Temperature Data Loggers"],
   [("Dual Independent Cooling System", "Two independent refrigeration circuits maintaining -70°C even if one compressor fails", "Dual TwinGuard independent compressors: if one system trips, remaining holds -75°C", "Zero risk of sample compromise"),
    ("Natural Hydrocarbon Refrigerants", "Eco-friendly HC refrigerants (R290/R170) with low global warming potential (GWP)", "Environmentally green hydrocarbon refrigerants, 40% lower power consumption", "Low energy footprint in Rwanda")]),

  # 38. Ndera 64-Channel Video EEG Telemetry
  ("tender-ndera-video-eeg", "NDERA-NEURO-EEG-2026", "Supply, Installation, and Commissioning of 64-Channel Clinical Video EEG Telemetry System with Polysomnography (PSG)", "Ndera Neuropsychiatric Teaching Hospital (Caraes)", "Imaging & Radiology", 82000000, 1640000, "2026-10-03T10:00:00+02:00", "2026-08-26T19:30:00+02:00", 94, 96, "DIAG", "Natus NicoletOne / Nihon Kohden Neurofax", "Biobase 64-Channel High-Precision Video EEG & EMG Workstation", 120000000, 74000000,
   ["64-Channel Digital EEG Headbox with Low-Noise Isolation Amplifier", "Infrared Pan-Tilt-Zoom High-Definition Video Monitoring Camera & Analysis Suite"],
   [("Sampling Rate & Input Impedance", "Minimum 2048 Hz sampling rate, 24-bit A/D conversion, input impedance >100 MOhm", "4096 Hz hardware sampling, 24-bit sigma-delta ADC, 200 MOhm high impedance", "Superior neurological waveform clarity"),
    ("Automated Spike & Seizure Detection", "Real-time automated spike, sharp wave, and epileptic seizure detection algorithm", "AI-powered automated spike-wave mapping with sleep staging polysomnography (PSG)", "Assists neurologist diagnosis")]),

  # 39. UR-HG Non-Contact Corneal Tonometer
  ("tender-urhg-tonometer", "URHG/G/2026/002/OPHTH-TONO", "Supply and Delivery of Non-Contact Auto Tonometer with Automated Corneal Thickness Pachymetry Compensation", "University of Rwanda Holding Group (UR-HG Ltd)", "Ophthalmology", 38000000, 760000, "2026-09-24T10:00:00+02:00", "2026-08-27T18:00:00+02:00", 98, 99, "EYE", "Topcon CT-80 / Nidek NT-530", "Biobase Automated Air-Puff Non-Contact Tonometer with Pachymetry", 54000000, 32000000,
   ["Non-Contact Auto Tonometer with Gentle Air Puff & 3D Auto-Tracking", "Built-In Thermal Printer and Bi-Directional EMR Interface Cable"],
   [("Measurement Puff Pressure & Comfort", "Soft and quiet air puff with auto-alignment and automated trigger", "Intelligent gentle air puff adjusting pressure based on previous patient readings", "High patient comfort"),
    ("Central Corneal Thickness (CCT) Compensation", "Automated intraocular pressure (IOP) compensation based on Scheimpflug/pachymetry", "Integrated pachymeter recalculating true IOP according to corneal curvature", "Accurate glaucoma screening")]),

  # 40. RMH High-End Dental CBCT 3D
  ("tender-rmh-dental-cbct", "000010/G/ICB/2026/2027/RMH-DENT", "Supply, Shielding, and Commissioning of 3-in-1 Dental Cone Beam Computed Tomography (CBCT), Panoramic, and Cephalometric Imaging System", "Rwanda Military Hospital (RMH Kanombe)", "Dental", 195000000, 3900000, "2026-10-11T10:00:00+02:00", "2026-08-25T20:00:00+02:00", 93, 95, "DIAG", "Carestream CS 8100 3D / Planmeca ProMax 3D", "LargeV HiRes 3-in-1 Dental CBCT & Panoramic Imaging System", 270000000, 172000000,
   ["3-in-1 Cone Beam CT Gantry with Multiple Field of View (FOV 5x5 to 16x10 cm)", "3D Implant Planning and Maxillofacial Diagnostic Workstation"],
   [("Spatial Resolution & Voxel Size", "Voxel size selectable down to 75 microns with pulsed X-ray beam technology", "Ultra-high resolution 70-micron isotropic voxels with pulsed low-dose exposure", "Micro-structural dental & root canal detail"),
    ("Implant & Orthodontic Software", "Full 3D implant library simulation with nerve canal tracing and surgical guide export", "Comprehensive implant database, nerve canal auto-detection, and open STL export", "Maxillofacial surgical planning")]),

  # 41. CHUB Electrosurgical Diathermy with Vessel Sealer
  ("tender-chub-diathermy-vessel", "000009/G/NCB/2026/2027/CHUB-SURG", "Supply and Delivery of High-Frequency Electrosurgical Diathermy Units with Advanced Bipolar Vessel Sealing (up to 7mm)", "University Teaching Hospital of Butare (CHUB)", "Surgical", 62000000, 1240000, "2026-09-26T10:00:00+02:00", "2026-08-26T20:00:00+02:00", 97, 98, "DIAG", "Covidien LigaSure / Erbe VIO 300D", "MedTech High-Frequency Electrosurgical Diathermy with LigaSeal 7mm Technology", 88000000, 54000000,
   ["400W High-Frequency Electrosurgical Generator with Monopolar & Bipolar Modes", "Tissue-Sensing Vessel Sealing Handpieces and Autoclavable Foot Switches"],
   [("Vessel Sealing Capacity", "Sealing of blood vessels and tissue bundles up to 7mm diameter with minimal thermal spread", "Intelligent tissue impedance feedback sealing vessels up to 7mm with <1.5mm thermal spread", "Fast bloodless surgical resection"),
    ("Contact Quality Monitoring (CQM)", "Return electrode contact quality monitoring to prevent patient grounding burns", "Dual-zone neutral plate monitoring with automatic RF cut-off and alarm", "Maximum operating room patient safety")]),

  # 42. KFH Smart Infusion & Syringe Pumps (50 Units)
  ("tender-kfh-infusion-pumps", "KFH/G/2026/015/ICU-PUMPS", "Supply, Delivery, and Central Wireless Networking of 50 Smart Volumetric Infusion Pumps and Dual-Channel Syringe Pumps", "King Faisal Hospital Rwanda (KFH)", "Neonatal & ICU", 75000000, 1500000, "2026-09-28T10:00:00+02:00", "2026-08-27T19:00:00+02:00", 98, 99, "ICU", "B. Braun Infusomat Space / Alaris CareFusion", "MedTech Smart Stackable Infusion & Micro-Syringe Pump System (50-Set)", 110000000, 68000000,
   ["30 Smart Volumetric Peristaltic Infusion Pumps with Dose Error Reduction", "20 High-Precision Dual-Channel Micro-Syringe Pumps (0.1 - 1500 mL/h)"],
   [("Flow Rate Accuracy & Micro-Infusion", "Accuracy ±5% for volumetric and ±2% for syringe pumps with anti-bolus function", "High precision ±4.5% volumetric and ±1.8% syringe delivery with auto anti-bolus pressure release", "Ultra-safe pediatric & ICU drug titration"),
    ("Drug Dose Library & Wi-Fi Gateway", "Customizable multi-department drug library with soft/hard dose limits", "Built-in 2000-drug library with customizable clinical limits and Wi-Fi central monitoring", "Prevents medication dosage errors")])
]

# Generate remaining tenders to make exactly 52 rich tenders
extra_tenders_raw = [
  # 43. Kibogora C-Arm
  ("tender-kibogora-c-arm", "000001/G/NCB/2026/2027/5600003001", "Supply, Installation, and Commissioning of Digital Mobile C-Arm Fluoroscopy Imaging System for Orthopedic Surgery", "Kibogora Hospital", "Imaging & Radiology", 165000000, 3300000, "2026-09-27T10:00:00+02:00", "2026-08-27T20:00:00+02:00", 96, 97, "DIAG", "Ziehm Solo FD / GE OEC One", "Angell Flat-Panel Mobile Surgical C-Arm System", 230000000, 145000000,
   ["Mobile C-Arm Gantry with Flat Panel Detector (21x21cm)", "Dual High-Resolution 19-inch Surgical Review Monitors"],
   [("Detector Type & Pulsed Fluoroscopy", "Dynamic CMOS or CsI flat panel detector with pulsed fluoroscopy up to 30 fps", "High-sensitivity flat panel detector with low-dose micro-pulsed fluoroscopy", "Superb bone fracture & implant guidance"),
    ("Orbital Movement & Free Space", "Minimum 135° orbital rotation with 780mm free space for orthopedic positioning", "140° orbital rotation with 800mm deep arc clearance", "Effortless positioning in sterile field")]),

  # 44. Kibilizi Lab Analyzers
  ("tender-kibilizi-lab-suite", "000001/G/NCB/2026/2027/4300003002", "Supply and Delivery of Automated 5-Part Hematology and Clinical Chemistry Analyzers for District Laboratory", "Kibilizi District Hospital", "Laboratory", 52000000, 1040000, "2026-09-24T10:00:00+02:00", "2026-08-26T21:00:00+02:00", 97, 98, "Lab", "Mindray BC-5000 / Dirui CS-T240", "Biobase BK-5000 5-Part Hematology & Auto-Chemistry Suite", 76000000, 48000000,
   ["5-Part Differential Automated Hematology Analyzer (60 samples/h)", "Benchtop Automatic Clinical Chemistry Analyzer (240 tests/h)"],
   [("Reagent Efficiency & Sample Volume", "Low sample volume <20 uL with only 3 routine reagents", "Micro-sample 15 uL whole blood with low reagent consumption", "Economical district operational cost"),
    ("LIS Integration & Quality Control", "Bi-directional RS232/Ethernet LIS interface with Levey-Jennings QC charts", "Full HL7 LIS integration with automated multi-rule Westgard QC verification", "Streamlined reporting")]),

  # 45. Kigeme Infant Incubators
  ("tender-kigeme-mch-incubators", "000001/G/NCB/2026/2027/5500003001", "Supply and Delivery of Servo-Controlled Neonatal Intensive Care Incubators and Intensive Phototherapy Units", "Kigeme District Hospital", "Neonatal & ICU", 46000000, 920000, "2026-09-22T10:00:00+02:00", "2026-08-25T21:30:00+02:00", 98, 99, "ICU", "Atom Air Incu i / Dräger Isolette 8000", "MedTech Intensive Infant Incubator with Servo Humidity & Air/Skin Modes", 68000000, 41000000,
   ["Double-Walled Intensive Care Neonatal Incubators with Servo Humidity", "High-Intensity LED Overhead Phototherapy Lamps"],
   [("Humidity & Temperature Control", "Servo humidity control up to 95% RH with double wall canopy to prevent heat loss", "Active ultrasonic humidity generator (up to 95% RH) with dual skin thermistors", "Prevents hypothermia in micro-preemies"),
    ("Quiet Acoustic Environment", "Internal hood noise level <45 dB to protect fragile infant auditory development", "Whisper-quiet airflow with internal acoustic level <42 dB", "Promotes neurodevelopmental care")]),

  # 46. Gisenyi Emergency Defibrillators
  ("tender-gisenyi-biphasic-defib", "000014/G/NCB/2026/2027/GISENYI-EMERG", "Supply and Delivery of Portable Biphasic Defibrillator Monitors with Pacing and Automated External (AED) Mode", "Gisenyi Referral Hospital", "Neonatal & ICU", 38000000, 760000, "2026-09-25T10:00:00+02:00", "2026-08-27T21:00:00+02:00", 98, 99, "ICU", "Zoll R Series / Mindray BeneHeart D3", "MedTech Biphasic 360J Defibrillator Monitor with Non-Invasive Pacing", 56000000, 34000000,
   ["Biphasic Defibrillator Monitors with Synchronized Cardioversion & Pacing", "Adult & Pediatric Multifunction Defibrillation Pads and Internal Paddles"],
   [("Energy Range & Waveform", "Biphasic truncated exponential waveform with selectable energy 1 - 360 Joules", "360J Biphasic waveform with impedance compensation and fast charge (<5 sec to 200J)", "Rapid resuscitation response"),
    ("Diagnostic 12-Lead ECG & SpO2", "Integrated 12-lead ECG analysis, SpO2, and non-invasive blood pressure monitoring", "12-lead diagnostic ECG with interpretive algorithm and real-time CPR quality feedback", "Exceeds emergency standards")]),

  # 47. CHUK Blood Bank Ultralow Freezers
  ("tender-chuk-blood-bank", "CHUK/G/2026/022/BLOOD-FREEZE", "Supply and Delivery of Blood Bank Refrigerators (+4°C) and Plasma Shock Freezers (-40°C) with Temperature Monitoring", "University Teaching Hospital of Kigali (CHUK)", "Laboratory", 64000000, 1280000, "2026-10-01T10:00:00+02:00", "2026-08-26T22:00:00+02:00", 97, 98, "Lab", "Helmer Scientific Blood Bank / B Medical Systems", "Haier Biomedical / Biobase +4°C Blood Bank & -40°C Plasma Storage Suite", 92000000, 58000000,
   ["+4°C Precision Blood Bank Refrigerator with Stainless Steel Roll-Out Drawers (600L)", "-40°C Quick-Freeze Plasma Storage Cabinet with Dual Refrigeration"],
   [("Temperature Stability & Alarm", "Forced-air circulation maintaining +4°C ±1°C with 7-day chart recorder", "Microprocessor PID control with multi-point temperature sensors and SMS remote alarm", "Guarantees blood product safety"),
    ("DIN 58371 Medical Standard", "Full compliance with DIN 58371 blood storage standard with auto-defrost", "Certified DIN 58371 / ISO 13485 compliant with power failure battery backup", "Zero spoilage guarantee")]),

  # 48. Muhima Maternity Delivery Beds
  ("tender-muhima-delivery-beds", "000015/G/NCB/2026/2027/MUHIMA-BEDS", "Supply and Delivery of Motorized Ergonomic Obstetric Labor and Delivery Beds with Leg Supports", "Muhima District Hospital", "Medical Equipment", 44000000, 880000, "2026-09-23T10:00:00+02:00", "2026-08-25T22:30:00+02:00", 98, 99, "DIAG", "LINET AVE 2 / Hill-Rom Affinity 4", "MedTech Motorized Obstetric Delivery Bed with Rapid CPR & Trendelenburg", 65000000, 39000000,
   ["Motorized Obstetric Delivery Beds with Integrated Fluid Basin", "Ergonomic Pneumatic Leg Crutches and Padded Arm Supports"],
   [("Motorized Height & Positioning", "Electric height adjustment, backrest, and pelvic tilt with foot switch controls", "Quad-motor smooth electric positioning with emergency mechanical CPR release", "Maximizes maternal comfort"),
    ("Infection Control & Materials", "Seamless antibacterial mattress with welded waterproof seams", "High-density visco-elastic foam mattress with removable fluid catch basin", "Easy hospital sanitation")]),

  # 49. Nyanza Surgical Suction Units
  ("tender-nyanza-suction-pumps", "000016/G/NCB/2026/2027/NYANZA-SUCT", "Supply and Delivery of Heavy-Duty High-Vacuum High-Flow Surgical Electric Suction Pumps for Operating Rooms", "Nyanza District Hospital", "Surgical", 26000000, 520000, "2026-09-24T10:00:00+02:00", "2026-08-26T22:30:00+02:00", 99, 100, "Consumables", "Medela Dominant Flex / Atmos C 451", "MedTech Heavy-Duty Mobile Surgical Suction Pump (Dual 4L Bottles)", 38000000, 22000000,
   ["Mobile Heavy-Duty Surgical Suction Units with Twin 4-Litre Autoclavable Jars", "Hydrophobic Antibacterial Overflow Filter Arrays (50-Pack)"],
   [("Suction Flow & Vacuum Level", "Flow rate minimum 60 L/min with vacuum up to -0.90 bar (-675 mmHg)", "Piston pump delivering 70 L/min flow and -0.92 bar maximum vacuum in <10 seconds", "Fast fluid evacuation during surgery"),
    ("Overflow Protection", "Mechanical float overflow valve combined with hydrophobic filter barrier", "Dual overflow safety: mechanical float valve + hydrophobic bacterial barrier", "Protects pump motor from fluids")]),

  # 50. Butaro Oncology Infusion Chairs
  ("tender-butaro-infusion-chairs", "000017/G/NCB/2026/2027/BUTARO-ONCO", "Supply and Delivery of Motorized Day-Care Chemotherapy Infusion Recliner Chairs with IV Pole & Arm Support", "Butaro Cancer Centre of Excellence Hospital", "Medical Equipment", 35000000, 700000, "2026-09-28T10:00:00+02:00", "2026-08-27T22:00:00+02:00", 98, 99, "DIAG", "Champion Medical Seating / LINET Therapy", "MedTech Motorized Oncology Infusion Recliner Chair Suite", 50000000, 31000000,
   ["Multi-Position Motorized Chemotherapy Infusion Recliners", "Stainless Steel Dual-Hook Heavy Duty IV Infusion Poles"],
   [("Reclining Mechanism & Comfort", "3-motor adjustment for backrest, leg rest, and height with zero-gravity position", "Smooth 3-motor whisper-quiet adjustment with one-touch Trendelenburg safety", "Ensures long oncology infusion comfort"),
    ("Upholstery & Chemical Resistance", "Hospital-grade antimicrobial vinyl resistant to hospital disinfectants and blood", "Medical grade fire-retardant vinyl, resistant to aggressive disinfectant wipes", "Maintains clean oncology hygiene")]),

  # 51. CHUB Video Bronchoscopes
  ("tender-chub-video-bronchoscope", "000018/G/NCB/2026/2027/CHUB-PULM", "Supply, Delivery, and Installation of Video Bronchoscopy System with Diagnostic Video Processor for Pulmonology", "University Teaching Hospital of Butare (CHUB)", "Surgical", 72000000, 1440000, "2026-10-05T10:00:00+02:00", "2026-08-26T23:00:00+02:00", 96, 97, "DIAG", "Olympus EVIS EXERA III / Pentax Medical", "Sonoscape & Biobase High-Definition Video Bronchoscopy Suite", 105000000, 64000000,
   ["High-Definition Video Bronchoscope with 2.8mm Instrument Channel", "Video Processor with Integrated LED Light Source & Medical Display"],
   [("Outer Diameter & Bending Range", "Outer diameter ≤5.8mm, distal bending Up 180° / Down 130°", "Slim 5.5mm insertion tube with 2.8mm channel, Up 210° / Down 130° angulation", "Smooth airway navigation"),
    ("Optical Magnification & Contrast", "Structure enhancement and hemoglobin color contrast technology", "Multi-spectral optical contrast enhancement with digital freeze and zoom", "High-definition diagnostic biopsy")]),

  # 52. RMH High-Field Orthopedic Power Tools
  ("tender-rmh-ortho-power-tools", "000019/G/NCB/2026/2027/RMH-ORTHO", "Supply and Delivery of Battery-Operated Surgical Orthopedic Power Tool Systems (Drills & Saws) with Dual Sterilization Cases", "Rwanda Military Hospital (RMH Kanombe)", "Surgical", 54000000, 1080000, "2026-09-30T10:00:00+02:00", "2026-08-27T23:00:00+02:00", 98, 99, "Consumables", "Stryker System 8 / DePuy Synthes Colibri II", "MedTech OrthoPower Surgical Drill & Sagittal Saw Suite with Dual Aseptic Batteries", 80000000, 48000000,
   ["Modular Surgical Cannulated Bone Drill Handpiece (0 - 1200 RPM)", "High-Speed Sagittal & Reciprocating Bone Saw with Autoclavable Blades"],
   [("Cannulation & Torque", "Cannulated bore diameter ≥4.0mm with high-torque reaming mode ≥5.0 N.m", "4.2mm cannulated drill with dual-speed trigger (0-1200 RPM) and 6.0 N.m reaming torque", "High surgical drilling precision"),
    ("Autoclavability & Battery Life", "Handpiece fully autoclavable at 134°C with aseptic battery housing transfer", "Full 134°C steam sterilizable handpiece with 2000 mAh high-density lithium cells", "Reliable trauma surgery performance")])
]

all_tenders = []

for item in dataset_specs + extra_tenders_raw:
    tid, ref, title, entity, category, val, sec_val, deadline, pub, rel_score, tech_score, icon, euro_brand, ch_model, euro_pr, ch_pr, lot_names, spec_items = item
    
    cost_adv = int(round((euro_pr - ch_pr) / euro_pr * 100)) if euro_pr > ch_pr else 35
    savings = euro_pr - ch_pr if euro_pr > ch_pr else int(val * 0.35)
    
    lots = []
    items = []
    lot_sec = int(round(sec_val / len(lot_names)))
    
    for idx, lname in enumerate(lot_names):
        lot_no = idx + 1
        lots.append({
            "lot_no": lot_no,
            "name": lname,
            "security_rwf": lot_sec,
            "place": entity,
            "delivery_days": 30 if "Consumables" in category else 45,
            "coverage_status": "COMPLIANT"
        })
        
        matrix = []
        for s in spec_items:
            matrix.append({
                "param": s[0],
                "req": s[1],
                "sup": s[2],
                "status": "COMPLIANT",
                "notes": s[3] if len(s) > 3 else "Meets or exceeds clinical specification."
            })
            
        items.append({
            "lot_id": f"Lot {lot_no}",
            "title": lname,
            "target_brand": euro_brand,
            "our_product": ch_model,
            "compliance": "Compliant",
            "compliance_class": "compliant",
            "specs_count": len(matrix),
            "specs_matched": len(matrix),
            "score": tech_score,
            "lot_tender_security_rwf": lot_sec,
            "qty": 1 if val > 100000000 else (10 if "Consumables" not in category else 500),
            "notes": f"Full ISO 13485 & CE technical certificates verified for {entity}.",
            "specs_matrix": matrix
        })
        
    equiv_score = int(round(tech_score * 0.4 + (tech_score - 1) * 0.3 + 100 * 0.2 + 95 * 0.1))
    
    strat_label = f"Bid In-Stock Solution (+{cost_adv}% Cost Advantage)"
    strat_desc = f"Verified opportunity for {entity}. Turnkey delivery with RWF {savings:,} public savings under RPPA Article 42."
    
    rec_act = "BID_HIGH_FIT" if rel_score >= 85 else ("OPPORTUNITY_EXPANSION" if rel_score >= 75 else "REVIEW_VERIFY")
    rec_lbl = "Bid (High Win Rate)" if rel_score >= 85 else ("Expansion Match" if rel_score >= 75 else "Review Specifications")
    
    brand_matrix = [
        {
            "parameter": "Core Clinical & Technical Performance",
            "european_benchmark": f"{euro_brand}: European standard benchmark specification",
            "chinese_supplied": f"{ch_model}: 100% parameter parity with ISO 13485 certification",
            "status": "EXACT_MATCH",
            "justification": f"Complies with Rwanda Public Procurement Law No. 62/2018, Article 42 brand neutrality standards for {entity}.",
            "standards_compliance": "ISO 13485, CE Marked, Rwanda FDA Approved"
        }
    ]
    
    all_tenders.append({
        "id": tid,
        "ref": ref,
        "title": title,
        "procuring_entity": entity,
        "category": category,
        "tender_value": val,
        "tender_security_amount": sec_val,
        "currency": "RWF",
        "deadline_at": deadline,
        "published_at": pub,
        "relevance_score": rel_score,
        "tech_spec_match": tech_score,
        "product_match": int(round(tech_score * 0.96)),
        "coverage_rate": 100,
        "eligibility_match": 100,
        "manufacturer_match": 95,
        "risk": "Low",
        "security": f"RWF {sec_val:,} (Tender Security / Bank Guarantee)",
        "authorization": "Required (Authorized OEM / Distributor)",
        "stock_readiness": "IN_STOCK" if "Consumables" in category or rel_score >= 94 else "PROJECT_DELIVERY",
        "stock_label": "In Stock (Kigali Distribution Hub)" if "Consumables" in category or rel_score >= 94 else "Turnkey Hospital Installation (30-45 Days)",
        "status": "bid_preparation",
        "recommended_action": rec_act,
        "recommendation_label": rec_lbl,
        "icon": icon,
        "source_url": "https://www.umucyo.gov.rw",
        "benchmarked_european_brand": euro_brand,
        "chinese_stocked_model": ch_model,
        "european_market_price_rwf": euro_pr,
        "chinese_bid_price_rwf": ch_pr,
        "cost_advantage_pct": cost_adv,
        "cost_savings_rwf": savings,
        "equivalence_score": equiv_score,
        "tech_parity_score": tech_score,
        "clinical_parity_score": tech_score - 1,
        "regulatory_parity_score": 100,
        "warranty_parity_score": 95,
        "sourcing_strategy": "BID_CHINESE_EQUIVALENT",
        "sourcing_strategy_label": strat_label,
        "sourcing_strategy_desc": strat_desc,
        "expansion_potential": f"Expands market share across public hospital tenders for {entity}.",
        "lots": lots,
        "items": items,
        "brand_equivalence_matrix": brand_matrix
    })

print(f"Generated {len(all_tenders)} rich medical tenders.")

# Output to JSON
with open("c:/Users/kagin/OneDrive/Desktop/My Projects/tender-mis/scratch/all_market_tenders.json", "w", encoding="utf-8") as f:
    json.dump(all_tenders, f, indent=2)

print("Saved all_market_tenders.json successfully.")
