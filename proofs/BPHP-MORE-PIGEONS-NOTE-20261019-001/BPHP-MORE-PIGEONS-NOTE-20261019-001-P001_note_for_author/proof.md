# A checkable note for Braun: bit PHP with more pigeons, bit-colouring, and an independent replay

Status: Proved

Ticket `BPHP-MORE-PIGEONS-NOTE-20261019-001`, 2026-10-19. This ticket packages
two earlier results for Kamil Braun, or any reader of his Res(⊕) preprint
(arXiv:2609.23015), to check without this repository:
- `HOLE-CRITERION-COLOURING-20261019-001B-P001`: his bound for more pigeons and
  for bit-colouring;
- `BPHP-RES-PARITY-AUDIT-20261019-001`: the independent replay and definitional
  audit.

It adds no new mathematics. Whether to send any of it, and how, is the
repository owner's decision.

## The package

| File | What it is |
| --- | --- |
| `note/more_pigeons.pdf` (source `more_pigeons.tex`) | A 4-page note. It states the three results, proves them, compares them with earlier work, and gives replay steps. Its appendix quotes the main Lean statements, which `check.py` extracts into `note/lean_statements.txt`. |
| `MorePigeonsColouring.lean` | The drop-in Lean file: B-P001's proof unchanged, with a header for an outside reader. It builds as `claims.MorePigeonsColouring` when copied into `formalization/claims/` of Braun's repository. |
| `note/replay_summary.pdf` (source `replay_summary.tex`) | A one-page summary of the audit. It covers the replay from source, the axiom report, the fresh kernel replay, the controls, the definitions compared and the witnesses against vacuity. It says plainly that an AI agent carried out the audit. |
| `note/cover_message.txt` | A draft cover message, unsigned and with no personal address, for the owner to edit or discard. |

## Why now

On 2026-10-19 we searched for prior statements and found none.
- **Braun's repository.** Its newest commit is `25239211`, 4698 commits after
  the audited `8904bf09`. Nothing there states the more-pigeons extension. It
  adds only new files under `formalization/`, plus edits to two documentation
  files, and the bit-PHP paper's changes since the pin are revision 2's
  exposition and verification appendix.
- **arXiv:2609.23015.** It still has only v1, and its abstract covers n+1
  pigeons only.
- **Byramji and Impagliazzo, arXiv:2511.20023.** Their Theorems 1.1 and 1.3
  cover m > n pigeons, but only depth-dependent: D√(log S) = Ω(n^1.5), and
  log S = Ω(min{n²/D, n⁴/(kD²)}) for m = n+k. At unrestricted depth they give
  no superpolynomial bound.

Braun's publication `FEEDBACK.md` also lists two open items:
- "Get the formalization built and its axioms printed by an independent
  party". The audit covers this.
- "Ask an independent Res(⊕) expert to check that the Lean definitions are the
  standard system". The audit is input to this, but not a substitute, since an
  AI agent rather than a human expert carried it out.

## What `check.py` establishes

| Check | Result |
| --- | --- |
| The drop-in's body is B-P001's kernel file, character for character after the header | pass |
| Copied into `formalization/claims/` at the pinned commit, it builds as a module of the author's library | pass; the checkout is clean again afterwards |
| The eight theorems depend only on `propext`, `Classical.choice` and `Quot.sound` | pass |
| From `8904bf09` to `25239211`, `formalization/` changes only by 30 added files and two documentation edits | pass, so the build result carries over |
| The note's appendix is the Lean statements, extracted from the drop-in | pass |
| The note's theorem constants match the Lean statements | pass |
| The note's numbers are recomputed: the ℓ = 32 range end 31,869,902,254 ≈ 7.42·2³², m = 2n in range from ℓ = 32, ⌊n^{3/2}⌋ in range from ℓ = 65 | pass |
| Every figure in the replay summary matches the audit's records: 7 declarations, standard axioms, `leanchecker --fresh` 206 s, control lines 41 and 125, toolchain, Mathlib pin, commit, an 11-line refutation | pass |
| Both PDFs build with xelatex, with no missing glyphs or overfull lines; any stored PDF carries the same text as a fresh build. PDFs are git-ignored in this repository; `check.py --write` rebuilds them into `note/` | pass; 4 pages and 1 page |
| The cover message has no e-mail address and is unsigned | pass |
| Controls: a tampered quotation, summary figure, drop-in body and note number | each caught |

## Scope

- **Inherited claims.**
  - The mathematical claims are B-P001's, and rest on Braun's kernel-checked
    development.
  - The audit's claims are those of `BPHP-RES-PARITY-AUDIT-20261019-001A-E001`
    and `-001B-P001`.
- **Not done.**
  - Nothing has been sent to anyone.
  - The byline names the lab, and the cover message is unsigned. Both are for
    the owner to decide.
  - No human expert has reviewed the note.
