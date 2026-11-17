# Is a two-orbit bond from the top the only thing that keeps the reach bounded?

Epic `CARRIER-20261117-001`. It takes direction #1 of `KEEP-REACH-20261117-001` at the coordinator's go-ahead (2026-11-17 17:58
UTC), within John's request of 16:52 UTC to reopen the line ("let's see if we can uncover anything here"). It serves G17, with G1,
and ran on 2026-11-17. Proof note:
[proof.md](../../proofs/CARRIER-20261117-001A/CARRIER-20261117-001A-P001_exact_pieces/proof.md). Code by the thread. The canonical
K1–K3 test is unchanged. **Referee pending.** **Deeper tests pending**: depth 13 for −73 at s = 7, 8 (LONG_RUNNING `CARRIER-A5`) and
a bound of 7 for −79 at depth 12 (`CARRIER-A6`).

## The question

KEEP-REACH proved that a bond inside two orbits, one at the top level and one s levels down, bounds the reach at every depth when it
survives at every distance (Theorem K). It conjectured the converse, C′: the reach is bounded only when such a two-orbit bond
survives. 25 patterns never forget, even on the values states take, yet hold no two-orbit bond from the top. 13 have top pair
projections that become products, and 12 keep an unexposed dependence. Their boundedness was open, and they are where C′ is tested.

## Answer

**No: C′ is false.** All 12 patterns with an unexposed dependence keep the reach bounded at every depth, at 5 members, without a
two-orbit bond from the top. What holds them is a bond inside a slightly larger piece whose projection is still exact:
- **An orbit and a block.** For 2 of them (bace53f8f952-147, -111), the bond is inside the top orbit and the block of the lower orbit,
  that is, the lower orbit with its children. At s = 5 it has one member at level 3, one at level 3 + s and two at level 4 + s.
- **A stem.** For the other 10 (bace53f8f952-58 and nine mutants of ca1efb37ad88), it is inside the top orbit, the lower orbit's
  two ancestor orbits just below the top, and the lower orbit. This is the **stem** of depth 2 (the advisor's word).

The dependence was unexposed inside the two orbits because one orbit's own constraint stood in the way (KEEP-REACH's Lemma E).
Holding the lower orbit's children, or the orbits between, exposes it. For the 13 mutants of 8db5da810c00, stems explain the
certified readings and stop there:
- **The readings.** They read exactly 6 at s = 5 and 6 at depth 11, carried by stem bonds.
- **Where stems stop.** Stems of depth 2 have no bond of at most 8 members from s = 7 on. On −73, a stem of depth 3 has none at s = 7
  either (depth 12).
- **Past the stems.** At depth 12 two of them, −73 and −79, have no bond of at most 6 members at s = 7 or 8 (certified by LRAT).
  So their reach keeps rising past every carrier found: 3, 4, 5, 5, 6, 6, then at least 7, 7.
- **What stays open.** Whether it rises without bound.

Three results:
- **Theorem K\* (proved).** A bond inside any set of addresses whose projection is exact, holding a distinction at level k and one at
  level k + s, bounds L_N(k, s). Two pieces have exact projections that the every-depth routine computes: an orbit with the block of
  the lower orbit, and a stem with the lower orbit (Lemma P). Theorem K is the case of two orbits.
- **C′ refuted (computed exactly, every depth).** The 12 unexposed patterns, bounded at 5, have no two-orbit bond from level 3 past
  s = 2 or 4.
- **Exact values.** L₁₁(3, 5) = L₁₁(3, 6) = 6 for all 13 mutants of 8db5da810c00: no bond of at most 5 (certified by LRAT), and a
  stem bond of 6 at every depth.

| Patterns | Two-orbit bond from level 3 | Orbit-and-block bond | Stem bond (depth 2) | Verdict |
| --- | --- | --- | --- | --- |
| bace53f8f952-147, -111 | to s = 2 | every s: 4 (5 at the bottom tiers) | | bounded at every depth (5) |
| bace53f8f952-58, nine of ca1efb37ad88 | to s = 4 | to s = 4 | every s ≥ 3: 5 (4 at s = 3 for ca1efb37ad88) | bounded at every depth (5) |
| 13 mutants of 8db5da810c00 | to s = 4 | to s = 4 | 5, 5, 6, 6 at s = 3..6; none of at most 8 from s = 7 | open; exactly 6 at s = 5, 6 (depth 11); at least 7 at s = 7, 8 (depth 12, two of them) |

