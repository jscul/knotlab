# The cost of reading a direction

Epic `READING-COST-20261024-001`, closed 2026-10-24.

## The question

The owner approved the recommendation of `WALLS-WITH-CHOICES-20261024-001`: "the cost of reading a direction".
- **The question.** How hard is it to decide whether a configuration contradicts along a class, now that walls can have choices?
- **The gate.** Two discriminators:
  - the fewest cover sheets needed by the four honeycomb contacts with a free place on 4 × 4 and 4 × 5;
  - an extremal-wall decider for the directed contacts with choices, tested against the frozen record.
- **Stop if** sheet counts stay below a small constant on every sample and the extremal decider matches the frozen record.

**The evidence:**
- [A polynomial rule for directed walls with choices](../../proofs/READING-COST-20261024-001A/READING-COST-20261024-001A-P001_directed_rule/proof.md)
  (A, proof);
- [Cover sheets for walls with choices](../../experiments/READING-COST-20261024-001B/READING-COST-20261024-001B-E001_sheets/contract.json)
  (B, frozen confirmatory experiment, supported;
  [result](../../artifacts/READING-COST-20261024-001B/READING-COST-20261024-001B-E001_sheets/result.json));
- **scoping (scratch, not evidence):**
  - repeated squares of good directed walls on the torus and on the type-preserving cover;
  - the decider against simple cycles and PySAT on about 19700 classes;
  - the shortening procedure on cover walls of up to 41 squares;
  - misjudgment rates of the honeycomb contacts on 4 × 4 and 4 × 5 before B's contract (disclosed there);
  - the closure of the triangle rules under height maxima.

## Outcome in one paragraph

**Directed walls with choices are easy, and the hard core of the question is now exactly the four honeycomb contacts with a free
place.**
- **The rule (A).** For the six directed contacts (54, 62, 110, 147, 155, 203), reading a class takes polynomial time.
  - **Moves one at a time.** A wall is a monotone path whose moves are allowed one at a time.
  - **A lattice.** The good walls are those lying strictly above, or strictly below, their copy one period of the cylinder away,
    and they are closed under pointwise maximum and minimum.
  - **Short good walls.** Aubry's ordering argument and a split at a repeated square shorten any good wall until it never repeats
    a square of the cover on which the twist is undone. So simple cycles of the wall graph decide these contacts on every torus.
  - **The decider.** For each candidate period, the remaining problem has max-closed constraints, which arc consistency decides.
- **Sheets do not measure difficulty.** Directed contacts sometimes need covers of 3, 5 or 7 sheets on 3 × 3, yet they are
  polynomial. What makes them easy is that every good wall shortens to a simple one, not that covers are small.
- **The honeycomb contacts (B).** Simple cycles keep misjudging them on larger tori.
  - **4 × 4.** 0.51 to 0.57% of their contradiction verdicts are wrong, against 0.229% on 3 × 4.
  - **4 × 5.** 0.32% pooled, and the misjudged classes need covers of up to 10 sheets.
  - **Uneven growth.** The share is not monotone in area: 4 × 5 is below 4 × 4, and two of the four placements sit below the
    3 × 4 share there.
  - **The control.** The directed placements, run as controls, had no misjudgment among 1.85 million verdicts.
- **Why the method stops there.** In height variables (the count of walls crossed), every directed or honeycomb triangle rule is
  closed under maximum for one chirality of the wall and under minimum for the other.
  - Directed walls keep one chirality along a whole family, which is why the lattice survives.
  - Honeycomb walls wind, so one family meets both chiralities and no order is respected.
  - This is scoping, not a theorem.

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Look for a decider for directed walls | Every move is allowed or not by itself, so walls of one left value form a lattice under pointwise maximum and minimum | Proved (A, Lemmas 1 to 3) |
| Ask whether good directed walls avoid repeated squares | On the torus, 4 to 5% of classes with an assignment need a wall that passes a square twice, once on each side of the twist. On the type-preserving cover a simple good wall existed in every sample | Scoping; then proved (A, Theorem 6) |
| Shorten long walls | Aubry's ordered maximum plus a split at a repeated square; it took cover walls of up to 41 squares down to simple ones | Proved (A, Lemmas 4 and 5); checked |
| Decide each period | Max-closed constraints, decided by arc consistency | Proved (A, Theorem 7); 1432 classes in the check, about 19700 in scoping, no disagreement |
| Measure honeycomb misjudgment as the torus grows | Wrong simple-cycle contradiction verdicts: 0.51 to 0.57% on 4 × 4 and 0.32% pooled on 4 × 5, against 0.229% on 3 × 4; none of 1.85 million for the directed controls; misjudged classes need 2 to 10 sheets | B, supported |

