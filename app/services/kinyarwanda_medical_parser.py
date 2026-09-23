"""
Kinyarwanda & Multi-Lingual Medical Procurement Linguistic Engine for Rwanda.
Accurately classifies Rwandan procurement notices in Kinyarwanda, French, and English.
Strictly distinguishes healthcare & hospital equipment from general civil works,
school food supplies, firewood, and non-medical commodities.
"""

import re
from typing import Dict, Any, List, Optional

# Kinyarwanda Healthcare Buyer Entities
KINYARWANDA_HEALTH_BUYERS = [
    "ikigo nderabuzima",      # Health Center
    "ibitaro",                 # Hospital
    "poste de sante",          # Health Post
    "ivuriro",                 # Dispensary / Clinic
    "urugaga rw'abavuzi",      # Medical Council / Association
    "minisiteri y'ubuzima",    # Ministry of Health
    "rwanda biomedical centre",# RBC
    "rbc",
    "rwanda medical supply",   # RMS
    "rms",
    "ubuvuzi",                 # Healthcare
    "inshuti mu buzima",       # Partners In Health Rwanda
    "partners in health",      # PIH
    "pih",
    "health builders",         # Health Builders Rwanda
    "unhcr",                   # UN Refugee Agency Health Operations
    "rsog",                    # Rwanda Society of Obstetricians and Gynecologists
    "rwanda society of obstetricians",
    "society for family health", # SFH Rwanda
    "sfh",
]

# Kinyarwanda Medical Equipment, Consumables & Clinical Supplies
KINYARWANDA_MEDICAL_TERMS = [
    "ibikoresho byo kwa muganga",      # Medical equipment & devices
    "ibikoresho by'ubuvuzi",          # Healthcare supplies
    "ibikoresho bishira by'ubuvuzi",  # Medical consumables
    "ibikoresho bishira",             # Consumables / disposables (in healthcare context)
    "imiti",                          # Pharmaceuticals / Medicines
    "kugemura imiti",                 # Supply of medicines
    "kugemura ibikoresho byo kwa muganga", # Supply of medical equipment
    "ibiryamirwa by'abarwayi",        # Patient hospital bedding / sheets
    "ibiryamirwa by'ibitaro",         # Hospital bedding
    "aleze",                          # Waterproof medical drawsheets / mattress covers
    "ibitanda by'ibitaro",            # Hospital clinical beds
    "ibitanda by'abarwayi",           # Patient ward beds
    "ibitanda byo kubyariraho",       # Obstetric delivery beds
    "ibipimo",                        # Medical tests / diagnostic parameters
    "gupima",                         # Diagnostics / testing
    "laboratwari",                    # Laboratory
    "reagents",                       # Lab reagents
    "ubuhumekero",                    # Respiratory care / ventilators
    "umwuka wa ogisijeni",            # Medical oxygen gas
    "ibyuma bya ogisijeni",           # Oxygen concentrators / plants
    "ubuvuzi bw'amenyo",              # Dental medicine & equipment
    "ubuvuzi bw'amaso",               # Ophthalmology / eye care
    "isuku n'isukura mu bitaro",      # Hospital infection control & hygiene
    "isuku yo kwa muganga",           # Clinical sanitation
    "inshinge",                       # Syringes / needles
    "uturindantoki",                  # Examination / surgical gloves
    "udupfukamunwa",                  # Medical masks
    "isanduku y'ubutabazi",           # First aid kit
    "ibipimo by'umuvuduko",           # Blood pressure monitors
    "gupima isukari",                 # Blood glucose testing
    "imashini zo mu bitaro",          # Hospital machines
    "imashini yo kwa muganga",        # Clinical medical device
]

# French Medical Procurement Keywords
FRENCH_MEDICAL_TERMS = [
    "médical", "médicaux", "médicament", "matériel médical", "consommables médicaux",
    "hospitalier", "hygiène hospitalière", "imprimés médicaux", "santé", "centre de santé",
    "hôpital", "laboratoire", "réactifs", "radiologie", "chirurgie", "anesthésie",
    "maternité", "stérilisation", "bloc opératoire", "hémodialyse", "blouse médicale",
    "dispositif médical", "pansements", "compresses stériles"
]

