# Referee report GROWN-END-READING-001-R1 (Codex; the 239-junction stage rebuilt from the proof's text, the table and census redone)

**Verdict: confirmed. The 239-junction stage is real: pair and triple readings, flips and the growing end are kept, and an
equation is not. No Block to this study.**
- **For THREE-RIGID (c71e9be18) it is a Block to R3 at all sizes.** R3 says a pair-table symmetry keeping every three-way reading
  carries the equations. This is a reached meet-once stage where it does not.
- **THREE-RIGID's frozen predictions Q1 and Q2 are untouched.** They concern stages of at most 14 junctions.
- **Three-way transport is untouched by this stage.** This renaming carries every later table. LATER-BOND-READING (referee
  pending) claims a 104-junction stage where it does not.

## The four points asked

1. **The table of readings: reproduced exactly.** The marking is pointwise, and the referee used its own engine, bonds and
   isometry search.

   | Stage | Pair table alone | With flips | With triples | With both |
   | --- | ---: | ---: | ---: | ---: |
   | Minimum meet-once arrangement 1 (7 starting junctions) | 4/8 | 4/8 | 4/4 | 4/4 |
   | Minimum meet-once arrangement 2 (8) | 4/8 | 4/8 | 4/4 | 4/4 |
   | Minimum meet-once arrangement 3 (8) | 4/8 | 4/8 | 4/4 | 4/4 |
   | Repeated-meeting six-junction start | 16/48 | 16/16 | 16/16 | 16/16 |

   - **Triple existence alone** keeps the same 4 and 16 there.
   - **The smallest existence counterexample: confirmed.** It has eight junctions and 15 distinctions, regrown from its six-junction
     start.
     - It has 32 pair maps, all extending to the next table.
     - 16 keep triple existence, and 12 of those change the equations.
     - 4 keep the full triples, and all 4 carry the equations.
     - **The swap 5 ↔ 6** keeps the 105 pair readings and existence on all 455 triples. Its triple sizes T(0, 5, 7) = 6 and
       T(0, 6, 7) = 7 are distances 5 and 6, as stated. With fresh names fixed it keeps the pair table at the next three stages,
       of sizes (10, 19), (14, 27) and (20, 39).
