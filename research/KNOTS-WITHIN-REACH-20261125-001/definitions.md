# Knots within reach, and the growing end: definitions

Epic `KNOTS-WITHIN-REACH-20261125-001`, ticket `KNOTS-WITHIN-REACH-20261125-001A`. Written with the
[pre-registration](../KNOTS-WITHIN-REACH-20261125-001A/preregistration.md) after the advisor's two passes. It builds on
[the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md) ("SD", by line) and
[the definitions of the study of parts that meet again](../PARTS-MEET-AGAIN-20261124-001/definitions.md) ("FD", by section
and item), and changes nothing in either. Words are the glossary's. The canonical K1–K3 test is unchanged. Every term is
numbered "KD" and is decided by a program from the structure, the birth record and the allowed states, within the bounds
of the pre-registration ("PR").

## 0. Words and symbols

- **Kept with their meaning in SD and FD**: structure, place, holder, loose, shared, live, dead, usable, barred, member,
  h(u) (usable loose count) and k(u) (barred count), met set, common knot, joinable, part, past its start, group, owing,
  short, waits, retires, join, offshoot, demand, ration, treatment, round, start, parent step, ancestor, descendant, take,
  taking rule, eligible, the choice. These symbols keep SD's meaning and no other.
- **Holder step** (glossary, "Parent step; holder step"); hs(u, v) is the number of holder steps on a shortest path. It is
  a count on what is built, given with it, like steps apart: not a bond distance, not a distance read from the allowed
  states, not an extended or metric distance. The text says how many holder steps lie between two knots, never how far
  apart they are.
- **The knot counted from**: the knot u a count is taken from. "Counted from u" is the only phrasing.
- **Symbols, one meaning each**: hs, ps, ws (holder, parent, witnessed steps); s(u) (steps from the start); s_min (least s
  of a member); ℓ(u) (end of the kept range); H (history count); P (roster count); b(t) (births in round t); S(r) (new
  knots at step r); ε(r) (exponent from r to 2r); j (a degree, 0 to 3); λ_u (loose count of a knot); σ_u (shared-place
  count of a knot); κ (pair reading of two distinctions); ρ (disagreement share); γ (between-knots reading); δ (arrival
  delay); Λ_t (the parity rules on loose distinctions). SD's D (demand) keeps its own meaning only.
- **Not used**: "ball"; "dimension" except for the program's target (a verdict is said instead); "level", "depth",
  "window", "radius", "centre", "around", "eccentricity", "nearer", "farther", "random" (a weighting is always written
  out; `random.Random` is only the name of the generator), "typical", "rare", "likely", and "most" or "some" without
  counts.

## 1. Structures and steps

1. **The holder graph**: one vertex per knot; two knots adjacent when they hold a common distinction, whatever its
   number of holders (FD 1.2). hs = ∞ with no path. Every knot is stepped through: live, dead, retired, members or not.
2. **The parent graph**: u adjacent to each of its parents (FD 1.4), either direction; ps(u, v).
3. **Steps from the start**: s(u) = the least hs(u, c) over start knots c.
4. **The witnessed graph** of the roster after round t: one vertex per member; two members adjacent when joinable (SD
   line 27). ws(u, v), ∞ between parts. It is the state-distance study's witnessed step
   (`STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001A/tree_delays.md` line 26), restricted to members.
5. **Taking-free law**: a law of SD and FD with no taking rule and no SHORT-TAKES, so that every distinction has one or two
   holders.
6. **Lemma E (argued, not refereed; check E).** Under a taking-free law, the edges of the holder graph less the edges
   joining two start knots are exactly the edges of the parent graph: a distinction shared by a knot made after round 0
   has exactly two holders, the knot that held it first and the one birth that took it, which is that knot's child. So
   the parent-step swap of runs 1 and 2 changes counts only through the start's own meetings; it is null outside them.
7. **Hub step swaps** (run 4, where distinctions can have three or more holders): (a) parent steps; (b) holder steps
   through distinctions of at most two holders only; (c) a weighted step costing m − 1 through a distinction of m holders
   (least total cost); and, per stage, the number of distinctions with each number of holders.

## 2. The history count and the roster count

