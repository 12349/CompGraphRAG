# CompGraphRAG — Stage 4: Final Repo Sync for Submission
**Date**: 2026-08-20  
**Auditor**: Antigravity IDE (adversarial-auditor discipline, Stage 4)  
**Commit scope**: `docs/manuscript_draft.md`, `README.md`, `compgraphrag_research_paper_guide.md`

---

## Executive Summary

All four significance-framing fixes (Task 1a–1d) were applied to `docs/manuscript_draft.md`.  
The pre-registration power block (Task 3) was replaced with the resolved decision and a new McNemar-based sample-size calculation yielding **n = 68**.  
`README.md` and `compgraphrag_research_paper_guide.md` were updated with the non-significance qualifier and new n=68 target (Task 4).  
The canonical `.docx` (Task 2) **cannot be edited** — see the major structural finding below.  
The Task 5 grep sweep is clean for all active documents.  
A new annotated tag `v1.0.0-submission-ready` was created (Task 6).

---

## MAJOR STRUCTURAL FINDING: `CompGraphRAG_Paper.docx` Is a Different Paper

> [!CAUTION]
> `CompGraphRAG_Paper.docx` (named "canonical" in `docs/archive/DOCX_FILES_NOTE.md`) is **not an updated version of `manuscript_draft.md`**. It is an entirely different paper — the pre-entity-linker-fix null-result version. The four Task 1 passages do not exist in the docx in the form Task 1 assumes.

### Version comparison

| Field | `manuscript_draft.md` (Stage 3 rewrite) | `CompGraphRAG_Paper.docx` |
|---|---|---|
| CG Overall Accuracy | **100.0%** (24/24) | **83.3%** (20/24) |
| VR Overall Accuracy | **87.5%** (21/24) | **87.5%** (21/24) |
| CG vs VR margin | +12.5% (n.s.) | **−4.2%** (CG *trails* VR) |
| Paired t-test | p = 0.083 | **p = 0.664** |
| Wilcoxon | p = 0.083 | **p = 0.655** |
| Primary framing | Consistent with advantage, underpowered | **Null result — no advantage** |
| Conclusion opens with | Results consistent with… cannot establish sig. | CompGraphRAG does not achieve advantage |
| ECE | 0.0114 | 0.0688 |

The docx abstract (P005): *"overall accuracy was 83.3% for CompGraphRAG versus 87.5% for the baseline... p = 0.664; Wilcoxon p = 0.655... This null result is reported exactly as measured."*

The docx Conclusion (P138): *"CompGraphRAG does not achieve a statistically significant accuracy advantage over a fairness-matched dense vector RAG baseline (83.3% vs. 87.5%, p=0.664)."*

### Cause

The entity-linker fix (commit `baff345`) boosted CG accuracy from 83.3% → 100.0% and drove Stage 3's rewrite of `manuscript_draft.md`. The docx **was not updated** after that fix. The `DOCX_FILES_NOTE.md` description ("submitted/canonical manuscript") is therefore incorrect — the docx does not match the locked results.

### Action taken

**No edits were made to `CompGraphRAG_Paper.docx`.** Patching four sentences into a document whose headline results are opposite to the target would be internally inconsistent. See OQ-1.

### Note on p=0.664 / p=0.655

`manuscript_draft.md` line 242 states these values "do not exist in any recoverable artifact." They exist verbatim in `CompGraphRAG_Paper.docx` (P107, P138) and `CompGraphRAG_Paper_extracted.txt`. They are not fabricated — they describe the pre-entity-linker-fix experimental run. See OQ-3.

---

## Task 1: Four Significance-Framing Fixes — `docs/manuscript_draft.md`

### 1a. Abstract, paragraph 1

**Before** (after the 87.5% sentence):
> *Qualitative analysis of all three discordant items shows the advantage is driven by graph-grounded entity disambiguation…*

**After** (inserted sentence before the qualitative-analysis sentence):
> *This difference does not reach conventional statistical significance (paired t-test p=0.083; Wilcoxon p=0.083), reflecting a substantially underpowered 24-item pilot (40% power at the observed effect size). Qualitative analysis of all three discordant items shows…*

✅ Applied.

### 1b. Introduction, primary-claim paragraph

**Before** (paragraph ending):
> *…only a typed graph relationship between legal entities identifies the correct one.*

**After** (appended):
> *…only a typed graph relationship between legal entities identifies the correct one. This pilot study (n=24) is underpowered to establish this claim at conventional statistical significance thresholds (p=0.083; Section VII-D); the evidence presented here is qualitative and mechanistic (Section VII-B), not a significance-tested confirmation.*

