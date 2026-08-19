# CompGraphRAG — Stage 3 Completion Report

**Date**: 2026-08-18  
**Commits in this stage**: `9c35c4e` (faithfulness fix), `977bc1f` (docs lock)  
**Auditor role**: Same adversarial-auditor role as Stages 1 and 2.

---

## Task 1: Faithfulness IE Fix — Completed

### What was wrong

`eval_harness.py` lines ~175–187: the IE step built `extracted_triples` by iterating over `included_edges` — the exact same edge objects used to generate the narrative — and confirming entity names appear in the narrative string. Since the narrative was generated *from* those edges, entity names always appeared. **Precision = 1.0 was structurally guaranteed by code, not measured.**

### Fix implemented (commit `9c35c4e`)

The IE step now runs three regex patterns over the narrative text **only**, with no access to `included_edges` or `retrieved_path` during extraction:

- **Pattern A**: `Step N: Entity S is linked via R to T.`
- **Pattern B**: `Step N: Subgraph edge shows S R T.`  
- **Pattern C**: `Step N: Verification reveals S --({R})--> T.`

If the generator misstates or omits an entity name, the extractor will parse the wrong token, the extracted triple will fail to match `retrieved_path`, and Precision will correctly fall below 1.0.

### Unit tests (4 passing, 0 failing)

| Test | Assertion | Result |
|------|-----------|--------|
| `test_precision_fails_on_corrupted_entity_name` | Corrupted entity → Precision = 0.0 | **PASS** |
| `test_precision_is_one_on_correct_narrative` | Correct narrative → Precision = 1.0 | **PASS** |
| `test_recall_drops_on_abstracted_middle_step` | Abstracted step → Recall < 1.0 | **PASS** |
| `test_harness_post_fix_invariants` | CG=100%, VR=87.5%, F1≤0.9679, ≥1 item Recall<1.0 | **PASS** |

### Post-fix harness output (3 deterministic runs, identical)

```
CG: 100.0%  VR: 87.5%  NR: 87.5%   ← accuracy UNCHANGED
Mean F1: 0.9679                      ← UNCHANGED (Recall was already the limiter)
Mean Precision: 1.0000               ← All current templates are regex-parseable
ECE: 0.0114                          ← UNCHANGED
Paired t-test p: 0.0830              ← UNCHANGED
Wilcoxon p: 0.0833                   ← UNCHANGED
```

### Why F1 is unchanged — and why that's the honest outcome

All three connector templates (`Entity S is linked via R to T.`, `Subgraph edge shows S R T.`, `Verification reveals S --({R})--> T.`) produce text that is exactly matched by the corresponding regex pattern. So Precision = 1.0 for all 24 items in the current dataset. The pre-fix Recall distribution was already < 1.0 for 5 items (Q18, Q19, Q22, Q23, Q24 — stochastic intermediate-edge abstraction at 3-hop/4-hop). F1 = 0.9679 was already being driven by Recall, not Precision.

**The fix matters for defensibility, not the current number.** The structural ceiling is broken — it's now a fact about the generator's current template quality that Precision = 1.0, not a guarantee enforced by the code. A reviewer can verify this by reading the regex and the templates side by side. A future generator that produces freer-form text would immediately produce Precision < 1.0 on the same evaluation code.

---

## Task 2: Locked Results Table

**File**: [`docs/LOCKED_RESULTS_2026-08-18.md`](LOCKED_RESULTS_2026-08-18.md)