1. **The history count** H(u, r), for a knot u of the structure after round t: the number of knots v of that structure
   with hs(u, v) ≤ r. **H counts the growth's history**: the knots of every round, those that have stopped growing as much
   as the members, not what exists at one round. Under a taking-free law the holder graph is the birth record read in
   both directions plus the start's own meetings (KD 1.6), so a power read on H includes one degree from the rounds.
   **Where the number of parts is fixed and the roster is the same after every round**, POWER(j) of H is read as "j − 1
   from the roster and 1 from the rounds", and only up to the roster's own greatest witnessed steps; beyond them H is
   expected to read 1. That is a reading registered where the number of parts is fixed, not a statement for all laws:
   where parts multiply (COPY-LAW) each part reads 1 or less and H need not read a power at all.
2. **The roster count** P_t(u, r), a **stage reading** at a stated round t, for a member u: the number of members of u's
   part with ws(u, v) ≤ r in the roster after round t; with, for every round, the number of parts and the members of each.
   **H and P are two readings under two names and are never added or combined.** P's verdict set: POWER(j), LINREC(k),
   RATIO(x) as for H (KD 3), read on 0 ≤ r ≤ the greatest ws from u in its part; **ALL WITHIN r** when that greatest
   number r gives fewer than j + 8 values for every j.
3. **Knots counted from, for H**: (a) every start knot; (b) made knots with s ≤ s_min/4; (c) made knots with
   ⌊s_min/2⌋ − 2 ≤ s ≤ ⌊s_min/2⌋; up to 8 of each of (b) and (c) in run 1 (16 made knots) and up to 64 of each in run 2.
   Each class is sampled uniformly without replacement from all knots of the structure after the run's last round that
   meet its condition, sorted by knot name (the weighting: each such knot once). Members are never counted from for H.
   Optionally, beside the gate and never part of it: (d) made knots with ⌊3s_min/4⌋ − 2 ≤ s ≤ ⌊3s_min/4⌋, read on their own
   kept range, in run 2 only (the counts from them use the same grown structure).
4. **Seeds.** Every sample uses `random.Random(n)` with n = int.from_bytes(sha256(text).digest(), "big"), text the UTF-8
   string `KWR|<start>|<law>|<knot law>|<class>`, where `<start>` is `census:<index in census_starts.json>` or the named
   start's key in named_starts.json; `<law>` is the law's label of PR's table (L0 … L11, T1 … T10); `<knot law>` is `nae` or
   `parity`; `<class>` is one of `b`, `c`, `d`, `members`, `knot-test`, `later-knots`, `takes:1`, `takes:2`, `shuffle`,
   `control`. The candidate list is sorted by name before sampling. Names fix which knots are drawn; under a taking-free
   law the weighting of each class does not depend on the numbering (KD 7.2).
5. **The kept range** of a knot u, after the last round t of a run under a taking-free law: 0 ≤ r ≤ ℓ(u), ℓ(u) =
   s_min − s(u), where s_min is the least s of a member after round t. When the run has **ended** (KD 3.6: stopped,
   stalled or jammed, SD lines 83–84), ℓ(u) is the greatest hs(u, v) in u's connected structure. A run under a waiting law
   whose s_min stays below 32 leaves the classes empty or the range too short; the number of such runs is reported. Under
   a taking rule there is no kept range (KD 2.7).
6. **Lemma F (argued, not refereed; check F), by induction on later rounds.** Fix the structure after round t, its
   members (each with s ≥ s_min) and a knot u with s(u) ≤ s_min. (i) For every v, s(v) ≤ s(u) + hs(u, v), so
   hs(u, v) ≥ s(v) − s(u). (ii) Claim for every t′ ≥ t: every knot made in rounds t + 1 … t′ has s ≥ s_min + 1, holds only
   distinctions of its parents and its own fresh ones, and adds no holder to any other distinction. For t′ = t + 1: a
   birth's parents are members after round t, it takes one usable loose distinction of each (held by that parent alone)
   and receives fresh ones, so it meets only its parents and s ≥ s_min + 1. For t′ + 1: the members after round t′ are
   members after round t (s ≥ s_min) or knots made in rounds t + 1 … t′ (s ≥ s_min + 1 by the claim), and the same step
   applies. (iii) So every path from u through a knot made after round t has more than s_min + 1 − s(u) − 1 = ℓ(u) holder
   steps, and no later birth adds an edge between two knots that existed after round t. Hence H(u, r) for r ≤ ℓ(u) is the
   same in every later structure of the run. It holds under RELEASE and HOLD, and is about H only.
