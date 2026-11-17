# Is a two-orbit bond from the top the only thing that keeps the reach bounded?

Epic `CARRIER-20261117-001`. It takes direction #1 of `KEEP-REACH-20261117-001` at the coordinator's go-ahead (2026-11-17 17:58
UTC), within John's request of 16:52 UTC to reopen the line ("let's see if we can uncover anything here"). It serves G17, with G1,
and ran on 2026-11-17. Proof note:
[proof.md](../../proofs/CARRIER-20261117-001A/CARRIER-20261117-001A-P001_exact_pieces/proof.md). Code by the thread. The canonical
K1–K3 test is unchanged. **Refereed** (CARRIER-R1, [report](referee-R1/report.md), commit d2df3f2e3): **confirmed with fixes**, no Block.
Theorem K\*, Lemma P and "C′ is false" hold at every depth; the counts are narrowed to distinct patterns, and the readings past
the stems are scoped by depth (below, "Referee"). **Deeper tests folded in** (LONG_RUNNING `CARRIER-A5`, `CARRIER-A6`, 2026-11-17).

## The question

KEEP-REACH proved that a bond inside two orbits, one at the top level and one s levels down, bounds the reach at every depth when it
survives at every distance (Theorem K). It conjectured the converse, C′: the reach is bounded only when such a two-orbit bond
survives. 25 descriptions never forget, even on the values states take, yet hold no two-orbit bond from the top. They are only 10
distinct patterns (the referee: identical clause sets, because the mutated words act identically). 13 descriptions (5 patterns) have
top pair projections that become products, and 12 (5 patterns) keep an unexposed dependence. Their boundedness was open, and they are where C′ is tested.

## Answer

**No: C′ is false.** All 12 descriptions with an unexposed dependence, 5 distinct patterns, keep the reach bounded at every depth, at 5 members, without a
two-orbit bond from the top. What holds them is a bond inside a slightly larger piece whose projection is still exact:
- **An orbit and a block.** For 2 of them (bace53f8f952-147, -111, two patterns), the bond is inside the top orbit and the block of the lower orbit,
  that is, the lower orbit with its children. At s = 5 it has one member at level 3, one at level 3 + s and two at level 4 + s.
- **A stem.** For the other 10 descriptions, 3 patterns (bace53f8f952-58, and nine mutants of ca1efb37ad88 that are 2 patterns), it is inside the top orbit, the lower orbit's
  two ancestor orbits just below the top, and the lower orbit. This is the **stem** of depth 2 (the advisor's word).

The dependence was unexposed inside the two orbits because one orbit's own constraint stood in the way (KEEP-REACH's Lemma E).
Holding the lower orbit's children, or the orbits between, exposes it. For the 13 mutants of 8db5da810c00 (5 patterns), stems explain the
certified readings and stop there:
- **The readings.** They read exactly 6 at s = 5 and 6 at depth 11, carried by stem bonds.
- **Where stems stop.** Stems of depth 2 have no bond of at most 8 members from s = 7 on. For −73 at s = 7 there is none of any
  size: the referee found 506 of the 512 stem projections to be products and no bond in the other 6. On −73, a stem of depth 3 has
  none of at most 8 at s = 7 either (depth 12).
- **Past the stems, for one pattern.** −73 and −79 are the same pattern: their two depth-12 runs refuted the same 25,518 formulas.
  At depth 12 it has no bond of at most 6 at s = 7 or 8 (certified by LRAT) and bonds of exactly 7, found by the bound-7 run under
  the name −79. So its readings are exactly 6 at s = 5, 6 (depth 11) and exactly 7 at s = 7, 8 (depth 12).
  - Reach need not be monotone in the depth, so these are readings at two depths, not one rising sequence.
  - Both bonds of 7 lie on the lower member's own line of orbits, spread every two or three levels (`TWO-ENDS-20261117-001` reads
    them).
  - At depth 13 the same pattern got no verdict on a bond of at most 6 at s = 7, 8 within 3,600 s per cell.
- **What stays open.** Whether the reach of the 5 patterns grows without bound.

Three results:
- **Theorem K\* (proved).** A bond inside any set of addresses whose projection is exact, holding a distinction at level k and one at
  level k + s, bounds L_N(k, s). Two pieces have exact projections that the every-depth routine computes: an orbit with the block of
  the lower orbit, and a stem with the lower orbit (Lemma P). Theorem K is the case of two orbits.
