# Survey of the record: knots within reach, and the growing end

Epic `KNOTS-WITHIN-REACH-20261125-001`, 25 November 2026 (UTC), with the [claim](claim.md), the [definitions](definitions.md) and
the [pre-registration](../KNOTS-WITHIN-REACH-20261125-001A/preregistration.md). Paths are relative to the repository root;
`path:line` cites the line read. Evidence classes: proved, computed (with range), argued, reading. Referee standing as the
record gives it. Two parts of this survey were read by helper searches and checked at the lines cited.

## 1. What a step is in the record

- **Holder step, parent step**: glossary, "Parent step; holder step" (`publication/knotlab/INTUITIONS.md:5563-5570`):
  every parent step is a holder step; counts of holder steps say how much of what is built a law's rule reads; neither is
  steps apart. Steps apart counts co-knotted pairs of distinctions (`INTUITIONS.md:5288-5293`). Reading.
- **Witnessed step**: the state-distance study, "a step of H covers exactly two ordinary meetings through any single
  intervening holder, live or spent", on live holders
  (`research/STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001A/tree_delays.md:26`); in code `witnessed_end`
  (`experiments/GENERATORS-20261120-001A/GENERATORS-20261120-001A-E001_generators/fixtures.py:58-64`). It is the shared
  definitions' joinable relation (`research/RING-IN-BALANCE-20261123-001/definitions.md:27`). Definition.
- **"A knot meets only its parents and its children"** holds under the taking-free laws, every distinction held once or
  twice (`research/PARTS-MEET-AGAIN-20261124-001/definitions.md:26-27`). Argued.
- **Ball, step ball**: the glossary's ball is the set of distinctions within a bond distance; the step ball counts
  distinctions by steps apart (`INTUITIONS.md:5273-5280, 5788-5790`). No record defines a count of knots within r holder
  steps. Definition.

## 2. Counts within reach already in the record

- **Bond balls, proved, in grown structures**: distinctions within bond distance r grow as Θ(r³) on the parity growth with
  three fresh distinctions per knot from one knot (`research/CUBIC-FROM-A-KNOT-20261117-001/cubic_growth.md`,
  proof lines 59-62; referee R1 "Confirmed, with framing fixes"), and as Θ(r^a) on the a-fold counting pattern when one
  count equals the first knot's size a (`proofs/FRESH-COUNT-20261118-001A/FRESH-COUNT-20261118-001A-P001_free_count/proof.md:185`,
  T5; refereed R1, T5 carried over). These are bond balls on the infinite limit, not counts of knots by holder steps;
  `research/FRESH-COUNT-20261118-001/fresh_count.md:160-161`: "the census counts junctions by round ... not bond balls".
- **The grown pattern is the down-closed sets of the descent order** of the one-parent junctions (FRESH-COUNT T1,
  `proof.md:52-60`; proved, refereed). With the cluster theorem (`INTUITIONS.md:3035-3046`, proved, refereed) a knot is a
  cluster of the unrolled map and its round is its size less one (`INTUITIONS.md:3059-3065`).
- **Every other "dimension" of growth counts knots by round** (lesson 8.2, `INTUITIONS.md:3181-3200`: "the junctions made
  up to round t number about t^D"; RELAY-IDENT, CHAIN-IDENT, CLUSTER-ALL, WEIGHTINGS, SCALE-THEOREM, all refereed; e.g.
  `research/WEIGHTINGS-20261119-001/weightings.md:48`). Eddies are exponential by a lap weight (`INTUITIONS.md:3214-3221`,
  proved, refereed); runaway growth is about two to the half of the previous count (`INTUITIONS.md:3288-3300`, proved,
  refereed). The kinds are of the count by round, not of a count by steps.
