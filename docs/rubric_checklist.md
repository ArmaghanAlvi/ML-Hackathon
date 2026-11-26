# Rubric checklist

| Rubric line | Points | Deliverable | Stream | Status |
|---|---|---|---|---|
| ML model & rigor: model beyond basics | 35 | Trained projection head on SigLIP 2 (+ review model, re-ranker) | A, B | TODO |
| ML model & rigor: baseline comparison | (35) | ResNet-50 and zero-shot SigLIP vs. trained head (`ml/artifacts/metrics/baselines.json`) | A | TODO |
| ML model & rigor: clean split | (35) | `parent_asin` split 70/15/15, `docs/data_card.md` | A | TODO |
| ML model & rigor: no leakage | (35) | Dedupe before split, thresholds on val, test used once | A, B | TODO |
| Problem & impact: specific problem | 25 | Problem statement + slide | D | TODO |
| Problem & impact: specific group | (25) | Target user in `docs/decisions.md` | All | TODO |
| Results & evidence: right metric | 20 | Recall@K, precision@3, macro-F1 / PR-AUC in `docs/evaluation.md` | A, B | TODO |
| Results & evidence: baseline comparison | (20) | Live comparison table (Lens order vs. ResNet vs. zero-shot vs. ours) | B | TODO |
| Results & evidence: at least 1 visual | (20) | Recall@K bars, confusion matrix (`ml/artifacts/figures/`) | A, B | TODO |
| Full-stack: works end to end | 10 | Photo → results on a phone | C, D | TODO |
| Full-stack: frontend | (10) | PWA (`frontend/`) | D | TODO |
| Full-stack: backend serving the model | (10) | `/api/search` with real matcher | C | TODO |
| Full-stack: live demo | (10) | Tunnel + cached mode | C, D | TODO |
| Demo: clear | 10 | `demo/script.md`, slides | D | TODO |
| Demo: on time | (10) | ≥3 timed rehearsals | All | TODO |
| Demo: can explain own code | (10) | `docs/notes/stream-*.md`, `demo/qa_prep.md` | All | TODO |

Points in parentheses belong to the same rubric line as the row above.
