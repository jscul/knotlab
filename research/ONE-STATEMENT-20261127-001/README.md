# A presentation is a completed system with one knot left out: both layers, and under not-all-equal

Epic `ONE-STATEMENT-20261127-001`, at the coordinator's pick of the advisor's third direction
([the advisor's answer](../TREE-PROOF-20261127-001/advisor/answer_directions.md)). A check by the thread, not registered;
computed. Each part's predictions are committed before its run.

## Part (a): the advisor's checkable claims ([`checks_a.py`](checks_a.py))

**Frozen predictions (the advisor's, unverified until run).**
- **a1.** Of the 840 bases of the relations among the nine facts of three rings of four (six family facts and the three
  ring facts, each ring's the sum of its two families'), 20 keep every fact in at most two relations; 12 of those have
  four relations meeting in a ring; exactly one has the six family facts each in a single relation (the tree).
- **a2.** On the grown witness at round 5, deleting any start law frees all three four-place relations (each four-place
  relation is the sum of every start law and one ring's round-1 births).
- **a3.** On rings of 10, 4 and 4 knots, the big ring's four-place relation is shorter in distinctions than its
  three-place one (about 36 against 40), though longer in places: so "prefer shorter relations" depends on what is
  counted.
- **a4.** Pair (i), 16 states on seven distinctions: the loose sets differ and the families number 2 against 1. Pair (ii),
  a ring of four knots with one loose distinction each against the completed system (a fifth knot meeting each ring
  knot once) with a ring knot left out, 16 states on eight distinctions: loose sets differ, families 2 against 1. Pair
  (iii), 8 states and the loose set {l, m}: the holdings differ and the families are the same.

**What was found in (a)** ([`checks_a.json`](checks_a.json)). All four held, a3 under one count. a1: 15 relations, 840
bases, 20 keep every fact in at most two relations, 12 of them meet in a ring of four, and exactly one leaves the six
family facts in a single relation each: the tree (p_i q_i R_i three times, and R1 R2 R3). a2: each four-place relation
has 8 joint values, and removing any one of the 18 start laws frees it, as does any of its own ring's 6 round-1 births.
a3: on rings of 10, 4 and 4 the three-place relation for the big ring is 3 places, 40 carrier distinctions and 10 laws
(40 distinctions); the four-place one is 4 places, 36 carrier distinctions and 34 laws (92 distinctions): shorter in
carriers, longer in places and in laws, so which presentation is "shorter" depends on what is counted. a4: pairs (i) and
(ii) have the same allowed states and different loose sets, with 2 families against 1; pair (iii) has the same states
and loose set, different holdings, and the same single family.

**Part (c), the recursion test** ([`recursion_c.py`](recursion_c.py), [`recursion_c.json`](recursion_c.json); run
right after (a), with the advisor's prediction as its hypothesis). The tree presentation read as a first-layer start
(root R1 R2 R3; T_i = R_i p_i q_i) grows three three-place births at round 1, one at round 2, and closes at round 3. The
nine facts on the grown witness instead gain, each round, one two-place relation per family (its fact on its new
carrier) and never close. They differ, as predicted: the second layer does not grow as a start of its own would.

## Part (d): the reader's question under each law ([`nae_pres.py`](nae_pres.py))

Under parity, a presentation of the reader's pair (allowed states, loose set) is a completed system with one knot left
out, and the families and the tree are fixed by the pair (`MARKED-LOOSE-20261127-001`: every census start; entailed, so
that agreement checks the code). Under not-all-equal nothing is entailed: no law is a sum of others.

**Frozen.** Every census start, under each law: every presentation of its pair (as many knots, each at least three
places, the loose set held once and every other distinction twice, connected, the same allowed states under that law).
**H_d.** Under not-all-equal too, the pair fixes the families and the tree on every census start. **Read:** on how
many starts the pair fixes the presentation itself (the knots), under each law; seen before the freeze on the first 200
census starts: 200 of 200 under not-all-equal, 136 of 200 under parity.

**Deviation, recorded before any not-all-equal result was read.** Timed at full size the not-all-equal run needs about
three and a half hours (about 33 starts a minute once past the small starts), past the two-hour limit. It is cut to the
first 2,000 census starts in the census order; the rest are not run. The parity run covers all 7,075.

**What was found in (d)** ([`frozen_parity.jsonl`](frozen_parity.jsonl), [`frozen_nae.jsonl`](frozen_nae.jsonl)). The
not-all-equal run stopped at its 90-minute limit after 1,194 of the planned 2,000 census starts (census 0 to 1,193);
starts 1,194 to 1,999 were not run.
- **H_d held on every start read.** Under not-all-equal the reader's pair fixes the families and the tree on all 1,194
  starts read; under parity on all 7,075 (entailed).
- **Under not-all-equal the pair fixes the knots themselves.** On 1,193 of the 1,194 starts read there is one
  presentation; the exception (census 959) is the closed pattern of four three-place knots each sharing one distinction
  with each other, which has two labellings with the same states and no loose distinction. Under parity on the same
  1,194 starts the knots are fixed on 509, and on 1,499 of all 7,075.
- **So, on the question of what chooses the knots:** under parity nothing in the states does (a presentation is a
  completed system with one knot left out, and the states fix only its cycles); under not-all-equal the states with the
  loose set marked do, on every start read but one. This is not entailed, and it agrees with the states-and-growth
  study's finding that the not-all-equal states alone fix the presentation on 79.8% of small stages, now with the loose
  set marked (`STATES-GROWTH-20261119-001`).