7. **Stage reading.** Under a taking rule a birth may take a distinction held by a knot that is not its parent, so a later
   knot can lower hs between two old knots. Counts are those of the structure after the stated round. Stage verdict:
   **ALL WITHIN r at round t**: every knot of u's connected structure has hs(u, v) ≤ r.
8. **Lemma R (argued, not refereed; check R).** Under a taking-free law, s(u) is the least ps from u to a start knot
   (KD 1.6). Under RELEASE with STALL, CANCEL-OFFSHOOT or CANCEL-RETIRE, with or without FILLERS, joins of three or more
   parents and closings included, every old member gives or loses all its usable loose distinctions in each round, so a
   knot made in round t has parents made in round t − 1 and s(u) is u's round. For any connected start (the triangle
   inequality, no law needed): B(t − e(c)) ≤ H(c, t) ≤ B(t), with B(t) the number of knots with s ≤ t and e(c) the
   greatest hs from c to another start knot ("greatest steps within the start"). So, counted from a start knot, H is the
   count of knots made by round t within a shift of e(c) under those treatments (L0, L3, L4, L6, L7, L8, L9, L10, L11), and
   the count of knots with s ≤ t under waiting or holding. The record's kinds of growth (lesson 8.2) give a verdict for H
   only where the record proves the kind for that law (ordinary growth); the shift e(c) can change a verdict on a finite
   range.

## 3. Reading a count

1. **Births per round** b(t), t = 1 … T. **New knots at step r** from u: S(u, r) = H(u, r) − H(u, r − 1).
2. **POWER(j), the exact reading (primary)**, j from 0 to 3 (j = 0 allowed for constant births). A count F(r) (F = H(u, ·)
   on its kept range, or b, or P) is POWER(j) on [a, z] when F(r) = p(r) for every whole r in [a, z], p a polynomial of
   degree exactly j with rational coefficients, with at least j + 8 values on [a, z]; or the **m-phase form**, m = 2, 3 or
   4, least m first: F(mi + q) = p_q(i) for q = 0 … m − 1, each p_q of degree j with at least j + 8 values. The reading
   reports p (or the p_q) and [a, z]. For b(t), POWER(j) of b is reported as such ("births of degree j"), never as a
   reading of H; under Lemma R's treatments it bounds H counted from a start knot between B(r − e) and B(r), which is not an
   exact polynomial.
3. **LINREC(k), the exact recurrence.** Least k first, k = 1, 2, 3: F(r) = c₁F(r − 1) + … + c_kF(r − k) with rational c_i,
   fitted on the last 2k terms of the segment and **verified on at least 8 further terms** of the segment (the verified
   terms, not counting the 2k fitted); the largest root of x^k = c₁x^{k−1} + … + c_k is reported.
4. **BOUND(j), the two-sided reading (second, where not exact).** c·r^j ≤ F(r) ≤ C·r^j for every r in [a, z], with
   a ≥ 4, z ≥ 8a and C/c ≤ 2; c, C and C/c reported. For one count, z ≥ 8a and C/c ≤ 2 fix j uniquely, and they admit
   exponents within a third of j (a count growing like r^{j ± 1/3} on [a, 8a] can pass): this is said with every BOUND.
5. **RATIO(x) on [a, z]**: S(r + 1) ≥ x·S(r) for every r in [a, z − 1], with z − a ≥ 8 and **x ≥ 1.25**, x the least ratio
   on the segment, reported. A strictly rising S with a least ratio below 1.25 is UNDECIDED, "rising".
6. **Precedence and the segment rule.** A count's verdict is the first that applies, in this order, on its **final
   segment**, the longest interval ending at the end of its kept range (for a stage reading, at its greatest r) on which
   that verdict holds: **ENDED** (the run stopped, stalled or jammed, SD lines 83–84, and H reaches its whole connected
   structure within the kept range); POWER(j); LINREC(k); BOUND(j); RATIO(x); UNDECIDED ("rising" when S rises with least
   ratio below 1.25). Exact readings on earlier, disjoint segments are listed beside the verdict, nearest first, and are not
   the verdict. UNDECIDED is never reported as "no power" or "none".