## What was measured (B, supported)

| Placement | Torus | Configurations sampled | Simple-cycle contradiction verdicts | Wrong | Share | Sheets of the wrong ones |
| --- | --- | --- | --- | --- | --- | --- |
| 111 | 4 × 4 | 300000 | 8465 | 48 | 0.57% | 2 to 8 |
| 125 | 4 × 4 | 300000 | 8434 | 43 | 0.51% | 2 to 5 |
| 159 | 4 × 4 | 300000 | 8629 | 46 | 0.53% | 2 to 5, once 10 |
| 215 | 4 × 4 | 300000 | 8735 | 49 | 0.56% | 2 to 6 |
| 111 | 4 × 5 | 120000 | 2107 | 4 | 0.19% | 3 to 5 |
| 125 | 4 × 5 | 120000 | 2036 | 12 | 0.59% | 2 to 5 |
| 159 | 4 × 5 | 120000 | 2144 | 8 | 0.37% | 2 to 4 |
| 215 | 4 × 5 | 120000 | 2135 | 3 | 0.14% | 2 and 4 |
| 62, 110, 155, 203 (controls) | 4 × 4 and 4 × 5 | 360000 | 1852000 | 0 | 0 | none |
| each honeycomb placement (baseline, exact) | 3 × 4 | all | 4009750 | 9168 | 0.229% | 3 and 5 in the certified witnesses |

- **The four predictions.** All hold.
  - The controls were never misjudged.
  - Every honeycomb placement is misjudged on both tori.
  - Each one's 4 × 4 share exceeds the 3 × 4 share.
  - The pooled 4 × 5 share exceeds it.
  - No class was undetermined.
- **How strong P4 is.** The pooled 4 × 5 share rests on 27 wrong verdicts. Its standard error is about 0.06 points, so it sits only
  about 1.5 standard errors above the 3 × 4 share. The growth from 3 × 4 to 4 × 4 is clear; the growth to 4 × 5 is weak.
- **The run.** It took 4859 s of its 7200 s budget. After writing every chunk it stopped in its summary step, because absent zero
  counts were read without a default. Recording them as zero, with no change to data or rules, produced the result
  (`run_notes.json`). `check_result.py` reproduced the table and re-verified all 213 wrong verdicts with the frozen engine and
  PySAT.

## What was proved

| Result | Content |
| --- | --- |
| A, Lemma 1 | In a directed placement a wall is a monotone path s(t) whose moves are allowed one at a time. |
| A, Lemmas 2 and 3 | Walls of one left value form a lattice. A wall is good exactly when its copy lies strictly above it or strictly below it, and good walls are closed under maximum, minimum and the type-preserving translations. |
| A, Lemmas 4 and 5 | The ordered maximum of the translates of a good wall is good and comparable with all its translates. Splitting it at a repeated square leaves a good piece. |
| A, Theorem 6 | A class with an assignment has a good wall that is simple on the type-preserving cover; simple cycles decide these placements on every torus. |
| A, Theorem 7 | Reading a class takes time polynomial in L · M and the bit length of the class. |
| A, Corollary 8 | Among the twelve bending placements, only 111, 125, 159 and 215 lack a known polynomial rule. |

## What this changes in `WALLS-WITH-CHOICES-20261024-001`

- **Its ticket B's observation becomes a theorem for all tori.** On 3 × 3 and 3 × 4, simple cycles sufficed for the directed
  contacts; Theorem 6 now proves this on every torus.
