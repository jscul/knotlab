# Bounded at every distance?

Epic `FAR-BOUND-20261112-001` (`TRAVEL-READ-20261112-001` direction 1; G1 with G17, question 9; program topology, group spacing),
2026-11-12, at the coordinator's go-ahead and in its order: the recheck, then far away, then a proof on one base. Pre-registered in
commit a0d2ee806 after the advisor model's critique; the runs came after. The canonical K1–K3 test is unchanged. **Referee pending**
(handed to the referee thread).

## Words

As in the pre-registration: eventually periodic strip, certified bond, bounded across, growing across, unresolved; frame,
along-count, across-count.

## The question

TRAVEL-READ's bounded bonds were window bonds. Are they real? Do they stay bounded far away, including where Ledrappier-type growth
would show? Can boundedness be proved on one base?

## The question in standard terms

For random periodic 3-uniform hypergraphs on ℤ² under proper 2-colouring with a finite pattern forcing its own translate: are the
small minimal non-shattered sets found up to a window certified by explicit colourings, and does their least size stay bounded as the
transverse offset grows to 23 and on rings to radius 15?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **A sound certificate for states that repeat along no step.** States periodic across and repeating along only outside a finite stretch (and the same in both directions) extend to states of the base by repetition. They carry exactly the patterns doubly periodic states miss on base 16, whose theorem is now certified in full (4, 5, 5, 6, 6). | proved (soundness); control held | A |
| 2 | **About half the bounded bases are bounded on certified bonds.** Of TRAVEL-READ's 66 rank-1 bases, 34 are bounded across on certified bonds, 3 grow across, 29 unresolved; the window values did not change in a window twice as large. F1 (at least 40) failed; TRAVEL-READ's headline (56) narrows to 34 and is logged. | computed, frozen (F1 failed) | A |
| 3 | **Far away, the bound holds on some bases and creeps up on others.** Of the 34, 26 were decided within the cap: 16 stay within one of their near value at every far target to 23 across (along 7, 10, 15), 5 rise by two (from 4 to 6, at 19 to 23 across), 5 lack certificates at more than a fifth of the far targets; 8 hit the 30-minute cap. The mean certified bond rises slowly with the across-count, from 4.08 at 7 to 4.59 at 23. F2 failed, and its validity bound (at most a fifth dropped) too. | computed, frozen (F2 failed) | A |
| 4 | **Around bases with two directions it stays bounded to radius 15.** On 77 of 102 rank-2 bases at least 80% of the ring-15 targets have a bond of at most 5, none larger than the ring-3 value + 1 (F3 held); 72.5% of the ring-15 bonds are certified. | computed, frozen (F3 held, window level) | A |
| 5 | **A proof on the selected base: no length on two quadrants.** On sample 24 at r = 3 (chosen by the frozen rule), every distinction in two opposite quadrants of the frame is within bond distance 3 of the origin, at any distance. The mechanism is a second travelling direction (4 across) outside the census's shift list: a triple's pattern travels along both and forces a cone. | proved (computer-assisted: a hand argument with exact finite checks, 1,620 cases); referee pending | B |
| 6 | **A second direction goes with staying bounded (exploratory).** With a wider, uncertified search for a second travelling direction (shifts up to 6): of the bases with a second direction whose far range was decided, 11 stay bounded and 1 grows (4 more lack certificates); of those with one direction, 5 stay bounded and 4 grow (1 lacks certificates). The three bases that grow across near the origin, like base 16, show one direction only. | computed, exploratory (designed after the recheck) | A |

## Answer

Partly. The bounded bonds are real on about half the bases (34 of 66 on certified bonds), and where a base has two unlengthened
shifts they stay bounded far away and can be proved bounded on whole quadrants (one base, proved). Where only one direction is found,
the bound often creeps up slowly with distance across (to 6 at 23 across on 5 bases), so "bounded at every distance" is not
established there: those bases may read a slowly growing distance across, between base 16's line and no length at all.

## Reading

**Interpretation, not a theorem.**
- **What the growing bases share with base 16.** Base 16, the three bases that grow across near the origin, and four of the five that
  creep up far away travel in one direction only, even in the wider search; most bases that stay bounded far away (11 of 16) have
  a second direction. So the law's reading looks set by how many shifts it leaves without length: two give no length in a cone (proved
  on one base), one gives a distance across that grows, linearly on base 16 and its like, more slowly on others. One direction is
  common to all the growing bases, but not sufficient: five one-direction bases stay bounded to 23 across.
- **For the owner's "globally influential".** Global influence at bounded bond distance is real and provable where two shifts fold;
  with one fold, influence across is bounded only near the origin and spreads with cost farther out.
