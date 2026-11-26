# The question to the advisor (26 November 2026), before the census of receivers was run

A colleague's check, please, before I run a census; be skeptical. Same growth system as in my earlier question (knots
hold distinctions; members are knots with usable loose distinctions; groups from met sets; a member is SHORT when
owe > h; a group with a short member is cancelled; a member that is not short spends everything, one distinction per
kept join and the rest on offshoots; a short member waits; each new knot gets f fresh distinctions, ordinary count
f = max(D, 3 - p, 1) with D its demand next round; CAP-3 is min(that, 3)).

Finding to explain and generalize. Two starts joined by a "meeting" through d - 1 link knots. Under CAP-3, one
receiver of 47 small starts (three knots each sharing a distinction with the other two, loose counts 1, 2, 2, joined
at the knot with 1 loose) grows "the slow way" (its own knots make 3, 4, 5, ... knots in rounds 1, 2, 3, ..., never
short) until round 2d + 1; then, if the far end's site holds exactly two loose distinctions, it switches to fast
growth (own knots short every other round). With three loose, or a stub at the far end, it never switches (through
round 16); with two particular one-loose senders it switches at 2d + 3. Identical at d = 2..6 and under waiting,
retiring or offshoots; under a cap of four the switch is at 3d + 2 with fewer senders; under the ordinary count
nothing reaches it. Mechanism seen in a trace: the receiver's site keeps kept joins with link-side knots that are owed
3 and hold 3; in the switch round those partners are owed 4, the cap gives 3, they are short, the joins with the site
are cancelled and the site makes own offshoots instead.

Design: every sited start of 1-4 knots (646 receivers) against five senders (site with 3 loose; 2 loose; 1 loose
in a path; the switch receiver itself; a stub), d = 2..5, laws CAP-3, CAP-4, the record's ONE-FEWER, ORD, 16 rounds
or 3,000 knots. A receiver "reads the far end" from the first round its own births differ between two senders; it
"switches" if that round is after 2d and no own knot was short before.

Predictions: (1) 1-10% switch under CAP-3 at d = 3; (2) always at 2d + 1 or 2d + 3, two rounds a step, the two-loose
sender apart; (3) every switching receiver's site holds one loose distinction; (4) fewer under CAP-4, at 3d + 2;
(5) ORD: none reads the far end; record's ONE-FEWER: readers have a waiting own knot first.

Questions:
1. Why two rounds per step under CAP-3 and three under CAP-4? Sketch the mechanism in terms of the demand D of the
   link side's knots growing along the line (I suspect the influence-cone result: a change at separation s first
   changes a fresh count at step s), and whether (k - 1) d + (k - 2) for a cap of k is what you would derive.
2. Why would the far end's site holding exactly two loose distinctions matter, and not three?
3. Is "after 2d" the right threshold for calling a reading late, given that the line itself takes time to grow?
   What control would show that the receiver reads the far end rather than just the line's own growth?
4. Which prediction do you expect to fail? Anything missing from the design?
Under 600 words, numbered.