7. **The swap: the doubling reading** (the reading first used, disclosed): ε(r) = log₂(H(2r)/H(r)); a run of r with
   |ε(r) − j| ≤ 0.3 for one whole j, starting at r ≥ 4 (a run that would start before 4 is trimmed to start at 4 and kept
   if it still spans a doubling), reported as [a, 2z]. Biased low at small r (C(r + 3, 3) first reads within 0.3 of 3 at
   r = 13) and blurring the end of a range (on Ring(33, 2) it reports [4, 38] for a count quadratic only to 32). A swap only.

## 4. The gate: the same power from every knot examined

1. **The gate** for one run (a law, a start, a knot law, at T rounds), knots examined as KD 2.3 (a), (b), (c), K in all:
   there is one j from 0 to 3 and one common range [a, z] with a ≥ 4, z ≥ 8a and z ≤ ℓ(u) for every knot examined, such
   that **every knot examined** u has its own constants c_u, C_u with c_u·r^j ≤ H(u, r) ≤ C_u·r^j for every r in [a, z] and
   C_u/c_u ≤ 2. It is written "the same power j from every knot examined (k of K)", with k the number that pass (k = K for
   the gate to hold).
2. **The canonical range.** z is the greatest value allowed (the least ℓ(u) over the knots examined, or less if no j and a
   work there), then a is the least value allowed for that z and j. Gates on earlier ranges (ending below the final a) are
   computed the same way on [4, a − 1] and listed apart, nearest first.
3. **The spread**, reported beside every gate that holds: max C_u / min c_u over the knots examined, in bands (at most 2;
   at most 4; above 4), on one line for start knots and one for made knots, and over all.
4. **The rule of three, per class.** Classes (b) and (c) are two weightings (each knot of its class once). When 0 of k
   sampled knots of a class fail, the share of knots **of that class** that fail is at most 3/k at 95 percent (3/64, 4.7
   percent, in run 2). Knots with other s are not examined.
5. **The scaling condition.** The run is grown again to 2T rounds; the gate must hold again with the same j and
   z(2T) ≥ 1.8·z(T); and, for the named family Ring(n, 2), z must not equal a fixed function of n across T. A gate that
   holds and fails the scaling condition is reported "same power on a range that does not lengthen" or "on a range set by
   the start".
6. **The roster count beside the gate**: P_T(u, r) from up to 8 sampled members (class `members`), the number of parts and
   the members per part, reported next to the gate's verdict and never part of it.

## 5. The growing end: readings between loose distinctions

1. **A reached stage**: the structure after round t ≥ 1 of a run.
2. **The stage weighting**: each allowed state of the structure after round t once. ρ(a, b), the **disagreement share**:
   the number of allowed states in which a and b differ divided by the number of allowed states, both counted exactly in
   integers; κ(a, b) = 1 − 2ρ(a, b). **|κ| says how strongly two distinctions are related, either sign.** The weighting
   of stages in any share over stages: each (start, law, knot law, round) once, a start being each census start once (the
   census weighting) or each labelled start once (the labelled weighting, KD 7.5). **The history weighting** (swap, on
   stages of at most 20 distinctions): μ₀ is uniform on the start's allowed states; μ_t(x) = μ_{t−1}(x′)/n_t(x′), where x′
   is x restricted to the distinctions that existed after round t − 1 and n_t(x′) the number of allowed states after round
   t that restrict to x′; the share is Σ μ_t(x) over allowed x with x_a ≠ x_b (the state-distance study's second
   weighting).
3. **Lemma N (argued, not refereed; check N).** Under not-all-equal, for knots u ≠ v holding loose distinctions a and b,
   each with at least one shared place, λ_u, λ_v their loose counts (barred included), expectations under the stage
   weighting: κ(a, b) = γ(u, v)/((2^{λ_u} − 1)(2^{λ_v} − 1)), with **the between-knots reading** γ(u, v) = E[g_u g_v],
   g_u = +1 when all of u's shared places are 0, −1 when all are 1, 0 otherwise. Every loose distinction of u has the same κ
   with every loose distinction of v, and |κ| ≤ 1/((2^{λ_u} − 1)(2^{λ_v} − 1)) (the record's bound,
   `STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001A/samples.md` lines 157–159). γ still depends on λ_u and λ_v (shared
   configurations weigh 2^λ or 2^λ − 1), and |γ_u| is bounded by how often u's shared places are all equal, which depends
   on σ_u. γ is not a share of states; it was named after the scratch runs (post hoc), and the lemma forces it.
