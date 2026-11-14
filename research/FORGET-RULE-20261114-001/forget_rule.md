# What makes every way down forget

Epic `FORGET-RULE-20261114-001` (`CENSUS-FORGET-20261114-001#1`; G17, with G1), 2026-11-14, at the coordinator's go-ahead. The
thread's work, reusing FREE-TARGET's per-call relations, with the advisor consulted on the proof. Pre-registered in two stages: the
held-out split (e75be4409), and the rules with their held-out predictions (4a37c96d4). The held-out half was then read once. The
canonical K1–K3 test is unchanged. **Referee pending.** The several-definition part rests on the gap argument's several-definition
premise, which is under FREE-TARGET's referee.

## Words

- **Forgetting**: some r with every product of r per-call port relations rectangular (FREE-TARGET).
- **Identity cycle**: a cycle of SELF calls along which a copy's port is handed on unchanged as a port of the next copy. The edges
  are j → k when a call's k-th argument is the copy's port j.
- **Peeling**: removing a knot, or a side relation full on every two coordinates, that holds a distinction occurring nowhere else.
- **Chains** and **non-chains** are as in `CENSUS-FORGET-20261114-001`.

## The question

Which syntactic feature of a family's SELF calls and knots makes every way down forget? It should be a proved implication, with its
coverage measured, rather than a fitted description.

## The question in standard terms

For iterated hyperedge-replacement NAE families, conditions on the call structure under which every long product of the per-call
port relations is a product relation (rectangular). Measured on 12,772 census families, split in half by key hash.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **An identity cycle prevents forgetting (rule N).** Along the cycle a port value passes unchanged, so the product projects onto two ports as equality. Every relation is complement-closed, so both values occur, and such an equality is never a product. No exception among 12,772 families. | proved | H1 held (0 of 6,384 held out) |
| 2 | **Separation after exact peeling implies forgetting (rule A).** A finite automaton decides it. It starts from a generic copy and tracks, layer by layer, which ports are connected to the stretch's top through the peeled knots and side relations, and which are untouched from above. Peeling is exact for NAE, and a disconnected system has a product solution set, so if no connected path survives r levels on any word, every r-product is rectangular. On the held-out half it certifies 1,051 families, all of which forget, and every exact r is within its bound. | proved | H2 held |
| 3 | **Rule A covers about three in eight.** It certifies 36.7% of held-out forgetting families (training 37.1%). By stratum: chains 40.8% (one definition) and 39.3% (several); non-chains 23.8% and 29.5%. All within 8 points of training. The rest forget through slack that peeling does not see: a knot can link a port to an argument without making it depend on it. | computed | H3 held |
| 4 | **In the census, no identity cycle nearly means forgetting.** Among held-out families without an identity cycle, all 2,096 chains forget, and 765 of 817 non-chains (93.6%; training 94.1%). The exceptions carry the correlation through knots: positive NAE can force two distinctions equal or opposite (the advisor's x ≠ y gadget, `gadget_control.py`). Such a gadget makes a chain without an identity cycle that does not forget, so the chain result is a fact about this census, not a theorem. | computed | H4 held |
| 5 | **The first connectivity rule was false.** Requiring only downward port-to-argument connections to be acyclic certified 705 of 705 training families. It is false in general: a path can go down, sideways through the child's knots, and back up, as the gadget shows. Rule A replaces it. | proved (counterexample) | — |

## Answer

Every way down forgets unless some way hands a value down unchanged, or carries it through knots that force equality. The first
half is a theorem: a port handed to itself around a cycle of calls blocks forgetting. A proved sufficient condition covers more than
a third of the families that forget: the top separates from the depth-r copy once the always-satisfiable knots are peeled away. In
this census the simple test is nearly exact. A family without such a cycle forgets in every chain and in 94% of the rest.

## Reading

**Interpretation, not a theorem.**
- *Scope, after FREE-TARGET's referee:* rules N and A are about forgetting, the rectangularity of products, and are unaffected.
  Reading forgetting as growth of the free bond holds for targets that are copies of the ray definition S. The bound is shifted by one
  level for wrapper mains, and does not reach copies of another recursive definition with its own distinctions.
- **What carries depth's memory.** A nested pattern keeps a trace of its top at depth only through identity: a distinction passed
  down unchanged, directly or through a gadget that forces equality. Without that, every few levels wipe the slate clean. That is
  why the bond must spend a member at every stretch, so that the law counts depth.
- **The owner's nested parts.** A part holds the larger pattern's memory only by literally containing one of its distinctions, or
  a forced copy of one. Otherwise it is independent of it, given a few levels.

## Lag cutoffs and census-only claims

The 12,772 census first-ray growers, split 6,388 training and 6,384 held out. Rules N and A are proved for every family. Coverage
and the near-characterization are census facts.

## Review

**Referee pending.** The advisor model answered the hard part cold (`advisor_review_answer.md`). It proved that disconnection
gives a product, refuted rule D with a gadget, and gave the layered automaton. The free-from-above flag and the generic start are
the thread's. A generic start was needed because a first version, started at main's top, accepted 8 several-definition families
that do not forget; I found and fixed this on the training half before freezing.

## Literature and provenance

Known: elimination of degree-one variables (peeling), products of disconnected systems, equality gadgets in positive NAE-3SAT
(NP-completeness reductions). Ours: rules N and A for nested families, the automaton, and the census coverage. Classification:
known-with-delta.

## Workspace assumptions

A79 used.

## Ratio

Substantive: two proved rules, a held-out test on 6,384 families. Administrative: the two freezes, this note.

## Corrections

One, of my own (`docs/CORRECTIONS.md`): **Not a block**. Stage 2 quoted rule A's training coverage as 35.7%; it is 37.1%
(1,107 of 2,980; I had divided by 3,105). The held-out band (30% to 42%) and its verdict are unaffected.

## Data

`experiments/FORGET-RULE-20261114-001A/FORGET-RULE-20261114-001A-E001_rule/`: `rule_A.py`, `gadget_control.py` (and `.json`),
`heldout.py` → `heldout.json` (both halves, every stratum, H1 to H4).

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the rule | **Status:** Successful (referee pending) | H1–H4 held; N proved necessary, A proved sufficient |
| Local direction — counting inside | Continue | The slack beyond peeling is the open part of the rule |
| Broader exploration — G17 | Searching | Counting inside is located, measured and explained by identity |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | What makes a nested pattern count depth, as a rule |

**Corrections:** one, Not a block. **Goals:** a checkpoint for G17 and G1; no goal change. **Assumptions:** A79 used.
**Basket:** `FREE-TARGET-20261114-001#2` (2/3 Payoff, 2/3 Concreteness), `CENSUS-FORGET-20261114-001#2` (2/3, 2/3),
`EVERY-RAY-20261113-001#3` (2/3, 2/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Identity as the whole story | 2/3 — Substantial | 2/3 — Testable | Extend rule N to forced ties: a cycle of calls along which some port is tied, equal or opposite, to a port of the next copy in every allowed state (computed per call word, not per call); test whether "no tie cycle" characterizes forgetting on the census, and prove the necessary half | Selected · awaiting go-ahead |
| 2 | Slack beyond peeling | 1/3 — Minor | 2/3 — Testable | Strengthen rule A with two-level peeling (a knot whose two other members are free) → coverage gained, still proved | Alternative · deferred |

1. Payoff 2: if forced ties are the whole story, "counting inside" has a one-line characterization. Concreteness 2: ties per word
   need the automaton over relations, which exists.
2. Payoff 1: more coverage of a sufficient rule. Concreteness 2.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