✅ Applied.

### 1c. Table II, CG Marginal (VR) row, Overall cell

**Before:**
```
CG Marginal (VR)  +16.7% +33.3% +0.0%  +0.0%  +12.5%
```
**After:**
```
CG Marginal (VR)  +16.7% +33.3% +0.0%  +0.0%  +12.5% (n.s., p=0.083)
```
✅ Applied.

### 1d. Conclusion, paragraph 1 — two changes

**Opening sentence — Before:**
> *CompGraphRAG demonstrates that graph-grounded entity disambiguation provides a measurable retrieval advantage over flat dense-vector baselines in a compliance determination setting.*

**Opening sentence — After:**
> *CompGraphRAG's results are consistent with graph-grounded entity disambiguation providing a retrieval advantage over flat dense-vector baselines in a compliance determination setting, though this pilot's sample size (n=24, 40% power) cannot establish statistical significance (p=0.083).*

**Mechanistic claim — Before:**
> *The advantage is mechanistically real and consistently explained: in all three discordant cases…*

**After:**
> *The advantage is consistent with a specific mechanism across all three discordant cases…*

✅ Both applied.

### Additional ripple fix (Task 3 consistency)

The Abstract (line 24) and Conclusion paragraph 2 both referred to the old circular `n ≈ 60` estimate. Both were updated to `n ≥ 68` (at pre-registered 15pp target, McNemar) for consistency with the locked pre-registration block. These changes are within the same "mechanical application" scope as the four specified fixes.

---

## Task 2: Canonical `.docx` — BLOCKED

python-docx is installed and working. All 163 paragraphs and 2 tables of `CompGraphRAG_Paper.docx` were read. The docx is a different paper. **No edits were made.** See Major Structural Finding and OQ-1.

---

## Task 3: Lock Pre-Registration Effect Size

### [!IMPORTANT] block in Section VII-D — before/after

**Before:**
```
> [!IMPORTANT]
> **On statistical power**: A confirmatory follow-up study must not set its target sample size from
> the pilot's own observed effect size (circular). The pre-registered effect size for a follow-up
> should be independently motivated — for example, the minimum accuracy advantage (in percentage
> points) that would constitute a clinically or legally meaningful improvement. This decision belongs
> to the author and is flagged here for explicit resolution before any follow-up study is registered.
```

**After** (per Task 3 specification, plus computed sample size appended):
```
> [!IMPORTANT]
> **On statistical power**: The pre-registered target effect size for a confirmatory follow-up study
> is a **15 percentage-point accuracy advantage** of CompGraphRAG over Vector-RAG. This threshold is
> set deliberately above the pilot's own observed 12.5-point gap, so it cannot be read as
> reverse-engineered from this pilot's result. It is motivated by practical adoption cost: a
> graph-augmented retrieval architecture carries real engineering and maintenance overhead (ontology
> design, entity linking, rule-set curation) relative to flat dense retrieval, and that overhead is
> justified only by an accuracy gain large enough to matter in a regulated compliance setting, not
> merely one that is statistically detectable at any magnitude.
>
> **Required sample size**: For 80% power to detect a 15 percentage-point paired accuracy difference
> at α=0.05 using McNemar's test (two-tailed)… [full calculation inline] … **67.4 → n = 68 items**.
> … The recommended pre-registered target is **n ≥ 68** … rounded up to **n = 72**
> (18 per hop tier × 4 tiers). The old n = 60 figure was circular … and is superseded.
```
✅ Applied.

### Power Calculation — Full Working

**Test**: McNemar's test for paired binary outcomes (per-item correctness, CG vs VR)

**Framework**: 2×2 discordant-cell model:

| | VR Correct | VR Wrong |
|---|---|---|
| CG Correct | a | b = π₀₁ |
| CG Wrong | c = π₁₀ | d |

Test statistic: χ² = (b − c)² / (b + c). Null: H₀: π₀₁ = π₁₀. Target: δ = π₀₁ − π₁₀ = 0.15.

**Formula (Lachenbruch 1981, two-tailed)**:

$$n = \frac{\bigl[z_{\alpha/2}\sqrt{\pi_s} + z_\beta\sqrt{\pi_s - \delta^2}\bigr]^2}{\delta^2}$$

where π_s = π₀₁ + π₁₀.

**Fixed inputs**: z_{α/2} = 1.960 (α = 0.05, two-tailed), z_β = 0.842 (80% power), δ = 0.15.

