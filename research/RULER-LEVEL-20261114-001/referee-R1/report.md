# Referee report RULER-LEVEL-R1 (Codex-assisted, fresh code)

**Verdict: Confirmed with fixes.**

**What holds.**
- **Theorems A and A\*\***, as displayed in `proof.md`, are sound.
- **The census table and weights** reproduce exactly with a fresh builder.

**The Block.** The overview's "there is no bond otherwise" is false. An acyclic pattern whose levels are joined only by a longer path
has a larger finite bond. The complete statement is L = (least knot-path length) + 2.

**What else needs fixing.** These are Narrowings:
- the coverage wording;
- the sixth breaking case, whose description is not in the evidence;
- the wording on cycles.

**How the work was split.** The background referee thread owns the verdict.
- **The referee.**
  - Read T1 and both proofs.
  - Found the statement's gap (a path with no descending chain) before Codex.
  - Checked that the advisor's acyclicity argument is complete.
  - Matched Codex's breaking cases against CYCLE-RULER's.
- **Codex.** The Codex command-line tool, at the owner's choice of model and effort, ran for about 15 minutes with fresh code and
  LEVEL-REACH-R1's fresh builder and search. It did not open the study's code.
- **Advisor.** The advisor model was not consulted.
- **The objects gate.** There is no pre-registration: this is a proof epic.

## 1. Theorem A** and T1 (owner's point a)

**T1 applies.** Not a block.
- **Its scope.** It covers finite 3-uniform Berge-acyclic patterns, including several components and addresses in only one knot,
  with the least bond taken over all sets.
- **The builder.** It drops repeated images and deduplicates knots, which gives exactly T1's object.

**The distance is right.** Not a block.
- **Why.** T1 counts the knots on the incidence path. Traversing a knot changes address length by at most one, so s ≤ d, and a
  descending chain has exactly s knots, so it reaches d = s.
- **The +2.** It is the bond's size.

**The statement's gap.**
- **What it covers.** `proof.md`'s two cases, a descending chain and no path, are correct but not complete.
- **What follows from T1.** In a finite acyclic pattern, L_k(s) = D_k(s) + 2, where D is the least knot-path length between the two
  levels. It equals s + 2 if and only if a descending chain exists.
- **The counterexample to the overview.** Codex's example at N = 3 has knots {0, 00, 01}, {00, 10, 11} and {10, 000, 001}. It has a
  3-knot path but no 2-knot descending chain, and its exact reach is 5, with bond {0, 01, 11, 000, 001}.
- **The census.** It has no such acyclic case.

**The fresh tests.** No violation of T1 or of the complete formula was found.
- **Exhaustive.** Every incidence forest on 7 labelled distinctions: 1,156 patterns, 24,276 pairs and 5,530 bonds.
- **Random.** 120 forests on 5 to 13 distinctions, with within-level knots, paths that rise before descending, and several
  components. The earlier referee's exact search agreed on all 423 level queries.

**Block** on the overview's "no bond otherwise" (`ruler_level.md`, Answer). **Narrowing:** state the complete formula in Theorem
A\*\*.

## 2. Theorem A (owner's point b)

**Every step holds.**

| Step | Why |
| --- | --- |
| The three addresses are distinct | by level and last letter |
| Distinct w give distinct knots | through the sole upper member g(w) |
| Each address is a lower member once and an upper member once | g permutes each level; the parent of v0 is g(h₁⁻¹(v)) |
| No two knots share two distinctions | knots on the same level pair are disjoint in their upper and lower members; consecutive pairs share at most one address |
| No cycle | the deepest address on a cycle has only its parent knot reaching it |
| Connected, with descending chains | every address ascends to the root |
| The words are automorphisms that preserve length | they come from an invertible Mealy automaton |

**The fresh tests.**
- **Structure.** 120 descriptions at 7 depths: all 840 patterns are incidence forests with the stated structure.
- **Exact search.** 24 of 24 values agree at N = 6 and 7, including descriptions whose knot parents are not word prefixes.

**Not a block.**

## 3. The census (owner's point c)

**The rebuild.** The fresh builder matches the recorded knot counts on all 1,288 descriptions and reproduces proof.md's table exactly.