2. **In the census, every renaming keeping the triple sizes keeps the equations.** The referee's own census uses
   GROWN-END-MEET-ONCE-R1's generator, whose start counts match Codex's at every width. It takes widths 3 to 16 (one past
   the study's 15) and stages of at most 11 junctions (the study goes to 16).
   - **The population.** 121,078 admissible starts, 87,648 of them at width 16. The counts at widths 13 to 15 equal Codex's
     2,019, 6,720 and 23,685.
   - **The open stages.** There are 41,862, with 223,598 pointwise pair-table maps. All extend, so there is no failure to 11
     junctions.
   - **The triples.** 100,233 of those maps keep the triple sizes, and **every one carries the equations**.
   - **Triple existence alone** keeps equation-changing maps at 214 stages. The smallest has 8 junctions and 15 distinctions,
     from a six-junction start of width 13, as in the study.
3. **The two-attachment theorem: proved as written.** The referee read it line by line and checked its formulas on random graphs.
   - **Why it holds.** A bond with marks in both parts must separate the attachments, and its two halves decouple, so
     K(X ∪ Y) = L_H(X) + L_Q(Y). With q on a minimum attachment cut of Q, L_H(X) = K(X ∪ {q}) − λ for one or two marks, so it is
     invariant. For marks in H, K(X) = min(B_H(X), L_H(X) + λ), where B_H does not depend on Q. So when λ′ ≤ λ,
     K′(X) = min(K(X), L_H(X) + λ′) is invariant.
   - **Growth.** A complete round confined to Q never raises λ: place the new junctions on the exterior's side of a cut.
   - **The random check.** On 400 random graphs split at two junctions, with every bond enumerated, both formulas hold on all
     10,718 marks in H and all 86,242 mixed marks.
   - **What was lighter.** λ under growth was checked only on 34 simple grafts, where λ stays 1.
4. **The reached stage of 239 junctions and 643 distinctions: confirmed, with the proof's ingredients checked one by one.** The
   referee built it from the proof's text.
   - **The start.** It has 235 junctions and 635 distinctions. It is admissible: connected, every two junctions meet once, every
     junction has three places or more, and every support is a bond.
   - **The study's literal start** is isomorphic to it as a junction graph with places and loose counts.
   - **The growth.** The referee's engine grows it to (239, 643), then (245, 655) and (253, 671). Round 1 adds four one-parent
     junctions with two fresh distinctions each.
   - **The index exchange σ = (2 3), at every one of those stages:**
     - it fixes every distinction of every live junction;
     - it keeps the flip relation (the only pairs with the same holders are loose twins at live junctions);
     - it sends h0's equation, and h1's, outside the equation span;
     - the referee's own solver finds a four-distinction certificate (72 such routes u–w–hub–w–u exist), and the study's literal
       certificate checks on its start.
   - **The core's hubs, h0 and h1:**
     - 105 distinction-disjoint routes join them, by maximum flow, both in the stage and in the bare core;
     - σ is an automorphism of the core with h0 and h1 identified, but not of the split core, and it fixes e.
   - **The small bonds.** For every one of the 15,225 sets of one to three names on six indices, e included, the referee's own
     search (not the study's construction) finds a bond of the identified core below 105, verified with both shores connected.
     The largest it needed were 3, 41 and 61 for one, two and three marks.
   - **What follows.**
     - **The core.** Bonds below 105 are the same in the split and identified cores, so every reading of three or fewer marks
       agrees between them. σ keeps the identified core's readings.
     - **The stage.** The substitution formula (point 3) carries them to every later stage, where λ = 1 throughout.
     - **The limit of the check.** The full tables were not computed; this rests on the proof and these checks, as the study
       says.

## What this means for the three-way study (THREE-RIGID, c71e9be18)

- **R3 on all reached stages is refuted: a Block to R3 as an all-size claim.** The advisor bet 60% on that claim.
  - PROVE-B-R1's census sample found no counterexample in 56,756 symmetries.
  - The counterexample needs a dense closed part, far outside every census.
  - So the route "R3, then Claim B\*, gives transport every round" is closed at all sizes.
- **The frozen hunt stands.** Its predictions Q1 and Q2 concern stages of at most 14 junctions and three named populations. This
  stage has 239 junctions, so it does not touch them.
- **Three-way transport is untouched by this stage: Not a block here.** Transport says that such a renaming carries every later
  table. This renaming carries every later pair and triple table.
- **Not proved here, as the study says:** whether a hidden equation can change a successor pair under every fresh naming once
  three or more junctions attach. LATER-BOND-READING (referee pending, next in this queue) claims it can, at four.
- **THREE-WAY and TRIPLE-GROWN.** The stage and its image under σ have the same pair and triple readings and different allowed
  states, so triples do not separate every reached collision. Both studies claimed this only for the collisions found so far, so
  their statements stand. The general reading narrows.

## Points for the owner (listed, not folded in)

1. **"The image of one junction equation is violated."** Both hub equations, h0's and h1's, leave the span under σ. They are
   complementary in the core, so this is the same obstruction. **Not a block.**
2. **The census bound.** The referee's census covers the study's widths and one more, but only stages of at most 11 junctions.
   The study goes to 16, so that part of claim 2 is lighter here. **Not a block.**

## How the work was split

- **The referee:**
  - read `decision.md`, `proof.md`, `theory.md`, `graft_check.md`, `obstruction.md` and `carry_census.md`, with their artifacts;
  - wrote `job_ger.py`, on its own engine, THREE-WAY-R1's bonds and readings, CREATED-PAIR-R1's isometry search and
    GROWN-END-MEET-ONCE-R1's census generator.
- **Read as data:** the study's stages, start and certificate.
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap: `runs/referee-ger` and `runs/referee-ger-exw`.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
