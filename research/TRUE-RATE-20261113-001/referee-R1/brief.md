# Referee brief TRUE-RATE-R1 (from the coordinator, 2026-11-13, lean, Codex-assisted)

**The study.** `TRUE-RATE-20261113-001`: note `true_rate.md`; commits c279678a2, 845f53cbe, c360f4552 and 5acfa91fa. The code is
Codex-written, so the recheck uses fresh code.

**Claims.**
- **Computed.** The uncapped side table closes in 24 of 226 families, all unshortened, with λ_true = λ_ray. P1 failed.
- **Proved** (the thread's certificate, advisor-checked). L(s) ≤ 3 at every depth in 10 families (262, 269, 302, 363, 579, 642,
  662, 908, 975, 1144), all of which carry a top port.
- **Counts.** 320 of BRANCH-DEPTH's 432 bounded rules are carried, and 112 are not.
- **Corrections** (Narrowing). The missed BRANCH-DEPTH prior work. A81 was filed.

**Points to check.**
- The certificate's steps 1–4.
- The mapping from idx to (sample file, line + 1).
- The carried-port test.
- Whether the missed prior work is a Block against TRUE-BOND.