This file is the **single source of truth**. Every number in every other document must match it. Contents:
- Table 1: Three-way per-hop accuracy (CG/VR/NR, all 4 tiers)
- Table 2: Per-item faithfulness distribution (all 24 items, P/R/F1)
- Table 3: Statistical validation (t-test, Wilcoxon, Cohen's d, power, ECE)
- Table 4: All 3 discordant items with mechanism
- Table 5: Benchmark validity notes (cosine gaps, distractor count, tier-level analysis)
- Faithfulness fix note
- Change log since last lock

---

## Task 3: Paper Rewrite Summary

**File**: [`docs/manuscript_draft.md`](manuscript_draft.md) (committed `977bc1f`)

### Abstract — before/after

**Before (hash-encoder, stale)**:
> CompGraphRAG achieves 70.8% overall accuracy vs. 79.2% for Vector-RAG and 83.3% for Naive-RAG. [...] The monotonically-growing hop-scaling hypothesis (H4/H8) is **not supported** on this dataset. Mean explanation faithfulness F1 = 0.9798. ECE = 0.1469.
> [...also a second paragraph with fabricated 37.5%/91.7%, p<0.005...]

**After (real-encoder, honest)**:
> CompGraphRAG achieves **100.0% overall accuracy** (24/24) versus **87.5%** (21/24) for both Vector-RAG and Naive-RAG. Qualitative analysis of all three discordant items shows the advantage is driven by **graph-grounded entity disambiguation**: the entity linker surfaces a legally critical graph node that distinguishes two passages sharing surface vocabulary but encoding opposing compliance determinations — a distinction flat retrieval cannot make.
>
> The monotonically-growing hop-scaling hypothesis (H4/H8) [...] was originally an empirical claim of this paper. Upon inspection, the current benchmark cannot yet test it [...] The hypothesis remains open. A pre-registered follow-up study requires n ≈ 60 items at the observed pilot effect size (Cohen's d = 0.37); the current 24-item pilot has 40% power.
>
> Mean explanation faithfulness F1 = **0.9679** (post-fix; IE is now independently text-derived, not structurally guaranteed). ECE = **0.0114**.

### Section changes applied

| Section | Change |
|---------|--------|
| Banner | CAUTION → IMPORTANT; updated to reference LOCKED_RESULTS and commit 9c35c4e |
| Abstract | Both paragraphs replaced; hash-encoder and fabricated numbers gone; entity-disambiguation claim; H4/H8 retained as open hypothesis; power noted |
| Introduction (H4/H8 paragraph) | Reframed from primary claim to original hypothesis, now explicitly untestable pending better benchmark |
| Contributions list | Item 3: "independently computable faithfulness metric"; Item 5: added power analysis; Item 6 [NEW]: adversarial audit pipeline as methodological contribution |
| Section V-A (results table) | Hash-encoder table replaced with three-way locked table (CG/VR/NR, real encoder) |
| Section V-B [NEW] | Qualitative analysis — Q03, Q11, Q12 with exact graph paths and competing passages |
| Section V-C [NEW] | Benchmark Validity: cosine-gap analysis, distractor count, per-tier signal audit, requirements for H4/H8-testable benchmark |
| Section V-D (statistical) | Updated to locked numbers; Cohen's d, power (40%), n-needed (60), power-circularity warning; p=0.664/0.655 permanently retired |
| Conclusion | Rewritten: entity-disambiguation mechanism, H4/H8 open, audit-pipeline contribution |

---

## Task 4: Other Documents

| File | Status |
|------|--------|
| `README.md` | Updated: three-way per-hop table, locked numbers, entity-disambiguation plain-language note, H4/H8 limitation, retired numbers note |
| `compgraphrag_research_paper_guide.md` | Updated: benchmark table to locked real-encoder numbers, retired hash-encoder figures labelled |
| `docs/manuscript_draft.md` | Full rewrite per Task 3 (same commit `977bc1f`) |
| Trade article | **Not touched** — explicitly out of scope for Stage 3 |

---

## Task 5: Grep Sweep Results

Sweep run on all `.md` and `.txt` files, excluding `docs/archive/` and `.git`.

| Pattern | Remaining occurrences OUTSIDE archive | Verdict |
|---------|--------------------------------------|---------|
| `70.8` (old CG overall) | `AUDIT_LOG`, `STAGE1_FINDINGS` (audit trail) + `manuscript_draft.md` line 4 (retirement banner) + `README.md` line 91 (retirement note) + `compgraphrag_research_paper_guide.md` (retired-numbers note) | ✅ All are intentional historical references |
| `79.2` (old VR overall) | Same files as above | ✅ Same |
| `0.9798` (old F1) | `AUDIT_LOG`, `STAGE1_FINDINGS` (audit trail) + `compgraphrag_research_paper_guide.md` retired-numbers note | ✅ All intentional |
| `0.1469` (old ECE) | Same as above | ✅ Same |
| `37.5` / `91.7` (fabricated) | `manuscript_draft.md` line 4 banner only (listing removed figures) | ✅ Intentional retirement notice |
| `p < 0.005` / `p<0.005` | `manuscript_draft.md` line 4 banner only + `AUDIT_LOG` (documenting what was fabricated) | ✅ Intentional |
| `0.664` / `0.655` | `manuscript_draft.md` Statistical Validation subsection (permanently retired statement) | ✅ Intentional — statement that these values do not exist |
| `14.7` | **None** | ✅ Clean |
| `0.0688` | **None** | ✅ Clean |

**All active documents (README, manuscript_draft, LOCKED_RESULTS, guide) contain only locked real-encoder numbers. The grep sweep is clean.**

---

## Items Deliberately Left for Author Judgment

The following are explicitly flagged as requiring the author's decision before submission:

### 1. Pre-registration effect size for follow-up study
The manuscript's Statistical Validation section explicitly warns that powering a confirmatory follow-up at the pilot's own observed d=0.37 is circular. The author must independently motivate a minimum meaningful effect size (e.g., "a ≥15 percentage-point accuracy difference is the smallest clinical/legal improvement worth detecting"). **This decision is not made here.**

### 2. Exact wording of all rewritten sections
The abstract, H4/H8 reframing, discordant-item narratives (Q03/Q11/Q12), benchmark-validity section, and conclusion are drafted. The factual content is constrained to verified output. **But tone, emphasis, and exact phrasing are the author's to approve.** The Stage 3 completion author strongly recommends reading the full rewritten abstract and Section V before submission.

### 3. CompGraphRAG_Phase1_Phase2.md — disposition unclear
This document (read in full in Stage 1) describes a broader research program that partially overlaps with the current N=24 harness. It was not referenced in any edited document because it is not verifiably connected to any committed code execution. **The author should decide whether this document should be in the repo, what version it describes, and whether it should be linked from the paper.**

### 4. Trade article — Stage 4 required
The trade article was explicitly out of scope for Stage 3 and has not been touched. It will need the same treatment as the manuscript: retire the hash-encoder numbers, reframe H4/H8 as untestable pending better benchmark, state entity-disambiguation finding, and add the faithfulness-fix note.

---

## Commit History (Stage 3)

```
977bc1f docs(stage3): Lock results, reframe paper, update README and guide
9c35c4e fix(faithfulness): Replace edge-derived IE with text-only regex extractor
```

---

## What Remains Unchanged

- **CG accuracy: 100.0%** — three deterministic runs confirmed
- **VR accuracy: 87.5%** — three deterministic runs confirmed  
- **NR accuracy: 87.5%** — three deterministic runs confirmed
- **ECE: 0.0114** — unchanged
- **Mean faithfulness F1: 0.9679** — unchanged (Recall-limited, not Precision-limited)
- All 7 bug-class checks pass under real encoder (Stage 2 Task 3)
- No modification to any retrieval logic, scoring weights, rule engine, or conformal predictor