| Outcome | Acyclic, a chain at every s | Acyclic, no chain at some s | Cyclic |
| --- | --- | --- | --- |
| chained | 299 | 0 | 158 |
| no bond | 0 | 170 | 18 |
| no join | 0 | 77 | 106 |
| direct | 0 | 0 | 100 |
| other | 0 | 0 | 73 |
| undecided + dead | 0 | 0 | 264 + 23 |

All 546 acyclic descriptions agree with D + 2, or with no path. The weights are 605 ruler, 394 acyclic, and 221 for the 117
descriptions of Theorem A's form.

**"Two thirds".** It is fair for the depth-9 readings, but not for every depth.

| Coverage of the rulers | By description | By weight |
| --- | --- | --- |
| A\*\* on the depth-9 pattern | 299/457 = 65.4% | 394/605 = 65.1% |
| Theorem A's form (every depth) | 117/457 = 25.6% | 221/605 = 36.5% |

- **The form is syntactic.** Description `2d27fb6fcfa3…` has two nominal placements, one of which is discarded at every depth, so it
  is the bare tree at every depth without passing the literal test.

**Narrowing:** "two thirds of the census's rulers are explained by a theorem, at depth 9; a quarter (a third by weight) at every
depth".

**"Every direct, other, undecided and dead description is cyclic"** is verified for this census.
- **Dead.** The leaf lemma rules out dead forests universally.
- **The others.** Given the measured path and chain facts, A\*\* fixes these forests' outcomes, so the agreement is a check of the
  census, not evidence for the theorem.

**Narrowing.**

## 4. The six breaking cases (Codex)

**Five reproduce.** The log lists six, but its JSON serialises only five keys. Those five rebuild with two builders, and their exact
profiles all agree: [3,3,4], [3,4,4], [3,3,3], [2,2,2] and [3,4,4], 15 values in all.
- **Siblings.** Each has a within-level knot holding two tree siblings, meaning the two lower members of one tree knot, not words
  with a common prefix.
- **Certificates.** The refutation proofs and witness states are checked.

**The sixth cannot be reproduced.** It is the second [3,3,4], logged at row 64, and its description is not in the evidence.

**Narrowing:** "5 reproduced, 1 logged only".

## 5. Known mathematics

**Unverified, from memory.**
- **Standard.** Leaf elimination and the localisation to paths are standard in tree-structured constraint satisfaction.
- **T1's exact d + 2.** The minimum is taken over every set of members, including ones off the path, and the bond must be minimal.
  That is stronger than tree CSPs being easy. RANDOM-FATES's referee did not find it stated.
- **What each adds.** A\*\* applies T1 with the level bound, and A is an elementary structural fact.
- **A caution.** Prime implicates of "acyclic CNFs" are not the same notion: NAE's two clauses share all three variables, and a bond
  needs every proper subset to be full.

The note's own "known-with-delta, nothing new beyond the application" is accurate. **Not a block.**

## 6. Wording

1. **"Exactly where the knots form no cycle"** (Answer). Write "a sufficient condition: no cycle of knots and a descending chain".
   The 158 cyclic rulers show that acyclicity is not necessary. **Narrowing.**
2. **"Cycles break the ruler both ways" and "halve its rate".** Write "within-level knots can shorten the finite profile". Every
   recovered failure shortens it; none lengthens it, and three levels show no rate. **Narrowing.**
3. **"Proved for every acyclic pattern"** (the position table). Write the complete formula, L = D + 2. **Narrowing.**

## Fixes for the thread

1. **Remove "no bond otherwise"** from the Answer, and state L = D + 2 in Theorem A\*\*. **Block** (on the overview sentence; no
   census number changes).
2. **Coverage.** Give it at depth 9 and at every depth, and call Theorem A's form syntactic. **Narrowing.**
3. **The breaking cases.** Five are reproduced and one is logged only; serialise its key if it is available. **Narrowing.**
4. **The wording in section 6.** **Narrowing.**

## Files

`codex/`: `codex_report.md`, `recompute_census.py`, `census.json`, `forest_audit/`, `tree_audit/`, `breaking_audit/` (the five
cases, with DRUP proofs and witness checks) and `audit_manifest.json`.
