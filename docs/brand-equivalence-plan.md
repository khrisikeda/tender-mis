# Chinese Stock vs European Tender Requirement — Brand Equivalence & Spec Comparison Plan

> **Context**: Our company sources most medical equipment from Chinese OEM manufacturers (Mindray, Comen, MedTech, Yuwell, SonoScape, Neusoft) due to significant cost advantages (40–55% lower acquisition cost vs European brands). However, Rwanda's procurement market — particularly Ministry of Health, RBC, CHUK, and KFH tenders — often benchmarks or references European brands (Philips, Dräger, GE Healthcare, Siemens Healthineers, Tuttnauer, Karl Storz, Roche, DiaSys) as the technical benchmark.

This plan introduces a dedicated **Brand Equivalence & Specification Deviation Comparison Engine** into MedTender, enabling our team to:
1. Instantly know how well our stocked Chinese equipment matches the European benchmark referenced in a tender.
2. Identify every specification that is an exact match, a clinical equivalent, or a genuine technical miss/gap.
3. Generate compliant RPPA equivalence justification defense statements to submit alongside our bid.

---

## IMPORTANT Notes

- **RPPA Legal Basis for Equivalence Defense**: Rwanda Public Procurement Law No. 62/2018, Article 42 expressly prohibits restricting competition to specific brand names without including an *"or equivalent"* clause. Our equivalence defense letters will cite this article.
- This feature is currently implemented as a polished **frontend with realistic mock data**. The architecture is ready to connect to the actual tender database, product database, and AI matching engine later.

---

## Features

### 1. Brand Equivalence Match Score (%)

For each tender that references or benchmarks a European model, the engine will compute:

| Score Dimension | Weighting |
|:---|:---|
| Technical Specification Parity | 40% |
| Clinical Performance Equivalence | 30% |
| Regulatory & Standards Compliance | 20% |
| OEM Authorization / Warranty Parity | 10% |

### 2. Granular Spec Miss / Deviation Analysis

Every technical parameter is classified:

| Indicator | Meaning |
|:---|:---|
| ✅ Exact Match / Exceeds | Chinese model meets or exceeds the European benchmark parameter |
| 🟡 Equivalent Alternative | Meets clinical intent via alternative engineering (e.g. Mindray SpO2 algorithm vs Philips FAST-SpO2) |
| ❌ Technical Miss / Gap | Chinese model falls materially short of the tender parameter |
| ⚠️ Regulatory Difference | Different certification body (NMPA vs CE 0197 / FDA) — requires registration validation |

### 3. Sourcing Strategy Recommendations

| Strategy | Trigger |
|:---|:---|
| `BID_CHINESE_EQUIVALENT` | ≥ 88% equivalence — bid with high confidence using Chinese stock |
| `BID_WITH_EQUIVALENCE_DEFENSE` | 70–87% equivalence — minor spec misses; attach RPPA justification letter |
| `SOURCE_EUROPEAN_PARTNER` | < 70% equivalence — critical gap; source European distributor partner |
| `FLAG_RESTRICTIVE_RFP` | Tender locks brand without "or equivalent" — request clarification under RPPA law |

### 4. Auto-Generated RPPA Technical Equivalence Defense Letter

For each tender, one click generates a structured equivalence defense statement citing:
- RPPA Law No. 62/2018, Article 42
- Detailed parameter-by-parameter technical equivalence comparison table
- Clinical evidence references (IEC 60601-1, ISO 13485 parity)
- Cost advantage quantification for public procurement interest

---

## Files to Modify

| File | Change Summary |
|:---|:---|
| `frontend/app.js` | Add `origin`, `european_benchmark`, `cost_advantage_pct`, and `equivalence_comparison` data to catalogue & tenders. Add `computeEquivalenceScore()`, `generateEquivalenceLetter()` engine. Add sourcing strategy filter to pipeline. |
| `frontend/index.html` | Add sourcing origin badges to pipeline table. Expand drawer with Chinese vs European comparison tab. Add equivalence letter generate/copy/download buttons. |
| `frontend/styles.css` | Add styles for origin flags, spec miss alerts, cost advantage pills, side-by-side benchmark cards, equivalence defense quote boxes. |

---

## Verification Plan

### Automated Tests
```bash
python scratch/validate_equivalence.py
```
Checks:
- Equivalence score computation for all 4 sourcing strategies.
- All 4 spec status types (✅ 🟡 ❌ ⚠️) are correctly classified.
- Equivalence defense letter text generation references RPPA Article 42.
- Origin badges rendered for all catalogue items.

### Manual Verification
1. Open `frontend/index.html` → Tender Pipeline → Open any tender spec matrix.
2. Switch to **"🇨🇳 vs 🇪🇺 Brand Comparison"** tab.
3. Verify: side-by-side parameter comparison, Spec Miss callouts, Cost Advantage pill, and RPPA equivalence letter generation.
