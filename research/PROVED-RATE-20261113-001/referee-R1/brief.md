# Referee brief PROVED-RATE-R1 (from the coordinator, 2026-11-13, lean, Codex-assisted)

**The epic.** `PROVED-RATE-20261113-001`, closed referee pending: pre-registration and spec 43bc81620, epic c3c951269, goals and
notebook ab97368c1.

**Independence.** The study's code was written by Codex from a frozen spec. So the recheck uses fresh code from the spec, without
the study's implementation, with more of the referee's weight on the proofs.

**Claims** (proved per family on complete graphs):
- **Gate and completeness.** 0 mismatches; 655 of 664 graphs complete.
- **Rates.** λ > 0 in 226, giving L_ray(s) ≥ λ(s − |V|). λ = 0 in 417, of which 305 are bounded_all. λ is None in 12.
- **Against BOND-DEPTH's classes.**
  - Of its 240 rising families, 214 have λ > 0 (P2 89%, failed).
  - Of its 163 flat families, 117 are bounded_all (P3 72%, failed).

**Points to check.**
- Karp on the trimmed graph, the trimming itself, and whether bounded_all is sufficient.
- The capped graphs, and whether the lower bound follows.
- Agreement with the referee's depth-512 sample.
- The run history, the wording (ray only), and the prior work.

**Report.** Send the verdict, with fixes marked Block, Narrowing or Not a block.