- **For question 9.** The law's own dimension is zero on two-fold bases and, on one-fold bases, somewhere between zero and one; base
  16's exact one is one end of that range.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic. **Proved.** The certificate's soundness; the two-quadrant theorem on one base.
  **Computed.** The recheck, the far range and the rings, within their caps and families; the second-direction comparison is
  exploratory and uncertified.

## Stress test

The far range is the stress test of TRAVEL-READ's range: 23 across instead of 6, rings of radius 15 instead of 6, and targets of high
binary weight (the advisor's guard against Ledrappier-type growth). It found slow growth on some bases.

## Review

Referee pending: handed to the referee thread on 2026-11-12. TRAVEL-READ's referee (R1) already judged the eventually periodic
certificate sound and this epic's one-base proof sound in logic; its finite checks are for this epic's referee.

## Literature and provenance

- **Known.** Directional determinism and expansive directions (Boyle and Lind; Guillon, Kari and Zinoviadis); forced cones in
  bootstrap percolation (Bollobás, Smith and Uzzell); Ledrappier's shift, where bond size tracks binary weight.
- **Not found** (bounded search): eventually periodic certificates of this kind for minimal non-shattered sets; slow growth of bond
  distance across a single unlengthened shift.
- **Classification.** Known-with-delta (mechanisms), new as stated (the counts and the two-quadrant theorem).

## Workspace assumptions

- **Relied on.** A64, A67, A71, A74, A76. **Changed.** None.

## Advisor model

Consulted before freezing on the certificate, the recheck's criteria, the far targets and the proof: it set the condition P at least
the kinds' span, asked for the headline to rest on certified bonds, added targets of high binary weight, and proposed the seed-and-
growth proof with finite checks by periodicity, which ticket B followed (with a certificate repeating in both directions where one
repeating across alone met an identification).

## Ratio

- **Substantive.** The certificate, the recheck, the far range and the rings, the one-base proof.
- **Administrative.** The pre-registration, this note, the closure.

## Corrections

None new here: TRAVEL-READ's headline narrowing from this recheck is logged with that epic's referee fixes (one entry, Narrowing).
Deviations: none; the far part's validity bound (at most a fifth of bases dropped) failed (8 of 34 at the 30-minute cap), recorded with
F2.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — bounded at every distance? | **Status:** Partially successful, referee pending | Bounded and proved where two shifts fold; slow growth on some one-fold bases; F1, F2 failed, F3 held |
| Local direction — one fold against two | Continue | The comparison the data now points to |
| Broader exploration — G1 on overlapping bases | Known alternatives | The harmony thread's repeat-size test on the unresolved bases (agreed side ticket) |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | A proved zero-dimensional reading on a whole quadrant of a random base, and a certificate for states that repeat along no step |

**Corrections:** none new (the narrowing is logged under TRAVEL-READ). **Goals:** a G1 checkpoint (capability gained, with G17); no
goal change. **Assumptions:** none changed. **Basket:** `TRAVEL-READ-20261112-001#2` (what makes a base grow, 2/3, 2/3), `#3`
(certificates, now done in part), `COMMON-FOLD-20261112-001#3` (other weightings, 2/3, 3/3); taken: `TRAVEL-READ-20261112-001#1`.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | One fold against two | 3/3 — Major | 2/3 — Testable | Certified search for a second direction (wider shifts) on all 169, then the conjecture: two directions ⇒ bounded on a cone (prove the general lemma), one direction ⇒ bond distance across unbounded (test far out on the clean one-direction bases) → a rule for the law's dimension from its folds, or a counterexample | Selected · awaiting go-ahead |
| 2 | The repeat-size test (the harmony thread's) | 2/3 — Substantial | 3/3 — Ready | On base 16 and the 29 unresolved bases, which repeat sizes certify a travelling pattern → their divisibility reading confirmed or refuted | Side ticket, agreed |
| 3 | Growth rate on one-fold bases | 2/3 — Substantial | 2/3 — Testable | Push the five creeping bases to 60 across with certificates → logarithmic, linear, or bounded | Alternative · deferred |

1. **One fold against two.** Payoff 3: a rule linking the number of unlengthened shifts to the law's dimension would be the program's
   first general statement of what space a law makes from overlap. Concreteness 2: the two-direction cone lemma is close to the
   one-base proof; the one-direction side needs a lower bound.
2. **Repeat sizes.** Payoff 2, concreteness 3, agreed with the coordinator.
3. **Growth rate.** Payoff 2, concreteness 2.

**Recommendation.** Research directions, #1, awaiting the go-ahead; #2 as the side ticket.