# English Medical Procurement Keywords
ENGLISH_MEDICAL_TERMS = [
    "medical equipment", "medical device", "biomedical", "patient monitor", "monitoring and critical",
    "vital signs", "ventilator", "radiology", "imaging", "pacs", "x-ray", "c-arm", "ct scanner",
    "ultrasound", "laboratory equipment", "clinical chemistry", "hematology", "analyzer", "reagents",
    "hospital equipment", "operating theatre", "surgical", "anesthesia", "infant warmer", "incubator",
    "phototherapy", "neonatal", "dialysis", "hemodialysis", "medical gas", "medical air compressor",
    "oxygen plant", "oxygen cylinder", "ophthalmology", "tonometer", "dental chair", "dental unit",
    "autoclave", "sterilizer", "defibrillator", "ecg", "suction machine", "tissue banking", "cornea",
    "metrology laborator", "hospital mattress", "medical consumables", "drawsheet"
]

# Non-Medical Keywords in Kinyarwanda (Must be strictly excluded)
KINYARWANDA_EXCLUSIONS = [
    "inkwi",                          # Firewood
    "umucanga",                       # Sand / building aggregates
    "amabuye",                        # Stones / quarry rocks
    "amashuri",                       # Schools (unless hospital teaching academy)
    "amashuri abanza",                # Primary schools
    "amashuri yisumbuye",             # Secondary schools
    "intebe z'abanyeshuri",           # School desks
    "ameza y'abarimu",                # Teacher tables
    "ibiribwa by'abanyeshuri",        # School student food supplies
    "ingemwe z'ibiti",                # Tree seedlings / forestry
    "ishwagara",                      # Agricultural lime
    "urubingo",                       # Elephant grass
    "amaterasi",                      # Terracing
    "ubwubatsi bw'ibyumba",           # Classroom construction
    "gusudira",                       # Welding
    "ubudozi",                        # Tailoring
    "siporo",                         # Sports
    "imyidagaduro",                   # Entertainment / recreation
    "amapikipiki",                     # Motorcycles (unless ambulance)
    "sonorisation",                   # Sound system / PA
    "decoration",                     # Event decoration
    "kurimbisha",                     # Beautification
]

# General Non-Medical Exclusions
GENERAL_EXCLUSIONS = [
    "security equipment", "security services", "genocide memorial", "vup program", "public works",
    "sports equipment", "football", "refreshment", "catering", "stationery", "stationaries",
    "printing and promotion", "solar home", "radio salus", "media production", "cctv", "fire extinguisher",
    "road", "bridge", "office furniture", "cupboard", "locker safe", "drainage"
]

# Excluded Buyer Entities (Government ministries/offices unrelated to healthcare)
EXCLUDED_BUYERS = [
    "senate", "parliament", "kigali city", "revenue authority", "rra", "edcl", "reg",
    "wasac", "police", "military", "rdf", "rwanda polytechnic", "court", "ombudsman",
    "minecofin", "mininfra", "rtda", "rura", "minaloc", "rab", "naeb"
]


