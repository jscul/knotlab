You are the design advisor for a pre-registered computational study in a research program on "knot growth". This is the SECOND look before the freeze on a study of how many knots lie within reach of a knot in what the growth makes, and whether the growing end carries a distance of its own. You reviewed its first drafts cold and said "freeze after listed changes, with a second look at KD 2–3 and 5.6", eleven required. You do not remember that review; the drafter's account of what it changed, item by item, is part (5) below. You have no tools; everything is below: (1) my questions; (2) the claim, second version; (3) the definitions, second version ("KD"); (4) the pre-registration, second version; (5) the drafter's account of the changes; (6) the drafter's report to me, with its seven questions for you; (7) the definitions of the study of parts that meet again ("FD"); (8) the shared definitions ("SD"), with line numbers.

Your first review's main point was that N(u, r), the knots within r holder steps of u through everything built, is a count of the growth's HISTORY, not of what exists at one round; that the roster at a stated round must be a separate reading; that the gate for "the same power from every knot examined" must be a two-sided bound on a common range that lengthens with the rounds; that the exact polynomial reading should be primary; and that the knot test belongs on the runs with taking rules.

The standard is unchanged: the claim stated before it is tested; laws fixed first; every added rule, weighting, reference and hand-built start a scaffold with its swap; supplied or made said plainly; nothing called typical, rare or likely without its weighting; no claim about physical space; words from the glossary, one word for one meaning, and no word from a space of two or three dimensions for the program's own objects ("dimension" only for the target; otherwise the verdict is said). The owner's standing rule on compute (25 November 2026): spend compute in proportion to what a result is worth; a run should finish in about an hour on at most 6 processes; a longer one is cut to a prefix or a seeded sample and what was not run is reported as "not run"; an exception only for a run that is really important at full size.

## What I need from you (answer under these numbers; short lines; no preamble)

1. **KD 2 and KD 3 as now written**: the history count, the roster count, the kept range, the classes of knot counted from, the exact reading (a polynomial on a range, with at least D + 8 values; the two-phase form; the reading on births per round), the two-sided bound, the ratio and linear-recurrence readings in place of "outgrows", the precedence rule, and the one gate. Anything still undefined, ambiguous, contradictory between the claim, KD and the pre-registration, or impossible to implement by a helper who has not seen the prototype? Answer the drafter's questions 1 to 4.
2. **KD 5.6 and the growing end**: the fixed directions for each reading; the headline rule (a disagreement is a headline only if it holds under the between-knots reading or among pairs with equal loose counts); the strata; the shuffle reference; integer arithmetic. Answer the drafter's questions 5 and 6. The drafter reports that your guess about the smallest disagreement was wrong (all three members hold two loose distinctions, and the disagreement survives the between-knots reading) while in aggregate you were right (discordant pairs fall from 17,448 to 5,438 under that reading, and to 201 among pairs with equal loose counts). What is the honest registered statement about how much of the disagreement is loose counts?
3. **The six advisor items not applied as worded** (the report's list): right in each case? In particular the knot test cut to the structure after round 25 in the run with taking rules (the drafter's question 7), 8 sampled made knots per class except where the gate is read, and the exact numbering check registered but untimed.
4. **Section 7's table** was computed on the 64 scratch starts: the two starts that read power 3 under ordinary growth read 2 under the cap of three; 25 that stall under ordinary growth read 2 under the cap; 56 of 61 runs under the cap have a fixed number of parts whose largest gains one or two members a round. The drafter concludes "the law sets the 2, on this range: 1 from a part that lengthens and 1 from the rounds". Is that the right reading, and is it worded within what 64 starts and 40 rounds show? What should the registered prediction be, and what would refute it?
5. **Value, under the compute rule.** After the changes, what does this study add that the record did not have (the record counts knots by round as a power of the round, and proved one count within reach from one knot under a fixed ration)? Is every registered run worth its hour? Name any run you would cut or make conditional, and say whether the study is the right size.
6. **Anything in the second versions that is still wrong**: a prediction true by implication, over-pinned or undecidable; a bound or share mis-stated for a sample; a sentence that says more than a finite count can; a word that breaks the rules (check "kept range", "the knot counted from", RATIO, LINREC, "between-knots reading", and any word from a space of two or three dimensions).
7. **The sentences for the owner** at the end of the drafter's report: correct as written? Rewrite any that is not, and add the one sentence that says what section 7's table found.
8. **Verdict.** Freeze as it is; freeze with listed sentence-level fixes that the thread can apply; or another round. Required fixes in order of importance, then optional.



# (2) The claim, second version

# Claim: how many knots lie within reach, and whether the growing end carries a distance of its own (second version)

Epic `KNOTS-WITHIN-REACH-20261125-001` (sub-goals B261 and B269; goals G1 and G2 with G5; assumptions A110, A97, A98,
A105). Second version, 25 November 2026 (UTC), after the advisor's cold review; written before any registered run.
Definitions: `definitions_v2.md` ("KD"). Law, pattern, clock and weighting are kept apart: the laws are rules we supply;
the structures they build are patterns; nothing here is a clock; every share names its weighting.

## 1. The owner's words, and how they are read

The owner asked (24 November 2026, Pacific time): "Could you work your way through all 4 of these? You can work in
parallel." The direction taken here, as the thread put it to him: "Space and dimension from the growth (goals G1, G2) ...
Two leads sit in the backlog: how many knots lie within reach, and whether the growing end carries a distance of its
own." Behind both stand his founding premise, "Distance is the only form of information" (A97, a reading under
challenge), his "if you're at 3 on the number line, you can't just skip 4 to get to 5, so there is an order" (A98's
reading), and his direction that blow-up is expected and is read by sampling (A110).

How the thread reads them:

- **The count is of the growth's history, not of what exists at one round.** "The knots within r steps of a knot" is
  read as the history count H(u, r): every knot of every round within r holder steps of u, the knots that have stopped
  growing as much as the members (KD 2.1). Under a law with no taking rule the holder graph is the birth record read in
  both directions, plus the start's own meetings, so **a power of H always includes one degree from the rounds: over a
  roster whose size does not change, POWER(j) of H is "j − 1 from the roster and 1 from the rounds"**. The bare ring
  shows it: the roster after every round is the same ring of n knots, and its "2" is 1 from the supplied ring and 1 from
  the rounds run.
- **What exists at one round** is read separately, by **the roster count** P_t(u, r): the members of u's part within r
  witnessed steps in the roster after round t, a stage reading, with the number of parts and the members per part beside
  it (KD 2.2). H and P are never added or compared as one count.
- **"A space with a dimension"** is the program's target, not a verdict. The verdict that would bear on it: the same
  power j from every knot examined, as a two-sided bound c·r^j ≤ H ≤ C·r^j on one common range, with a range that
  lengthens when the rounds double and is not set by the start's size (KD 4). Anything less is reported as its verdict
  (POWER(j) on [a, z] counted from a stated knot, and so on), never as a dimension.
- **"The growing end carries a distance of its own"** = among members of one part, the share of allowed states (each
  allowed state of the structure after round t once) in which a loose distinction of one member and one of another
  differ is ordered as the members' witnessed steps and their arrival delay are: fewer steps or sooner never farther in
  the states (KD 5.6). The share ρ is always a pseudo-distance (a mean of 0/1 differences), so "carries a distance" is
  trivially true; the questions are whether it is graded beyond the members' own loose counts and whether it keeps the
  order of steps and of delay.

The literature's name for H is volume growth (the literature's, marked). Nothing here is named by space, and no claim is
made about physical space or time, living things or minds.

## 2. The laws, fixed first

