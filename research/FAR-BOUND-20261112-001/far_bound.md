# Bounded at every distance?

Epic `FAR-BOUND-20261112-001` (`TRAVEL-READ-20261112-001` direction 1; G1 with G17, question 9; program topology, group spacing),
2026-11-12, at the coordinator's go-ahead and in its order: the recheck, then far away, then a proof on one base. Pre-registered in
commit a0d2ee806 after the advisor model's critique; the runs came after. The canonical K1–K3 test is unchanged. Refereed: confirmed with fixes, far reading narrowed (Review).

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
| 3 | **Far away, certified upper bounds stay on some bases and rise on others.** Of the 34, 26 were decided within the cap: 16 stay within one of their near value at every far target to 23 across (along 7, 10, 15); on 4 the certified upper bound rises by two (4 to 6, at 19 to 23 across), and on 6 certificates are missing at more than a fifth of the far targets (the referee's recount; 183/4, whose window values are 4 everywhere, belongs here, not with the rises); 8 hit the 30-minute cap, among them the base proved bounded in ticket B, so dropping is no sign of growth. No lower bound on the least bond is computed: window values rise only on one law (17/4 and 17/5, the same base at two r), stay within one of the near value on 109/3 and 112/4, and the far data are compatible with a bound of 6. The mean certified bound rises from 4.08 at 7 across to 4.59 at 23. F2 failed, and its validity bound (at most a fifth dropped) too. | computed, frozen (F2 failed); refereed, narrowed | A |
| 4 | **Around bases with two directions it stays bounded to radius 15.** On 77 of 102 rank-2 bases at least 80% of the ring-15 targets have a bond of at most 5, none larger than the ring-3 value + 1 (F3 held); 72.5% of the ring-15 bonds are certified. | computed, frozen (F3 held, window level) | A |
| 5 | **A proof on the selected base: no length on two quadrants.** On sample 24 at r = 3 (chosen by the frozen rule), every distinction in two opposite quadrants of the frame is within bond distance 3 of the origin, at any distance. The mechanism is a second travelling direction (4 across) outside the census's shift list: a triple's pattern travels along both and forces a cone. | proved (computer-assisted: a hand argument with exact finite checks, 1,620 cases); referee pending | B |
| 6 | **A second direction and staying bounded (exploratory, not significant).** With my uncertified search for a second direction: of the decided bases with one, 11 stay bounded and 1 rises; of those without, 5 and 4. With the referee's certified search: 8 of 9 and 4 of 12; Fisher's p = 0.34 (certified) and 0.12 (uncertified), neither significant. What survives: no base with a certified second direction rose by 2 at window level. | computed, exploratory; refereed | A |

## Answer

Partly. The bounded bonds are real on about half the bases (34 of 66 on certified bonds), and where a base has two unlengthened
shifts they stay bounded far away and can be proved bounded on whole quadrants (one base, proved). Elsewhere the certified upper
bounds rise slowly on a few bases (to 6 at 23 across on 4), but no lower bound is computed and the data are compatible with a bound
of 6: "bounded at every distance" is neither established nor refuted there.

## Reading

**Interpretation, not a theorem.**
- **What the growing bases share with base 16.** Base 16, the three bases that grow across near the origin, and four of the five that
  creep up far away travel in one direction only, even in the wider search; most bases that stay bounded far away (11 of 16) have
  a second direction. So the law's reading looks set by how many shifts it leaves without length: two give no length in a cone (proved
  on one base), one gives a distance across that grows, linearly on base 16 and its like, more slowly on others. One direction is
  common to all the growing bases, but not sufficient: five one-direction bases stay bounded to 23 across.
  *Corrected on 2026-11-12 (`SHIFT-COUNT-20261112-001`): the wider search here was uncertified and used sets in a 2 × 3 box; a
  certified search with sets in [0, 2]² found that one of the three growing bases (sample 97 at r = 3) has a second direction, whose
  cone lies on its other side. What the growing bases share is a side that no cone of travel reaches, not a single direction (logged
  in `docs/CORRECTIONS.md`).*
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

The background referee thread (report `research/FAR-BOUND-20261112-001/referee-R1/report.md`, 7d52e8e5c) confirmed the epic with
fixes: ticket B confirmed (rerun with its own parameters, 176 representatives and 4,800 cases, every representative covered), the
eventually periodic certificate and the representative argument sound; ticket A's far reading narrowed (fix 1, Narrowing: rises of
certified upper bounds, no lower bound, compatible with a bound of 6; the recount 16 / 4 / 6 / 8); the second-direction pattern kept
exploratory with the certified numbers (fix 2, Not a block); ticket B's wording (fix 3, Not a block: three of the 1,620 cases are
knots of the base at values of j the proof does not use, the across period must be a multiple of 8, and C4's census check was a window
non-refutation, certified by the referee, who also found that the travel along t′ needs the third kind); dropped bases not a sign of
growth (fix 4, Not a block). A completion run on the 8 dropped bases is the referee's to fold in.

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

One, found later and logged in `docs/CORRECTIONS.md` (Narrowing): the Reading's "the growing bases travel in one direction only" (see the
note there). Before that, none new here: TRAVEL-READ's headline narrowing from this recheck is logged with that epic's referee fixes (one entry, Narrowing).
Deviations: none; the far part's validity bound (at most a fifth of bases dropped) failed (8 of 34 at the 30-minute cap), recorded with
F2.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — bounded at every distance? | **Status:** Partially successful, refereed (narrowed) | Bounded and proved where two shifts fold; slow growth on some one-fold bases; F1, F2 failed, F3 held |
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

## Final report as sent

Sent to the owner on 2026-11-12 at about 13:55 UTC, summarized here (the tables are those above, directions 1 to 3). Headline: partly;
where a base has two unlengthened shifts influence stays bounded, proved on one rule-selected base (every distinction in two opposite
quadrants within bond distance 3 of the origin); with one, the bound often creeps up slowly far away. 34 of 66 one-direction bases
bounded on certified bonds; to 23 across 16 of 26 decided stay bounded, 5 creep from 4 to 6; two-direction bases bounded to radius
15. What the growing bases share with base 16: one travelling direction only, which is common to all of them but not sufficient.
No new correction. Referee handed to the referee thread; holding for a go-ahead on #1, with the repeat-size test as the side ticket.