- **Its recommended extremal-wall decider exists.** It is Aubry's ordered maximum followed by max-closed constraints.
- **Its proposed sheet test is misdirected.** The recommendation proposed sheet counts as the discriminator for hardness. A shows
  that many sheets coexist with polynomial reading.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| The number of cover sheets measures how hard a class is to read | `WALLS-WITH-CHOICES-20261024-001` recommendation | **False.** Directed contacts need up to 7 sheets on 3 × 3 and are polynomial. The measure that matters is whether good walls shorten to simple ones on the type-preserving cover. |
| Good directed walls can be taken simple on the torus itself | Implicit in "simple cycles suffice" | **Refined.** Some must pass a torus square twice, once on each side of the twist. They are simple on the cover that undoes the twist. |
| Trivial polymorphisms mean no tractable structure | `DIRECTIONAL-RIGIDITY-20261023-001B-P001`, Proposition 1, read as a hardness signal | **Refined.** In the original variables the relations have only trivial polymorphisms. Yet one wall, written as an integer-valued function, satisfies max-closed constraints. The tractability lives in the wall picture and in the restricted instances (one periodic lattice with a twist), not in the relations. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A, Lemma 1 | The allowed places {0, 2} | Elementary; new to the program |
| A, Lemmas 2 and 3 | Non-crossing of monotone paths | Elementary |
| A, Lemma 4 | Aubry's ordering argument for ground states | Classical method |
| A, Lemma 5 | Splitting a periodic orbit at a repeated point | Classical method |
| A, Theorems 6 and 7 | These combined with the tractability of max-closed constraints (Jeavons and Cooper) | New to the program; moderate folklore risk (rotation numbers of monotone circle maps are close) |
| B | Sampled computation with PySAT verification | A recorded computation |

**Did the perspective do real work?** Yes.
- **A change of variables.** The wall picture turns a Boolean problem whose relations have only trivial polymorphisms into a
  lattice problem on one integer-valued wall. That change of variables is where the tractability comes from.
- **An explanation of the frontier.** It also explains which kind resists: honeycomb walls with a free place are not functions of a
  time coordinate, so two of them cannot be combined.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the cost of reading a direction | **Partially successful** | Directed walls with choices are read in polynomial time (a theorem), which settles eight of the twelve bending placements with the four without choices. For the four honeycomb placements with a free place the question is open; their simple-cycle failures persist on larger tori. |
| Local direction — directed walls | Practically exhausted | Every directed placement has a polynomial rule, and simple cycles suffice on every torus. |
| Broader exploration — where reading a direction gets hard | One kind left | Among the bending placements, only walls that turn both ways and have a free place resist. The lattice method fails there because one wall family meets both chiralities. |
| Long-term goal — emergence at the two/three boundary | Capability gained | A three-place contact can make reading a direction easy (directed walls, by a lattice of walls) or possibly hard (winding walls with choices). Missing bridge: a hardness proof, or a polynomial rule, for the honeycomb kind. |
| Next recommendation — honeycomb walls: hard or easy? | **Next step:** Continue with a fresh epic on reading a class for 111, 125, 159 and 215. First a lattice test: do two good walls combine under the height maximum or minimum? A certified pair where both fail closes the lattice route. Then a bounded search for configurations that confine walls to corridors on tori up to 6 × 6, the building block of a hardness reduction. Alternatives: selectivity of these four on every torus (1/3, overlaps with the corridor search); the 3/4 constant (1/3); a note on the wall theorem and the directed rule (1/3). | Settles whether the cost of reading changes exactly where walls wind and branch. |
| Interest — honeycomb walls: hard or easy? | **2/3 — Promising** | Three pieces of evidence: A's method fails at exactly these four; D-P001 of WALLS-WITH-CHOICES-20261024-001 shows good walls must repeat states; B shows the failure persists on larger tori. Main uncertainty: neither a reduction nor an algorithm may close in one epic. |
| Execution — honeycomb walls | Deferred to the owner | Bound: one epic. Stop if the lattice test passes (then pursue a polynomial rule instead), or if no confining configuration appears on tori up to 6 × 6. |
