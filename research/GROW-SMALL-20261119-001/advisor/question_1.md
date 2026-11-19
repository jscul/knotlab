A colleague's check before I freeze a computation. Be concrete and critical; give a bet.

Context (from the previous study, which you advised on). Arrangements of parity junctions; "meet once" = no two junctions share
two distinctions; collisions = non-isomorphic arrangements with isomorphic bond-distance tables; states = equation spaces up to
renaming. The census law (complete rounds, cheapest counts) never made a meet-once collision with other states from the census's
26,441 starts (to 40 junctions; 50 by a referee). Backed pairs (proved kept by the law) do not keep the states: among all 503,039
legal meet-once arrangements of at most 7 junctions, 242 other-states pairs have both sides backed, 38 both peel once, 0 both
peel twice (77 such arrangements), 0 both "self-grown" (85: one round of the law from its own peel gives it back).

Plan. Take each of the 503,039 as a start; grow one and two complete rounds of the law (a stall ends a start; most 7-junction
starts stall at once). In a 1,000-start sample: 696 stages, 10-30 junctions. Every stage meets once (new junctions meet each
parent once). Key: Weisfeiler-Leman hash of the table read exactly to distance 8 and pooled beyond, plus the number of
distinctions. Then MEET-ONCE's amended pairing: exact arrangement classes; candidate groups by exact isomorphism of the pooled
tables; states first (a junction-graph isomorphism, else every pooled-table isomorphism on twin classes tested by rank, cap
5,000); classes with other states escalated to tables read to 12, 16, ... and the full table under an alarm. Prediction G1: no
pair of non-isomorphic stages (rounds 1-2) with isomorphic full tables and other states. G2: same-states collisions exist.
Control: every stage is self-grown, checked on a sample.

Questions: (1) any flaw in the design (e.g. a stage of start X colliding with a stage of start Y at a different round; isomorphic
starts; stalls)? (2) Is "self-grown at depth 1" the right population, or should rounds 1 and 2 be scored separately? (3) Your bet
on G1. (4) If G1 fails, where would you expect the first pair, and how should it be checked?
