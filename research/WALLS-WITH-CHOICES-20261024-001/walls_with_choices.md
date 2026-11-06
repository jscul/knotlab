# Walls with choices

Epic `WALLS-WITH-CHOICES-20261024-001`, closed 2026-10-24.

## The question

The owner approved the recommendation of `DIRECTIONAL-RIGIDITY-20261023-001`: "walls with choices".
- **The question.** Is the wall rule exact for the eight bending contacts whose walls have choices? And is every contact whose
  walls can turn selective on every large enough torus?
- **The gate.** The exact 3 × 3 and 3 × 4 records of the eight.
- **Stop if** no rule reproduces them.

**The evidence:**
- [Periodic walls decide every direction](../../proofs/WALLS-WITH-CHOICES-20261024-001A/WALLS-WITH-CHOICES-20261024-001A-P001_wall_theorem/proof.md)
  (A, proof);
- [Simple wall cycles on small tori](../../experiments/WALLS-WITH-CHOICES-20261024-001B/WALLS-WITH-CHOICES-20261024-001B-E001_simple_cycles/contract.json)
  (B, frozen confirmatory experiment, refuted;
  [result](../../artifacts/WALLS-WITH-CHOICES-20261024-001B/WALLS-WITH-CHOICES-20261024-001B-E001_simple_cycles/result.json));
- [Planted walls](../../proofs/WALLS-WITH-CHOICES-20261024-001C/WALLS-WITH-CHOICES-20261024-001C-P001_planted_walls/proof.md)
  (C, proof);