- **Band growth** (its structure is the literature's tube, drawn): rings within ring-graph distance r number 2r² + 2r + 1 up to r = (n − 1)/2, then +2n per
  step (`research/GROWN-DISTANCE-20261109-001/grown_distance.md:22, 29-31`; proved, no referee recorded). A different
  substrate (rings of cells); the same shape as this study's bare ring (claim C2).
- **Blind recognition** read distinctions within r meeting steps at r = 8, 12, 18, 26; on the cubic construction the fits
  were 2.2 to 2.6 against a true 3 (`research/GROWTH-STATISTICS-20261121-001/decision.md:51-58`; computed, within-task
  review only). Lesson for this study: short ranges under-read high exponents.
- **Loose-end rules at 200 knots** gave a line, small worlds and saturation (`artifacts/OPEN-END-GROWTH-20261107-001A/`
  interpretation lines 21-25; exploratory, no referee).
- **Explosive stages have small diameters**: candidate-graph diameters 2 to 6 (`research/HEAVY-GROWTH-20261119-001/separation.md:4-5`;
  referee pending).
- **INFLUENCE-CONE**: under ordinary growth "within n continuing parent steps, a knot shares descendants with exactly the
  original knots within n witnessed steps" (`research/INFLUENCE-CONE-20261120-001/decision.md:22`; proved, referee
  pending); 426 of 426 sampled pairs (line 28). So arrival delay equals witnessed separation there.
- **Sub-goal B261 itself** says no study has measured the count within reach. The record
  agrees: the nearest are the bond balls above and the counts by round.

## 3. The growing end and state distance

- **State distance** is "the probability of unequal bits on the specified marks" in "uniformly weighted allowed words"
  (`STATE-DISTANCE-...-001A/preregistration.md:7`); ticket B adds a second weighting dividing each earlier word's mass over
  its extensions (`STATE-DISTANCE-...-001B/results.md:7`, `preregistration.md:23`). On trees under not-all-equal,
  C = ∏ (−1)/(2^{q−1} − 1) over the holders of the route (`tree_delays.md:9-14`; proved, referee pending).
- **Parity, loose distinctions**: "On a proper subset of current loose names, parity has no nonzero equation. The only
  possible such equation on the whole loose set is the sum of all holders" (`STATE-DISTANCE-...-001A/rival_joins.md:15`);
  "the raw rates on two loose names are 1/2 whenever there is a third loose name on the connected stage" and two age-one
  edited samples at age one with exactly two loose names have r = 0 (`samples.md:123-127`); the ring study states it as settled
  (`research/RING-IN-BALANCE-20261123-001A/preregistration.md:100-101`). Argued, referee pending, without taking. **So B269's
  parity pencil is already in the record** for laws whose distinctions have at most two holders, as a statement about pairs
  of single loose distinctions under the uniform weighting on allowed states.
- **Not-all-equal, loose distinctions of two holders**: |1 − 2r| ≤ 1/((2^f − 1)(2^g − 1)), f and g the private counts
  (`samples.md:148-158`; proved). This study's Lemma N (KD 5.3) restates it as an identity.
- **The mismatch on reached cuts**: at tree age 1, a reached cut, 4 of 21 not-all-equal "near" pairs never had a common
  descendant while 9 of 25 "far" pairs did (`samples.md:99-102`; computed, 64 sampled starts, referee pending). **This contradicts
  B269's premise** that the recorded mismatch involves only knots that share a distinction directly: the record already has
  near-but-never and far-but-met pairs after one full round. The 40 below-half rates at age 0 all lie across separate
  witnessed parts (`samples.md:109-111`).
- **The rival joins are inactive on every reached cut** (`rival_joins.md:9`; proved, referee pending): two live newborns
  share no distinction directly, so D and W differ from ordinary growth only at round 1.
- **Distance carries what grows only partly** (lesson 8.4, `INTUITIONS.md:3373-3459`, refereed): pair bond distances and
  the live roster carry the next round on every census stage to 14 junctions but fail on two built stages.

## 4. The laws in balance and the laws with taking

- **The ring that returns** under (CAP-3, CANCEL-WAIT, RELEASE): an odd ring of five or more returns every two rounds
  while two-knot parts come apart from it; with FILLERS the parts end and the roster is in balance
  (`research/RING-IN-BALANCE-20261123-001/decision.md:12-16`; computed, referee pending). Under ordinary growth no part
  comes apart (`RING-IN-BALANCE-20261123-001A/preregistration.md:105-106`, citing GENERATORS).