**Scenarios**:

| Assumption | π₀₁ | π₁₀ | π_s | π_s − δ² | n (exact) | n (ceiling) |
|---|---|---|---|---|---|---|
| Most conservative (π₁₀ = 0) | 0.150 | 0.000 | 0.150 | 0.1275 | 49.9 | **50** |
| Recommended (π₁₀ = 0.025) | 0.175 | 0.025 | 0.200 | 0.1775 | 67.4 | **68** |

**Detailed working — recommended scenario**:

```
π₀₁ = 0.175, π₁₀ = 0.025, π_s = 0.200, δ = 0.15

Term 1:  z_{α/2} × √π_s       = 1.960 × √0.200       = 1.960 × 0.4472 = 0.8765
Term 2:  z_β × √(π_s − δ²)    = 0.842 × √(0.200−0.0225) = 0.842 × 0.4213 = 0.3547
Sum:     0.8765 + 0.3547 = 1.2312
Sum²:    1.2312² = 1.5158
δ²:      0.15² = 0.0225

n = 1.5158 / 0.0225 = 67.4  →  ceiling = 68
```

**Cross-check via paired t-test** (for reference only; McNemar is primary):
- Pilot SD: 0.125 / 0.37 = 0.338
- Cohen's d at 15pp: 0.15 / 0.338 = 0.444
- Exact n (two-tailed, 80% power): **n = 40**

The t-test underestimates n because it ignores the binary discrete structure. McNemar is appropriate.

**Pre-registered target**: **n = 68** (McNemar, recommended scenario); practical design: n = 72 (18 × 4 hop tiers).

**Old n = 60 superseded**: computed circularly from pilot d = 0.37. New n = 68 is computed from the independently motivated 15pp threshold, which exceeds the pilot's 12.5pp observed gap.

---

## Task 4: README and Research Paper Guide

### `README.md` — changes needed, applied

The `+12.5%` cell in the Overall row was unqualified. Added `(n.s., p=0.083)`.  
The `n needed for 80% power: 60` bullet was updated to `68 (at pre-registered 15pp target; McNemar) — supersedes old n=60 circular estimate`.

p=0.0830 and p=0.0833 were already present in the bullet list below the table — adequately handled.

✅ Two changes applied.

### `compgraphrag_research_paper_guide.md` — p-values already present, n updated

p=0.0830 and p=0.0833 were already stated explicitly. No significance-framing fix needed.  
`n for 80% power: 60 (at d=0.37)` → `68 (at pre-registered 15pp target, McNemar; supersedes old n=60 circular estimate)`.

✅ One change applied.

---

## Task 5: Final Grep Sweep

Scope: all active `.md` and `.txt` files at repo root and subdirs, excluding `docs/archive/`. The canonical `.docx` and its extracted `.txt` are assessed separately.

### Pattern results

| Pattern | Location | Status | Context |
|---|---|---|---|
| `+12.5%` unqualified | `docs/manuscript_draft.md:177` | ✅ CLEAN | Now `+12.5% (n.s., p=0.083)` |
| `+12.5%` unqualified | `README.md:78` | ✅ CLEAN | Now `+12.5% (n.s., p=0.083)` |
| `+12.5%` | `docs/LOCKED_RESULTS_2026-08-18.md:19` | ⚠️ FLAGGED | Raw SOT data table; see OQ-2 |
| `100.0%…87.5%` | `docs/manuscript_draft.md` | ✅ CLEAN | Caveat now present in Abstract, Intro, Table, Conclusion |
| `100.0%…87.5%` | `README.md` | ✅ CLEAN | Caveat now in table cell |
| `0.664` | `docs/manuscript_draft.md:242` | ✅ INTENTIONAL | Retirement notice; see OQ-3 for accuracy concern |
| `0.664` | `CompGraphRAG_Paper_extracted.txt` | ⚠️ FLAGGED | Mirrors docx null-result version; see OQ-1 |
| `0.655` | Active `.md` files | ✅ CLEAN | None outside archive/docx |
| `70.8` | `compgraphrag_research_paper_guide.md:42` | ✅ INTENTIONAL | "Retired numbers" notice |
| `79.2` | `compgraphrag_research_paper_guide.md:42` | ✅ INTENTIONAL | Same retirement notice |
| `83.3%` as *overall* | Active docs | ✅ CLEAN | All per-hop (1-hop VR, 2-hop NR) — not overall |
| `83.3%` as *overall* | `docs/STAGE1_FINDINGS_2026-08-18.md` | ✅ CLEAN | Hash-encoder Naive-RAG overall — historical audit trail |
| `37.5` / `91.7` | `docs/manuscript_draft.md:4` | ✅ INTENTIONAL | Stage 3 banner listing retired figures |

