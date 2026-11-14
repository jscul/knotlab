# Returns across levels: patterns that die and come back

Epic `LEVEL-RETURN-20261113-001` (`ADDR-KNOTS-20261113-001#1`; G17, with G8; program topology, group spacing), 2026-11-13 to 14, at
the coordinator's go-ahead. Pre-registered in 470992577 ([preregistration.md](preregistration.md)), with the rigidity addendum R5
(052c3fffb) and two procedure fixes (4f0ff2aef, 972b9d8eb), all before any registered result was used. Code by the thread
(`certify.py`, `lrat_check.c`, `job.py`, `job_rigid.py`, `prover.py`); the census's `addr.py` (Codex's) as the second pattern generator;
CaDiCaL 2.1.2 from the Lean toolchain. The canonical K1–K3 test is unchanged. **Refereed** (LEVEL-RETURN-R1, `referee-R1/report.md`,
commit 8f155c867): **confirmed with fixes**, one Block (the refutations were not archived) and two Narrowings, folded in below and
logged in `docs/CORRECTIONS.md`; the referee also proved two things this note had only computed.

## Words

As in `ADDR-KNOTS-20261113-001`: address, level, address map, placement; a **return** is a dead level followed by a living one. A
pattern is **rigid** at a level when it has exactly one state up to complement there. "Certified": alive by a model checked against
every knot; dead by an LRAT refutation checked by the thread's checker; anything else undecided. *Narrowed after the referee
(Block on the evidence claim):* the refutations were checked at run time, and neither the CNFs, the proofs nor their hashes were kept,
though the pre-registration promised the hashes; the referee recertified 12 of the 13 dead and all 13 living cells of the seven at
levels 13 to 16 from fresh code (30 of 34 sampled cells overall, no disagreement), its certificates on disk with hashes.

## The question

The census found 48 patterns that die at a level and live at a later one, 7 alternating with the level's parity to level 12. Do the
returns and the alternation hold to level 16 with every verdict certified, and why do the seven alternate?

## The question in standard terms

Certified satisfiability of the 48 NAE-3-SAT families {g₁x, g₂x, g₃x} on {0,1}ⁿ, n = 1..16; for the seven period-2 families, all-n
proofs of satisfiability at one parity, and a mechanism for unsatisfiability at the other.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **The seven keep alternating to level 16.** Every certified verdict at levels 13 to 16 follows the parity (26 of 28 decided; one level each undecided in two patterns); 5 of the 7 are certified period 2 on levels 5 to 16. | certified to level 16 | R1 held |
| 2 | **The living half is proved at every level for two of them.** For #2 the address's parity is a state at every odd level n ≥ 3; for #3 the first letter XOR the last is a state at every even level n ≥ 2. A finite product check decides each statement for all n (reachable configurations of the three runs, the state's automaton on their outputs, which pairs have differed, the level's parity). The census's level-13-to-16 checks replay both. For the other five none was found among the feature automata tried (up to 424 states; *narrowed after the referee*). The referee's independent product automaton confirms both proofs, and direct checks pass to level 21 (#2) and 22 (#3). | proved; replayed | R2 held |
| 3 | **Why #2 dies at even levels: two knots and rigidity.** At every even level n ≥ 4, parity violates exactly two knots, at the addresses 0ⁿ⁻²10 and 0ⁿ⁻²11 of one placement (*proved by the referee*: the violating inputs are exactly (00)+1(0|1) on placement [0, 8, 10], their images pairwise distinct; this note had computed it to 14), so parity is a state of the pattern without them and that pattern lives at every even level. The pattern without them is **rigid** at every even level 6 to 14: its only states are parity and its complement. Since a part's states include the whole's, the whole has at most those two, both of which violate the two knots: so death at each even level from 6 follows from that level's rigidity. Rigidity at every even level is open. | proved (the two knots, the implication); rigidity certified at 6 to 14 (recertified by the referee at 6 to 12) | R4 held (proved at every even level), R5b held (to 14) |
| 4 | **Five of the seven are rigid where they live.** #2 (at its odd levels 7 to 13; it has other states at 3 and 5, for example 01101000 at level 3; level 15 undecided), #3 (from level 4; non-complementary states at level 2), #4, #5 and #7 (level 15 undecided) have exactly one state up to complement at every living level certified from 4 to 16 (*ranges narrowed after the referee*); #1 and #6 have more at every living level. So in five, the law fixes the whole pattern from one value whenever it lives at all. | certified to level 16 | R5a held |
| 5 | **The other returns keep their fate.** Of the 41 other returning patterns, those alive at levels 10 to 12 stayed alive at every decided level 13 to 16 (15 of 15 decided), those dead stayed dead in 14 of 15. Fates on levels 5 to 16: 9 constant from level 5, 5 of period 2, the rest neither or with undecided levels. | certified | R3 held |
| 6 | **Checks.** 775 cases, every one finished: 420 alive (models checked) and 294 dead (refutations checked at run time, not archived), 61 undecided (two hard patterns hold most); the two pattern generators agree at every case and the census's verdicts at every level both decided. Gates: Fano dead, corrupted and truncated proofs rejected, 400 of 400 small patterns agree with brute force. | computed | gates |

## Answer

Yes. Every certified verdict to level 16 keeps the returns and the alternation, so the seven are a harmony in the level within level
16. For two of them the living half is a theorem at every level, by a state that a small automaton computes from the address. For one,
the dying half reduces to rigidity: remove two knots and the pattern has only the parity state, which those two knots forbid, so it dies
at each even level where that rigidity holds (certified to 14). Rigidity is common here: five of the seven have exactly one state up to
complement wherever they live.

