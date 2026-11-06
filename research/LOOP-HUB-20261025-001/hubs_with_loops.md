# Hubs with loops

Epic `LOOP-HUB-20261025-001`, closed 2026-10-25.

## The question

The owner asked to continue the recommendation made at the close of `SOFT-HUB-20261024-001`.
- **What was known.**
  - Native gadgets never make an exact hub.
  - Tree gadgets of the six open knots satisfy the arm inequality F(u)F(ū) ≤ s_u + F(u + eᵢ)F(ū) + F(u)F(ū + eᵢ), so their hub ratio
    is at most 3.
  - With a cycle, the rerouting behind that proof collides.
- **The question.** Does the arm inequality, and so the bound 3, hold for gadgets with loops?
- **Intuitions this epic targets:** the complexity side of the thesis, through whether emergence without reuse can copy a bit to
  three places.

**The evidence:**
- [Searching for violations of the arm inequality on gadgets with loops](../../experiments/LOOP-HUB-20261025-001A/LOOP-HUB-20261025-001A-E001_arm_violations/contract.json)
  (A, frozen-contract experiment, supported;
  [result](../../artifacts/LOOP-HUB-20261025-001A/LOOP-HUB-20261025-001A-E001_arm_violations/result.json));
- [What a proof of the arm inequality must contain](../../proofs/LOOP-HUB-20261025-001B/LOOP-HUB-20261025-001B-P001_what_a_proof_must_contain/proof.md)
  (B, proof);