- **C′ refuted (computed exactly, every depth).** The 12 unexposed descriptions (5 patterns), bounded at 5, have no two-orbit bond from level 3 past
  s = 2 or 4.
- **Exact values.** L₁₁(3, 5) = L₁₁(3, 6) = 6 for all 13 mutants of 8db5da810c00 (5 patterns): no bond of at most 5 (certified by LRAT), and a
  stem bond of 6 at every depth.

| Patterns | Two-orbit bond from level 3 | Orbit-and-block bond | Stem bond (depth 2) | Verdict |
| --- | --- | --- | --- | --- |
| bace53f8f952-147, -111 | to s = 2 | every s: 4 (5 at the bottom tiers) | | bounded at every depth (5) |
| bace53f8f952-58, nine of ca1efb37ad88 (3 patterns) | to s = 4 | to s = 4 | every s ≥ 3: 5 (4 at s = 3 for ca1efb37ad88) | bounded at every depth (5) |
| 13 mutants of 8db5da810c00 (5 patterns) | to s = 4 | to s = 4 | 5, 5, 6, 6 at s = 3..6; none of at most 8 from s = 7 (none at all for −73 at s = 7) | open; exactly 6 at s = 5, 6 (depth 11); exactly 7 at s = 7, 8 for one pattern (−73 = −79, depth 12) |

Two observations came out of this:
- **A mutant can pass its parent's bound and stay bounded.** bace53f8f952-58 reads 5 at every distance from s = 3, past its parent's
  4, yet is bounded at every depth. So −73's passing its parent's 5 at depth 11, noted in KEEP-REACH, says nothing yet about growth.
