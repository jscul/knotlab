# Referee brief CHEAP-COUNT-R1 (from the coordinator, 2026-11-12, lean, Codex-assisted)

**The epic.** `CHEAP-COUNT-20261112-001`: pre-registration 15f676529, epic 0b0cc8025, goals and notebook a3365d006.

**Files.** The code is `experiments/CHEAP-COUNT-20261112-001A/.../census.py` (pysat). The data is `artifacts/.../{s1.json, s2.json,
s3_*.jsonl, summary.json}`.

**Claims.**
- **S1, least gadgets.** For f = 0, 1, 2 there is none. For f = 3 the least is 12 knots, with 168 minimal gadgets. For f = 4, 5 and
  6 it is 10 (the P1 plateau).
- **S2, the growth.**
  - Rule 60 built with the gadget equals the exact parity to depth 64. It is alive at 1–6, 11–14, 27–30 and 59–62.
  - Rules 90 and 150 are unexplained, and rule 102 dies at depth 3.
  - Hop lives to depth 11 and is dead from 12 to 64 (P3 failed).
- **S3, mutations.** Of 240 mutations, 3 keep parity, 169 are constant and 68 eventually constant (P2 held).
- **Weight.** About 105.6 or 103.6 bits per description. The 504 counting descriptions found weigh about 2^−97.

**Points to check.**
- The synthesis encoding, minimality and completeness, and collisions in the gadget build.
- The weight arithmetic.
- What is settled by construction or known.
- Whether P3 and rules 90 and 150 are reported honestly.

**Report.** Send the verdict, saying where Codex was used and what it caught or missed.