- [Good walls that repeat themselves](../../proofs/WALLS-WITH-CHOICES-20261024-001D/WALLS-WITH-CHOICES-20261024-001D-P001_repeating_walls/proof.md)
  (D, proof, added after B's refutation);
- **scoping (scratch, not evidence):**
  - the quadrant test on the frozen record before Theorem 3 was written;
  - the full 3 × 3 histograms of 155 and 159 by simple cycles before B's contract (disclosed there);
  - design searches for planted configurations, including a failed search for the honeycomb kind with a free place.

## Outcome in one paragraph

**The wall rule holds for every contact with a constant frame, and the gate was met by a theorem, not just a computation.**
- **The theorem (A).** For every three-place tiling contact with a constant frame, an odd class has an assignment on its cylinder
  exactly when some periodic wall crosses that cylinder without meeting its own copies.
  - The converse needed no determinism. A cylinder's assignments form a one-dimensional shift of finite type, so if any exist,
    some cyclic cover has one.
  - One of that cover's walls crosses the loop an odd number of times, and it is the periodic wall required.
- **Simple cycles (B, refuted; D).** Simple cycles of the wall graph decide every configuration on 3 × 3, and on 3 × 4 for eight
  of the twelve contacts. For the four honeycomb contacts with a free place they report contradictions that do not exist. D
  certifies why: there a good wall must sometimes repeat a wall state and wind several times around the torus.
- **Direction structure (A, Theorem 3).** For the six contacts whose walls move only up or left, every first-quadrant odd class
  contradicts together; selectivity lives among the other directions.
- **Selectivity everywhere (C).** A planted staircase makes eight of the twelve bending contacts selective on every torus with
  both sides at least 3.
- **Open.** The four contacts whose walls turn both ways and have a free place are selective on every torus computed, but walls
  are almost unavoidable for them. None of their configurations on 3 × 3 or 3 × 4 contradicts along every odd class, so a planted
  wall has no quiet background, and no uniform construction was found. They are also the contacts where simple cycles fail.

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Ask why a cylinder with an assignment must have a good periodic wall when walls branch | Its assignments form a one-dimensional shift of finite type, so some cyclic cover has one; that cover's walls contain one crossing the loop an odd number of times | Proved (A, Lemma 2 and Theorem 1) |
| Test the quadrant rule on the frozen record | No split among the 363331584 configuration-twists of the six directed contacts that have a first-quadrant odd class; about 14 million splits for the honeycomb ones | Scoping; then proved (A, Theorem 3) |
| Check both directions of the theorem on samples | 292 assignments explained by a crossing wall and rebuilt from it alone; 469 contradictions with no simple cycle passing | A's check |
| Compare simple cycles with the frozen record on every configuration | Equal on all 3 × 3 histograms and on 3 × 4 for eight contacts; for 111, 125, 159 and 215 on 3 × 4 the histograms differ by 5640 configurations per contact | B, refuted |
| Look inside three of the misjudged configurations | Each has an assignment on a cover of 3 or 5 sheets; no simple cycle passes, and the crossing wall of the cover assignment repeats a wall state | Proved (D) |
| Plant a staircase and kill every other wall | Works for the directed kinds (all other walls die) and for the honeycomb kind without a free place (all other walls are loops or a braid that also collides), on every torus | Proved (C) |
| Try the same for the honeycomb kind with a free place | No period-2 filling works; on small tori no configuration contradicts along every odd class | Recorded as open (C, Remark 4) |

## What was measured (B, refuted)

| Torus | Contacts | Configuration-twists compared | Histograms differ by |
| --- | --- | --- | --- |
| 3 × 3 | all twelve | 12582912 | 0 |
| 3 × 4 | 54, 62, 109, 110, 147, 151, 155, 203 | 536870912 | 0 |
| 3 × 4 | 111, 125, 159, 215 | 268435456 | 5640 per contact: 240, 744 and 4656 in three of its four twists, 0 in the fourth |

- **Lower bounds.** B compared histograms of contradiction patterns, so the differences are lower bounds on the number of
  misjudged configurations.
- **One direction only.** By Theorem 1 (⇐), a good simple cycle always yields an assignment. So every misjudgment reports a
  contradiction where the frozen record has an assignment.
- **The same counts for all four.** The counts agree across the four contacts, which the frame flip and the half turn relate.
- **Budget.** The run took 9119 s of its 10800 s budget, and the controls passed.

## What was proved

| Result | Content |
| --- | --- |
| A, Lemma 2 | A cylinder has an assignment exactly when some cyclic cover does. |
| A, Theorem 1 | An odd class has an assignment exactly when some periodic wall crosses its cylinder without meeting its own copies; equivalently, when the wall graph has a closed walk with a transverse class and no overlap in ℤc + ℤe. |
| A, Theorem 3 | For directed walls, every odd class with c₁c₂ > 0 contradicts exactly when the wall graph has no cycle. |
| C, Theorem 2 | Planted staircases make 54, 62, 109, 110, 147, 151, 155 and 203 selective on every L × M torus with L, M ≥ 3. |
| C, Remark 4 | For 111, 125, 159 and 215 no uniform construction; no fully blocked configuration exists on 3 × 3 or 3 × 4. |
| D, Proposition 1 | Three certified configurations of 159 on 3 × 4 have an assignment along an odd class while no simple cycle passes the criterion, so every good closed walk repeats a wall state. Their crossing walls have det(c, e) equal to the number of sheets (3, 3, 5). |

## What this changes in `DIRECTIONAL-RIGIDITY-20261023-001`

- **Its Theorems 3 and 7 and Remark 8 become special cases** of one theorem. Straight walls, rotating walls and walls with
  choices all obey the same rule.
- **Its open question about the eight is answered** for exactness. For selectivity on every torus it is answered for eight of the
  twelve bending contacts.
- **The classification.** On every torus with both sides at least 3:
  - 18 three-place tiling contacts are rigid;
  - 8 are selective;
  - 4 are selective on every torus computed, with the general case open.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| Walls with choices might need a different, transfer-matrix rule | `DIRECTIONAL-RIGIDITY-20261023-001` recommendation | **False.** The same periodic-wall rule holds; only the search for a good closed walk becomes harder. |
| A good wall is a simple cycle of the wall graph | This epic's contract for B | **False for one kind.** For the honeycomb contacts with a free place a good wall can need to repeat a state and wind several times (D). |
| Selectivity can always be built by planting one wall on a quiet background | This epic's plan for C | **False for one kind.** For the honeycomb contacts with a free place, quiet backgrounds do not exist on small tori. |
| Directed and honeycomb bending contacts select in the same way | Implicit in treating "bending walls" as one kind | **Refined.** Directed walls keep the whole first quadrant together; honeycomb walls can split it. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| Lemma 2 (cyclic covers) | Periodic points of one-dimensional shifts of finite type | Classical |
| Theorem 1 (periodic walls) | Decomposing a periodic assignment into domain walls | Standard method; the statement is new to the program; low to moderate folklore risk |
| Theorem 3 (quadrant rule) | A Lipschitz bound for monotone walls | Elementary; new to the program |
| B (simple cycles) | Exhaustive computation | A recorded computation |
| D (repeating walls) | Certified witnesses located by computation | Low novelty: cycles that must avoid their own translates need not be simple, which is generic; the witnesses are new |
| C (planted walls) | Planting one defect line and killing the rest; a state count for the honeycomb kind | Standard method; the constructions are new to the program |

**Did the perspective do real work?** Yes. The wall picture turned a question about infinite cylinders into one about closed walks
on a finite graph, and it showed why one kind resists planting: its walls cannot be silenced.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — walls with choices | **Successful** | The wall rule is proved for every contact with a constant frame, and eight of the twelve bending contacts are proved selective on every torus with both sides at least 3. The simple-cycle shortcut is refuted for the other four. |
| Local direction — selectivity of bending contacts | Practically exhausted except for one kind | What remains is selectivity of 111, 125, 159 and 215 on every large torus. No quiet background exists on small tori, so planting one wall will not do it. |
| Broader exploration — the two/three boundary in direction structure | Sharper picture | Two literals: rigidity from algebra. Three places: one wall rule for every kind, with rigidity exactly for stripes and straight walls. The kinds now differ in how hard their good walls are to find. |
| Long-term goal — emergence at the two/three boundary | Capability gained | Deciding a direction is a search for a closed walk that avoids its own copies. For one kind of three-place contact such walks must sometimes repeat states, so the simplest search fails there. Missing bridge: whether that difference is a complexity boundary. |
| Next recommendation — the cost of reading a direction | **Next step:** Continue with a fresh epic, "the cost of reading a direction". Decide whether reading a class stays polynomial when walls have choices. First measure the fewest sheets needed for the four open contacts on 4 × 4 and 4 × 5, and test an extremal-wall decider for the directed contacts with choices. Alternatives: selectivity of the four open contacts on every large torus (1/3); the 3/4 constant (1/3). | Straight walls and walls without choices already have polynomial rules. A polynomial bound on sheets would put the decision in NP with walls as certificates; growth would point to hardness at exactly the kind where simple cycles fail. |
| Interest — the cost of reading a direction | **2/3 — Promising** | D shows that for the four honeycomb contacts with a free place good walls need not be simple, so the obvious search fails exactly there. Main uncertainty: a bounded cover search may make every kind polynomial, which would end the line with a negative answer. |
| Execution — the cost of reading a direction | Deferred to the owner | Bound: one epic. Gate: sheet counts on samples of 4 × 4 and 4 × 5. Stop if they stay below a small constant and the extremal decider matches the frozen record; then record the polynomial rule and stop. |
