# Why does the growth never reach the static pairs? Pre-registration

Epic `PARENT-RULE-20261119-001` (`MEET-ONCE-20261119-001#1`, the coordinator's go-ahead; A97, G1), 2026-11-19. Frozen before
the runs. The canonical K1–K3 test is unchanged.

## The question

UNIQUE-TABLE's six static pairs meet once and have other states with the same bond-distance table, but the law never builds their
rivals. MEET-ONCE found no reached meet-once collision with other states to 40 junctions (50 by its referee). Is there a property
that every reached stage has and the rivals lack? Do complete rounds keep it at every size? And is it, together with meeting
once, enough for the table to carry the allowed states? Only the last would turn "to 40 junctions" into a statement for every
size.

## Prior work in the program

`python3 -B scripts/track.py objects "property of reached stages that static rivals lack parent rule backed pairs table determines states" --until 2026-11-19 --exclude PARENT-RULE-20261119-001`

- `THREE-WAY-20261119-001`: readings that separate the same rivals (a relative).
- `UNIQUE-TABLE-20261119-001`: the six static pairs and their 11 rivals (the population this explains).
- `CENSUS-READ-20261118-001`: the census stages (the population checked).

Also `FRESH-COUNT-20261118-001` and `FIRST-KNOT-20261118-001` (the joining rule), and `MEET-ONCE-20261119-001` and
`GROWN-PAIR-20261119-001` (reached collisions). From the literature: Whitney's 2-isomorphism theorem (same states exactly when
the cycle matroids agree), and his edge-isomorphism theorem, whose small exceptions include the four-junction arrangement in which
every two junctions meet (the literature's K4).

## Words

A junction is **live** when it holds a loose distinction; two junctions **meet** when they share a distinction.
- **Backed pairs (P1):** for every live junction, any two junctions it meets also both meet a junction other than it.
- **P1⁺:** P1 with that third junction holding no loose distinction.
- **Live junctions never meet (P2).**
- **Peel:** remove the live junctions. The **peel depth** is the number of successive peels at which P1⁺ and P2 hold.
- **Strata:**
  - **closed:** no live junction;
  - **pendant-only:** every live junction meets at most one junction;
  - **backed:** some live junction meets two or more.
- **Control Q:** backed pairs required of the closed junctions instead of the live ones.

The advisor chose "backed pairs" and "live junctions never meet" over my "parent rule": statically there are no parents.

## Design-stage observations (disclosed; seen before the freeze)

- All six truths satisfy P1 and P2. All 11 rivals violate P1, with 5 to 8 violating triples each, and 10 of 11 violate P2. This
  is what suggested the property, so it is not counted as fresh evidence.
- A smoke test on 20 census starts showed two closed stages whose table has an isomorphism onto itself that does not carry the
  equation space; one is the four-junction arrangement in which every two junctions meet. Rigidity (R1) is therefore predicted
  for open stages only.
- Small tests showed that the bond tables equal `exact_table_v2`'s on 94 census stages, and that the arrangements of at most 5
  junctions give 143 collision groups, all with the same states.

## Method

**Ticket A (proof).** [proof.md](../../proofs/PARENT-RULE-20261119-001A/PARENT-RULE-20261119-001A-P001_backed/proof.md):
- Theorem 1: P1⁺ and P2 hold at every stage of round ≥ 1 from a connected start.
- Theorem 2: peeling an open stage gives the previous stage exactly, so its peel depth is at least its round.
- Theorem 3: the next open stage never lengthens a bond distance between the previous stage's distinctions.

**Ticket B (`experiments/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent/`).**
- **Part C (`census_job.py`),** on every census start regrown, rounds 0 to 8, every stage of at most 40 junctions:
  - the violations of P1, P1⁺ and P2;
  - whether peeling gives the previous stage;
  - whether the peel depth is at least the round;
  - rigidity: every isomorphism of the table onto itself, on twin classes, cap 2,000, tested by rank for whether it carries the
    equation space. This uses full tables up to 14 junctions, and tables read to distance 8 for the meet-once stages of 15 to 40;
  - Theorem 3's comparison, on open stages of at most 14 junctions.
- **Part S (`static_job.py`, `static_pairs.py`),** on every legal meet-once arrangement of 2 to 7 junctions: every connected
  simple graph of the networkx atlas, and every loose count per junction up to the graph's automorphisms, at most 3 (at most 2 at
  7 junctions). That is 503,039 arrangements. For each:
  - its exact table by bonds;
  - table groups by isomorphism (a hash of sorted rows, then VF2);
  - state groups by a junction-graph isomorphism, else every table isomorphism on twin classes checked by rank (cap 5,000,
    undecided past it);
  - for every other-states pair, the properties of both sides.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| C1 | Every census stage of round ≥ 1 to 40 junctions: no violation of P1⁺ or P2; peeling gives the previous stage; open stages have peel depth ≥ round (Theorems 1, 2) | any violation |
| C2 | No previous-stage pair is farther in the next open stage (Theorem 3), on open stages ≤ 14 junctions | any |
| R1 | Every open meet-once reached stage of ≤ 14 junctions is rigid: every table isomorphism onto itself carries the equation space (my bet 70%) | one is not |
| S0 | Control: other-states collisions exist among the 503,039, the pop-0308 pair (7 junctions) among them | none, or the pair is missing |
| S1a | No other-states pair with both sides backed (P1) in the backed stratum (my bet 80%; the advisor 85%, "mostly for lack of room") | one exists |
| S1b | No other-states pair with both sides of peel depth ≥ 1 (P1⁺ and P2; my bet 60%) | one exists |
| S1c | No other-states pair with both sides of peel depth ≥ 2 (my bet 80%; the advisor 85%) | one exists |

Reported without a prediction:
- the closed and pendant-only strata;
- the control Q;
- the population counts (P1, P1 backed, depth ≥ 1, ≥ 2, Q; tables with a P1 member);
- rigidity of two-sharing and closed stages, and on tables read to 8 at 15 to 40 junctions;
- Theorem 3's share of equal and shorter distances.

If S1a to S1c hold, they are evidence at up to 7 junctions only: the advisor expects the first non-vacuous collisions at 8 to 10.

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)).
- **Taken:**
  - the third junction must differ from the live one;
  - the stall clause and connected starts stated in the lemma;
  - P1⁺, live junctions never meeting one round back, and peeling, recorded (Theorems 1 and 2);
  - strata;
  - a ladder frozen in advance (S1a to S1c), not a rescue after the fact;
  - a complete states test (every table isomorphism on twin classes, by rank);
  - population counts and a matched control (Q);
  - the contamination disclosed;
  - its rigidity test (R1) and its check of how peeling changes distances (C2, Theorem 3);
  - its names.
- **Not taken now:** building the backed side by construction to 9 or 10 junctions. That is recorded as the first follow-up if
  S1 holds here.
- **Its bets:** S1 as a whole at ≤ 7 about 55%, the backed stratum about 85%, at 9 to 10 junctions about 60%, the peeled form
  about 85%.

## Runs and stop rule

`census_job.py` (265 shards) and `static_job.py` (113 cases), each on the shared runner with 8 workers and the 16G cap. Then
`static_pairs.py`. One run each; then stop.
