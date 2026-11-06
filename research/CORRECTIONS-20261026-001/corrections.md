# Reissued twisted-triple-product proofs and corrected discovery records

Epic `CORRECTIONS-20261026-001`, closed 2026-10-26.

## The request

After `COPRIME-CLASS2-20261026-001`, the owner answered three questions:
- "Whether to reissue the corrected twisted-triple-product proofs": "Yes, please do."
- On the three outdated discovery records: "Could you update them?"
- A short note on the Rowell consequence was approved separately (`ROWELL-NOTE-20261026-001`).

## What was done

**Reissued proofs.** Each supersedes its closed original, which is left unchanged.
- **`CORRECTIONS-20261026-001A`** reissues `TRIPLE-PRODUCT-20261026-001A`. The Samperton–Weiß sentence is corrected (item R2), and the
  shared library's `insert_at` handles insertions at a common level (m9).
- **`CORRECTIONS-20261026-001C`** reissues `TRIPLE-PRODUCT-20261026-001C`, with these changes:
  - Moussard 2017 as precursor, with the novelty downgraded;
  - Habiro's Props. 3.3–3.4 with disk framing and preservation of the Seifert framing (m1);
  - the trivial covering over the surgery region, and existence of the cocycle extensions (m2);
  - basing paths (m3);
  - the leaf convention, with a typo fixed (m4);
  - proved versus interpreted parts of the realizability statement (m7).
- **`CORRECTIONS-20261026-001D`** reissues `TRIPLE-PRODUCT-20261026-001D`, with these changes:
  - an explicit construction (R1a–c);
  - corrected novelty (R2);
  - the Turing-reduction wording (m6);
  - the characteristic-2 scope of the gadget lemma (m5);
  - the Hantzsche–Wendt remark labelled heuristic (m8);
  - a new knot-group corollary, |Hom(knot group)| = |Hom(3-surgery)| + 63, with its consequence for Rowell's Conjecture 3.2(b).

**Every check was rerun on the reissued library** and passes: 18.9 s, 2.8 s and 45.3 s.

**Superseded records.** Four discovery records are superseded by corrected ones (`CORRECTIONS-20261026-001R`):

| Old | New | Reason |
| --- | --- | --- |
| `SL23-BOUNDED-20261025-001-D001` | `CORRECTIONS-20261026-001-D001` | The Fitting-height line was refuted |
| `CLOSED-H1-20261025-001-D001` | `CORRECTIONS-20261026-001-D002` | The quandle equality is implied by Livingston 1995 |
| `HARD-3D-20261025-001-D001` | `CORRECTIONS-20261026-001-D003` | The S₃ hardness is a case of Galindo 2026; the explicit constructions stay |
| `TRIPLE-PRODUCT-20261026-001-D001` | `CORRECTIONS-20261026-001-D004` | Rebound to the reissued proofs, with knot groups |

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: corrections | **Status:** Successful | All review items are applied; checks are rerun; records are superseded with their texts preserved. |
| Local direction | Exhausted | No further corrections are known. |
| Broader exploration | Known alternatives | The three scouting lanes of `NEXT-DIRECTION-SCAN-20261026-001` are running. |
| Long-term goal: the complexity side of the 2-versus-3 thesis | No new capability; consistency restored | The repository's records now match the strongest checked statements. |
| Next recommendation | **Next step:** Continue with the approved note (`ROWELL-NOTE-20261026-001`) and the scouting reconciliation | Both are already approved by the owner. |
| Interest | **2/3: Promising** | It is housekeeping, but it is what lets the note cite consistent, reviewed artifacts. |
| Execution | Started | The note is drafted next; the lanes are reconciled when they report. |