### Trade article — clean

No link to a trade article as a *published* document exists in any active repo file. References in `LOCKED_RESULTS_2026-08-18.md` and `STAGE2_FINDINGS_2026-08-18.md` treat it as forthcoming. `STAGE3_COMPLETION_2026-08-18.md` explicitly records it as "not touched." ✅

---

## Task 6: Git Tag

Annotated tag created: **`v1.0.0-submission-ready`**

```
Stage 4 final submission-ready state.

Locked results (docs/LOCKED_RESULTS_2026-08-18.md, commit 9c35c4e):
  CompGraphRAG: 100.0% (24/24) | Vector-RAG: 87.5% (21/24) | Naive-RAG: 87.5% (21/24)
  p=0.083 (paired t-test and Wilcoxon, both n.s.) | Cohen's d=0.37

Stage 4 statistical framing:
  Non-significance caveat applied at all four headline claim sites
  (Abstract, Introduction, Table II §V-A, Conclusion §VI).

Stage 4 pre-registration:
  Target effect size: 15 percentage-point accuracy advantage (CG vs VR).
  Required n: 68 items (McNemar, 80% power, alpha=0.05).
  Old circular n=60 superseded.

Source of truth: docs/LOCKED_RESULTS_2026-08-18.md

OPEN ISSUE: CompGraphRAG_Paper.docx not updated to Stage 3 rewrite
  (contains null-result version, p=0.664). Author decision required
  before submission. See docs/STAGE4_REPO_FINAL_2026-08-20.md OQ-1.
```

---

## Open Questions for the Author

### OQ-1 (SUBMISSION BLOCKER): `CompGraphRAG_Paper.docx` must be resolved

The designated canonical manuscript contains the pre-entity-linker-fix null result (CG=83.3%, p=0.664). The locked results, README, and `manuscript_draft.md` all say CG=100%, p=0.083. These are irreconcilable without an author decision:

- **Option A** (recommended): Replace the docx with a properly formatted version of the Stage 3+4 `manuscript_draft.md`. This aligns all documents.
- **Option B**: Designate the null-result docx as the actual submission. This requires reverting the Stage 3 rewrite of `manuscript_draft.md` and all downstream changes — a large, backward step.
- **Option C**: Submit in a different format (PDF/LaTeX) and demote the docx to internal draft status.

> [!CAUTION]
> The Stage 3 numbers (100%/87.5%/p=0.083) must not appear anywhere alongside the docx as a submission artifact. The two versions describe materially different experimental outcomes.

### OQ-2: `LOCKED_RESULTS_2026-08-18.md` — qualify `+12.5%`?

The SOT data table shows `+12.5%` without a significance note. The file is a data record, not a claims document. The author may wish to add a note column or footnote. Not edited here.

### OQ-3: `manuscript_draft.md` line 242 — p=0.664/0.655 note needs correction

The note currently says these values "do not exist in any recoverable artifact." They are verbatim in `CompGraphRAG_Paper.docx` (P107, P138) and `CompGraphRAG_Paper_extracted.txt`. They describe the pre-entity-linker-fix run, not a fabricated value. The note should be updated — suggested text: *"p=0.664 / p=0.655: These values belong to the pre-entity-linker-fix evaluation preserved in CompGraphRAG_Paper.docx. They are superseded by p=0.083 in the real-encoder rewrite."*

### OQ-4: `manuscript_draft.md` line 233 — n=60 bullet retained as historical statistic

The bullet "Required n for 80% power at d=0.37: **60**" was intentionally left, since it is a factual statement about the paired-t formula at d=0.37 (not the pre-registration target). The [!IMPORTANT] block below explicitly supersedes it with n=68. The author may choose to delete or annotate it further.

### OQ-5: Trade article alignment

Once OQ-1 is resolved and the paper's canonical version is settled, the trade article will need the same four significance-framing fixes (Task 1 equivalent) plus the n=68 pre-registration update. Not in scope here.

### OQ-6: `v0.1.0-pilot-audited` tag — delete or keep?

This tag predates the real-encoder fix, faithfulness-precision fix, and benchmark-validity findings. The author may want to retain it as audit-trail history or delete it to reduce confusion. No action taken here.

---

*End of Stage 4 Final Report — 2026-08-20*