def evaluate_medical_relevance(title: str, buyer: str = "", description: str = "") -> Dict[str, Any]:
    """
    Evaluates whether a tender notice in Kinyarwanda, French, or English is a valid medical opportunity.
    Returns relevance status, score (0-100), detected language, matched terms, and category.
    """
    combined_text = f"{title} {buyer} {description}".lower()
    title_lower = title.lower()
    buyer_lower = buyer.lower()

    matched_medical_kw = []
    matched_exclusions = []

    # 1. Check for exclusions
    for ex in KINYARWANDA_EXCLUSIONS + GENERAL_EXCLUSIONS:
        if re.search(r'\b' + re.escape(ex) + r'\b', title_lower):
            matched_exclusions.append(ex)

    # If title has clear non-medical indicators (e.g. firewood, school desks, construction sand)
    if matched_exclusions and not any(k in title_lower for k in ["medical", "kwa muganga", "ubuvuzi"]):
        return {
            "is_medical": False,
            "relevance_score": 0,
            "category": "Non-Medical",
            "matched_terms": [],
            "exclusions": matched_exclusions,
            "confidence": 0.99
        }

    # Exclude non-medical buyers unless title is explicitly medical equipment
    if buyer_lower and any(ex_b in buyer_lower for ex_b in EXCLUDED_BUYERS):
        if not any(k in title_lower for k in ["medical equipment", "biomedical", "hospital equipment", "kwa muganga"]):
            return {
                "is_medical": False,
                "relevance_score": 0,
                "category": "Non-Medical",
                "matched_terms": [],
                "exclusions": ["excluded_buyer"],
                "confidence": 0.95
            }

    # 2. Check for Kinyarwanda medical terms
    for term in KINYARWANDA_MEDICAL_TERMS:
        if term in combined_text:
            matched_medical_kw.append(f"rw:{term}")

    # 3. Check for French medical terms
    for term in FRENCH_MEDICAL_TERMS:
        if re.search(r'\b' + re.escape(term) + r'\b', combined_text):
            matched_medical_kw.append(f"fr:{term}")

    # 4. Check for English medical terms
    for term in ENGLISH_MEDICAL_TERMS:
        if re.search(r'\b' + re.escape(term) + r'\b', combined_text):
            matched_medical_kw.append(f"en:{term}")

    # 5. Check if buyer is a recognized Rwandan health center or hospital
    is_health_buyer = any(hb in buyer_lower or hb in combined_text for hb in KINYARWANDA_HEALTH_BUYERS + ["hospital", "hopital", "clinic", "chub", "chuk", "kfh", "rmh"])

    is_medical = False
    score = 0
    category = "General Healthcare Supplies"

    if len(matched_medical_kw) >= 2 or (is_health_buyer and len(matched_medical_kw) >= 1):
        is_medical = True
        score = min(98, 80 + len(matched_medical_kw) * 4)
    elif is_health_buyer and any(w in title_lower for w in ["equipment", "materiel", "ibikoresho", "fourniture", "supply", "plan"]):
        is_medical = True
        score = 82
    elif len(matched_medical_kw) == 1:
        is_medical = True
        score = 80

    # Categorize
    if any(k in combined_text for k in ["imaging", "x-ray", "radiology", "ct", "ultrasound"]):
        category = "Imaging & Radiology"
    elif any(k in combined_text for k in ["icu", "neonatal", "warmer", "incubator", "ventilator", "ubuhumekero", "patient monitor"]):
        category = "Neonatal & ICU"
    elif any(k in combined_text for k in ["laboratory", "laboratwari", "reagent", "analyzer", "gupima", "hematology"]):
        category = "Laboratory"
    elif any(k in combined_text for k in ["surgical", "theatre", "operating", "suction machine"]):
        category = "Surgical"
    elif any(k in combined_text for k in ["oxygen", "ogisijeni", "air compressor"]):
        category = "Medical Gas & Infrastructure"
    elif any(k in combined_text for k in ["dental", "amenyo"]):
        category = "Dental"
    elif any(k in combined_text for k in ["ophthalmology", "amaso", "cornea"]):
        category = "Ophthalmology"
    elif any(k in combined_text for k in ["aleze", "ibiryamirwa", "drawsheet", "bedding", "mattress"]):
        category = "Hospital Furniture & Ward Supplies"
    elif any(k in combined_text for k in ["imiti", "consumables", "inshinge", "uturindantoki", "imprimés médicaux", "disposables"]):
        category = "Medical Consumables & Supplies"

    return {
        "is_medical": is_medical,
        "relevance_score": score if is_medical else 0,
        "category": category if is_medical else "Non-Medical",
        "matched_terms": matched_medical_kw,
        "is_health_buyer": is_health_buyer,
        "confidence": 0.94 if is_medical else 0.85
    }