## Reading

**Interpretation, not a theorem.**
- **A harmony in depth.** For the owner's harmonies: these patterns live or die by the level's parity, the first fates in the
  program's nested line that are neither monotone nor constant. Two are proved alive at every level of their parity; none is proved
  dead at every level of the other.
- **The law fixing everything.** Rigidity means one value decides every address: the extreme of "the top binds the deep levels",
  which `LEVEL-REACH-20261114-001` measures.
- **Counting mod 2.** In #2 the only states are the address's parity and its complement: the law, on a pattern placed by three maps,
  forces a count of ones modulo 2 at every odd level, and that count is what kills the even levels.

## Lag cutoffs and census-only claims

Levels 1 to 16, the 48 patterns of the census; 1,800 seconds per solve. A certified verdict holds for its level only; every all-level
statement is in conclusion 2 or the implication of conclusion 3.

## Literature and provenance

Parity of the Gray code is its last bit (classical; the computation behind #2's state); automatic sequences and regular properties
of automaton runs (product constructions, known in kind); two-fold covers and voltage graphs (Gross and Tucker). Not found: fates of
not-all-equal patterns that alternate with the level. Ours: the certified readings, the two all-level states, the two-knot reduction
and the rigidity readings. Classification: known-with-delta.

## Procedure

The first run lost 400 of 775 cases: refutation proofs left in the memory-backed `/tmp` by stopped cases filled the run's memory
allowance (23 GB, removed). The second streamed proofs through a pipe and the checker throttled the solver. Both were stopped before any
result was used; the third solves without a proof first and re-solves a refuted formula with its proof written to disk, checked and
deleted. Disclosed in the pre-registration. The smoke test's one alternating pattern was seen to level 16 before the freeze.

## Review

Refereed (LEVEL-RETURN-R1, Codex-assisted, fresh code; confirmed with fixes; above). The advisor model was consulted before the freeze (`advisor_design_*.md`): its hand proof of #2's parity state, the
two-knot prediction R4, the second generator and the checker's negative controls are its.

## Workspace assumptions

A82 (the automaton reading). No new assumption.

## Ratio

Substantive: the certified runs, the product proofs, the reduction. Administrative: the pre-registration, two procedure fixes, this
note.

## Corrections

None to published claims. (Of `ADDR-KNOTS-20261113-001`'s, see its referee report.)

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — returns and alternation to level 16 | **Status:** Successful | R1 to R5 held on every decided level; two living halves proved at every level |
| Local direction — the alternating patterns | Continue | The dying half reduces to rigidity, open at every level |
| Broader exploration — G17 nested line | Known alternatives | The reach study is under way; rigidity links them |
| Long-term goal — G17 Typical and rare meeting patterns (with G8) | Capability gained | Fates that depend on the level's residue, certified and in part proved |

**Corrections:** none. **Goals:** a G17 checkpoint (with G8), capability gained; no goal change. **Assumptions:** A82 used.
**Basket:** `BOND-BALLS-20261111-001#2` (2/3, 3/3), `ACROSS-FOLD-20261112-001#3` (2/3, 3/3), `FAR-BOUND-20261112-001#2` (2/3, 3/3),
B175 (the finite inflation for bounded patterns).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Reach across levels | 3/3 — Breakthrough-scale | 2/3 — Testable | `LEVEL-REACH-20261114-001`, approved by John, under way → its registered census | Selected · started |
| 2 | Rigidity at every level | 2/3 — Substantial | 2/3 — Testable | Prove #2's reduced pattern rigid at every even level: an automatic description of the forced ties, checked by the product construction → a proof of death at every even level, or a level where rigidity fails | Alternative · deferred |
| 3 | States for the other five | 1/3 — Incremental | 2/3 — Testable | Search wider state automata (two letters of memory per run, sections of the relative maps) → an all-level living proof, or evidence that none is automatic | Alternative · deferred |

1. Payoff 3 as John rated it: whether the top binds the deep levels; rigidity is its extreme. Concreteness 2: the exact bond search is
   built and gated, its cost at nine levels the open point. Under way.
2. Payoff 2: the first all-level proof of a dying half in the nested line. Concreteness 2: the ties are certified to 14; their
   description is not yet known to be automatic.
3. Payoff 1: completes the living half; Concreteness 2.

**Recommendation.** Research directions, #1 (started), #2 next.

## Hand-off to the referee

Folder: this one (note, pre-registration with R5 and the procedure notes, `summarize.py`, `summary.json`, `exploratory/`, advisor
Q/A); the proof family `proofs/LEVEL-RETURN-20261113-001B/` (`prover.py`, `check.py`, `result.json`); code and runs in
`experiments/LEVEL-RETURN-20261113-001A/LEVEL-RETURN-20261113-001A-E001_certified_levels/` (`run3/`, `run_rigid3/` are the registered
runs; `run/`, `run2/`, `run_rigid/`, `run_rigid2/` are the stopped ones, kept, not used). Proved: the two all-level states (finite
product check) and the implication rigidity + two knots ⇒ death. Certified: every verdict in conclusions 1, 3, 4, 5. Least sure: (a)
the product check's handling of the identity word and of knots dropped for coinciding images; (b) whether the checker's RUP-only
rule could accept a wrong step (it rejected every corrupted proof tried); (c) the "exactly two knots" claim is now proved by the referee; (d) the feature-automaton search for the other five was exploratory.