Two observations came out of this:
- **A mutant can pass its parent's bound and stay bounded.** bace53f8f952-58 reads 5 at every distance from s = 3, past its parent's
  4, yet is bounded at every depth. So −73's passing its parent's 5 at depth 11, noted in KEEP-REACH, says nothing yet about growth.
- **A mutant can sit below its parent.** The nine ca1efb37ad88 mutants are bounded at 5, below their parent's two-orbit bound of 6
  (the parent's own stems also read 6).

In the program's words: a dependence between two orbits far apart that no bond inside them shows is not lost. A bond appears once
a little more of either strand is held: the lower orbit's children, or the orbits just below the top on the way down. What holds the
top is a bond between two bounded pieces, one at each end, and not between two orbits.

**The repaired conjecture (C\*, the advisor's form).** The reach from level k is bounded at every depth exactly when, for some fixed
d and e, a bond exists at every s and every depth inside two pieces: the orbits within d blocks of the top orbit, and those within e
blocks of the lower orbit. The "if" direction is Theorem K* with Lemma P's argument. The advisor sketched a proof of "only if" by
pumping, not checked: a bond's empty stretches compose finitely many block transfer relations, so a long stretch can be shortened or
lengthened by a repeated factor until only one is long. It is open. For the 13 mutants it would turn the question into a choice
between a bond in fixed pieces at both ends at every distance and growth.

| # | Conclusion | Kind |
| --- | --- | --- |
| 1 | Theorem K*: a bond in an exactly projected piece bounds the reach; orbit-and-block and stem pieces project exactly (Lemma P) | proved |
| 2 | The 12 with an unexposed dependence are bounded at every depth at 5 (2 by orbit-and-block bonds, 10 by stem bonds) | computed exactly at every depth tier (check passed) |
| 3 | Conjecture C′ is false (item 2) | follows |
| 4 | L₁₁(3, 5) = L₁₁(3, 6) = 6 for the 13 mutants of 8db5da810c00 | computed, certified (threshold search, LRAT) with stems at every depth |
| 5 | Stems of depth 2 give no bond of at most 8 for the 13 from s = 7 on; on −73 a stem of depth 3 gives none at s = 7 | computed (depth 3 at depth 12 only) |
| 6 | L₁₂(3, 7), L₁₂(3, 8) ≥ 7 for 8db5da810c00-73 and -79 | computed, certified (threshold search, LRAT, 3,600 s per cell) |
| 6 | Conjecture C* (bounded pieces at both ends) | stated, with the advisor's proof idea |

## Predictions

Frozen in [predictions.md](predictions.md), committed in 7ff989e6b. The threshold run had been launched before the file was written,
with its outputs unread, as disclosed there.
- **P1 holds.** All 12 mutants of 8db5da810c00 besides −73 have no bond of at most 5 members at s = 6 (and at s = 5).
- **P2 fails, on both counts.** Only 1 of the 12 unexposed patterns was decided within 900 s, against at least 8 predicted.
  - The decided one, bace53f8f952-147, has a bond of 4, within its parent's bound.
  - The every-depth computation later showed bonds within the parent's bound at s = 5 and 6 for 11 of the 12; bace53f8f952-58 has 5,
    past its parent's 4.
  - The search left those cells undecided because it did not find the bonds within its budget.

The block and stem computations were not pre-registered. The predictions file named the follow-up for a decided "yes": a search for a
structure of more than two orbits. Those computations are exact at every depth and are not tests with an outcome to predict.

## Lessons

- A dependence that no bond inside two orbits shows can still hold the top. A bond appears in a slightly larger piece, so test
  carriers before calling a dependence idle.
- Passing a parent's bound is not growth: bace53f8f952-58 passes its parent's 4 and stays at 5 at every depth.
- An undecided certified search is not evidence against a bond. The searches missed 4- and 5-member bonds that the exact
  every-depth routine finds within about a minute.

## Checks

Gates (`gate_two_block.py`, `gate_head.py`, outputs `gate_two_block.json`, `gate_head.json`; LONG_RUNNING `CARRIER-A2`, `CARRIER-A4`),
all passed:
- the bond search agrees with brute force on 2,000 and 1,000 random relations;
- the exact projections agree with SAT on 120 orbit-and-block pieces at depth 7 and 120 stem pieces at depth 8;
- the every-depth tiers agree with the computation at each depth on 1,200 and 720 values;
- no bound is below any of 2,021 decided census cells at depth 9 and certified readings, or 40 certified readings for stems.

`verify_bonds.py` (`verify_bonds_N11.json`) takes, for each of the 25 at depth 11 and s = 5, 6, a least bond found on an actual pair
of orbits. It maps the bond to its addresses and confirms by SAT on the whole depth-11 pattern that it is a bond: constrained, with
every subset one smaller free. All 50 are bonds: 4 members for bace53f8f952-147 and -111 (orbit and block), 5 for the other 11 of the 12 (stems), 6 for the 13 mutants (stems). The proof's `check.py` recomputes five of the stored every-depth results and the table,
and passes.

## Advisor

Used once, on the analysis and the word, after the computations (`advisor/head_question.md`, `advisor/head_answer.md`):
- **The repair.** It showed why C* in its first form (the stem only) is likely false: a bond can use orbits off the line, such as a
  sibling or a side child. It proposed bounded parts of the tree of blocks around each end, adopted.
- **"Only if".** It sketched the pumping proof, recorded as unchecked.
- **Growth.** It noted that a stem adds nothing to a product hypothesis (the stem's lowest orbit separates), and proposed that growth
  be read as the absence of bonds between bounded pieces at distance.
- **The word.** It proposed "stem", with no clash in the glossary.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt (C′ on the 25) | **Status:** Successful | C′ refuted on 12 patterns; carriers found; exact values for the other 13 |
| Local direction (carriers of bounded reach) | Continue | C* is the sharp form; the 13 are its test, and the pumping proof is concrete |
| Broader exploration (G17's addressed line) | Known alternatives | B186 (least-mark costs) and B188 (growing orbits) stand |
| Long-term goal (G17, Typical and rare meeting patterns, with G1) | Capability gained | Bounded reach now has a proved sufficient carrier family and a repaired conjecture |

**Corrections:** none. C′ was a stated conjecture, and nothing was built on it as if true (`docs/CORRECTIONS.md`'s rule). **Goals:** a
G17 checkpoint (with G1), capability gained; G17's stands-on bullet for KEEP-REACH updated to say C′ is refuted. **Assumptions:** A83
used; none added.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove C*'s "only if" by pumping, and settle the 13 | 3/3 — Major | 2/3 — Testable | Write the normal-form lemma for bonds of bounded size (transfer monoid of blocks, tiers in the type); then for the 13, either a bond in fixed pieces at both ends at every s, or the growth hypothesis (no such bond past some distance) → a proof of C*, or a bounded pattern that needs a middle piece | Selected · awaiting go-ahead |
| 2 | Exact reach by least-mark costs (B186) | 2/3 — Substantial | 2/3 — Testable | As filed | Alternative · deferred |
| 3 | Lower bounds when orbits grow (B188) | 2/3 — Substantial | 1/3 — Stated | As filed | Alternative · deferred |

The reasons for each rating:
1. **C\* and the 13.** Payoff 3: proved both ways, C* says that bounded reach is always held by two bounded pieces, one at each end,
   and it gives a semi-decision for boundedness. In the knot picture, what holds the top to every depth would always be a knot between
   two bounded strand pieces, never something spread along the way. Concreteness 2: the pumping argument has a clear shape (finite
   monoid, tiers as types), and the 13 are a concrete test set with exact readings to s = 6. The uncertain part is the growth side,
   which needs a lower bound the program has only for products.
2. **Least-mark costs.** As filed; it would give exact reach values where orbits stay small.
3. **Growing orbits.** As filed.

**Recommendation.** Research directions, #1, awaiting the coordinator's go-ahead. Stop or reassess if the normal-form lemma fails on
a pattern whose bounded bonds need a middle piece.

## Hand-off to the referee

**Files.**
- This folder: the note and predictions, with `threshold.py` and `threshold_*.json`; `two_block.py`, `run_block.py` and
  `block_25.json`; `head_bond.py`, `run_head.py` and `head/`; the gates and their outputs; the advisor's Q/A; `exploratory_d3.log`;
  `threshold_deep.py` and its outputs (`threshold_deep_*_c6.json`; the depth-13 and bound-7 runs are pending).
- The proof family `proofs/CARRIER-20261117-001A/`: `proof.md`, `check.py` and `result.json`.
- Certificates of the threshold run, packed: `codex/certificate_archives/` (see the index there).

**Status.** Proved: Theorem K* and Lemma P. Computed: the carriers of the 25, the exact values of the 13 at s = 5 and 6.

**Least sure.**
- (a) `head_bond.py`'s stem descent in case (ii), where the lower orbit is not below the top orbit: the stem then holds ancestors of
  the lower orbit only. The gate checks it against SAT at depth 8.
- (b) The tiers of the every-depth routine for blocks, whose children read one level shallower, so the tiers run to r₀ + 1.
- (c) That "none of at most 8" for the 13 from s = 7 is a cap, not a proof that no stem bond exists.