4. **Lemma P (argued, classical, not refereed; check P).** Under parity with any number of holders, the allowed states
   form a linear space over the two-element field (the literature's binary linear code), and every pair of distinctions
   has ρ = 0 or ρ = 1/2. With every distinction held once or twice and a connected holder graph, the only rule on the loose
   distinctions (barred counted as loose) is their sum, so with three or more every pair has ρ = 1/2, and with two they are
   tied. This is about pairs of single loose distinctions under the stage weighting; "tied" is an equivalence and gives
   classes. **Λ_t**: the rules the allowed states satisfy that involve loose distinctions only (the row space of the knots'
   rules intersected with the span of the loose distinctions), reported per stage by its **rank** and its **least number of
   distinctions in one rule**, beside the number of loose distinctions.
5. **Arrival delay** δ(u, v) of two members after round t: the least d ≥ 1 such that a knot made in round t + d has an
   ancestor in {u} ∪ desc(u) and one in {v} ∪ desc(v) (a waiting member counts as its own descendant), grown on under the
   same law for at most 6 rounds and the run's knot bound. **δ = ∞** when the law is taking-free, the roster after round t
   is past its start, and u and v lie in different parts (the ring study's settled statement, `RING-IN-BALANCE-20261123-001A/
   preregistration.md` lines 95–99). **Never: growth ended** when the growth stops, stalls or jams before the descendants
   meet. Under HOLD a member may be an ancestor of another member: such pairs form the stratum "ancestor". Otherwise, not
   met within 6 rounds or the knot bound while growth goes on: **undecided**. Under L0, δ = ws by INFLUENCE-CONE's theorem
   (`INFLUENCE-CONE-20261120-001/decision.md` line 22, referee pending), so there "against δ" and "against ws" are one test.
6. **The orders, with a fixed direction.** For a stage, a reading X of each pair of members (one loose distinction of each;
   by Lemma N the choice does not matter) and a key Y:
   - **more strongly related** means larger |κ| (primary), or larger |γ|; for the swap ρ, smaller ρ, with the count of pairs
     by the sign of κ at each ws reported beside it (κ is negative at one witnessed step, so the ρ order fails there by sign
     alone);
   - **sooner** means smaller δ; **fewer steps** means smaller ws or smaller hs.
   For two pairs P, Q with Y decided for both: **concordant** when P is strictly more strongly related and strictly sooner
   (or strictly less and strictly later), **discordant** when strictly more strongly related and strictly later, **tied**
   when X or Y is equal (exact integers). Per stage: the counts of concordant, discordant and tied comparisons, and
   Kendall's S = concordant − discordant.
7. **The member shuffle** (the reference): within each part, every permutation of the part's members applied to the key
   Y (δ of the permuted pair), X fixed; S's exact distribution over all permutations when every part has at most 8 members,
   otherwise over 2,000 permutations drawn with seed class `shuffle`. The pair shuffle (Y permuted among pairs, which share
   members) is reported under its own name, with its variance, as descriptive only.
8. **Strata**, reported apart and never pooled: (i) pairs in one part with δ decided; (ii) δ = ∞; (iii) never: growth
   ended; (iv) one part, δ undecided; (v) ancestor. Inside (i), **three nested counts** of comparisons: (i-1) all;
   (i-2) those whose two pairs have the same multiset {λ_u, λ_v} (equal loose counts); (i-3) those with equal loose counts
   and the same multiset {σ_u, σ_v} (equal shared-place counts). With equal loose counts the |κ| order equals the |γ| order.
9. **Headline levels.** A discordance in (i-2) is "not loose counts"; in (i-3), "not loose or shared-place counts". A
   discordance only in (i-1) is "explained by loose counts". Per law and knot law, the smallest stage at each level is
   reported (in the order: number of knots, number of distinctions, round; the start's label is a label only), with that
   stage's S beside it.
10. **The within-part law L-W**: on every stage, for pairs of stratum (i), |γ| strictly larger whenever ws is strictly
    smaller; reported with the number of stages that test it with at least one untied comparison.
11. **The betweenness test** (A98's reading): for members u, v, w of one part with ws(u, v) + ws(v, w) = ws(u, w),
    |γ(u, w)| ≤ min(|γ(u, v)|, |γ(v, w)|); triples tested and failing, stages tested and failing.

## 6. The knot test

1. Under parity, both methods of FD 7 (ranks, kernel); under not-all-equal, the birth method on every knot made after
   round 0 and the direct test on every knot of at most 12 places, compared (FD 7). The parity closing form is IMPLIED
   (FD 2.8) for every law, taking rules included.
2. **Which knots**: every start knot of every run; **run 4**: every knot of the structure after round 25 (or the last
   round if earlier), and 100 knots made after round 25 sampled uniformly (class `later-knots`), each tested by the birth
   method at its birth under not-all-equal and by both methods on the last structure under parity; **run 5**: every knot of
   every stage computed, each once at its birth under not-all-equal (its verdict is then fixed, FD 7) and on the stage's
   structure under parity; **runs 1 and 2**: the class argument (under parity a knot that receives a fresh distinction
   passes and keeps passing with at most two holders, `RING-IN-BALANCE-20261123-001A/preregistration.md` lines 102–105,
   referee pending; under not-all-equal a knot's verdict is fixed at its birth when every birth receives a fresh
   distinction, FD 7), and in run 3 a sample of 200 knots per run (class `knot-test`) on run 2's runs and on run 1's runs of
   three- and four-knot starts. **Five-knot runs of run 1 get no test**, and the report says so.
3. **Wording of every result**: "n of N knots tested, all passed; a failing share above 3/n is excluded at 95%; untested
   knots are not tested and rest on the argued statement." Failures are named (kind, parents, round). Shares over runs are
   given twice only for tested runs: over all tested runs, and over tested runs with no failing knot (a conditioned
   weighting, named).

## 7. Laws, numberings, weightings and caps

1. **Uniform takes**: each take of Q, MET, STEPS-1 and STEPS-2 chooses uniformly among its eligible candidates,
   independently, drawn in birth order from the candidate list sorted by name with `random.Random` seeded by KD 2.4 with
   class `takes:1` or `takes:2` (the two seeds of run 4). CARRY (T9, T10) is defined by "oldest" and runs under OLDEST
   only; T9 and T10 are never pooled with T1–T8 in a share.
2. **Names**: under a taking-free law every count is the same under every numbering of a start (the copier study's
   Settled 1, checked there); names fix which knots are sampled, the order in which takes use the seed, and the labels.
3. **The 4n numberings** of a start with n distinctions (named 0 … n − 1 by FD 2.1) and m knots: for each k = 0 … n − 1,
   the renaming i ↦ (i + k) mod n, or i ↦ (n − 1 − i + k) mod n, each with the knots in their given order or reversed.
   **The 200 further numberings**: from `random.Random(202611252)`, for each in turn, `shuffle(list(range(n)))` gives the
   new name of each distinction and then `shuffle(list(range(m)))` the new order of knots.
4. **The guard** (FD's engine's, multiplied by ten, as numbers): a round is not read, and the run stops, when its count of
   joinable pairs exceeds 200,000, of groups 200,000, of births 200,000, of distinctions 4,000,000, of incidences
   20,000,000, or of maximal cliques examined 2,000,000.
5. **The labelled weighting**: each labelled start once, that is, a census start of n knots weighs n!/|A|, where |A| is the
   number of permutations of its knots that keep its meeting graph and its tuple of loose counts (the number of distinct
   labellings of its knots); the weights are in census_starts.json (`w_labelled`). **Estimators of a share in run 1**:
   census weighting, (count among the 219 three- and four-knot starts + 3.157 × count among the 1,000 sampled five-knot
   starts) / 3,376; labelled weighting, (Σ w over the 219 + 3.157 × Σ w over the sample, both over starts with the verdict)
   / (the same over all starts); with the effective sample size (Σw)²/Σw² of the sample stated. Under parity the starts
   failing the knot test at round 0 are left out of both numerator and denominator (3,344 in the census).
6. **The stage cap of run 5** (count-based, name-free): a stage is computed when it has at most 30 members and at most 50
   shared distinctions; every other stage is "not run" and listed with its counts. A stage within the cap that takes more
   than 60 s of process time is "not finished" and listed (none in the scratch).
7. **The checks** (engine checks, each passing before the runs that use it): check E (KD 1.6, every structure of runs 1
   and 2); check F (KD 2.6: H after round t and after round t + 10 agree on the kept range, every knot counted from in run
   2); check R (KD 2.8, both parts, every run of run 2 under its treatments); check N (KD 5.3, every stage of run 5 with at
   most 20 distinctions, by enumeration of every state); check P (KD 5.4, every stage of run 4 under parity); check I (the
   engine's integer counts against enumeration on every stage of at most 20 distinctions).

## 8. Controls (built by hand, supplied; files in named_starts.json, "controls")

1. **Ring of knots** R_400 (knot i holds i − 1, i mod 400 and one loose): every knot examined, range end 64: H = 2r + 1;
   POWER(1); the gate holds with j = 1 on [4, 64].
2. **Branching** T_12 (the holder graph is the tree in which every knot meets three, 12 steps from the root, knot 0):
   counted from the root, H = 3·2^r − 2 on [0, 12]; S reads LINREC(1) with root 2 (2 terms fitted, 10 verified).
3. **Six-regular weave** W_99 (drawn, hand-built: the six-regular one-pair weave of 99 × 99, two knots per square of the
   drawn grid): 16 knots examined (class `control`), range end 32: H = 6r² + 6r + 1; the gate holds with j = 2 on [4, 32].
4. **The fixed ration of three from one knot** (L8 from the start [[0, 1, 2]], 65 rounds): b(t) = C(t + 2, 2) (births of
   degree 2 from round 1), H counted from the start knot = C(r + 3, 3), POWER(3) on [0, 64].
5. **Negative control for the gate**: the comb (the literature's comb; hand-built): a chain of 64 knots (the spine), and
   from each spine knot a chain of 64 knots, every knot topped up to three places. Knots examined: every spine knot, the far
   end of every leg, and the 32nd knot of every leg (192 knots); range end 63. Counted from the first spine knot H =
   C(r + 2, 2), from a far leg end H = r + 1, for r ≤ 63. The gate must fail (no j from every knot examined).
6. **Positive control for the order test**: T_12 under not-all-equal (every knot three places); every pair of leaves: κ
   equals the product formula of `STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001A/tree_delays.md` lines 9–14 exactly, |κ|
   is strictly smaller when hs is larger, and the order test against hs counts no discordant comparison.
7. **A known tie**: two pairs of leaves of T_12 with equal hs have equal κ exactly; the order test counts them tied.
8. **The bare rings** Ring(n, 2), odd n ≥ 5 (n = 5, 7, 9, 11, 15, 21, 33), grown under L0, a family whose short range is
   set by the start: counted from a made knot of round t ≥ n with ℓ ≥ n, H = 2r² + 2r + 1 for r ≤ n − 1 and n(2r + 1) for
   r ≥ n (the step from n − 1 to n is 3n − 1). Counted from a start knot, H = 2r² + 2r + 1 for r ≤ (n − 1)/2, then rises by
   n + 1 a step to (r + 1)² at r = n − 1, then by n a step (seen for n = 15 and 33); so from a start knot the count is not
   POWER(2) on [4, n − 1] (on Ring(33, 2) its own C/c there is 2.41). Each knot made by the bare ring is fixed by two whole numbers, its first and last start knot
   in the order i, i + 2, i + 4, … of the joins, and a holder step changes one of them by one.

## 9. What is supplied by hand (scaffolds)

Everything SD line 157 and FD 8 list for the laws used; and here: the holder step; stepping through dead and retired
knots; the members as the growing end; the classes of knots counted from and their sampling; the readings of KD 3 and
their precedence; the gate's thresholds (a ≥ 4, z ≥ 8a, C_u/c_u ≤ 2, 1.8); the RATIO floor 1.25; the kept-range rule;
the bounds and the guard; the census weightings and their estimators; the stage weighting; the history weighting; γ (post
hoc); the delay horizon; the order rule, the strata and the member shuffle; the stage cap; the controls; the order of
running. Each has a registered swap in PR.
