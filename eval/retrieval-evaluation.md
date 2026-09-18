## Retrieval Evaluation

Measured with a 25-query golden dataset (`eval/golden_dataset.json`) against precision@5 / recall@5, scored at the document level (see `eval/run_eval.py`). Re-run anytime retrieval logic changes: `python eval/run_eval.py`.

| Method           | Precision@5 | Recall@5  |
| ---------------- | ----------- | --------- |
| Vector-only      | 0.272       | 0.900     |
| Keyword-only     | 0.208       | 0.720     |
| **Hybrid (RRF)** | **0.288**   | **0.960** |

**Note on precision@5:** most queries have only 1–2 genuinely relevant source documents, so the maximum achievable precision@5 for those queries is 0.2–0.4 regardless of retrieval quality — precision numbers in this range reflect the dataset's structure, not weak retrieval. Recall@5 is the more directly comparable metric across methods.

**Concrete cases where hybrid fusion outperformed both individual methods:**

- _"field mapping syntax"_ — vector-only scored 0.0 (total miss); hybrid recovered the correct result via keyword matching.
- _"GitHub repository not showing as trigger option"_ — keyword-only scored 0.0; hybrid held vector-only's correct result.
- _"SCIM provisioning"_ — both individual methods scored 0.5 recall; hybrid alone reached 1.0, exceeding either input list — Reciprocal Rank Fusion correctly promoting a chunk that ranked well in both lists but wasn't #1 in either.

Full per-query breakdown: `eval/results.json`. Qualitative analysis from the Week 3–4 build process: `eval/retrieval-comparison.md`.
