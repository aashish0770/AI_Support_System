# Retrieval Comparison:

Manual comparison of vector-only, keyword-only, and hybrid retrieval across the Week 3 spot-check query set. Raw output: `week4-comparison-raw.txt`.

## Key findings

| Query                                    | Vector-only                             | Keyword-only                    | Hybrid                                      |
| ---------------------------------------- | --------------------------------------- | ------------------------------- | ------------------------------------------- |
| "what happens if I exceed my rate limit" | Ranked wrong chunk (Billing & Plans) #1 | Correctly ranked Rate Limits #1 | Corrected — Rate Limits #1                  |
| "how do I verify a webhook signature"    | Correct (Webhooks #1)                   | Correct (Webhooks #1)           | Correct, no regression                      |
| "AUTH_KEY_REVOKED"                       | Ambiguous top result                    | Ambiguous top result            | Both relevant chunks tied at top via fusion |

Full precision/recall numbers, not just spot-checked examples, are in Week 5's `eval/results.json` this file captures the qualitative "what actually happened and why" version.