| # | Law (SD and FD names) | Added by hand beyond ordinary growth |
| --- | --- | --- |
| L0 | ORDINARY: (ORD, STALL, RELEASE) | nothing beyond the complete round (A104) |
| L1 | RING-LAW: (CAP-3, CANCEL-WAIT, RELEASE) | a cap of three fresh distinctions, waiting, release (A224) |
| L2 | RING-LAW with FILLERS | as L1, and fresh distinctions beyond demand barred |
| L3, L4, L5 | COPY-LAW(t) = (FLOOR1, t, RELEASE), t = RETIRE, OFFSHOOT, WAIT | enough for three places and never none; the treatment |
| L6, L7 | CAP-3(t) = (CAP-3, t, RELEASE), t = RETIRE, OFFSHOOT | the cap; the treatment |
| L8 | RATION-3 with STALL (FRESH-COUNT's one count for every birth) | a fixed three fresh distinctions |
| T1–T8 | taking rule Q, MET, STEPS-1 or STEPS-2 (FD 3.3), with uniform takes, on CAP-3(RETIRE) (T1–T4) or on COPY-LAW(RETIRE) (T5–T8) | a taking rule; the weighting of takes (each candidate equally) |
| T9, T10 | CARRY on CAP-3(RETIRE) and on COPY-LAW(RETIRE), under OLDEST only (CARRY is defined by a name and has no uniform form) | a taking rule chosen by name |

The rival joins of the first version (L9) are cut: they are not defined in SD, FD or KD, and the record proves them
inactive on every reached cut (`STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001A/rival_joins.md` line 9). Swaps (named
starts): HOLD for RELEASE under L3 and L6; caps of 2 and 4 under L1 and L6; OLDEST and NEWEST for uniform takes under
T1–T8, with the 4n numberings. Knot laws: not-all-equal and parity throughout; the parity closing form is IMPLIED.

## 3. The claims (each decided by a program; class of laws, starts and knots counted from stated)

**Claim 1, counted from start knots (L0–L8).** H counted from a start knot is the count of knots made by round r within
a shift of the greatest steps within the start (KD 2.7, Lemma R, argued, not refereed), under the treatments STALL,
CANCEL-OFFSHOOT and CANCEL-RETIRE; from a start knot it says only how fast births grow. **Claimed**: on every census start
of three and four knots (219, exhaustive) and on the first 1,000 five-knot starts of the registered order (a uniform
sample of the 3,157), the verdict of H from every start knot and the exact reading of b(t), under each of L0–L8 and each
knot law, with shares under the census weighting and the labelled weighting (KD 5.2), and the start-by-start table of the
verdict under L0 against the verdicts under L1, L6 and L7, with b(t) split by part.

**Claim 2, the same power from every knot examined (L0–L8).** **Claimed**: for each run of claim 1's family, whether the
gate of KD 4 holds, with its j, [a, z], c, C, C/c and k of K, and whether the scaling condition holds; and the roster count
beside it. The bare ring family is the registered case where the gate holds on a range set by the start: counted from a
knot made at round t ≥ n, H = 2r² + 2r + 1 for r ≤ n − 1 and n(2r + 1) for r ≥ n, odd n ≥ 5 (argued in the sketch below,
seen for n = 5, 9, 15, 21). "Each knot of a bare ring's history is fixed by two whole numbers, its first and last start
knot, and a step changes one by one. The count is the literature's count for two such numbers. One comes from the supplied
ring, hence the range n − 1; the other from the number of rounds run. The roster never changes; the law made nothing
here."

**Claim 3, laws with a taking rule (T1–T10).** **Claimed** (stage readings, KD 2.6): at rounds 25, 50 and 100 of each run,
the knot count, the greatest holder steps from each start knot, the same under the hub swaps of KD 1.7 (a), (b), (c), the
holder-number distribution, and the base law's greatest holder steps at the same round. The verdict **"held by hubs"** is
given when the knot count at round 100 is at least twice that at round 50 while the greatest holder steps from every start
knot do not rise from round 50 to 100; it is qualified "the hubs make it so" when it fails under swap (b) or (c).

**Claim 4, the growing end under parity.** **Argued** (Lemma P, KD 5.4): under parity every pair of distinctions has
ρ = 0 or 1/2, with any number of holders; with at most two holders and a connected holder graph, every pair of loose
distinctions has ρ = 1/2 when there are three or more (the record's statement, argued, referee pending, for laws without
taking). This is about pairs of single loose distinctions under the stage weighting; "tied" gives classes, not a graded
reading. **Claimed** (computed, stage readings, existence only): under T1–T10, per stage, the dimension and least weight of
Λ_t (the parity rules on loose distinctions alone), the tied pairs, which knots hold them, and the holder steps between
those knots.

**Claim 5, the growing end under not-all-equal (L0–L8).** **Argued** (Lemma N, KD 5.3): one reading between two knots, with
|κ| ≤ 1/((2^{λ_u} − 1)(2^{λ_v} − 1)). **Claimed** (computed, integer arithmetic): on the reached stages of rounds 1 to 3 of
every census start (rounds 1 to 4 for three- and four-knot starts), within the stage cap (KD 7.3): per stage and per law,
concordant, discordant and tied counts of |κ| and of |γ| against δ, ws and hs in stratum (i), Kendall's S with its exact
permutation reference; the strata apart; the smallest stage with a headline disagreement (KD 5.8), or none; L-W; the
betweenness test.

The first version's C6 (a lasting source nearby) is dropped: under STALL a short member of the source stalls every part,
and under parity barring switches the closing off everywhere (SD lines 73–74), so the argued statement holds only for
non-STALL treatments with no closing in either run, and then it says only that the source adds its own descendants. A
later ticket can take it up under taking rules.

## 4. What is settled by argument (stated, checked, not findings)

Lemmas E, F, R, N, P (KD 1.6, 2.5, 2.7, 5.3, 5.4), each with its checks (KD 7.4); the renaming statement for taking-free laws
(the copier study's Settled 1), from which counts of L0–L8 hold under every numbering and the sampled classes have the same
weighting under every numbering; the uniform-takes statement (pre-registration, Settled 3), checked exactly with every
choice enumerated on small starts; the agreement of the knot laws up to a closing; INFLUENCE-CONE's theorem that under
ordinary growth two members first share a descendant after exactly their witnessed steps (referee pending), checked, not
assumed for other laws.

## 5. Verdicts, as questions with exclusive answers

1. For each law, knot law, start and knot counted from: the verdict of H on its final segment, by the precedence of KD 3.6
   (ENDED, POWER(j), LINREC(k), BOUND(j), RATIO(x), UNDECIDED), with earlier segments listed apart. Shares over starts
   under each weighting, the denominators stated (KD 5.2; under parity the 3,344 starts passing the knot test, under
   not-all-equal the 3,376).
2. For each run: does the gate hold (the same power j from every knot examined, k of K), and does the scaling condition
   hold? Yes with both / gate only / no / undecided (the gate's range shorter than [4, 32]). Over the family: the number
   of runs in each answer and its share under each weighting.
3. Under T1–T10: held by hubs / held by hubs only under holder steps (the hubs make it so) / not held / ended.
4. Under parity: does any stage of T1–T10 have Λ_t of least weight below the number of its loose distinctions (a rule on a
   proper subset)? Yes (smallest stage, least weight, dimension) / no on every stage examined.
5. Under not-all-equal, per law: the smallest stage with a headline disagreement against δ / none; the same against ws
   and hs; L-W holds on every stage that tests it / fails (smallest stage); betweenness: failing triples k of K.

## 6. What a result would and would not show

- A POWER(j) of H counted from a knot says that the knots of the growth's history within r holder steps of that knot
  number p(r), a polynomial of degree j, on the stated segment of a finite structure. One degree of it comes from the
  rounds. It is not a bond distance or any distance read from the allowed states.
- **No limit object.** Every count is of a finite structure at its last round. Nothing is said of a structure "in the
  limit", and the kept range says only that later rounds do not change the count up to its end.
- **The count depends on the knot counted from.** A power read from start knots need not hold from made knots; only the
  gate's form (every knot examined, one common range, shared constants, k of K) says more, and even it covers only the
  knots examined.
- **The birth order read in both directions gives the roster's exponent plus one.** Under a law with no taking rule H is
  the birth record's two-way neighbourhood; so a POWER(j) of H is expected to be the roster's own exponent, read by P,
  plus one from the rounds. The study reads the roster (P) and the history (H) apart; it does not read the birth order by
  chains and intervals, which a later study could.
- With hubs (taking rules) the step convention changes the counts by more than a bounded factor; claim 3's verdicts are
  given under each of the four steps, and "the hubs make it so" says which.
- A disagreement of orders on a stage shows that the disagreement share is not an order-keeping reading of steps or delay
  there; how much of it is the members' own loose counts is said (KD 5.8). Agreement on every stage examined would be a
  finite census under the cap, not a theorem.
- Under parity, Lemma P says pairs of loose distinctions are tied or unrelated; a rule of Λ_t on a proper subset shows a
  rule among a few loose distinctions exists under a taking rule, not that it is a distance.


# (3) The definitions, second version (KD)

# Knots within reach, and the growing end: definitions (second version)

Epic `KNOTS-WITHIN-REACH-20261125-001`. Second version, 25 November 2026 (UTC), after the advisor's cold review
(`reach_advisor/answer.md`, "freeze after listed changes, with a second look at KD 2–3 and 5.6"); not frozen. It builds on
[the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md) ("SD", by line) and
[the definitions of the study of parts that meet again](../PARTS-MEET-AGAIN-20261124-001/definitions.md) ("FD", by section
and item), and changes nothing in either. Words are the glossary's. The canonical K1–K3 test is unchanged. Every term is
numbered "KD" and is decided by a program from the structure, the birth record and the allowed states, within the bounds
of the pre-registration. What changed from the first version is listed in `changes_v2.md`.

## 0. Words and symbols

- **Kept with their meaning in SD and FD**: structure, place, holder, loose, shared, live, dead, usable, barred, member,
  h(u) (usable loose count) and k(u) (barred count), met set, common knot, joinable, part, past its start, group, owing,
  short, waits, retires, join, offshoot, demand, ration, treatment, round, start, parent step, ancestor, descendant, take,
  taking rule, eligible, the choice. These symbols keep SD's meaning and no other.
- **Holder step** (glossary, "Parent step; holder step"). The count of holder steps between two knots is written
  **hs(u, v)**. It is a count on what is built, given with it, like steps apart. It is not a bond distance, not a
  distance read from the allowed states, and not an extended or metric distance. The text never writes "distance" for it
  and never says how "far apart" two knots are; it says how many holder steps lie between them.
- **The knot counted from**: the knot u a count is taken from (the first version's "centre"). "Counted from u" replaces
  "around u". C6's "marked knot" of the first version is withdrawn with C6.
- **New symbols here**, one meaning each: hs (holder steps), ps (parent steps), ws (witnessed steps), s(u) (steps from the
  start), s_min (least s of a member), ℓ(u) (end of the kept range), H (history count), P (roster count), b(t) (births in
  round t), S(r) (new knots at step r), ε(r) (exponent from r to 2r), j (a degree), λ_u (loose count of a knot), κ (pair
  reading of two distinctions), ρ (disagreement share), γ (between-knots reading), δ (arrival delay), Λ_t (the parity
  rules on loose distinctions). SD's D (demand), FD's choice names and the copier study's W1–W4 keep their own meanings
  and are not used for anything here.
- **Not used**: "ball" (the glossary's ball is measured by bond distance); "dimension" except for the program's target
  ("dimension" is never a verdict: the verdict is said, POWER(j) on a stated range); "level", "depth", "window",
  "radius" for a kept range, "centre", "around", "eccentricity", "rate" for anything but the disagreement share, "random"
  (a weighting is always written out), "typical", "rare", "likely".

## 1. Structures and steps

1. **The holder graph** of a structure: one vertex per knot; two knots adjacent when they hold a common distinction,
   whatever its number of holders (FD 1.2). hs(u, v) is its count of edges on a shortest path; hs = ∞ with no path.
   Every knot is stepped through: live, dead, retired, members or not.
2. **The parent graph**: u adjacent to each of its parents (FD 1.4), either direction; ps(u, v).
3. **Steps from the start**: s(u) = the least hs(u, c) over start knots c.
4. **The witnessed graph** of the roster after round t: one vertex per member; two members adjacent when joinable (SD
   line 27). ws(u, v), ∞ between parts. This is the state-distance study's witnessed step
   (`STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001A/tree_delays.md` line 26), restricted to members.
5. **Taking-free law**: a law of SD and FD with no taking rule and no SHORT-TAKES, so that every distinction has one or two
   holders.
6. **The identity of the two graphs (Lemma E, argued, not refereed; check E).** Under a taking-free law, the edges of the
   holder graph less the edges joining two start knots are exactly the edges of the parent graph. Reason: a distinction
   shared by a knot made after round 0 has exactly two holders, the knot that held it first and the one birth that took
   it, which is that knot's child. Check E compares the two edge sets on every structure of runs 1 and 2.
7. **Hub step swaps** (registered for run 4, where distinctions can have three or more holders): (a) parent steps;
   (b) holder steps through distinctions of at most two holders only; (c) a weighted step, costing m − 1 through a
   distinction of m holders (least total cost); and, per stage, the number of distinctions with each number of holders.

## 2. The history count and the roster count (second look requested)

1. **The history count** H(u, r), for a knot u of the structure after round t and r ≥ 0: the number of knots v of that
   structure with hs(u, v) ≤ r. **H counts the growth's history**: the knots of every round, those that have stopped
   growing as much as the members, and not what exists at one round. Under a taking-free law the holder graph is the
   birth record read in both directions, plus the start's own meetings (KD 1.6), so a power read on H always includes
   one degree from the rounds: over a roster whose size does not change, a reading POWER(j) of H is "j − 1 from the
   roster and 1 from the rounds". H(u, 0) = 1.
2. **The roster count** P_t(u, r), a **stage reading** at a stated round t, for a member u: the number of members of u's
   part with ws(u, v) ≤ r in the roster after round t. Beside it, for every round: the number of parts and the number of
   members of each part. **H and P are two readings under two names and are never added, combined or compared as one
   count.** (The first version's member count M, members within r holder steps, is withdrawn: every member has s ≥ s_min,
   so M(u, r) = 0 for r < ℓ(u) and M reads only the knots at the end of the kept range; and its membership changes at the
   next round, so Lemma F does not hold for it.)
3. **Knots counted from**, for H: (a) every start knot; (b) made knots with s ≤ s_min/4; (c) made knots with
   |s − ⌊s_min/2⌋| ≤ 1; up to 8 of each class in run 1 and up to 64 of each class in run 2, where the gate is read (with
   0 of 128 failing, the failing share is at most 3/128, about 2.3 percent, at 95 percent). Each class is sampled uniformly without replacement from all knots of the structure after
   the last round of the run that meet its condition (the weighting: each such knot once). Seeds: the integer value,
   big-endian, of SHA-256 of `KWR|<start label>|<law>|<knot law>|<class>`, fed to Python's `random.Random`, sampling from
   the class sorted by knot name. The names fix which knots are drawn; under a taking-free law the weighting over the
   class does not depend on the numbering (KD 7.2). Members are never knots counted from for H (their kept range is 0).
4. **The kept range** of a knot u counted from, for H, after the last round t of a run under a taking-free law that has
   not ended: 0 ≤ r ≤ ℓ(u) with ℓ(u) = s_min − s(u), where s_min is the least s of a member after round t. When the run
   has ended (no member), ℓ(u) is the greatest hs(u, v) in u's connected structure. For laws with a taking rule there is
   no kept range: every count is a stage reading (KD 2.6).
5. **Lemma F (argued, not refereed; check F).** Under a taking-free law a knot made after round t meets only its parents,
   which are members after round t, so its s is at least s_min + 1 and every path from u through it has more than
   ℓ(u) holder steps. Hence H(u, r) for r ≤ ℓ(u) is the same in every later structure of the run. This holds under RELEASE
   and HOLD. It is about H only.
6. **Stage reading.** Under a taking rule a birth may take a distinction held by a knot that is not its parent, so a later
   knot can lower hs between two old knots. Counts are those of the structure after the stated round, and every sentence
   says so. Stage verdict: **ALL WITHIN r at round t**: every knot of u's connected structure has hs(u, v) ≤ r.
7. **Lemma R (argued, not refereed; check R).** Under a taking-free law, s(u) equals the least ps from u to a start knot
   (KD 1.6). Under RELEASE with STALL, CANCEL-OFFSHOOT or CANCEL-RETIRE, with or without FILLERS, joins of three or more
   parents and closings included, every old member gives or loses all its usable loose distinctions in each round, so
   the parents of a knot made in round t were made in round t − 1 and s(u) is u's round. Separately, for any connected
   start (the triangle inequality, no law needed): B(t − e(c)) ≤ H(c, t) ≤ B(t), where B(t) is the number of knots with
   s ≤ t and e(c) is the greatest hs from c to another start knot ("greatest steps within the start"). So counted from a
   start knot, H is the count of knots made by round t within a shift of e(c), under those treatments; under waiting or
   holding it is the count of knots with s ≤ t. The record's kinds of growth (lesson 8.2) give a verdict for H counted
   from start knots only where the record proves the kind for that law (ordinary growth); the shift e(c) can also change
   a verdict on a finite range.

## 3. Reading a power (second look requested)

1. **Births per round** b(t), t = 1 .. T: the number of knots made in round t. **New knots at step r** from u:
   S(u, r) = H(u, r) − H(u, r − 1).
2. **POWER(j), the exact reading (primary).** A count F(r) (F = H(u, ·) on its kept range, or b) is POWER(j) on [a, z]
   when F(r) = p(r) for every r in [a, z], p a polynomial of degree exactly j with rational coefficients, with at least
   j + 8 values on [a, z]; or, the **two-phase form**, F(2i) = p₀(i) and F(2i + 1) = p₁(i) with p₀, p₁ of degree j, each
   with at least j + 8 values (for parity effects of the rounds). The reading reports p (or p₀, p₁) and [a, z]; [a, z] is
   the longest interval ending at the end of the kept range on which it holds (the segment rule, KD 3.6). For b(t),
   POWER(j) of b reads POWER(j + 1) for H counted from start knots under Lemma R's treatments, and is reported as such,
   not as a reading of H.
3. **LINREC(k), the exact recurrence.** S (or b) satisfies F(r) = c₁F(r − 1) + … + c_kF(r − k), k ≤ 3, rational c_i,
   fitted on the last 2k terms of the segment and verified on every other term of it, at least 8; the largest root of
   x^k = c₁x^{k−1} + … + c_k is reported. A LINREC with a root above 1 says the new knots grow at least as fast as that
   root on the segment; nothing is said beyond it.
4. **BOUND(j), the two-sided reading (second, where not exact).** c·r^j ≤ F(r) ≤ C·r^j for every r in [a, z], z ≥ 8a,
   a ≥ 4, with C/c ≤ 2 (registered limit); c, C and C/c reported.
5. **RATIO(x) on [a, z]**: S(r + 1) ≥ x·S(r) for every r in [a, z − 1], with z − a ≥ 8 and x > 1, x the least ratio on the
   segment, reported. It replaces the first version's OUTGROWS. "Faster than any power" is never read from a count.
6. **Precedence and the segment rule** (so that the answers of verdict 1 exclude one another). A count's verdict is the
   first that applies, in this order, on its **final segment**, the longest interval ending at the end of its kept range
   on which that verdict holds: ENDED (the run ended and H reaches its whole connected structure within the kept range);
   POWER(j); LINREC(k); BOUND(j); RATIO(x); UNDECIDED. Exact readings that hold on earlier, disjoint segments are listed
   beside the verdict ("before a: POWER(2) on [1, 32]") and are not the verdict. UNDECIDED is never reported as "no
   power" or "none".
7. **The swap: the doubling reading** (the reading first used, disclosed): ε(r) = log₂(H(2r)/H(r)); a run of r with
   |ε(r) − j| ≤ 0.3 for one whole j, starting at r ≥ 4 (a run that would start before 4 is trimmed to start at 4, and
   kept if it still spans a doubling), reported as [a, 2z]. It is biased low at small r (C(r + 3, 3) first reads within
   0.3 of 3 at r = 13) and blurs the end of a range (on Ring(33, 2) it runs to z = 19, reporting [4, 38] for a count
   quadratic only to 32). It is a swap only.

## 4. The gate: the same power from every knot examined (second look requested)

1. **The gate** for one run (a law, a start, a knot law, at T rounds): there are j, a common range [a, z] with a ≥ 4 and
   z ≥ 8a, and constants c, C with C/c ≤ 2, such that c·r^j ≤ H(u, r) ≤ C·r^j for every r in [a, z] and **every knot
   examined** u (the start knots and both sampled classes of KD 2.3, k of K, K the number examined), with z ≤ ℓ(u) for
   each. It is written "the same power j from every knot examined (k of K)". When 0 of k sampled made knots fail, the
   share of made knots of the structure that fail is at most 3/k at 95 percent (the rule of three, under the uniform
   weighting of each class).
2. **The scaling condition.** The run is grown again to 2T rounds; the gate must hold again with the end of its common
   range z(2T) ≥ 1.8·z(T); and, for a named family of starts indexed by a size n (Ring(n, 2)), z must not equal a fixed
   function of n across T (the range is not set by the start's size). A gate that holds and fails the scaling condition is
   reported "same power on a range set by the start" or "same power on a range that does not lengthen".
3. **The roster count beside the gate**: P_T(u, r) counted from 8 sampled members, the number of parts and the members per
   part, reported next to the gate's verdict and never part of it.

## 5. The growing end: readings between loose distinctions (second look requested)

1. **A reached stage**: the structure after round t ≥ 1 of a run.
2. **The stage weighting**: each allowed state of the structure after round t once. ρ(a, b), the **disagreement share**
   of two distinctions, is the number of allowed states in which they differ divided by the number of allowed states,
   both counted exactly in integers; κ(a, b) = 1 − 2ρ(a, b). **The weighting of stages** in any share over stages: each
   (start, law, knot law, round) once, a start being each census start once (the census weighting) or each labelled start
   once (the labelled weighting). Swap: **the history weighting** of `STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001B`
   (preregistration line 23), on stages of at most 20 distinctions.
3. **Lemma N (argued, not refereed; check N).** Under not-all-equal, for knots u ≠ v holding loose distinctions a and b,
   each with at least one shared place, λ_u, λ_v their loose counts (barred included), and expectations taken under the
   stage weighting: κ(a, b) = γ(u, v) / ((2^{λ_u} − 1)(2^{λ_v} − 1)), with **the between-knots reading**
   γ(u, v) = E[g_u g_v], g_u = +1 when all of u's shared places are 0, −1 when all are 1, 0 otherwise. So every loose
   distinction of u has the same κ with every loose distinction of v (one reading between two knots), and
   |κ| ≤ 1/((2^{λ_u} − 1)(2^{λ_v} − 1)) (the record's bound, `STATE-DISTANCE-...-001A/samples.md` lines 157–159).
   γ still depends on λ_u and λ_v, through the weights 2^λ and 2^λ − 1 of shared configurations, so dividing by the two
   factors removes the members' own loose counts only in part. γ is not a share of states. γ was named after the scratch
   runs were seen (post hoc); the lemma forces it.
4. **Lemma P (argued, classical, not refereed; check P).** Under parity with any number of holders, the allowed states
   are a linear space over the two-element field, and every pair of distinctions has ρ = 0 or ρ = 1/2. With every
   distinction held once or twice and a connected holder graph, the only rule on the loose distinctions (barred ones
   counted as loose) is their sum, so with three or more of them every pair has ρ = 1/2, and with two they are tied. This
   is about pairs of single loose distinctions under the stage weighting; "tied" is an equivalence and gives classes, not
   a graded reading. **The parity rules on loose distinctions**, Λ_t: the rules that the allowed states satisfy and that
   involve loose distinctions only (the row space of the knots' rules intersected with the span of the loose
   distinctions); reported per stage: its dimension and its least number of distinctions in one rule.
5. **Arrival delay** δ(u, v) of two members after round t: the least d ≥ 1 such that a knot made in round t + d has an
   ancestor in {u} ∪ desc(u) and one in {v} ∪ desc(v) (a waiting member counts as its own descendant), grown on under the
   same law at most 6 rounds and at most the run's knot bound. **δ = ∞** when the law is taking-free, the roster after
   round t is **past its start** (no member meets a member), and u and v lie in different parts (the ring study's settled
   statement "Parts act alone past the start", `RING-IN-BALANCE-20261123-001A/preregistration.md` lines 95–99). Under HOLD
   a member may be an ancestor of another member; then δ is counted the same way and the pair is reported in its own
   stratum "ancestor". Otherwise, not met within the horizon or the knot bound while growth goes on: **undecided**.
6. **The orders, with a fixed direction for every reading.** For a stage, a reading X of each pair of members (one loose
   distinction of each; by Lemma N the choice does not matter) and a key Y:
   - "nearer in the states" means **larger |κ|**, or **larger |γ|**, or **smaller ρ** (swap; the record's second ruler);
   - "sooner" means smaller δ; "fewer steps" means smaller ws or smaller hs.
   For two pairs P, Q with Y decided for both: **concordant** when P is strictly nearer and strictly sooner (or strictly
   farther and later), **discordant** when strictly nearer and strictly later, **tied** when X or Y is equal (exact
   integers). Per stage: the counts of concordant, discordant and tied pairs of pairs, and Kendall's S = concordant −
   discordant with its exact distribution under all permutations of Y among the stage's decided pairs (enumerated when
   at most 9 pairs are decided; otherwise its exact mean 0 and its variance with ties, the literature's formula for
   Kendall's S, are reported). Per law: ΣS with Σ variance.
7. **Strata**, reported apart and never pooled: (i) pairs in one part with δ decided; (ii) pairs with δ = ∞; (iii) pairs in
   one part with δ undecided; (iv) "ancestor" pairs; and, inside (i), the pairs of pairs whose two pairs have the same
   multiset {λ_u, λ_v} ("equal loose counts").
8. **A headline disagreement** is a discordant pair of pairs in stratum (i) that is also discordant under |γ| or that has
   equal loose counts. A discordance under |κ| that is neither is reported "explained by loose counts".
9. **Smallest reached stage**: in the order (number of knots, number of distinctions, round), the first stage of the
   registered family with a headline disagreement against δ, per law and knot law; the start label is reported as a
   label only. Or "no headline disagreement on any stage of the family", with the number of stages in which stratum (i)
   holds two or more decided pairs (the stages that test it).
10. **The within-part law L-W**: on every stage, for pairs of stratum (i), |γ| strictly larger whenever ws is strictly
    smaller. Reported with the number of stages that test it non-vacuously.
11. **The betweenness test** (A98's reading): for members u, v, w of one part with ws(u, v) + ws(v, w) = ws(u, w),
    |γ(u, w)| ≤ min(|γ(u, v)|, |γ(v, w)|). Reported: triples tested, triples failing, stages tested and failing.

## 6. The knot test

1. Under parity, both methods of FD 7 (ranks, kernel); under not-all-equal, the birth method on every knot made after
   round 0 and the direct test on every knot of at most 12 places, compared (FD 7). The closing form under parity is
   IMPLIED (FD 2.8) for every law, taking rules included.
2. **Which knots**: every knot of every stage of runs 4 and 5; every start knot of every run; for runs 1 and 2, the class
   argument cited with its standing (under parity a knot that receives a fresh distinction passes and keeps passing, with
   at most two holders: `RING-IN-BALANCE-20261123-001A/preregistration.md` lines 102–105, referee pending; under
   not-all-equal a knot's verdict is fixed at its birth when every birth receives a fresh distinction, FD 7), and a
   sample of 200 knots per run, uniform over all knots of the last structure (each knot once), seeded as KD 2.3 with class
   `knot-test`.
3. **Wording of every result**: "n of N knots tested, all passed; a failing share above 3/n is excluded at 95%; untested
   knots are not tested and rest on the argued statement." Failures are named (kind, parents, round). Shares over runs
   are given twice only for tested runs: over all tested runs, and over tested runs with no failing knot (a conditioned
   weighting, named). Five-knot runs of run 1 get no test, and the report says so.

## 7. Laws, numberings and caps

1. **Uniform takes**: each take of Q, MET, STEPS-1 and STEPS-2 chooses uniformly among its eligible candidates,
   independently; the engine draws from the candidate list sorted by name with `random.Random` seeded as KD 2.3 (class
   `takes`), in birth order. CARRY is defined by "oldest", a name, and has no uniform form: it is run under OLDEST only,
   with the numbering swap. The rival joins (the first version's L9) are cut: they are not defined in SD, FD or here, and
   the record proves them inactive on every reached cut.
2. **Names**: under a taking-free law every count is the same under every numbering of a start (the copier study's
   Settled 1); names still fix which knots are sampled (KD 2.3), the order in which takes use the seed, and the start
   labels. The sampled knots' weighting does not depend on the numbering; a given sample does.
3. **The stage cap of the growing end** (name-free): a stage is computed when it has at most 30 members and at most 50
   shared distinctions; every other stage is "not run" and listed with its counts.
4. **The checks** (engine checks, not predictions; each must pass before the runs that use it): check E (KD 1.6), check F
   (KD 2.5: H at round t and t + 10 agree on the kept range, every knot counted from in run 2), check R (KD 2.7, both
   parts, on every run of run 2 under the treatments it names), check N (KD 5.3: every pair of loose distinctions of two
   members has the same κ, and κ equals γ over the two factors, on every stage of run 5 with at most 20 distinctions by
   enumeration of every state), check P (KD 5.4, every stage of run 4 under parity), check I (the engine's integer counts
   against enumeration on every stage of at most 20 distinctions).

## 8. Controls (built by hand, supplied)

1. **Ring of knots** R_n (knot i holds i − 1, i and one loose): H = 2r + 1 for r < n/2. POWER(1).
2. **Branching** T_d (the holder graph is the tree in which every knot meets three, d steps from the root): H counted
   from the root = 3·2^r − 2. LINREC(1) with root 2.
3. **Six-regular weave** W_L (drawn, hand-built: the six-regular one-pair weave of L × L, two knots per square of the drawn
   grid): H = 6r² + 6r + 1 for r < L/3. POWER(2).
4. **The fixed ration of three from one knot** (RATION-3, STALL, from [[0,1,2]]): b(t) = C(t + 2, 2), H counted from the
   start knot = C(r + 3, 3). POWER(3); and b reads POWER(2) from round 1.
5. **Negative control for the gate**: the comb (the literature's comb; hand-built): a chain of 64 knots (the spine), and
   from each spine knot a chain of 64 knots, every knot topped up to three places (named_starts_v2.json, "comb_64_64"); H
   counted from the first spine knot is C(r + 2, 2) and counted from the far end of a leg is r + 1, both for r ≤ 63
   (checked in scratch). The gate must fail.
6. **Positive control for the order test**: the branching structure T_d under not-all-equal with every knot of three
   places; κ between leaves equals the product formula of `STATE-DISTANCE-...-001A/tree_delays.md` lines 9–14 exactly,
   |κ| is strictly decreasing in hs, and the order test against hs gives no discordant pair of pairs.
7. **A known tie**: two pairs of leaves of T_d at equal hs have equal κ, exactly; the order test must count them tied.
8. **The bare rings** Ring(n, 2), odd n ≥ 5 (a family whose range is set by the start): counted from a knot of round t with
   t ≥ n and ℓ ≥ n, H = 2r² + 2r + 1 for r ≤ n − 1 and H = n(2r + 1) for r ≥ n (the step from n − 1 to n is 3n − 1). The
   gate's scaling condition must fail on this family.

## 9. What is supplied by hand (scaffolds)

Everything SD line 157 and FD 8 list for the laws used; and here: the holder step as the step counted; stepping through
dead and retired knots; the members as the growing end; the classes of knots counted from and their uniform sampling;
the readings of KD 3 and their precedence; the gate's thresholds (z ≥ 8a, C/c ≤ 2, 1.8); the kept-range rule; the
bounds; the census weightings; the stage weighting; the history weighting; γ (post hoc); the delay horizon; the order
rule; the stage cap; the controls; the order of running. Each has a registered swap in the pre-registration.


# (4) The pre-registration, second version

# How many knots lie within reach, and whether the growing end carries a distance of its own: pre-registration (second version)

Epic `KNOTS-WITHIN-REACH-20261125-001` (sub-goals B261 and B269; goals G1 and G2 with G5; assumptions A110, A97, A98,
A105). **Second version, 25 November 2026 (UTC)**, after the advisor's cold review ("freeze after listed changes, with a
second look at KD 2–3 and 5.6"); not frozen. The engine is written by a helper that has not seen the prototype, from
this text ("PR"), [the claim](claim_v2.md), [the definitions](definitions_v2.md) ("KD"), SD and FD, and the data files
`census_starts.json`, `named_starts_v2.json`, `five_knot_order_v2.json`. It may import the fold study's engine
(`experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again/pm.py`, `knots.py`)
read-only. The canonical K1–K3 test is unchanged. No claim is made about physical space or time, living things or minds.
The account of every change from the first version is `changes_v2.md`.

## The question

As the first version, unchanged: the owner's words of 24 November 2026 and the direction they take up ("how many knots lie
within reach, and whether the growing end carries a distance of its own"), with A97, A98 and A110 behind them (claim,
section 1). **Read here as**: the count of the growth's history within r holder steps of a knot (H), the roster at one
round apart (P), and the order of the disagreement share among members of one part against witnessed steps and arrival
delay.

## In standard terms

In the literature's words: the grown object is a hypergraph whose edges carry constraint relations (parity: a linear
code; not-all-equal: 2-colourings). H is the volume growth (the literature's) of its line graph over the whole history,
counted from a stated vertex; under a taking-free law that graph is the birth order (a partial order of knots by descent)
made symmetric, plus the start's own edges. P is the volume growth of one slice's own graph. Question 2 asks whether
two-point correlations of degree-one variables under the uniform measure on solutions are monotone in the slice's graph
steps and in a first-common-descendant time.

## Prior work in the program

The searches and their top rows are those of the first version (unchanged; `track.py objects` with `--until 2026-11-25
--exclude KNOTS-WITHIN-REACH-20261125-001`, run read-only on 25 November 2026): "within reach" `RULER-LEVEL-20261114-001`,
`CHEAP-COUNT-20261112-001`, `LOCAL-ROOM-20261118-001`; "growth of balls" `FRESH-COUNT-20261118-001`,
`INFLUENCE-CONE-20261120-001`, `COUNT-BALLS-20261118-001`; "knots within r steps" `LOCAL-ROOM-20261118-001`,
`LEVEL-REACH-20261114-001`, `ADDR-KNOTS-20261113-001`; "ball growth grown structure" `COUNT-BALLS-20261118-001`,
`REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001`, `KNOT-RATION-GAME-20261121-001`; "bond distance" `RING-READ-20261118-001`,
`MEET-ONCE-20261119-001`, `ORDINARY-DYNAMICS-20261120-001`; "state distance loose distinctions" `CREATED-PAIR-20261119-001`,
`ORDINARY-DYNAMICS-20261120-001`, `BOND-CLOSURE-20261120-001`; "arrival delay" `MEET-HIST-20261118-001`,
`OLD-CORE-20261112-001`, `RANDOM-FATES-20261112-001`. What is used is in [the survey](survey_v2.md); one addition: the
copying-parts study's "each two-knot part becomes one chain gaining a member a round" under a cap of three
(`research/COPYING-PARTS-20261123-001A/results.md` line 55), which the start-by-start table below reads directly.

## Prior work outside the program

From memory, the literature's, not checked, not leaned on: volume growth and the degree of polynomial growth (Milnor;
Gromov; Bass–Guivarc'h), which concern homogeneous graphs and limit objects, neither of which is here; causal sets and
growth models (Rideout–Sorkin's sequential growth; the counting of chains and intervals of a partial order for its
dimension, Myrheim–Meyer), where reading a partial order by its two-way neighbourhoods is known to give the slice's
exponent plus one, which is why H and P are read apart here; correlation decay for 2-colourings on trees (the product
formula). What this would add: the first counts of knots by holder steps in what the record's laws make, read exactly
where the counts are polynomials, with the gate of "the same power from every knot examined" and its scaling condition,
and the order test on the growing end with the members' loose counts separated.

## Known before the runs (disclosed)

The drafter's scratch prototype (`proto/`; unreviewed; not the study's engine; it imports `pm.py` and `knots.py`):
everything of the first version's "Known before the runs" stands as disclosed there (controls; named starts; the 512-run
census of 64 sampled starts; the growing-end census of 2,330 stages; parity ties; knot-test timings; the census
reproduced), with these corrections and additions.

- **Corrections to the first version's disclosure** (found by the advisor and checked): C(r + 3, 3) first reads within 0.3
  of 3 at r = 13, not 14; the bare ring's step from n − 1 to n is 3n − 1, then 2n a step, so H = n(2r + 1) for r ≥ n
  (seen in the saved counts: 26 then 18 for n = 9, 44 then 30 for n = 15, 62 then 42 for n = 21); the golden-ratio eddy
  passes 50,000 knots after round 17, so a doubling reading there could reach at most 5, not 6; the 325 checks of Lemma F
  covered H only; the member count M of the first version is empty below the end of the kept range and is withdrawn.
- **The start-by-start table** (`table7.py`, the same 64 starts: `random.Random(20261125).sample` of the 3,376 in file
  order; not-all-equal; at most 40 rounds and 50,000 knots; 256 runs in 36.5 s; births read exactly, KD 3.2: degree j of
  b(t) with at least j + 8 values reads POWER(j + 1) from start knots): ORDINARY against CAP-3(RETIRE): 25 starts read
  POWER(2) under both; 25 that end under ORDINARY (stall) read POWER(2) under the cap; 4 read POWER(1) under both; 4 go
  from POWER(1) to POWER(2); both POWER(3) starts (census 3103 and 3192) go to POWER(2); 1 goes from ended to POWER(1); 3
  end under both. CAP-3(OFFSHOOT) and RING-LAW give the same pattern: 60 and 55 of 64 read POWER(2) by b(t) (RING-LAW ends 5;
  under waiting Lemma R's s = round does not hold, so there b(t) is a reading of births only). No run
  of the 256 was undecided by the exact reading. **Split by part**: under CAP-3(RETIRE), in 56 of the 61 runs that went on
  for 10 or more rounds the number of parts was the same over the last five rounds and the largest part gained one or two
  members a round (39, 40, 41 members at rounds 38 to 40 in most; 77, 79, 81 in some); in the other 5 both were fixed; under ORDINARY the two POWER(3) starts had one part whose
  members grew from 2,816 to 3,124 over rounds 39 to 41. So on this sample the cap sets the "2", by making a fixed number
  of parts each of which gains one member a round: POWER(2) of H is 1 from a lengthening part and 1 from the rounds.
- **The growing end re-read in the advisor's strata** (`ge_strata.py` on the saved first-version data; floating point,
  ties within a relative 10⁻⁹; the registered reading is integer): stratum (i) (one part, δ decided) holds 6,872, 5,473,
  5,092 and 1,102 pairs of members under ORDINARY, RING-LAW, CAP-3(RETIRE) and COPY-LAW(RETIRE); stratum (ii) (δ = ∞)
  2,342, 11,880, 6,684 and 10,153. Concordant / discordant pairs of pairs in stratum (i), |κ| against δ: 41,651 / 17,448
  (ORDINARY), 20,071 / 1,570, 16,873 / 1,051; under |γ|: 53,662 / 5,438, 20,679 / 963, 17,319 / 606; among pairs with
  equal loose counts, |κ|: 13,695 / 201, 12,695 / 443, 10,320 / 165. Kendall's S summed per law is positive with a ratio
  to its permutation standard deviation of 24 (|κ|) and 48 (|γ|) under ORDINARY, 49 and 52 under RING-LAW, 50 and 53 under
  CAP-3(RETIRE). **Under COPY-LAW(RETIRE) all 1,224 comparisons in stratum (i) are tied in δ**, so the first version's
  "0 of 592" was vacuous there. Discordance survives |γ| on 130, 129 and 97 stages and equal loose counts on 33, 81 and
  66; the smallest stage with a discordance under |γ| is the same as under |κ|: census start 157 after round 1 (7 knots),
  under all three laws.
- **The smallest case is not explained by loose counts** (exact, every state enumerated, and the integer contraction
  agreeing): census start 157 after round 1 has three members, the four-parent join and two offshoots, **each holding two
  loose distinctions**; κ = −1/2,121 (join, first offshoot; ws 1, δ 1), −1/707 (join, second offshoot; ws 1, δ 1) and
  19/19,089 (the two offshoots; ws 2, δ 2). With equal loose counts the order still disagrees: the join's four shared
  places are all equal less often than an offshoot's one. The advisor's guess that loose counts drive it is not borne out
  on this stage.
- **Betweenness** (on the saved data): |γ(u, w)| > min(|γ(u, v)|, |γ(v, w)|) for v on a shortest witnessed path in 878 of
  5,734 triples (149 of 435 stages tested) under ORDINARY; 315 of 3,917 (69 of 494) RING-LAW; 220 of 3,594 (47 of 490)
  CAP-3(RETIRE); 197 of 1,320 (38 of 435) COPY-LAW(RETIRE). It needs no new contraction.
- **Exact integer contraction, timed**: 114 stages of 40 four-knot starts under ORDINARY, rounds 1 to 3, 2,606 pairs, 2.7 s;
  five-knot starts (the first 60 of the registered order × ORDINARY and CAP-3(RETIRE), rounds 1 to 4): 397 stages, 12,049
  pairs, 41.4 s; 17 stages over elimination width 20, each with at least 58 shared distinctions; no stage with at most 57
  shared distinctions was over width 20.
- **Taking rules at 20 and 100 rounds** (`c3_v2.py`; 4 named starts × 2 base laws × Q, MET, STEPS-1, STEPS-2 × 2 seeds of
  uniform takes, parity; 64 runs, 2.4 s): from round 10 to 20 no run doubled its knots with its greatest holder steps from
  start knot 0 not rising. At 100 rounds (three runs, 0.1 to 0.4 s each): Ring(5,3) CAP-3(RETIRE) MET 514, 1,575, 3,389
  knots at rounds 25, 50, 100, greatest holder steps 8, 14, 17 (weighted step 25, 38, 55); Ring(7,3) CAP-3(RETIRE)
  STEPS-2 228, 378, 678 knots, 9, 14, 21; three-knot CAP-3(RETIRE) STEPS-2 125, 250, 500 knots, 23, 48, 98. **The first
  version's expectation that taking rules keep every knot within a few holder steps (P11) is not borne out past 20
  rounds.**
- **Parity rules on loose distinctions under taking rules** (the same 64 runs, rounds 10 and 20): Λ_t of dimension 0 in
  most stages (no rule on the loose distinctions alone); dimension 1 with least weight 4, 5 or 7 in 8 stages of 5 runs;
  whether the least weight is below the number of loose distinctions was not recorded. The first version's tied pairs
  (least weight 2) were at rounds 3 to 6.

**Not run by the drafter**: the gate and its scaling condition; the two-sided bound; LINREC on S; every swap of the
scaffold table; the comb, the order-test controls, the exact numbering check; the history weighting; parity runs of the
count census; the knot test in runs 4 and 5; five-knot starts in the count census beyond the 64; HOLD; CARRY.

## Settled by construction (stated, not tested)

1. Lemmas E, F, R, N, P (KD 1.6, 2.5, 2.7, 5.3, 5.4), argued, not refereed, with exact hypotheses where stated, each checked
   by a check of KD 7.4 that could contradict it. Under L8 (RATION-3, STALL) Lemma R's first part applies.
2. **Renaming** for taking-free laws (the copier study's Settled 1, checked exactly there): counts of L0–L8 do not depend
   on the numbering; the weighting of each sampled class does not either; a given sample does.
3. **Uniform takes**: with each take of Q, MET, STEPS-1, STEPS-2 drawn uniformly among its candidates, the weighting of
   runs from a renamed start is the image of the weighting from the start. It holds for the weighting of runs, not for one
   seeded run, and is checked exactly in run 4b with every choice enumerated.
4. **Parity runs** of a taking-free law equal the not-all-equal runs up to the first birth that takes every loose
   distinction of the structure, none barred, after which the parity run has ended.

## What is supplied

Everything SD (line 157) and FD (section 8) list for the laws used; every law beyond ordinary growth; the starts and both
census weightings; the holder step, stepping through dead and retired knots, members as the growing end, the classes of
knots counted from and their sampling; the readings of KD 3 and their precedence; the gate's thresholds; the kept range;
the bounds; the stage weighting and the history weighting; γ (post hoc); the delay horizon; the order rule and the
strata; the stage cap; the controls; the order of running. **Supplied or made**: every count is of a pattern the law makes
from a supplied start; one degree of every POWER of H comes from the rounds we run; a range set by the start's size is
said to be the start's.

## Scaffolds and their swaps

| Scaffold | Swap (fixed direction where a reading is swapped) | Run |
| --- | --- | --- |
| Holder step | parent step (runs 1, 2, 4); steps through distinctions of at most two holders, and the weighted step (run 4) | 1, 2, 4 |
| Stepping through retired knots | retired knots counted, not stepped through | 2 |
| Members as the growing end | every live knot (barred included), for P | 2 |
| Exact reading primary | BOUND(j) second; the doubling reading with 0.3 (the reading first used) as swap | 1, 2 (re-read only) |
| Gate thresholds z ≥ 8a, C/c ≤ 2, 1.8 | z ≥ 4a, C/c ≤ 3, 1.5 | 2 (re-read only) |
| Census weighting | labelled weighting (exact on three and four knots; on the five-knot sample by reweighting, effective sample size stated) | 1, 5 |
| Bounds 100 rounds (128 for the gate), 50,000 knots | 60 rounds, 20,000 knots (named starts) | 2 |
| The cap, the ration, the treatment, RELEASE | caps 2 and 4; HOLD | 2 |
| Uniform takes | OLDEST and NEWEST under the 4n numberings | 4 |
| Stage weighting | the history weighting (stages of at most 20 distinctions) | 5 |
| |κ| (larger = nearer) | |γ| (larger = nearer); ρ (smaller = nearer) | 5 |
| Delay horizon 6 rounds | 10 rounds | 5 |
| Stage cap 30 members, 50 shared distinctions | 40 members, 60 shared (three- and four-knot starts only) | 5 |

## What a result would and would not show

As the claim, section 6 (no limit object; the count depends on the knot counted from; the birth order read in both
directions gives the roster's exponent plus one; the step convention under hubs; a disagreement of orders and how much is
loose counts; parity's tied-or-unrelated).

## Starts and files

- `census_starts.json` (unchanged): the 3,376 census starts (and 4 entries of one and two knots, not in the census).
  Denominators: under parity the 3,344 that pass the knot test at round 0; under not-all-equal all 3,376.
- `five_knot_order_v2.json`: the 3,157 five-knot starts in the order of `random.Random(202611251).shuffle` of their file
  order; the first 1,000 are the registered sample, census weighting; whether each is among the 64 scratch starts is
  marked, so every share is reported with and without them.
- `named_starts_v2.json`: the first version's named starts, the controls of KD 8 as stars (ring R_40, branching T_9, the
  comb of 64 and 64, the bare rings Ring(n, 2) for odd n from 5 to 33), and the six-regular weave rule (built by the
  engine).
- The 4n numberings and 200 further numberings of a named start: as the first version (rule and seeds 202611252).

## Runs (sized from measured rates; at most 6 processes; the order listed is the order of running)

| Run | Items | Measured seconds per item | Wall time, 6 processes | Readings |
| --- | --- | --- | --- | --- |
| 0 | controls of KD 8; checks E, F, R, I on the named starts | < 1 | < 5 min | exact counts; every check passes |
| 1 | L0–L8 on the 219 starts of three and four knots and the first 1,000 five-knot starts, not-all-equal (parity derived, Settled 4); 100 rounds, 50,000 knots, the fold engine's guard × 10 | 0.9 (mean of 512 scratch runs at these bounds, 0.0 to 8.2) | 10,971 runs ≈ 9,900 s ≈ 28 min | H's verdicts from start knots and both classes; b(t) exact; the start-by-start table with b(t) by part; shares by weighting, with and without the 64 |
| 2 | named starts × L0–L8 and the swaps, both knot laws directly; the gate with its scaling condition (T and 2T, T = 64 and 128 where the knot bound allows); P with parts per round | 0.1 to 8 growth, plus about 10 s for 128 counts from sampled knots on structures of up to 50,000 knots (estimated from 0.05 to 0.1 s a count in scratch) | about 700 runs ≈ 7,000 s + growth ≈ 30 min | the gate (k of K, c, C, C/c, [a, z]); scaling; P; the comb must fail |
| 3 | the knot test of runs 1 and 2: every start knot, and 200 sampled knots per run (KD 6.2), both knot laws | about 1.3 per run (200 knots at 6 ms under not-all-equal, 0.7 ms under parity) | ≈ 11,700 runs ≈ 42 min | "n of N knots tested, all passed; ..." |
| 4 | T1–T8 with 2 seeds of uniform takes and T9, T10 under OLDEST, on the named starts and the 219 small census starts, parity and not-all-equal, 100 rounds, at most 50,000 knots; readings at rounds 25, 50, 100 under the four steps (KD 1.7); Λ_t per stage read; the knot test on every knot of the structure after round 25 (the cut that fits the hour; rounds 50 and 100 are read, not tested) | 0.1 to 0.4 s growth per 100-round run (scratch, 3 runs), plus about 6 ms a knot (not-all-equal) and 0.7 ms (parity) for the test at round 25 (at most about 500 knots in the scratch) | 234 × 18 × 2 = 8,424 runs × about 2 s ≈ 16,800 s ≈ 47 min | claim 3 and claim 4 verdicts; "n of N knots tested, ..." |
| 4c | OLDEST and NEWEST under the 4n numberings on the 15 named starts, T1–T10, not-all-equal, 100 rounds | 0.3 | 15 × about 80 numberings × 2 choices × 10 laws ≈ 24,000 runs ≈ 7,200 s ≈ 20 min | how many numberings change the claim-3 verdict |
| 4b | the exact check of Settled 3: every choice enumerated, two-knot and three-knot starts and Ring(5,3), 3 rounds, T1–T8, comparing the weighting of structures up to renaming under the 4n renamings; at most 10⁵ histories per case, else "not finished" | not measured | not measured: run only if run 0 shows a case finishing in under 10 s | the statement holds / fails (the case) |
| 5 | the growing end: L0–L8 on every census start, rounds 1 to 3 (rounds 1 to 4 on three and four knots), within the stage cap, integer arithmetic; the history weighting on stages of at most 20 distinctions; the knot test on every knot of every stage computed; the two order controls and the known tie | 0.35 per (start, law) on five-knot starts, rounds 1 to 4 (scratch, integer) | 3,376 × 9 ≈ 30,400 items ≈ 10,600 s ≈ 30 min, plus the knot test on stages of at most 120 knots (< 1 s each) | KD 5.6 to 5.11 per stratum; the smallest headline stage; L-W; betweenness; S and its reference |

**How many rounds and knots a reading needs, and whether an hour reaches them.** The exact reading needs j + 8 values:
for b(t) about a dozen rounds decide a start knot's verdict (all 256 scratch runs were decided within 40 rounds). The gate
needs z ≥ 8a with a ≥ 4, so z ≥ 32, and the made knots near s_min/2 need ℓ ≥ 32, so s_min ≥ 64 and T ≥ 64 rounds; the
scaling condition then needs 2T = 128 rounds. For POWER(2) that is about 16,000 knots at 128 rounds (reached); for POWER(3)
about 50,000 knots at 64 rounds and 360,000 at 128, **so the scaling condition for a third power cannot be decided within
the knot bound**, and run 2 reports it "undecided at the bound". RATIO(x) needs 9 steps of S, reached by every
exponential law in the scratch. A fourth power is not reachable and is not registered.

**Not registered, with the advisor's reason** (not asked for): (i) all 3,157 five-knot starts in run 1 — a sample of 1,000
gives shares within ±2.6 points at 95 percent in the worst case, and "none seen" there excludes 8 or more such starts, not
"none in the census"; ask only if the sample turns up a candidate for the gate, or if the owner wants "no start of the
census"; (ii) the knot test on every knot of every run — the sample with the cited argument is honest; (iii) bounds of a
million knots — nothing registered needs a fourth power, and the exact reading of b(t) decides RING-LAW's t² cheaply.

## Predictions

Marks: **(a)** seen in the scratch runs, **(b)** by argument, **(c)** undecided. Engine checks are not predictions (checks
E, F, R, N, P, I and the controls, KD 7.4 and 8). **Replication** marks a count the registered runs repeat on the same
exhaustive family.

| # | Prediction | Mark | Fails when |
| --- | --- | --- | --- |
| P1 | Under L1, L6 and L7, at least half of the census starts (census weighting; denominators as stated) have b(t) of POWER(1), so H reads POWER(2) from their start knots by Lemma R (L6, L7; under L1 by the direct reading of H), under not-all-equal. | (a): 55, 56 and 60 of 64 by b(t) | fewer than half |
| P2 | In the start-by-start table, every start that reads POWER(3) from its start knots under ORDINARY reads POWER(2) under CAP-3(RETIRE). | (a): 2 of 2 | one does not |
| P3 | Under CAP-3(RETIRE), in every run that goes on to round 40, the number of parts is the same over the last five rounds and the largest part gains a fixed number of members per round (zero included). | (a): 61 of 61 (56 gaining one or two a round, 5 fixed) | a run where parts multiply or a part's gain varies |
| P4 | Under COPY-LAW (L3–L5), at least half of the census starts read RATIO(x) or LINREC with a root above 1 from their start knots (census weighting). | (a) | fewer than half |
| P5 | No run of runs 1 and 2 passes the gate with its scaling condition at j ≥ 2; at least half of the runs of run 1 that go on to round 128 are decided (gate holds, fails, or holds only on a range that does not lengthen). | (a) for the first part (no same power from every knot examined above 1 in 512 scratch runs), (c) for the decided share | a run passes both, or fewer than half are decided |
| P6 | Ring(n, 2), odd n from 5 to 33: counted from a knot made at round t ≥ n with ℓ ≥ n, H = 2r² + 2r + 1 for r ≤ n − 1 and n(2r + 1) for r ≥ n; the gate holds with j = 2 on a range ending at n − 1, and the scaling condition fails. | (b) sketch; (a) for n = 5, 9, 15, 21 | another count, or scaling holds |
| P7 | RATION-3 from one knot reads POWER(3) from the start knot on a final segment of at least 11 values, and b(t) = C(t + 2, 2) reads POWER(2) from round 1. | (b) | not read |
| P8 | The roster count P under L1, L6, L7 reads POWER(1) or ENDED for every member counted from on the runs of run 2. | (a): witnessed-step counts were POWER(1), undecided or ended in every scratch run but one | a POWER(j ≥ 2) |
| P9 | Under T1–T8, no run of run 4 is "held by hubs" at rounds 50 to 100. | (a): none of 64 from round 10 to 20; 3 of 3 at 100 rounds | a run held by hubs |
| P10 | Under parity, some stage of run 4 has a rule of Λ_t on a proper subset of its loose distinctions, and some has a tied pair at two knots that both pass K1–K3. | (a) for tied pairs, rounds 3 to 6 | none |
| P11 | Under not-all-equal, for L0, L1 and L6, the smallest stage of run 5 with a headline disagreement against δ has at most 7 knots, and its members have equal loose counts. | (a): census start 157 after round 1 | larger, or none, or unequal loose counts |
| P12 | Per law (L0, L1, L6), ΣS of |γ| against δ in stratum (i) is positive with a ratio to its permutation standard deviation above 10. | (a): 48, 52, 53 | not |
| P13 | Under COPY-LAW(RETIRE), stratum (i) holds no untied comparison against δ on rounds 1 to 3 of the three- and four-knot starts. | (a), replication | an untied comparison |
| P14 | L-W fails on some stage that tests it, for each of L0, L1, L6, L7. | (a) for L0, L1, L6 | holds on every stage for one of them |
| P15 | The betweenness test fails on some triple for each of L0, L1, L6. | (a) | none fails |
| P16 | Under the history weighting the headline disagreements of P11 remain. | (c) | — |

Registered questions (not predictions): whether the history weighting keeps the order where the stage weighting does not;
whether any law of L0–L8 gives the same power 1 from every knot examined other than with constant births per round.

## Runs and stop rule

- One engine from this text; run 0 passes before any other run.
- **Stop**, read (the filed stop, unchanged): for each law and class of knot counted from, H's verdict on its final segment
  with its interval, the gate and scaling verdicts, P beside them; for the growing end the smallest stage with a headline
  disagreement against δ, per law and knot law, or none, with L-W and betweenness; every prediction given a verdict.
- Disagreements with the disclosed prototype are replayed round by round; the listing decides.
- Every run within about an hour of wall time on at most 6 processes, each under 6 GB; the order of items is the registered
  order, so a run cut for time leaves a prefix that is still a sample; a cut is reported.
- Deviations in `deviations.md` of the experiment family before the affected run.

## Words

As KD 0, with the advisor's replacements: "kept range" (for "final radius" and "radius read"), "the knot counted from"
(for "centre"), "counted from" (for "around"), "greatest steps within the start" (for "eccentricity"), "the between-knots
reading γ" (for "knot-level rate"), "the same power from every knot examined" (for "homogeneous"), the verdict said in
place of "D-dimensional" or "dimension D". RATIO(x) replaces OUTGROWS. Literature's names once each, marked: volume
growth, comb, taxicab (the bare ring's count), tube (none left). "Counterexample" is kept: it is an ordinary word; the ban
is on "counter" as a noun for a thing that counts.

## Questions for the advisor's second look (KD 2–3 and 5.6)

1. KD 2.1 states the history count's meaning and the "1 from the rounds" sentence: is "j − 1 from the roster" right only
   when the roster's size is fixed, and should the general sentence be "POWER(j) of H is expected to be P's exponent plus
   one" (registered as a reading, not argued)?
2. KD 2.3 samples made knots near s_min/2 and keeps members out of H: is the class near s_min/2 enough, or should a class
   near 3·s_min/4 be added for the gate?
3. KD 3.2 and 3.6: is "the final segment ending at the end of the kept range" the right anchor for precedence, given the
   bare ring (POWER(1) on the final segment, POWER(2) listed before it), and is the two-phase form wide enough?
4. KD 3.4: are C/c ≤ 2 and z ≥ 8a the right registered limits, given that (r + 1)² over r² on [4, 64] has C/c ≈ 1.52 and
   C(r + 3, 3) over r³ on [8, 64] about 1.76?
5. KD 5.6: are the three fixed directions right (|κ| and |γ| larger nearer; ρ smaller nearer), given that ρ above and below
   1/2 differ in sign of κ and the record's trees alternate sign with the steps?
6. KD 5.8: is the headline rule (discordant under |γ|, or among equal loose counts) strict enough, given that γ still
   depends on loose counts in part?
7. Run 4 is cut to fit the hour (knot test at round 25 only; 2 seeds): is that acceptable, or should the knot test at
   round 100 be kept and the starts cut instead?


# (5) The drafter's account of the changes

# Changes from the first version, item by item (the advisor's `reach_advisor/answer.md`)

One line per item. "Applied" = applied as worded; "applied with a change" says the change; "not applied" says why. KD =
`definitions_v2.md`, PR = `preregistration_v2.md`, claim = `claim_v2.md`.

## Section 16, required, in order

1. History count, roster count, M removed — **applied**: claim §1 says "The count is of the growth's history, not of what exists at one round" and "1 from the rounds"; KD 2.1, 2.2 (H and P under two names, never added); M and member-class final readings withdrawn (KD 2.2, 2.3).
2. One gate — **applied**: KD 4.1 (two-sided bound on one common range, every knot examined, k of K, 3/k), KD 4.2 (scaling condition), made knots near s_min/2 (KD 2.3); with a change: 8 per class in run 1 and 64 per class in run 2, where the gate is read, to fit the hour.
3. Exact reading primary, 0.3 as swap, OUTGROWS replaced, precedence — **applied**: KD 3.2 (also on b(t)), 3.3 (LINREC), 3.4, 3.5 (RATIO), 3.6 (precedence with a final-segment rule), 3.7 (swap, disclosed as the reading first used, the trimming rule stated).
4. Growing end — **applied**: |γ| beside |κ| and the headline rule (KD 5.8), strata (5.7), concordant/discordant/tied with Kendall's S and its exact permutation reference (5.6), integers (5.2), fixed directions (5.6); with a finding against the advisor's guess (section 8 below).
5. Knot test — **applied with a change**: every start knot; every knot of every stage in run 5; in run 4 every knot of the structure after round 25 only (testing rounds 50 and 100 too does not fit an hour; PR run 4); a seeded sample of 200 knots per run with the cited argument for runs 1 and 2; the advisor's wording exactly (KD 6.3).
6. C6 and "past its start" — **applied**: C6 dropped (claim §3, with the reason); δ = ∞ needs past its start (KD 5.5).
7. C3 and P11 — **applied**: 100 rounds, readings at 25, 50, 100, the base law at the same round, the four steps, "held by hubs" with the doubling-knots condition, "ALL WITHIN r" as the stage verdict (claim 3, KD 2.6, 1.7). The rescaled scratch run already contradicts the first version's P11 (PR, disclosure).
8. Definitions and symbols — **applied**: checks E, F, R, N, P, I defined (KD 7.4, named by letters, not C1–C6); L9 cut (claim §2, KD 7.1); uniform CARRY not defined, so CARRY runs under OLDEST only (T9, T10); IMPLIED closing stated (KD 6.1); name-free stage cap (KD 7.3); symbols renamed (KD 0).
9. P9, P8, C1, denominators, run 5 family — **applied**: P6 (old P9) with the closed form for odd n; P5 (old P8) needs a decided share; claim 1 no longer says "every start of the census"; denominators 3,344 / 3,376 (PR, files); run 5 on every census start, rounds 1 to 3, with the five-knot cost measured (0.35 s per start and law).
10. Controls and the table — **applied**: the comb as the gate's negative control (KD 8.5, counts checked), the branching structure under not-all-equal as the order test's positive control (8.6), a known tie (8.7); the start-by-start table registered (claim 1, PR run 1) and computed now (PR, disclosure).
11. Words of section 14 — **applied** (section 14 below).

## Optional

- Betweenness test — **applied**: it needs no new contraction (the pair readings already computed), so it adds no run time; computed now on the saved data (PR disclosure).
- Parity rules on loose distinctions per stage — **applied**: KD 5.4 (Λ_t's dimension and least weight), claim 4, PR run 4; computed now on 64 runs.
- Exact numbering check — **registered** as run 4b; **not run and not timed** by the drafter, so its wall time is not stated; it runs only if run 0 shows a case finishing in under 10 s. This is the one registered run whose cost is unmeasured.
- With and without the 64 scratch starts — **applied**: `five_knot_order_v2.json` marks them (23 of the first 1,000 five-knot starts are among them); every share is reported both ways.
- Exception (i) — **not registered**, listed in PR with the advisor's reason; also (ii) and (iii).

## Sections 1 to 15, other points

- §1 the two critics — **applied** in claim §6 ("no limit object"; "the count depends on the knot counted from"; "the birth order read in both directions gives the roster's exponent plus one"; the step convention under hubs). Reading by chains and intervals is named as a later study, not registered.
- §1 "M is empty", "member centres have ℓ ≤ 0" — **agreed and applied**; my scratch M was computed only from members as a stage reading, never as a final reading, but the first version's text registered it wrongly.
- §2 "uniform doubling alone does not fix D" — **applied**; the doubling reading is now a swap only.
- §3 Ring(33, 2) blur, C(r+3,3) at 13, the trimming of a run that starts before 4 — **applied**; the disclosure corrects "14" to "13".
- §4 hub swaps for run 4 — **applied** (KD 1.7).
- §5 R: s = round with FILLERS, joins of three, closings — **applied**; sandwich as the triangle inequality with a connected start — **applied**; "verdicts follow the record's kinds" only where proved — **applied**; L8 qualifies for R — **applied**; F covers N and HOLD, not M — **applied**, and the 325 checks are said to have covered H only; N "E under the stage weighting", K depends on λ, (1 − K)/2 not a share — **applied** (the share ρ_K is dropped); P "connected holder graph, barred counted as loose" — **applied**.
- §6 bare ring: odd n ≥ 5, two-apart order, N = n(2r + 1) for r ≥ n, step 3n − 1, r ≤ round and ≤ ℓ — **applied**; checked against my saved counts (26 then 18 for n = 9; 44, 30 for n = 15; 62, 42 for n = 21: the advisor is right and my first version was wrong). The even-n remarks are **taken on the advisor's word, not checked**; only odd n are registered. The advisor's honest sentence is used in claim 2.
- §7 the table — **applied and computed** (PR disclosure).
- §8 "the smallest case compares offshoots with a four-parent join, so loose counts are the likely driver" — **applied as a rule, but the guess is not borne out**: all three members of census start 157 after round 1 hold two loose distinctions each, so the disagreement there is among pairs with equal loose counts, and it survives |γ| (PR disclosure, exact counts). In the pooled data, though, most discordance under |κ| is removed by |γ| or by equal loose counts (17,448 → 5,438 and 201 under ORDINARY), so the advisor's caution is right in aggregate.
- §8 "ρ is always a pseudo-distance" — **applied** in claim §1.
- §8 "use no 'random'" — **applied** in the drafts' own words; `random.Random` remains as the name of the generator in seeds.
- §9 knot test — **applied** (item 5 above).
- §10 ±2.6 points and 8 or more — **applied** in PR; golden eddy k = 5 — **agreed**, disclosed as a correction; effective sample size for the labelled reweighting — **applied** (to be stated with each labelled share).
- §11 names still entering — **applied** (KD 2.3, 7.2, 5.9); "four seeds cannot check" the uniform-takes statement — **applied**: run 4b checks it exactly; run 4 keeps 2 seeds as a sample of runs, not as a check.
- §12 every point — **applied**: m when growth has ended (KD 2.4); δ under HOLD in an "ancestor" stratum and undecided at the knot bound (KD 5.5); SATURATED replaced by ENDED and, for stages, ALL WITHIN r; "commonest verdict" and "growing" removed; P4 replaced by Lemma E's identity; "common range of at least 32" is now z ≥ 32 as the endpoint with z ≥ 8a; L-W's non-vacuous stages; T1–T10 as ten labels; symbol collisions removed (KD 0).
- §13 predictions — **applied**: engine checks separated; replication marked; P5 needs a decided share; P9 (now P9) and C3 rescaled; old P19 and P20 turned into registered questions; P6, P7 fixed; old P18 limited to the laws run; the missing predictions added (P2, P3, P8, the controls). **Against the record of my own data**: the old P16 (no disagreement under COPY-LAW(RETIRE)) was vacuous, since every comparison in stratum (i) is tied in δ; the new P13 says so.
- §14 words — **applied**: "steps from the start", "the count within r holder steps", POWER(j) kept (never for a test's strength); OUTGROWS replaced by RATIO(x) on [a, z] (the advisor kept the word with a range and suggested the ratio form; I took the ratio form); "kept range", "the knot counted from", "counted from", "greatest steps within the start", "the between-knots reading γ", "the same power from every knot examined"; "dimension" only for the target; literature's names once and marked; "to depth d", "draws", "grows above every power", "how far apart", "rate" in three senses, "spaces of one dimension" removed; "counterexample" kept (an ordinary word, not "counter" as a thing that counts); the weave control marked drawn and hand-built.
- §15 sentences for the owner — **applied** at the end of the report, adjusted to what is registered; the blurs listed are removed from the drafts ("CAP-3 laws grow by powers", "nears 3", "for most small starts" without a weighting, "as the record already showed", "no graded reading at all" now limited to pairs, the owner sentence no longer states results before the runs).

## What changed in the files

`claim_v2.md`, `definitions_v2.md`, `preregistration_v2.md` rewritten; `survey_v2.md` with small changes (a quoted word, the parity statement's standing, the cap's chains, the denominators); new data files `named_starts_v2.json` (controls added, odd bare rings), `five_knot_order_v2.json`, `data_table7_v2.jsonl`, `data_c3_v2.json`. The first versions are left in place.


# (6) The drafter's report

The second versions of the claim, definitions and pre-registration are written, and the start-by-start table the advisor asked for (section 7) is computed. On the 64 scratch starts it says the cap of three sets the second power, not the start. All the reruns together took under 2 minutes of compute; nothing went into the repository.

**Files** (in `/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/7d6e7b9e-634d-564b-a5b8-21bd756b246b/scratchpad/reach_survey/`):
- `claim_v2.md`
- `definitions_v2.md`
- `preregistration_v2.md`
- `survey_v2.md` — small changes only: a quoted "draws", the parity statement's standing, one added row on the cap's chains, the denominators.
- `changes_v2.md` — one line per advisor item.
- Data:
  - `named_starts_v2.json` — adds the comb, R_40, T_9 and the odd bare rings 5 to 33.
  - `five_knot_order_v2.json` — 23 of the first 1,000 are among the 64 scratch starts.
  - `data_table7_v2.jsonl`
  - `data_c3_v2.json`
- New scratch scripts in `proto/`: `table7.py`, `ge_strata.py`, `c3_v2.py`, `nae_exact.py`.

The first versions are left in place.

**Advisor items not applied exactly as worded:**
- **Required 2 (sampled made knots):** 8 per class in run 1, and 64 per class only in run 2 where the gate is read (3/128 ≈ 2.3%). 64 everywhere would not fit the hour.
- **Required 5 (knot test):** in run 4 every knot is tested only on the structure after round 25. Testing rounds 50 and 100 as well would have run about 17 hours; the cut fits in about 47 minutes.
- **The exact numbering check:** registered as run 4b but not run or timed by me. It is the one registered run whose cost is unmeasured.
- **OUTGROWS:** section 14 says keep it with a range, section 3 says it can't be decided. I took the ratio form, RATIO(x) on [a, z], beside the exact recurrence reading LINREC.
- **Even bare rings:** the advisor's remarks about even n are taken on its word, not checked. Only odd n are registered.
- **Uniform CARRY:** CARRY is defined by "oldest", so it runs under OLDEST only. The rival joins (L9) are cut.

Everything else is applied, with the advisor's wording where it gave any, including the knot-test sentence and the section 15 sentences below.

**What section 7's table says** (64 starts, not-all-equal, at most 40 rounds and 50,000 knots, 256 runs, 36.5 s; births per round read exactly):
- **Ordinary growth against the cap of three with retiring:**
  - 25 starts read power 2 under both.
  - 25 that stall under ordinary growth read power 2 under the cap.
  - 4 read power 1 under both, and 4 go from 1 to 2.
  - Both power-3 starts (census 3103 and 3192) drop to 2.
  - 1 goes from stalled to power 1, and 3 stall under both.
- **The other cap-of-three laws:** 60 of 64 read power 2 with offshoots, and 55 under waiting (where it is a reading of births only). No run was left undecided.
- **Split by part:** under the cap with retiring, 56 of the 61 runs that lasted 10 rounds or more had a fixed number of parts. Their largest part gained one or two members a round; in the other 5 nothing changed.
- **So the law sets the 2, on this range.** It comes as 1 from a part that lengthens and 1 from the rounds, as the copying-parts record's "one chain gaining a member a round" predicts.

**Where I found the advisor wrong, or its answer unclear:**
1. It guessed loose counts drive the smallest disagreement (a join against two offshoots). They don't: all three members hold two loose distinctions each, checked exactly. The disagreement also survives the between-knots reading. In aggregate it is right: under ordinary growth, discordant pairs fall from 17,448 to 5,438 under that reading, and to 201 among pairs with equal loose counts.
2. It treated the old P16 (no disagreement under the copying law with retiring) as a replication. It was vacuous: all 1,224 comparisons are tied in delay.
3. Its "taking rules keep every knot within a few steps" was in fact my first-version claim. It fails past 20 rounds: at round 100 the greatest holder steps are 17, 21 and 98 on three runs. That is now disclosed and predicted.

It was right on four counts I had wrong:
- The bare ring's step from n−1 to n is 3n−1, then n(2r+1).
- C(r+3,3) first reads within 0.3 of 3 at r = 13, not 14.
- The golden-ratio eddy can only read 5, not 6, at 50,000 knots.
- The member count M was empty below the kept range.

**Questions for its second look at KD 2–3 and 5.6:**
1. Should "j − 1 from the roster" be limited to rosters of fixed size, with the general form "the roster's exponent plus one" registered as a reading?
2. Is the class of made knots near s_min/2 enough for the gate, or should one near 3·s_min/4 be added?
3. Is the final segment ending at the kept range the right anchor for precedence (the bare ring then reads power 1, with power 2 listed before it)? Is the two-phase form wide enough?
4. Are C/c ≤ 2 and z ≥ 8a the right limits? The registered forms give C/c of about 1.52 and 1.76.
5. Are the fixed directions right: larger |κ| and |γ| nearer, smaller ρ nearer, given that κ alternates in sign with steps on the record's trees?
6. Is the headline rule strict enough, given that γ still depends on loose counts in part?
7. Is cutting run 4's knot test to round 25 acceptable, or should starts be cut instead?

**Not asked for, with the advisor's reasons:**
- All 3,157 five-knot starts: a sample of 1,000 is within ±2.6 points; ask only if a gate candidate appears.
- Every knot tested: the sample plus the cited argument is honest.
- A million knots: nothing registered needs a fourth power.

**Sentences for the owner**, adjusted to what is registered:
- "We will count the knots within r holder steps of a knot in the whole history each law makes from each supplied start."
- "From a start knot this count is the count of knots by round and says only how fast births grow. We expect it to grow like r² for more than half of the census starts under the cap of three, with shares under each start-once weighting."
- "We expect no start examined to give the same power from every knot examined on a range that lengthens with the rounds."
- "A bare ring reads 2 only as supplied ring plus rounds."
- "Separately, the roster at one round is expected to read 1 or nothing."
- "Under parity, two loose distinctions are tied or unrelated; this is argued for laws without taking and computed with taking."
- "Under not-all-equal the share of states where they differ is expected not to follow how soon descendants meet, and we will say how much of that is loose counts."
- "None of this is a claim about space; all of it is finite counts."

# (7) The definitions of the study of parts that meet again (FD)

# Parts that meet again: definitions

Epic `PARTS-MEET-AGAIN-20261124-001`, ticket `PARTS-MEET-AGAIN-20261124-001A`. Frozen on 2026-11-24 with the
pre-registration of ticket A, after the advisor's cold review (`advisor/answer.json`) and the thread's decisions on it. It extends
[the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md) of `RING-IN-BALANCE-20261123-001` ("the
definitions" below, cited by line) and changes nothing in them where every distinction has one or two holders. Words are
the glossary's and the definitions'. The canonical K1–K3 test is unchanged.

## 0. Words

- **Kept with their meaning in the definitions:** start, structure, place, loose, live, dead, usable, barred, member,
  h(u), k(u), met set, common knot, joinable, part, past its start, the same, group, owing, short, waits, retires, join,
  offshoot, demand, ration, treatment, round, come apart, returns, ended (definitions lines 9–93).
- **Shared** means held by two or more knots. The number of holders is given wherever it matters.
- **Take.** A birth takes a distinction; a shared distinction it takes gains a holder. This study's own laws use no other
  verb for the move. The other thread's records call it "re-read"; the word is theirs and appears only in citations.
- **Reads** is kept for the owner's sense: a part reads another when its course depends on whether the other is there.
  Rules and engines **use** or **look at** what they need.
- **The choice** is the rule that says which of several eligible shared distinctions a birth takes (section 2, item 5).
  The owner's "index" keeps his sense: which part of another pattern is looked at. Under the laws that take from beyond
  the parent (MET and the ancestor-taking laws) the choice decides which knots the new knot meets, and so stands in for
  his index there.
- New here, each defined where it first appears: **parent step, ancestor, the descendants of g, common ancestor,
  ancestral common knot, share nothing, wholly apart, one part again, one part for the first time, eligible, taking
  rule, parent-taking, ancestor-taking, course, trace, the paired test, the four marks of a pair, way**.
- "A knot meets only its parents and its children" holds **under the earlier laws** (the definitions, with every
  distinction held once or twice) and is never used here without that qualifier.
- "Root", the owner's candidate for the knot a set of knots descends from, is not adopted: the birth record is not a
  tree, since a join has two or more parents, and "root" is already used for the root of an equation that gives a rate.

## 1. Structures in which a distinction may have any number of holders

1. A distinction has one or more holders: **loose** with one, **shared** with two or more (definitions line 12,
   extended). A knot's places are fixed when it is made. Two facts used below:
   - **holders never decrease**: a birth adds itself as a holder of what it takes, and nothing removes a holder (run
     B(ii) of the paired test, section 5, is the one construction that does, and it is defined only where stated);
   - **a barred distinction is never unbarred**, and a knot never gains a place, so a knot that is no member never
     becomes one.
2. Two knots **meet** when they hold a common distinction, whatever its number of holders; the m holders of one
   distinction meet pairwise (the definitions' line 14, read for any number of holders; as the other thread's engines
   read it, `rlaw.py` lines 372–381).
3. Live, dead, member, h, k, met set, common knot, joinable, part, groups, owing and short are worded as in the
   definitions (lines 14–40), read with this meeting. **A knot is not in its own met set**: the met set of w is the set of
   members other than w that w meets, when there are at least two.
4. **Parents** are written by each birth (definitions lines 49–51; `LOCAL-ROUND-20261123-001/definitions.md` lines
   27–31): the birth record is not a reading of the holders. A start knot has none. One **parent step** goes from a knot to
   one of its parents. The **ancestors** of a knot are the knots reached by one or more parent steps; the **descendants of
   g** are the knots that have g as an ancestor, g not included; **X and its descendants**, for a set X, includes X.
   Start knots have no ancestors. A **common ancestor** of two knots is an ancestor of both; it says nothing of meeting.
5. An **ancestral common knot** of two members u and v is a common knot of u and v that is a recorded ancestor of each and
   not the parent of both. (The owner approved the term on 24 November 2026.) The start's own common knot of two start
   members, which is no recorded ancestor of their descendants, is not an ancestral common knot and is reported as its
   own class (section 5, item 7).
6. **Share nothing and wholly apart.** Two parts of a roster **share nothing** when no member of one holds a distinction
   that a member of the other holds. Link two parts when they share something; the **classes** of a roster are the sets
   of parts connected by such links. Two parts are **wholly apart** when they lie in different classes: the parts of the
   roster can then be split into two sets, one holding each, such that no part of one set shares anything with a part
   of the other. (A third part may not link them.)

## 2. One complete round with taking

Steps 1 to 8 of the definitions (lines 34–67), with these additions and exact readings.

1. **Order of births and names.** The joins are the kept groups: groups of three or more in lexicographic order of their
   sorted member names, then pairs in the same order. Then the offshoots, in increasing name of the member; a member's
   offshoots in increasing name of the loose distinction each takes. Each member gives its usable loose distinctions, in
   increasing name, to its births in birth order (its joins first). Under HOLD a member keeps the first of its usable
   loose distinctions after those its joins take, and its offshoots take the rest (as the ring study's engine does). New
   knots are named in birth order once every birth of the round is formed; their fresh distinctions are named after the
   demand step, in birth order, each knot's usable ones before its barred ones. A start's distinctions are named by its
   stars' labels in increasing order. The swap "order of births reversed" reverses the whole list of births before any
   distinction is given out.
2. **Eligible.** A distinction is **eligible** for a take when it has two or more holders at the start of the round. A
   distinction loose at the start of the round is never eligible. Several births may take one distinction in one round.
3. **SHORT-TAKES** (rule R, A230, as a treatment of a short member, in place of the base law's treatment). No group is
   cancelled. A short member gives its usable loose distinctions to its first births in birth order and, for each further
   birth, takes one distinction it holds that is eligible, is held at the start of the round by no other parent of that
   birth, and differs from the others it gives this round; which one, by the choice (OLDEST or NEWEST, ALL-CHOICES on small
   cases). A short member owes more than it holds, so it makes no offshoots. If some short member has no allowed
   distinction for one of its births, no birth is made in the round (a **residual stall**); the structure is then
   unchanged, so the residual stall repeats for ever and the run stops.
4. **Step 5′, the taking rule.** After the round's births are formed and before any is made, the law's taking rule (section
   3) adds distinctions to some births, read on the structure at the start of the round, birth by birth in birth order.
   Every taking rule adds at most one distinction to a birth, except CARRY, under which a join takes up to one for each of
   its parents. A take never repeats a distinction the birth already takes; the fresh count uses **distinct** inputs.
5. **The choice.** Among the eligible distinctions a birth may take, sorted by name:
   - **OLDEST**: the smallest name; **NEWEST**: the largest (A231, A236). Both use the names, and so the start's numbering.
   - **IN-TURN**: defined for offshoots: the i-th offshoot of one parent in the round (counting from zero, in birth order)
     takes the i-th, cycling. With one offshoot per parent it equals OLDEST. A join under MET(IN-TURN) takes by OLDEST;
     IN-TURN is not used with SHORT-TAKES.
   - **BY-COUNT**: the taking birth's parent's number of places (for a join, its first parent's, by name), modulo the
     number of eligible distinctions, counting from the oldest at zero. It uses the structure only.
   - **BY-RECEIVED** (a named case only): the parent's number of places less its number of parents, modulo the number of
     eligible distinctions, counting from zero. It uses the birth record.
   - **ALL-CHOICES**: every choice enumerated (small cases).
6. **Step 6, demand.** As the definitions, with the met sets read from the structure after the takes and before the fresh
   distinctions, so that a knot that took a shared distinction is already met by that distinction's other holders (the
   other thread's lookahead, `rlaw.py` lines 480–494). Swap: **demand before the takes**, read on the structure in which
   each birth holds only what it took loose (and, under SHORT-TAKES, what it was given).
7. **Step 7, fresh distinctions.** The ration's formula with p read as the number of distinct distinctions the birth takes
   (A235, `ONE-PARENT-REREAD-20261123-001A/preregistration.md` line 47). For a birth that takes nothing extra this is its
   number of parents, so nothing in the definitions changes. Swap: **fresh by parents**.
8. **Closing (parity).**
   - **IMPLIED** (primary): a birth receives no fresh distinction when the parity of what it takes lies in the span of the
     rules of the knots of the structure before the round (A230's form, `REREAD-...-001A/preregistration.md` line 47).
     Each birth of the round is tested against the structure before the round, not in sequence, so that the result does
     not depend on the order of births within the round. Several births of one round may be implied. The definitions'
     clauses "it is then the round's only birth, nothing is barred and no old member keeps anything" do not apply.
   - **LITERAL**: the definitions' exception (line 63), a swap only, never in a paired test (any barred distinction
     switches it off everywhere, definitions lines 73–74, and run B(i) always bars).
   - With every distinction held at most twice, in a connected structure, the two agree (the settled statement of
     `RING-IN-BALANCE-20261123-001A/preregistration.md` lines 100–101). A birth that IMPLIED leaves with no fresh distinction
     and that then fails the knot test is a failure.

## 3. The laws

### 3.1 The base laws and their swaps

- **RING-LAW**: (CAP-3, CANCEL-WAIT, RELEASE), "the two added rules" (definitions line 70); swap with FILLERS.
- **COPY-LAW(t)**: (FLOOR1, t, RELEASE), t = CANCEL-RETIRE, CANCEL-OFFSHOOT, CANCEL-WAIT. FLOOR1 is primary because every
  birth receives a fresh distinction under it (`COPYING-PARTS-20261123-001A/results.md` line 91). Swaps: FLOOR0 and
  ONE-FEWER (a join of three parents can receive nothing).
- **CAP-3(t)**: (CAP-3, t, RELEASE) on the copier starts, a registered swap in every ladder run: a ration that uses
  demand, so that a meeting can change a birth's fresh count through its demand.
- With no taking rule, after round 0 parts that have come apart are never joinable again (the earlier laws' settled
  statement, `RING-IN-BALANCE-20261123-001A/preregistration.md` lines 95–99, an argument).

### 3.2 Arm A: the record's laws

- **Q(choice)**, rule Q (A235), **parent-taking**: every offshoot whose parent holds an eligible distinction also takes one
  of them, by the choice. Joins do not take (rule Q's wording: a one-parent birth). A short member's offshoots, under
  CANCEL-OFFSHOOT, take.
- **SHORT-TAKES(choice)**: section 2, item 3.
- **Late start**: the base law alone through round s0, and Q or SHORT-TAKES from round s0 + 1; s0 is 2 on the ring starts
  and the three-knot start and 3 on the two-knot start, the first round after which the base law has parts that came
  apart. This arm exists because rules Q and R, from round 1, keep the would-be parts together, so that almost no pair is
  left to test.
- **The A225 move** is not a growth law. It is registered as one supplied control, placed by hand on each object (3.4).

### 3.3 Arm B: the ladder

| Law | The rule | Kind |
| --- | --- | --- |
| **RECORD-k** (k = 2, 3) | Two members are also joinable when the birth record gives them a common ancestor at most k parent steps above each. Nothing is taken. | not taking: it links nothing in the structure and drops the definitions' requirement that some knot meets both |
| **ALL-JOINABLE** | Every two members are joinable. | the trivial end |
| **Q(choice)** | as arm A | parent-taking |
| **CARRY** | Every birth, joins included, takes for each parent p the oldest eligible distinction that p shares with one of p's recorded parents (for a start parent, its oldest eligible distinction). | parent-taking; one distinction of a knot is carried to its descendants |
| **MET(choice)** | Offshoot clause: an offshoot also takes one eligible distinction that is held by a knot its parent meets and is not held by its parent. Join clause: a join also takes one eligible distinction held by a common knot of its parents (a knot that meets every parent) and held by no parent. | record-free; under RELEASE a member makes all its births in one round, so it has no children when it makes them; while every distinction the parent holds has at most two holders, the knots it meets are then its parents, and the offshoot clause is STEPS-1 (for a parent that is not a start knot) |
| **STEPS-k(choice)** (k = 1, 2) | Every offshoot also takes one eligible distinction held by a recorded ancestor exactly k parent steps above its parent and not held by its parent. Several such ancestors: the union of their eligible distinctions, then the choice. No ancestor k steps above, or nothing eligible: no take. | ancestor-taking |
| **UP-TO-k(choice)** (k = 2) | The same with every ancestor 1 to k parent steps above the parent (the union). UP-TO-1 is STEPS-1. | ancestor-taking |
| **FIRST(PARTS)** (one control) | Every offshoot also takes, by the choice, one eligible distinction not held by its parent, held by its parent's nearest recorded ancestors (fewest parent steps) whose member descendants lie in two or more parts of the roster. | ancestor-taking; its trigger looks at the other part |

Joins do not take under Q, STEPS-k, UP-TO-k and FIRST: a join's parents are already joinable, and these rules are meant
to act where a part is founded, which is by offshoots. This is a scaffold. MET and CARRY have join clauses.

**The cost of a law** is a vector, compared component by component:
- holder steps looked at: the largest number of holder steps, from the taking birth's parent, to a knot whose places or
  holders the rule looks at;
- parent steps of the birth record looked at;
- anything looked at across the whole roster;
- what supplies the choice: the names (OLDEST, NEWEST), the order of births (IN-TURN), the structure (BY-COUNT), the
  record (BY-RECEIVED), or an enumeration.

| Law | Holder steps | Record steps | Whole roster | Choice |
| --- | --- | --- | --- | --- |
| Q, SHORT-TAKES | 1 | 0 | no | the choice |
| CARRY | 1 | 1 | no | oldest |
| MET | 2 | 0 | no | the choice |
| STEPS-k, UP-TO-k | at most k + 1 | k | no | the choice |
| FIRST(PARTS) | any | any | yes: the parts | the choice |
| RECORD-k | 0 | k | no | none |
| ALL-JOINABLE | 0 | 0 | yes | none |

### 3.4 The A225 control, placed by hand

After round s, with X and Y two parts that are wholly apart, one knot is placed by hand. It takes two distinctions, each
then held by exactly two knots: one that X's lowest-named member holds with one other knot, and one that Y's
lowest-named member holds with one other knot (the oldest such, by name). It receives one fresh distinction and has no
parents. It is the supplied birth of A225 (`THIRD-HOLDER-20261123-001B/preregistration.md` line 49), placed where it
links two parts that are wholly apart. Nothing in the growth makes it.

### 3.5 The HOLD arm

The base laws with HOLD in place of RELEASE, with no taking rule, with Q and with STEPS-2. Under HOLD a member that keeps a
distinction meets its own child, so parts need not be wholly apart; the paired test is run on every pair of parts,
labelled wholly apart or not. The two-knot start's own two parts (its two knots meet directly and are not joinable) are
labelled the same way.

## 4. Coming apart, and one part again

1. **Come apart** keeps the definitions' sense (line 87): the members after round t descended from a part after round s
   lie in two or more parts.
2. **The descendants of X after round s**, X a part after round s: the knots made after round s that have a parent among X
   and its descendants.
3. Two parts X and Y after round s that are wholly apart, and that descend from one part after an earlier round, are
   **one part again** at round t > s when a member of X or its descendants and a member of Y or its descendants lie in one
   part after round t. When X and Y have no common part in their ancestry they are **one part for the first time**. The
   owner's "meet again" is quoted only in his words.

## 5. The paired test

1. **Runs.** Run A grows the start under the law. For a round s and two parts X and Y after round s:
   - **B(i), the second part barred** (primary): run A through round s; then every usable loose distinction of Y's members
     is barred; Y stays built and makes nothing more; then the same law.
   - **B(ii), the second part never made** (swap): run A through round s; then Y's members are removed with their fresh
     distinctions, and each distinction they took returns to its other holder, loose and barred. It is defined only when
     no knot outside Y holds a fresh distinction of a member of Y and every distinction a member of Y took has exactly one
     other holder; otherwise it is reported "not defined".
   - Runs are compared only through the last round both reached, with the same bounds on rounds and knots.
2. **The trace of X.** For each round t > s: the births of round t all of whose parents are in X or its descendants (a
   joint birth, with a parent outside them, is excluded; its children are included), each with its kind, its parents, what
   it takes, which of those were shared at the start of the round, its fresh count and its usable and barred fresh
   counts; the members after round t in X or its descendants with h and k; and their met sets, each met set intersected
   with X and its descendants first and then reduced to the inclusion-maximal ones. Knots made by round s and
   distinctions existing after round s keep their names; knots made after round s for X and its descendants, and their
   fresh distinctions, are renamed in order of name (an order-preserving renaming); any other new knot or distinction is
   "other". **The course of X** is its trace. The demand of X's births is recorded beside the trace and reported on its
   own line (the first round at which it differs); it is not part of the course.
3. **The four marks of a pair** (facts about run A, and comparisons; not a scale):
   - **one part again**: the first round t > s at which they are one part again (section 4);
   - **a joint birth**: the first round of run A with a birth that has a parent in X or its descendants and a parent in Y
     or its descendants;
   - **the course differs**: X's trace in run A and in run B(i) differ (the first round);
   - **the course differs with what the other is**: X's trace differs between two runs A from starts that differ only in
     the holdings of the start knot Y descends from (renaming every knot and distinction of the trace by first
     appearance, since the two starts are numbered differently).
4. **The choice is necessary** (a control, not a mark): the same start and law, with only the takes of X and its
   descendants using another choice (OLDEST, NEWEST, IN-TURN, BY-COUNT, BY-RECEIVED) while every other birth keeps the
   law's own; reported: whether the course differs under each.
5. **The way** of a "course differs" mark, by the first differing step of the first differing round, in the order of the
   round's own steps: **a group or owing** (the groups containing a member of X or its descendants, or their owing); **a
   round-wide trigger** (a stall, a residual stall or a closing differs between the runs); **a take**; **fresh** (the
   fresh counts, through the demand).
6. **Confirmation through a meeting.** A masked run M is run A in which, from round s + 1, no member of X or its
   descendants is joinable with a member of Y or its descendants (the pair is removed from the joinable relation in the
   round and in its demand step). The difference is **through a meeting** when X's trace in M equals its trace in B(i). If
   not, an isolating run M′ makes no member of Y or its descendants joinable with any other member; when X's trace in M′
   equals B(i), the difference is **through a third part**.
7. **The verdict** of each "course differs" mark:
   - **through a knot the growth made**: confirmed through a meeting (or a third part), and at the round they are one part
     again X's and Y's descendants are joinable using only met sets that have a common knot made after round 0;
   - **through a start knot** (the start's own meeting reopened): confirmed, and joinable only through met sets whose
     common knots are start knots;
   - **supplied**: the way is a round-wide trigger; or the law is FIRST(PARTS) and the way is a take (its rule looked for
     the other part); or the law is RECORD-k or ALL-JOINABLE (the record alone);
   - **unconfirmed**: none of these.
   With each verdict, the class of the knots linking the two at that round: an ancestral common knot (made, or a start
   knot that is a recorded ancestor); a knot made by the growth that is no ancestor of both; a start knot that is no
   recorded ancestor of both (the start's common knot of the founders).
8. **Pairs.** For each round s from 1 to 6: the parts after round s in order of their smallest member name; the first eight;
   every pair (i, j), i < j, in lexicographic order, that is wholly apart, at most four per round. Each pair is labelled as
   having come apart (a common part in its ancestry) or not. In the HOLD arm, and on the two-knot start's own parts, every
   pair is taken and labelled wholly apart or not.

## 6. The two hypotheses that split the laws

- **H1, parents only.** Every distinction a new knot takes is held, at the start of its round, by one of its parents; its
  other places are fresh.
- **H2, joinable from the structure.** Two members are joinable only when some knot meets both, and every birth's parents
  lie in one part of the roster its round reads.
- The earlier laws, Q and SHORT-TAKES (every choice, every start round), CARRY, and every ration, treatment, release rule,
  extra and closing of the definitions satisfy H1 and H2. RECORD-k and ALL-JOINABLE break H2. MET, STEPS-k, UP-TO-k and
  FIRST break H1. The A225 control breaks H1 once, by hand.

## 7. The knot test with three or more holders

- **Parity**, two methods that must agree on every knot: **ranks** (the definitions' line 133), which needs no limit on
  holders; and **kernel**, a basis of the allowed states projected onto the knot's places, rank |S| − 1. The definitions'
  cut method needs two holders per shared distinction and is not used. Both are checked against brute force before any run.
- **Not-all-equal**: a SAT solver for each of the 2^|S| assignments of each knot's places (definitions lines 137–139).
  Under not-all-equal with a ration that gives every birth a fresh distinction (ORD, CAP-k, FLOOR1, RATION-k), every round
  extends (a birth with a fresh distinction forbids no old word), and a knot's relation on its places does not change
  after its birth: a knot tested at any round after its birth is tested for every later round. Under FLOOR0 and ONE-FEWER
  a birth can receive nothing, and every knot is tested at every round.
- **The birth method** (not-all-equal, for knots of any size, where every birth receives a fresh distinction). A knot u
  born in round t passes, at round t and every later round, exactly when its inputs that existed before round t are
  jointly free in the structure before round t (every assignment of them extends to an allowed state). The argument: at
  the end of round t every other birth of the round can be satisfied by one of its own fresh distinctions, which nothing
  else holds yet, so the allowed states on u's places are those whose old part is allowed before round t and which are
  not all equal; and u's own fresh distinction completes any old part to one that is not all equal. Joint freedom of a
  set I is decided exactly by removing, again and again, every knot that has a distinction held by it alone among the
  knots left and not in I (such a knot can always be satisfied); splitting what is left into pieces linked by
  distinctions outside I; and testing, for each piece, every assignment of the distinctions of I it touches (half of them,
  by the symmetry of flipping every distinction). A start knot is tested directly. The method is checked against the
  direct test on every knot of at most 12 places of run A, and on drawn grown structures with failing knots.
- Each run's knots are tested under the run's own knot law. A knot that passes has, in the whole structure, exactly its
  own rule on its places: constrained as a whole, every part free, some state allowed (K1–K3 with forgetting).
- With three or more holders a birth with a fresh distinction need not pass: its inputs may be constrained together. The
  earlier laws' settled statement (`RING-IN-BALANCE-20261123-001A/preregistration.md` lines 100–105) needs two holders.

## 8. What is supplied by hand (scaffolds)

Everything the definitions list as supplied (line 157), and here: every taking rule (rule Q, A235; SHORT-TAKES from rule R,
A230; CARRY, MET, STEPS-k, UP-TO-k, FIRST(PARTS), RECORD-k and ALL-JOINABLE, all new); the choice of each (A231, A236 and
the new ones); the late start and its round s0; the order of births and the naming of the start; the eligibility rule;
reading demand after the takes; the fresh count by distinct inputs; the closing in two forms; the birth record wherever a
law looks at it; the A225 control; the paired test's barring and removal, the trace and its renaming, the masked runs,
the marks, ways and verdicts; the bounds on rounds and knots.


# (8) The shared definitions (SD), with line numbers

     1	# A ring in balance: definitions shared by the three studies
     2	
     3	Epic `RING-IN-BALANCE-20261123-001`, 2026-11-23. Frozen with the three pre-registrations, before any of the study's code is
     4	written. Tickets A, B and C cite this file and add only what is their own. The canonical K1–K3 test is unchanged. Words are the
     5	glossary's (Intuitions guide). The growth records' "junction" is a knot and their "growing end" is the live roster. Their
     6	"witness" is here a **common knot**, their "witnessed set" a **met set** and their "adjacent" **joinable**, because the glossary
     7	keeps witness for a helper variable and graph theory uses adjacent for what the program calls meeting.
     8	
     9	## Structure
    10	
    11	- A **structure** is a finite set of knots, each holding a set of distinctions, its **places**. A distinction has one or two
    12	  **holders**. It is **loose** with one holder and **shared** with two. Every knot of a start has at least three places, and so
    13	  has every new knot except one that receives no fresh distinction (below).
    14	- Two knots **meet** when they share a distinction. A knot is **live** while it holds a loose distinction and **dead** otherwise.
    15	- A **start** is a structure given before any birth, written as its list of knots, each a list of distinction numbers (the
    16	  records' stars).
    17	- A loose distinction is **usable** unless the law has **barred** it: a barred distinction stays loose and is never taken by any
    18	  birth. (The Intuitions guide and the site call a barred distinction "never used".)
    19	
    20	## The live roster
    21	
    22	- The **members** of the live roster are the knots holding at least one usable loose distinction. Write h(u) for the number of
    23	  usable loose distinctions member u holds and k(u) for the number of barred ones. A knot holding only barred distinctions is
    24	  live and is not a member.
    25	- A **met set** is the set of members that one knot of the structure meets, when it has at least two members. That knot is a
    26	  **common knot** of those members; it may be dead or itself a member. Two knots with the same met set count once.
    27	- Two members are **joinable** when some met set contains both. A **part** of the live roster is a connected component of the
    28	  relation joinable. The roster is **past its start** when no member meets a member (the records' positive age).
    29	- Two rosters, or two parts, are **the same** when a one-to-one renaming of members carries h, k and the family of
    30	  inclusion-maximal met sets of one onto the other.
    31	
    32	## One complete round
    33	
    34	A **law** is a knot law (parity or not-all-equal), a ration, a treatment and optional extras. One round, on real knots:
    35	
    36	1. **Groups.** First take every inclusion-maximal set of at least three pairwise joinable members that is contained in no
    37	   single met set. Then take every joinable pair that is contained in none of the sets just taken. These are the groups
    38	   ([ORDINARY-DYNAMICS-20261120-001](../ORDINARY-DYNAMICS-20261120-001/end_operator.md), "The operator on the present end", step 1).
    39	2. **Owing.** Member u owes one usable loose distinction to each group containing it. It is **short** when it owes more than
    40	   h(u). Shortness is read once, here, for the whole round.
    41	3. **Treatment of a short member.**
    42	   - STALL: if any member is short, no birth is made and the growth has stalled.
    43	   - CANCEL-OFFSHOOT: every group containing a short member is cancelled; the short member makes an offshoot from each of its
    44	     usable loose distinctions.
    45	   - CANCEL-WAIT: every group containing a short member is cancelled; the short member **waits**: it makes nothing and keeps
    46	     everything it holds.
    47	   - CANCEL-RETIRE: every group containing a short member is cancelled; the short member **retires**: it makes nothing now or
    48	     later, and its loose distinctions are barred.
    49	4. **Joins.** Each group that is kept makes one new knot, a **join**, whose parents are its members; it takes one usable loose
    50	   distinction from each.
    51	5. **Offshoots and the release rule.** A member that is not short, after paying its kept groups, makes one new knot of one
    52	   parent, an **offshoot**, from each usable loose distinction it has left. RELEASE (the default): this includes the
    53	   distinctions that its cancelled groups would have taken. HOLD: it keeps those and makes offshoots only from the rest. With
    54	   the extra NO-OFFSHOOT it makes no offshoot, and the distinctions an offshoot would have taken are barred.
    55	6. **Demand.** Count every new knot as a member holding one usable loose distinction, whatever it will receive, and keep every
    56	   old member that still holds a usable loose distinction after steps 3 to 5 (one that waits; under HOLD, one that keeps what
    57	   its cancelled groups would have taken) with what it holds. Form the groups of that roster as in step 1. The **demand** D of
    58	   a new knot is the number of those groups that contain it.
    59	7. **Fresh distinctions (the ration).** A new knot with p parents and demand D receives f fresh distinctions, each loose and held
    60	   by it alone. With q = max(D, 3 − p, 1), the ordinary count:
    61	   - ORD: f = q. CAP-k: f = min(q, k). RATION-k: f = max(k, 3 − p).
    62	   - ONE-FEWER: f = min(q, max(3 − p, 0, q − 1)). FLOOR0: f = max(3 − p, 0). FLOOR1: f = max(3 − p, 1).
    63	   - **Closing exception** (parity only, every ration): a new knot that takes every loose distinction of the structure receives
    64	     none; it may then have fewer than three places. It is then the round's only birth, nothing is barred and no old member
    65	     keeps anything. Under not-all-equal there is no exception
    66	     ([NAE-GROWTH-20261119-001](../NAE-GROWTH-20261119-001/nae_growth.md): the growth reads the knot law in this one place).
    67	8. **Extra FILLERS.** Of a new knot's f fresh distinctions, min(f, D) are usable and the rest are barred.
    68	
    69	The records' ordinary growth, the cheapest growth of lesson 8.1, is the law (ORD, STALL). **The two added rules** are the law
    70	(CAP-3, CANCEL-WAIT with RELEASE). **The three added rules** are (CAP-3, CANCEL-WAIT with RELEASE, FILLERS). They were added by
    71	hand (assumption A224, a scaffold); RELEASE is part of what was added. The pilot's program counted a short member by all its
    72	loose distinctions; the two readings agree, because a member holding a barred distinction owes exactly its usable count in
    73	the one round it acts. One barred distinction anywhere switches the closing exception off everywhere, since the exception needs
    74	a birth that takes every loose distinction there is.
    75	
    76	A distinction taken by a new knot becomes shared between its old holder and the new knot. Which of a member's usable loose
    77	distinctions goes to which birth makes no difference up to renaming.
    78	
    79	## Kinds of outcome under complete rounds
    80	
    81	A run is one start grown under one law through a stated number of rounds, or until a stated number of knots. After each round:
    82	
    83	- The growth has **stopped** when the roster has no member, **stalled** (STALL only) when a member is short, and **jammed** when
    84	  the roster has members and the round makes no birth.
    85	- A part Y of the roster after round s, past its start, **returns** at round t > s when the members after round t that descend
    86	  from Y (through parents; a waiting member descends from itself) include a part that is the same as Y. The other parts those
    87	  descendants form have **come apart** from Y, and Y **gives parts off** when there is at least one. Returns are searched with
    88	  the least s first and then the least t, and t − s is the period.
    89	- The roster is **in balance** from round s with period T when at least one birth is made in every round and the whole roster
    90	  after round t + T is the same as the whole roster after round t for every t ≥ s in the run. The structure still grows.
    91	- A part has **ended** when none of the knots descending from it is a member. It may still hold barred distinctions.
    92	- For a census a run is given one kind, the first that applies: stalled; jammed; stopped; a part returns giving parts off; a
    93	  part returns giving none off; grows to the bound with no return found.
    94	
    95	## One part at a time, and one birth at a time
    96	
    97	- **Part-round law.** A move is one complete round of one part: steps 1 to 8 applied to the members of that part alone, the
    98	  other parts left as they are (the closing exception as stated: only for a birth that takes every loose distinction of the
    99	  whole structure). The **own time** of a start knot is 0; a new knot's is one more than its parents'; and a member that
   100	  waits through a move of its part gains one. So a member's own time is the number of moves its line of descent has taken
   101	  part in. A **priority** chooses the part that moves next among the parts that would make a birth:
   102	  - ALL-IN-TURN: every part once, then again; this is the complete round.
   103	  - UNIFORM: each part with equal chance.
   104	  - BY-MEMBERS: each part with chance in proportion to its number of members.
   105	  - LARGEST: a part with the most members; SMALLEST: one with the fewest; ties uniform.
   106	  - MOST-LOOSE: a part whose members hold the most usable loose distinctions in all; ties uniform.
   107	  - LEAST-TIME: a part whose members have the least own time; ties uniform. This priority reads the history, not the structure.
   108	- **Birth-by-birth law** (the present-state reading of [ROUND-FREE-20261119-001](../ROUND-FREE-20261119-001/round_free.md), with
   109	  waiting). A move is one birth, and everything is read again after every move.
   110	  1. Form the groups of the present roster as in step 1, with every knot allowed as a common knot (ANY) or only dead knots
   111	     (DEAD). A group is **open** when no knot already made has all of its members among its parents.
   112	  2. A member is short when it is in more open groups than h(u); a short member makes nothing. Under FIRST-COME, used only to
   113	     check the engine against the record, no member counts as short.
   114	  3. Every open group with no short member is a join move. A member that is not short and holds more usable loose distinctions
   115	     than the number of open groups without a short member that contain it has an offshoot move. (Under FIRST-COME: every open
   116	     group is a join move, and a member has an offshoot move when h(u) exceeds the number of open groups containing it.)
   117	  4. The new knot receives max(3, 3 − p) fresh distinctions (RATION-3), or max(d, 3 − p, 1) (PRESENT-ORD), where d is the number
   118	     of open groups containing it immediately after its birth, the new knot counted as a member before it receives anything.
   119	     Closing exception, parity only: a move that takes every loose distinction of the structure, with d = 0 where d is read,
   120	     receives none.
   121	  5. Start knots have **generation** 0 and a new knot has generation one more than the greatest generation of its parents; a
   122	     move's generation is the greatest generation of its parents. The next move is chosen uniformly among all moves (UNIFORM)
   123	     or among the moves of least generation (BY-GENERATION), with joins first, offshoots first, or uniformly among those. The
   124	     generation is the simulator's record of who was made from whom; it is not read from the structure.
   125	  - A birth-by-birth run has **jammed at generation g** when no move of generation g or less is available and some member of
   126	    generation g or less is short.
   127	
   128	## The knot test
   129	
   130	- **Parity.** Each knot is the rule that its places have even parity. A knot with place set S passes K1–K3 in the whole
   131	  structure when the allowed states of the structure, restricted to S, are exactly the even assignments of S. Two methods are
   132	  run and must agree on every knot. Ranks: with H the matrix over the field of two elements with one row for each knot, the
   133	  rank of H less the rank of H with the columns of S removed is one (the records' test, ORDINARY-DYNAMICS, `rulers.py`). Cut:
   134	  in the graph with one vertex for each knot and one for the outside, an edge between the two holders of each shared
   135	  distinction and an edge to the outside for each loose one, deleting the knot leaves the rest connected (the knot is not a cut
   136	  vertex; the allowed states are the graph's cycle space).
   137	- **Not-all-equal.** Each knot is the rule that its places are not all equal. A knot passes when the assignments of S that
   138	  extend to an allowed state of the whole structure are exactly the assignments that are not constant, decided by a SAT solver
   139	  for each of the 2^|S| assignments (the records' test, ORDINARY-DYNAMICS, `source_cert.py`).
   140	- **Extension.** A round, or a move, extends when every allowed state of the structure before it is the restriction of an
   141	  allowed state after it.
   142	
   143	## Named starts
   144	
   145	- **Ring(n, a).** Knots 0 to n − 1. Knot i shares one distinction with knot i + 1 (mod n) and holds a loose distinctions.
   146	  Ring(5, 3) is the start of the golden-ratio eddy.
   147	- **Cycle through dead knots, doubled, D2(n, a).** Members 0 to n − 1, each holding a loose distinctions, and dead knots
   148	  w_0 to w_{n−1}; w_i shares two distinctions with member i and two with member i + 1 (mod n), so w_i has four places and its
   149	  met set is {i, i + 1}.
   150	- **Cycle through dead knots that meet one another, DW(n, a).** As D2 with single meetings: w_i shares one distinction with
   151	  member i, one with member i + 1, one with w_{i−1} and one with w_{i+1}.
   152	- **The seven-knot generator.** Stars [0,1,2,9,10,11], [0,1,3], [4,5,12,13,14], [6,7,15,16,17], [2,3,4,6,18,19,20], [7,8,21,22],
   153	  [5,8,23,24] ([GENERATORS-20261120-001](../GENERATORS-20261120-001/source.md)).
   154	
   155	## What is supplied by hand
   156	
   157	The complete round (assumption A104); every ration other than ORD, every treatment other than STALL, the release rule and both
   158	extras (A224); the part-round law, the birth-by-birth laws and every priority; the starts; the reading of a part as a thing (as
   159	in A125); the bounds on rounds, moves and knots; and each weighting named where a share is given. Each study says which of
   160	these it swaps.