- **Parts act alone past the start** under RELEASE (`RING-IN-BALANCE-20261123-001A/preregistration.md:95-99`, argued); with
  no taking rule parts that came apart are never joinable again (`PARTS-MEET-AGAIN-20261124-001/definitions.md:125-126`).
- **Under a cap of three no part copies itself**: "each two-knot part becomes one chain gaining a member a round"
  (`research/COPYING-PARTS-20261123-001A/results.md:55`; computed, referee pending). This is the reading behind the cap's
  second power of H (pre-registration, the start-by-start table).
- **Small parts copy themselves** under FLOOR1 and the other "enough for three places" rations: doubling, Fibonacci,
  Pell (`research/COPYING-PARTS-20261123-001A/results.md:55-74`; computed, referee pending); in 93, 97 and 85 percent of
  the census's 3,344 starts by round 10 under FLOOR1 (`results.md:68-74`, census weighting).
- **Taking rules** (Q, MET, STEPS-k, CARRY, ...) and their costs: `PARTS-MEET-AGAIN-20261124-001/definitions.md:128-172`;
  under them parts can be one part again (`research/PARTS-MEET-AGAIN-20261124-001/decision.md`, computed, referee pending).
- **The census of starts**: connected graphs on three to five knots, one shared distinction for each pair of meeting knots, 0 to 3 loose
  distinctions per knot with degree plus loose at least 3, least loose tuple in its orbit
  (`experiments/COPYING-PARTS-20261123-001A/COPYING-PARTS-20261123-001A-E001_copies/cpcensus.py:1-5`); 3,376 starts, 32
  failing the parity knot test at round 0, 3,344 passing (`COPYING-PARTS-20261123-001A/results.md:68`; reproduced in
  the drafter's runs before the freeze: 19, 200 and 3,157 starts of three, four and five knots; 3 and 29 parity failures, none under not-all-equal). The
  denominators are therefore 3,344 under parity and 3,376 under not-all-equal.
  Weightings: each start once (A238) and each labelled start once.
- **The renaming statement** for taking-free laws (`research/MADE-COPIER-20261125-001B/preregistration.md:183-200`,
  settled by construction, checked exactly on 5,184 renamed runs): runs are carried by any renaming of a start.

## 5. The founding premise and the goals

- THEORY.md section 1, "Distance is the only form of information" (`publication/knotlab/THEORY.md:89-150`): the owner's
  premise and interpretation; "Paths, separation and extended distance come later, from networks of contacts" (line 85).
- A97 (under challenge), A98 (assumed: "no skipping" read as betweenness), A105 (a growth starts from the smallest knot),
  A110 (blow-up expected; read by sampling): `docs/ASSUMPTIONS.md:2679, 3042, 3308, 3515`.
- Goals G1 and G2 (by number only): G1 counts bond-distance spacing; G2 rests the three of the cubic
  growth on one count and a three-place first knot (FRESH-COUNT, FIRST-KNOT).

## 6. Where the record contradicts the brief

1. **The parity statement is already argued** (section 3): the brief's "prove or refute" is answered for laws without
   taking; what is new is only the case with three or more holders.
2. **B269's premise does not hold as stated**: near-in-states pairs that never meet occur on reached cuts (section 3), and under
   waiting laws members can still share a distinction directly after round 1 (seen before the runs: census start 133 under
   RING-LAW).
3. **"With no taking rule ... descent has no cycles beyond the start's"** is false: joins make cycles inside every part
   (a join's parents share a common knot), and the ideals of the descent order (FRESH-COUNT T1) are full of them. What is
   true is that parts that came apart are never joined again, so the parts form a tree.
4. **"The count within reach is either that of a small part or grows by doubling"** does not hold in the runs before the freeze (disclosed in the
   pre-registration): with no taking rule, counted from start knots, the two- and three-knot starts read POWER(2) under the
   cap-of-three laws, the two-share start reads POWER(2) under ordinary growth, and the rings under RING-LAW read an
   exponent of 2.8 by the doubling reading from r = 8 to 16 (a finite reading, not a limit).
5. **"Since 11 November none of what the growth makes has been read for this count"**: bond balls of grown structures were
   proved on 17 and 18 November (CUBIC, FRESH-COUNT), though not counts of knots by holder steps.
