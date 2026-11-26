**Advisor answer for `BUILT-BINDING-20261126-001`, before the freeze.** Nothing was run. Each claim is `unverified` unless I say which line I read. The hivemind has one new entry.

I use the stage as `multi_class.py` 15–37 reads it: each distinction joins its two holders, and every loose one joins its holder to one extra point U, so the allowed changes are the closed loops.

## 1. The origin test

The test is right, and it does not depend on the representative chosen.

- **The test itself.** A carrier f depends only on the start's values on the allowed states exactly when f is even on Z_new. That holds exactly when f lies in the span of the stage laws plus the single start distinctions, which is what `old_representative` computes (`repro.py` 119–130, read).
- **Independence.** Two representatives g and g′ differ by a sum of stage laws supported on start distinctions. By the projection lemma that sum vanishes on the start's allowed states, so it is a sum of start laws. "Label" and "read by no single knot" at the start are also properties of the function. Only the sizes and the disjointness of the supports depend on the representative.
- **Defect.** `repro.py` line 164 tests "sum of the representatives a sum of start laws" only when k == 3; for any other k it tests the zero vector and returns True. P1 includes four rings, so this would pass vacuously.
- **Power.** For your ring carriers the test cannot fail. Each carrier is every fresh distinction of a set of births, so adding those births' laws gives their inputs, and so on down to the ring's ten loose distinctions. The test has power only on a carrier that takes part of a birth's fresh distinctions.

## 2. Z_new in H: I think it is true at every round

I could not break it; here is a hand proof for you to check.

**Premises, with where I read them:**
1. No birth takes two distinctions of one parent, and each round uses every loose distinction (`rival_growth.py` line 71 and line 81, asserts).
2. Any two live knots with a common neighbour are parents of one birth next round. `fastlib.py` 46–58: every candidate pair is in a group of three or more or is its own pair group, and `rival_growth.py` line 12 asserts the canonical engine agrees.
3. A birth with no fresh distinction is the only birth of its connected structure, and all its parents have one loose distinction each. Your tallies in `closing_census_parity.jsonl` and `closing_heldout_parity.jsonl` show this (1,819 and 33 implied births, all taking every loose distinction; none otherwise).

**Argument:**
- Z_new is the loop space of the stage with the start knots removed. Call that F: the births of rounds 1 to t, plus U.
- A round-s birth joins only round s − 1 births (its parents), round s + 1 births (its children), or U if s = t. So F has no loop of three, and by premise 1 its only loops of two are pairs of fresh distinctions at one newest birth.
- Build F from the newest round down. The newest births with U give only the pairs. Add an older birth w with children v₁…v_d. Any two children with a fresh distinction have a common neighbour: U if they are newest, else a common child by premise 2. That gives a loop of four: w, vᵢ, the common point, vⱼ.
- Every other loop through w differs from these by a loop not through w. A child with no fresh distinction is w's only child (premise 3), so it adds no loop at w.
- So Z_new is spanned by pairs and loops of four. Each loop of four is a shortest change through its distinction w–vᵢ, since no loop of two or three passes through it. Hence Z_new lies in H under both readings, at every round.

**Where you asked it might fail:**
- **Rounds past 3:** covered by the induction.
- **Implied births:** covered by premise 3.
- **Double meetings:** these involve only start knots, which are outside F.
- **Second reading:** only loops of two and four are used.

**Where it does fail (outside the frozen scope):**
- The cut arms: a birth that is not implied gets no fresh distinction while its sibling does, so premise 3 fails.
- Capped groups (`groups_among(..., cap)`): siblings need not be co-parents; three rounds later the loop through them has eight distinctions, so changes of at most five should fail first.

I have no candidate counterexample under the ordinary count. This is not a proof until you assert premises 1 to 3 on every birth record and check that the rank of the pairs and loops of four inside F equals dim Z_new.

**Consequence a referee will press.** Class facts are then linear functions on the start's allowed states. A relation among three of them is a linear dependence, and one exists whenever the label space has dimension two (g₁, g₂, g₁ + g₂). The standing fact from `LAYERS` R1 already says a rule defined as a sum passes K1 to K3 trivially. So the content of the 30-knot witness is that the third function has a disjoint carrier no single knot reads. Growth makes carriers and decides which functions are labels; it makes no relation.

## 3. The predictions

- **P1.** The relation is the telescoping identity above, not a test. The testable parts are "label" and "read by no single knot". Expect differences by ring size (hand reading of the group rule):
  - n = 4: each ring knot is in one pair and has one offshoot.
  - n = 6: knots {0, 2, 4} and {1, 3, 5} form births of three parents.
  - n = 5 and 7: pairs only.
  
  Freeze the label outcome per n, or it reduces to the n = 5 case you already ran.
- **P2.** False as worded: two fresh distinctions of one birth and the parity of its inputs are bound by the birth's own law and fail the origin test. Say "among class facts"; then it is entailed by section 2. Add a control where the test fails (such a triple, and `origin_scan.py` under the cut arms); no run so far shows it can return False.
- **P3, loose distinction.** A connecting knot with one loose distinction should stall round 1. Under split attachment it is a candidate with the ring neighbours of both its ring knots; under paired attachment with two; it has one loose distinction. "Removes the relation at every round" would then be vacuous. Put the loose distinction on a detour's middle knot, which has no live candidate. Also, `connector_loose` gives it to every connecting knot, not one.
- **P3, cut links.** If the link distinctions are deleted, each ring with its connecting knots is its own structure, and its law sum forces the ring fact to a constant: one tuple, not eight, and the fact is no longer a label. If they are left loose, the connecting knots become live and may stall. Say which.
- **P4.** It reproduces the referee. State what the relation is: the cut birth's own law on the three middle knots' loose distinctions, which with the start laws gives the ring relation. That is the start with one closed knot added, the same kind as "the cuts can fix a loose value" (upheld). The referee's 360 funding settings left it free.
- **P5.** Nearly certain and weak: under not-all-equal the carriers are not functions of the ring's loose distinctions at all, so eight tuples does not separate "no binding" from "a parity is the wrong fact for this law".
- **P6.** Entailed by section 2. Freeze the stronger form instead (premises plus the rank equality, at every round reached). Report starts that give no stage: `origin_census.jsonl` has 3,782 ended or unread rows against 7,075 starts. Name the weighting: `forbid.sampled` draws with p_meet 1/3 and at most 18 distinctions, which at 12 knots admits only sparse starts.

## 4. The rungs

- **Repetition:** reached. The same relation holds on new carriers at every round from 2 on, by inheritance.
- **Tower:** not reached by ordinary growth. The next layer's rule is a dependence among chosen carriers; the labels themselves form a free space with no laws. A next layer needs a rule, not supplied by hand, that picks the carriers (for example labels of least support) and its own small changes. The referee's first direction asks for the same.
- **Recursion:** not reached.
- **Cut law:** different on one point. It makes an equation the start lacked. But it is one knot law on start values, supplied by the arm, on one construction, and both cuts stall at round 2 there (referee report, line 29), so nothing iterates.

## 5. A relation made by ordinary growth

Among class facts there is none, if section 2 holds. Any made relation involves values the start does not fix, and the only such relations are the births' own laws, whose terms are single fresh distinctions that every pair or loop of four changes.

The cheapest search is therefore for a broken premise, not for a relation: assert premises 1 to 3 on birth records at large starts and many rounds. That needs no linear algebra and no 400-distinction cap. A violation is the only place a counterexample can be. After that, the capped engines under changes of at most five are where I expect the first real failure.