- **A mutant can sit below its parent.** The nine ca1efb37ad88 mutants (2 patterns) are bounded at 5, below their parent's two-orbit bound of 6
  (the parent's own stems also read 6).

In the program's words: a dependence between two orbits far apart that no bond inside them shows is not lost. A bond appears once
a little more of either strand is held: the lower orbit's children, or the orbits just below the top on the way down. What holds the
top is a bond between two bounded pieces, one at each end, and not between two orbits.

**The repaired conjecture (C\*, the advisor's form).** The reach from level k is bounded at every depth exactly when, for some fixed
d and e, a bond exists at every s and every depth inside two pieces: the orbits within d blocks of the top orbit, and those within e
blocks of the lower orbit. The "if" direction is Theorem K* with Lemma P's argument. The advisor sketched a proof of "only if" by
pumping, not checked: a bond's empty stretches compose finitely many block transfer relations, so a long stretch can be shortened or
lengthened by a repeated factor until only one is long. It is open. For the 13 mutants (5 patterns) it would turn the question into a choice
between a bond in fixed pieces at both ends at every distance and growth.

| # | Conclusion | Kind |
| --- | --- | --- |
| 1 | Theorem K*: a bond in an exactly projected piece bounds the reach; orbit-and-block and stem pieces project exactly (Lemma P) | proved |
| 2 | The 12 descriptions with an unexposed dependence (5 patterns) are bounded at every depth at 5 (2 patterns by orbit-and-block bonds, 3 by stem bonds) | computed exactly at every depth tier (check passed) |
| 3 | Conjecture C′ is false (item 2) | follows |
| 4 | L₁₁(3, 5) = L₁₁(3, 6) = 6 for the 13 mutants of 8db5da810c00 (5 patterns) | computed, certified (threshold search, LRAT) with stems at every depth |
| 5 | Stems of depth 2 give no bond of at most 8 for the 13 from s = 7 on, and none of any size for −73 at s = 7 (the referee); on −73 a stem of depth 3 gives none of at most 8 at s = 7 | computed (depth 3 at depth 12 only) |
| 6 | L₁₂(3, 7) = L₁₂(3, 8) = 7 for one pattern (8db5da810c00-73, which is -79) | computed, certified (threshold search, LRAT, 3,600 s per cell) |
| 7 | Conjecture C* (bounded pieces at both ends) | stated, with the advisor's proof idea |

## Predictions

Frozen in [predictions.md](predictions.md), committed in 7ff989e6b. The threshold run had been launched before the file was written,
with its outputs unread, as disclosed there.
- **P1 holds.** All 12 mutants of 8db5da810c00 besides −73 (4 patterns besides −73's own) have no bond of at most 5 members at s = 6 (and at s = 5).
- **P2 fails, on both counts.** Only 1 of the 12 unexposed descriptions (5 patterns) was decided within 900 s, against at least 8 predicted.
  - The decided one, bace53f8f952-147, has a bond of 4, within its parent's bound.
  - The every-depth computation later showed bonds within the parent's bound at s = 5 and 6 for 11 of the 12 (4 of the 5 patterns); bace53f8f952-58 has 5,
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

## Referee

CARRIER-R1 ([report](referee-R1/report.md)), confirmed with fixes, no Block. Folded in on 2026-11-17 and logged in
`docs/CORRECTIONS.md`:
- **Counts (Narrowing).** The 25 descriptions are 10 distinct patterns. The 12 are 5, the 13 are 5, −73 and −79 are one, and the nine
  ca1efb37ad88 mutants are 2. C′ is refuted by 5 patterns. Upstream, KEEP-REACH's 2,380 small-orbit descriptions are 583 patterns and
  its 39 are 16 (6, 5 and 5), and the census's 786 descriptions are 181 (139 that forget, 42 that never do; the thread's count).
- **Readings past the stems (Narrowing, wording).** "Keeps rising past every carrier found: 3, 4, 5, 5, 6, 6, then at least 7, 7"
  joined two depths. It now gives the readings by depth and pattern.
- **The cap (Not a block).** For −73 at s = 7, "none of at most 8" is "none of any size" (the referee's product test).

The referee also checked, with its own SAT code, 108 of 108 block values and 50 of 50 stem values against the stored tiers, found
carriers of at most 5 at depth 12 for the five patterns at s = 5, 7 and 9, and confirmed the case (ii) descent and the block tiers.

## Checks

Gates (`gate_two_block.py`, `gate_head.py`, outputs `gate_two_block.json`, `gate_head.json`; LONG_RUNNING `CARRIER-A2`, `CARRIER-A4`),
all passed:
- the bond search agrees with brute force on 2,000 and 1,000 random relations;
- the exact projections agree with SAT on 120 orbit-and-block pieces at depth 7 and 120 stem pieces at depth 8;
- the every-depth tiers agree with the computation at each depth on 1,200 and 720 values;
- no bound is below any of 2,021 decided census cells at depth 9 and certified readings, or 40 certified readings for stems.

`verify_bonds.py` (`verify_bonds_N11.json`) takes, for each of the 25 at depth 11 and s = 5, 6, a least bond found on an actual pair
of orbits. It maps the bond to its addresses and confirms by SAT on the whole depth-11 pattern that it is a bond: constrained, with
every subset one smaller free. All 50 are bonds: 4 members for bace53f8f952-147 and -111 (orbit and block), 5 for the other 11 of the 12 (stems), 6 for the 13 mutants (stems); 50 bonds over 25 descriptions, 10 distinct patterns. The proof's `check.py` recomputes five of the stored every-depth results and the table,
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
| This attempt (C′ on the 25) | **Status:** Successful | C′ refuted on 12 descriptions (5 patterns); carriers found; exact values for the other 13 (5 patterns) |
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
  `threshold_deep.py` and its outputs (`threshold_deep_*_c6.json`, `threshold_deep_8db5da810c00-79_N12_c7.json`, and
  `threshold_deep_8db5da810c00-73_N13.json`, written before the bound was added to the name, bound 6).
- The proof family `proofs/CARRIER-20261117-001A/`: `proof.md`, `check.py` and `result.json`.
- Certificates of the threshold runs, packed and verified: `artifacts/CARRIER-20261117-001/certificates/` (`INDEX.md`; 79,393
  certificates in 15 zstd archives, 2.09 GB, from 18.14 GB of gzip files).

**Status.** Proved: Theorem K* and Lemma P. Computed: the carriers of the 25, the exact values of the 13 at s = 5 and 6.

**Least sure.**
- (a) `head_bond.py`'s stem descent in case (ii), where the lower orbit is not below the top orbit: the stem then holds ancestors of
  the lower orbit only. The gate checks it against SAT at depth 8.
- (b) The tiers of the every-depth routine for blocks, whose children read one level shallower, so the tiers run to r₀ + 1.
- (c) That "none of at most 8" for the 13 from s = 7 is a cap, not a proof that no stem bond exists.
