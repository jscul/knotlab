# Referee report COPY-READ-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **The proofs hold.** A1 is MID-RULE's E1 applied to absorbing fills, and the referee confirmed E1 independently (MID-RULE-R1). A2
  is KEEP-READ's R2.
- **The referee's own SEEDK runs reproduce the counts.** They used other seeds and the referee's own knot-local engine, with no state
  limit.
  - 528 absorbing fills among 1,762,024 crossing-making fills after the switch: 0.030%, against the study's 0.032%.
  - The median n is 10.
- **No exact reading at tier 0 or the closure tier, as claimed.** The clean-witness fraction is 0, pooled and held out, with exact
  classes.
- **But the answer's "no sign" is too strong.**
  - Every absorbing fill falls in one closure class, which holds only 1.8% of the crossing-making fills: a 57-fold lift.
  - So the betweenness among the move's distinctions gives a local necessary condition for absorbing, with recall 1 and precision
    1.7%, though not an exact rule. **Narrowing (wording),** and a lead for the study's direction 2.
- **The owner's process questions.**
  - **P1 and P2 are not predictions.** The disclosed exploration settled them, so they are replications at scale. Only P3 and P4 were
    open.
  - **The headline is scoped** to the move's own knots and the closure tier, with one step out called untestable, as the referee
    asked for KEEP-READ.
  - **The advisor lapse is disclosed.** Not a block.

## What holds

- **A1.** An absorbing fill gives an uncrossed split crossers, which is a new crossing. By E1, each of its certificates has two
  different end knots. Every absorbing move the referee met has exactly two end knots and one middle knot.
- **A2.** It is R2's bound with "absorbing" and "refused" for "keeps" and "raises". The held-out version that the KEEP-READ referee
  asked for is implemented: classes learnt on even start indices, scored on odd ones, with the share of test extensions whose class
  was seen.
- **The referee's runs** (`referee_copy.py`; SEEDK from every bracketing of 5, 6, 7 and every third of 8, to n = 30; exact
  canonical classes):

  | Reading | Referee | Study |
  | --- | --- | --- |
  | Crossing-making fills after the switch; absorbing; share | 1,762,024; 528; 0.030% | 1,787,986; 566; 0.032% |
  | Median n of an absorbing fill | 10 | 10 |
  | Tier 0: classes of crossing-making moves; with absorbing ones | 6; 1 | not reported |
  | Tier 0: clean-witness pooled; held-out seen; held-out clean | 0; 1.0; 0 | 0; 1.0; 0 |
  | Closure: classes; with absorbing ones | 97; **1** | not reported |
  | Closure: clean-witness pooled; held-out seen; held-out clean | 0; 1.0; 0 | 0; 1.0; 0 |

## 1. The closure tier carries a strong sign (Narrowing, wording)

- **Where the absorbing fills sit.**
  - **At tier 0,** all 528 absorbing fills share one class of the move's knots (one middle and two end knots), with 632,862 refused
    fills. That is a lift of 2.8: the class holds 36% of the crossing-making fills.
  - **At the closure tier,** all 528 share one class: the same knots, plus a fixed pattern of betweenness among the five old
    distinctions. Only 30,490 refused fills share it, so the class holds 1.76% of the crossing-making fills, a lift of 57.
- **An example** (`referee_copy_examples.json`): the knots B(1, r, 4), B(2, 1, r) and B(3, 5, r), with nine implied betweennesses
  among 1 to 5. Three runs, three bracketings, the same class.
- **What it means.**
  - A local reading cannot accept absorbing fills exactly: the clean-witness fraction is 0, and the held-out score is 0.
  - But "lies in this closure class" is a necessary condition at these sizes: every absorbing fill met satisfies it, and 98% of
    the refused crossing-making fills do not.
  - So the note's "the move's own knots carry no sign of absorbing" holds for an exact sign only. The advisor's base-rate caveat
    is right, and this is the measurement it asked for.
- **Fair wording.** "No reading of the move's own knots, or of the betweenness among its distinctions, accepts exactly SEED's
  absorbing fills. But every absorbing fill met has one closure picture, shared by under 2% of the crossing-making fills: a local
  necessary condition, not a sufficient one."
- **For the next step.** The study's direction 2 (the advisor's copy predicate) can start from this class. Ask what separates
  absorbing from refused fills inside it, at tier 1 or by the copied split's place.

## 2. P1 and P2, and the headline (the owner's questions)

- **P1 and P2 are not predictions.** The exploration disclosed before the freeze read six runs and saw 20 absorbing against 21,609
  refused moves, all in mixed tier-0 and closure classes. P1 (share below 1%) and P2 (clean witness 0) restate that.
  - They are fair replications at scale, but the score "4 of 4 held" should read "P3 and P4 held; P1 and P2 replicated the
    exploration".
  - The note says the exploration settled them. The predictions table should say so too.
- **P3 and P4** were open, and held: held-out seen 4% at tier 1 (because classes are unique there), and median n 10.
- **The headline's scope** is right in form. It names tier 0 and the closure tier, and calls tier 1 untestable here: the ball
  covers 96% and held-out classes go mostly unseen. Only its "no sign" needs §1's correction.
- **The advisor lapse.** The advisor was consulted after the freeze, before the read-out. The note discloses it, and the caveats it
  added are in the limitations. Not a block.

## Fixes for the thread (listed for the owner, not folded in)

1. **"No sign" at the closure tier.** Replace it with §1's wording. Every absorbing fill met shares one closure class (528 of 528
   here), covering under 2% of crossing-making fills, a 57-fold lift: a local necessary condition. Report the lift per class, with
   the held-out score. **Narrowing (wording).**
2. **P1 and P2.** Mark them as replications of the disclosed exploration, not predictions. **Not a block.**
3. **The direction.** Start direction 2 from the closure class. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, proofs A1 and A2, `copylib.py` and `readout.py`, and the read-out;
  - wrote `referee_copy.py`: its own SEEDK runs on its MID-RULE-R1 knot-local engine, an exact canonical form for tier-0 and closure
    pictures, the pooled and held-out clean-witness fractions, and the per-class lift.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_copy.py`.**
- **`referee_copy.json`** and **`referee_copy_examples.json`** (three absorbing fills with their pictures).

Reproduce, from `research/COPY-READ-20261118-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_copy.py > referee_copy.json
```