- [bounded scan](scan.md);
- **scoping (scratch, not evidence; disclosed in A's contract):**
  - adversarial annealing up to 20 knots;
  - chains of double edges;
  - the split bounds;
  - the failures of the strengthenings;
  - matchings and switch tests;
  - the minor inequality.

## Outcome in one paragraph

**The inequality survived every attack, and no local proof of it exists.**
- **No counterexample (A).** Adversarial search maximized the ratio of the inequality's two sides over 384 runs from 4 to 40 knots, over
  chains of double edges and over fully looped cores. It never exceeded 1, and it reached exactly 1 in every run up to 16 knots: the
  inequality is sharp.
- **Both halves hold (A).** On 371,328 linked pairs the split by the empty side at the first branching knot always obeyed both halves.
- **What a proof must contain (B).**
  - Rerouting is one-to-one for each fixed pattern of differences, so a proof would follow if different patterns never shared an image.
    They do share one when the gadget has loops.
  - Explicit gadgets of two or three knots satisfy the inequality but break every natural local strengthening. So a proof has to be
    global: it must sometimes change the partner solution, move pairs across image patterns, use more than one-sided path flips, and
    count the pairs that agree at the rerouted terminal.
- **The no-copy reading (B).** Written symmetrically, the inequality says that a terminal cannot copy the joint value of the other two
  without leaving mixed values on the cross patterns, and co-independence never lets those two be locked together.

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Adversarial annealing, structured families | No violation; equality common | Supported (A) |
| Split linked pairs by the empty side | Both halves hold on every small gadget | Supported (A) |
| Per partner, per image pattern, minor | Each fails on a small fraction of cases | Reported (A); witnesses proved (B) |
| Matchings by one-sided path flips | Fail on a three-knot gadget although targets suffice | Proved (B) |
| One difference pattern at a time | Injective; trees give injective patterns | Proved (B, Lemma 1) |
| Symmetric form | \|minor\| ≤ agree + cross; G > 0 always | Proved (B, Proposition 2) |

## What was proved

| Result | Content |
| --- | --- |
| B, Lemma 1 | For a linked difference pattern d, rerouting maps its compatible configurations injectively into those of d ⊕ arm(d); trees map patterns injectively, which gives a second proof of the tree theorem. |
| B, Proposition 2 | For axes u and u + eᵢ together, the arm inequality ⟺ \|minor\| ≤ agree + cross ⟺ 2F(u)F(ū) ≤ G(A)G(Ā) + split_j + split_k; G > 0 on every pattern. |
| B, Proposition 3 and Corollary 4 | Witnesses of two or three knots break the per-partner, per-image-pattern, path-flip and minor strengthenings, so any proof for gadgets with loops must be global. |

**What was supported (A).** All three predictions held:
- no violation in annealing (best ratio exactly 1);
- no violation in the structured families;
- the split bounds held on all 21,660 small axis-terminal cases.

## What this changes

- **The conjecture is now well supported, and its proof is harder than expected.** Two epics of evidence put the hub ratio of every
  native gadget of the open knots at most 3, and in practice at most 65/53. The remaining gap is a global counting statement.
- **The "no fan-out" picture of native emergence is sharper.**
  - A native network can carry a bit along a wire.
  - It cannot copy that bit onto three terminals exactly (proved).
  - On trees it cannot even approximately (proved), and with loops it apparently cannot either (conjecture).
- **For the thesis.** Hardness on the three-literal side needs reuse as well as emergence. The evidence is now strong for every native
  gadget, not only trees.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| The tree proof extends to loops with a smarter routing rule | `SOFT-HUB-20261024-001C` (Proposition 3 left it open) | **False for local rules.** Per-partner and per-pattern injections cannot exist. |
| Collisions of the reroute signal violations | Scoping in `SOFT-HUB-20261024-001` | **False.** Collisions occur only with slack; the inequality survives them. |
| The agreeing terms are slack | The determinant view | **False.** Without them the bound fails, even on a two-knot tree. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A | Adversarial search, exact pair counts | A recorded computation |
| B, Lemma 1 | The symmetric difference of two solutions, one-sided version | Elementary; new to the program |
| B, Proposition 2 | Algebra of the two-by-four table; co-independence | Elementary |
| B, Proposition 3 | Explicit small gadgets | Computation, exact |

**Did the perspective do real work?** Little this time.
- **What it supplied.** The question is the program's: can emergence imitate reuse? The defect picture (0, 1 or 3 defects) made the
  difference-pattern lemma short.
- **What the epic is.** A careful mapping of evidence and proof requirements, not a new mechanism.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: the arm inequality with loops | **Status:** Inconclusive | No violation under adversarial search (sharp); no proof; every local proof route ruled out. |
| Local direction: injective rerouting | Retire | Corollary 4 rules out per-partner, per-pattern and path-flip versions. |
| Broader exploration: hub imitation | Practically exhausted for the program's purposes | Exact: impossible (proved). Trees: bounded (proved). Loops: bounded in all evidence. A proof needs a global method, a technical task with modest conceptual payoff. |
| Long-term goal: the complexity side of the thesis | Capability gained | Hardness needs reuse: proved for deciding, for exact hubs and for trees, and well supported in general. |
| Next recommendation: twists in three dimensions | **Next step:** Full pivot to the space intuition | See below. |
| Interest: that recommendation | **2/3: promising** | It is the one place where the complexity and space lines meet: the open knots are Fibonacci with a twist, and Fibonacci in three dimensions needed a negative weight. Main uncertainty: native counts may still see only mod-2 cohomology. |
| Execution | Deferred to the owner | Bound: one epic; stop if no twisted native law survives the 2–3 and 1–4 moves beyond the parity class. |

**The pivot in more detail.**
- **The question.** Can a native law built from the twisted Fibonacci knots give a count on triangulated 3-manifolds that is invariant
  under Pachner moves and sees more than H¹(M; Z₂)?
- **Why now.**
  - `HUB-DIMENSION-20261024-001` found that symmetric edge-bit laws see only mod-2 cohomology, and that the Fibonacci rule needs a
    negative weight.
  - The twist is a native relation that becomes a signed reflection in the Fibonacci basis (`NATIVE-APPROX-20261024-001B`).
- **The first discriminator.** An exhaustive test of 2–3 and 1–4 invariance for laws that place the six open knots, with their slot
  orders, on the faces of tetrahedra. This extends the earlier census of 32,768 symmetric laws to twisted ones.
- **Stop if** every surviving twisted law reduces to the trivial or parity class.

**Alternatives:**
- **A computer search for a closed family of inequalities proving the arm bound (1/3).** Technical; it would finish the hub story.
- **Markov-chain experiments for approximate counting of the six (1/3).** Evidence only.
- **A note on native complexity (1/3).** Deciding, refuting, exact and approximate counting, and hubs. Magnitude moderate, folklore
  risk medium to high.
