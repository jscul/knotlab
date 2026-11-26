# A sign to the sides: what a swap of two sides of a meeting pattern makes

Epic `SIDE-SIGN-20261126-001`, under G18, at the coordinator's pick after the owner's message: "it might be a symmetry
thing too where there's a sign to the sides or something. It'd be a complex meeting pattern". Design, arguments and
predictions frozen before the census, after the advisor's review; [the code](sides.py), [the controls](controls.py)
([output](controls.txt)), [the named cases](named.py), [the census job](job.py), [the pre-count](precount.md). The
results will be added in a section of their own after the run; nothing above it changes except by a dated notice.

## The question

The coordinator's reading of the owner's idea, in three parts. Take meeting patterns made by ordinary growth that have a
symmetry exchanging two sides, with no added rule.

1. Do the allowed states sort into those the swap leaves alone and those it turns into their complement, and does growth
   keep the two kinds apart, so that the pattern itself carries a two-valued label?
2. Are there patterns where going round a loop brings you back with the two sides exchanged, so that the label cannot be
   removed by relabelling?
3. If such a label exists, can it weight whole configurations so that two ways of reaching one reading cancel, and does
   that survive with readers' settings free and no signalling?

Stop at a native sign with a frozen runnable test, or at an argument or clean census showing every such label is trivial
or supplied by us. Two later questions from the coordinator, after the other thread found a preserved two-class sign under
parity that needs no symmetry (`READS-HOLDERS-SOURCES-20261120-001`; mapped in `TWO-CLASS-SIGN-20261126-001`): is that
sign the label a swap gives, and does a swap exchange its two classes, fix them, or act as the missing second check that
would put a relative sign between them?

**What is added together.** The fold study found that the missing piece is a sum, not a sign: nothing in the law adds
orders together (`FOLD-SIGN-20261126-001`). Here the things added together are the **completions of a reading**: every
allowed state that agrees with what the readers read. Forgetting the unread distinctions is native (lesson 1.6); counting
each completion once is the counting weighting (A240); adding them with signs, and the two ways of turning the signed sums
into chances (R1 and R2 below), are readings we supply. The swap supplies only which distinctions are paired, which states
it keeps or flips, and which side is which.

## The objects

- **Swap.** A renaming of a stage of order two that moves at least one knot: a permutation of the knots keeping how many
  distinctions each pair of knots shares and how many loose distinctions each knot holds, carried to the distinctions by a
  **lift**. The **minimal lift** keeps every distinction it can (the shared distinctions of a pair of knots the swap keeps,
  and the loose distinctions of a knot it keeps); the **maximal lift** exchanges them two by two. Swaps that a renaming of
  the stage carries into one another give the same results, so one is read from each such class.
- **Sides.** The knots the swap moves, joined when they share a distinction the swap moves. **Two-sided**: two such
  groups, which the swap exchanges, and these are the sides. **Several**: more groups, exchanged in pairs, so which groups
  make a side is a choice. **One-sided**: some group is carried onto itself, so a chain of knots joined through moved
  distinctions leads from a knot to its image and the sides cannot be told apart.
- **Kept and flipped states.** A state is kept when the swap leaves it unchanged and flipped when the swap turns it into
  its complement (every value reversed).

## Arguments (before the census)

**A1. Growth keeps every swap of the knots (argument from a proved lemma).** From round 1 on, ordinary growth reads a stage
only through its live knots, their open counts and the maximal blocks of live knots meeting a common knot (Lemma R,
`REDUCE-BLOCKS-20261119-001`, proved and refereed). A permutation of the knots that keeps all three carries the round's
births onto births with the same parents and fresh counts, so it extends to the next stage, again of order two. Growth
can add swaps (two births of one parent with the same fresh counts are exchanged by one) and never removes a swap of the
knots. **The lift need not extend** (the advisor's counterexample): on the five-knot ring, a reflection keeping knot 0
exchanges the groups {0, 2} and {0, 3}, so its extension must exchange knot 0's two loose distinctions, which the minimal
lift kept; so a swap's pairs, and its kind of sides, can change from round to round. Check (P1): every start with a swap
at round r has one at round r + 1 where the growth goes on, from the pre-count's rows.

**A2. Flipped states need a swap that moves every distinction (proved).** If the swap keeps a distinction d, a flipped
state would hold both values at d. Under parity, x and its complement are both allowed only if every knot has an even
number of places, so after a round that makes a knot of three places no stage has a flipped state under parity. The
finer trace is the mismatch x + swap(x), of which kept and flipped are two values (the advisor); the study also counts
the states **flipped on the moved distinctions** (the mismatch is every moved distinction, the kept distinctions
unchanged), which under parity need only that every knot holds an even number of moved distinctions.

**A3. The sides exchanged round a loop (proved; the literature's double cover).** For a one-sided swap, read the pattern
with the two sides not told apart: each pair of knots {k, swap(k)} as one, each pair of distinctions {d, swap(d)} as one.
In that reading a chain of knots that leads from k to swap(k) is a loop, and going round it returns with the sides
exchanged. This is the literature's nontrivial double cover (Möbius's band over its central circle is the standard
example; here it is a fact about which knots share which distinctions, not a drawing). No renaming removes it, since
whether a swap is one-sided is unchanged by renaming. What a state sees of it: a parity read off a state's values along a
loop of the pattern is a parity along a loop that closes in the pattern, and the twist vanishes on those (the double cover
read on itself is trivial), so no such read carries it. Its only trace in the states is the sort into kept and flipped:
a flipped state is exactly an assignment that changes value each time a twisted loop is gone round, a kept state one that
does not. By A2 that trace is empty under parity once growth has made a three-place knot. What reads the twist directly
is the two-distinction read x_d + x_swap(d), the two ends of an open chain, which the frozen single-distinction readers do
not make (not shown).

**A4. A swap and the preserved two-class sign (proved for two classes).** Under parity the allowed states with the
shortest changes through each distinction fall in some stages into classes (the other thread's sign). A renaming carries
shortest changes through d onto shortest changes through its image, so a swap acts linearly on the classes (the allowed
states S over the group H the changes generate) and keeps the class of the all-0 state. **Where there are exactly two
classes a swap never exchanges them**, and the class sign is unchanged by every swap. Where there are four or eight (24
and 2 census starts in `TWO-CLASS-SIGN-20261126-001`) a swap can permute the other classes (the advisor); P9 checks
every swap's action on every census stage of rounds 0 and 1 with two classes or more. A swap is a permutation of the allowed states, so it leaves the counting
weighting unchanged and gives the classes no relative sign: it cannot be the missing second check by itself. Exchanging the
classes takes a translation by an allowed state of the other class (adding it to every state), which the parity law allows
and no renaming gives.

**A5. Under parity a character weights no excess (proved by a lemma and an exhaustive check).** Under parity the allowed
states are closed under addition, and a weighting (−1)^q(x) with q of degree at most two in the values (a quadratic sign)
gives, at any four read distinctions, a signed weighting of the four values that is a constant times a quadratic sign on
an affine set of four-bit words (the sum over the completions of each word is a Gauss sum over a coset of one fixed
subspace; the literature's fact that marginals of a quadratic-phase function are of the same kind). Control C4 runs every
quadratic sign on every affine set of four-bit words: the largest R1 CHSH (below) is 4, reached only on eight-word sets in
which one read of each reader is tied to one of the other's, and **no sign of degree one (a character) exceeds 2**. So
under parity and R1 the preserved two-class sign, every other character, and the sector sign of a swap (W3, a degree-one
sign on the kept-or-flipped states, which form a coset of a subspace) never give an excess. More simply (the advisor):
a nontrivial character sums to zero over all allowed states, so its normalizer is 0 and it fails G0, and a trivial one is
a nonnegative weighting; under R2 a character gives at most 2. So for W3, W3m, W5 and W1 on kept states (a character there)
"no hit" under parity is empty, and is reported as G0 failing, not as a test passed. The pair and block signs are of
degree two and are not excluded; the advisor's lemma (unverified): W2's sum over the completions of four reads is
nonnegative unless both sides' parities are functions of the four read values, so W2 can exceed 2 only where the sides are
small and the reads are tied.

## The census (frozen)

**Population.**
- *The census:* the forbidding study's 7,075 arrangements of three to five knots (`FORBID-EDITS-20261126-001`, each once up
  to relabelling), grown 0, 1 and 2 rounds by ordinary growth under each law; every stage with a swap; every class of
  swaps; both lifts. States are enumerated when there are at most 2^22 of them; larger stages are recorded as not run.
- *Named cases* ([named.py](named.py)): N1 the bare five-knot ring with two loose distinctions a knot, rounds 0 and 1 (the
  preserved sign's own case), with its class sign W5 beside the swap's weightings; N2 the bare rings of four and six knots
  in the same form; N3 the lone four-place knot grown to its 16-knot end; N4 the partnered start of order three
  (`WALL-READ-20261119-001`, runaway growth: rounds of 8, 10, 24 and 4,086 births) under parity, rounds 0 to 2, by exact
  quadratic sums. The record's realization of N4 has no renaming at all (its chain of connector knots breaks every
  symmetry), so N4 is built with every renaming of its points kept: one dead knot per block, each dead knot sharing its
  third distinction with the partner block's (`partnered_symmetric`); its blocks are the record's, so by Lemma R its rounds
  from 1 on are the same (checked: 8 and 10 births), and its stages have 48 renamings and 19 swaps in 5 classes. Round 3
  is cut: the engine's funding of round 4 (4,086 births) does not finish in minutes. Census parity stages with more than
  2^22 states go by the exact sums too (quadratic weightings only); not-all-equal stages with more are not run, counted.
- *P9*: every census stage of rounds 0 and 1 under parity that has a swap and two classes or more under the other
  thread's definition (its `classes2.analyse`, read as code), with each swap's action on the classes.
- *The pre-count* (structure only, run before this freeze, [counts](precount.md)): 2,164 of the 7,075 starts have a swap;
  after one round 2,442 of 5,111 stages under parity and 2,414 of 5,111 under not-all-equal, after two 2,304 of 3,398 and
  3,341 of 5,111. Most are two-sided; one-sided swaps occur in 85 to 226 stages a round under the minimal lift and 377 to
  809 under the maximal one.

**What is weighted.** Each weighting gives every allowed state a weight of +1, −1 or 0.

| Name | Weight of a state x | What is ours |
| --- | --- | --- |
| U | 1 | The control: the counting weighting (A240) |
| W1 | (−1)^(number of pairs {d, swap(d)} with both holding 1) | The cost −1 of exchanging two held distinctions (A275), on the swap's own pairs; 1 read as "holds" |
| W1c | the same with 0 read as "holds" | The other convention (a scaffold test of W1) |
| W2 | (−1)^(n₁ n₂), n_i the number of side i's distinctions holding 1 | Exchanging the two sides as blocks costs −1 when both hold an odd number; two-sided swaps only |
| W3 | +1 on kept states, −1 on flipped states, 0 elsewhere | The twist read as a sign (the literature's choice between the two characters of the double cover), and the restriction to states read with the sides not told apart; only where flipped states exist |
| W1k | W1 on kept states, 0 elsewhere | Nothing beyond the swap: on a kept state W1 is the sign of the swap as a permutation of the distinctions the state holds (the advisor) |
| W3m | +1 on kept states, −1 on states flipped on the moved distinctions, 0 elsewhere | As W3 |
| W4 | +1 when side 1 holds more 1s than side 2, −1 when fewer, 0 when equal | The one weighting the swap reverses (the advisor's candidate), two-sided swaps only; its normalizer is 0, so it is read under R2 only |
| W5 | (−1)^(old shared distinctions holding 1) | Named rings only: the other thread's class sign, for comparison |

**Readers and readings.** Reader 1 reads one of two distinctions s₁, s₂ (its setting), reader 2 one of t₁, t₂. On a
two-sided swap reader i's distinctions are those held only by side i's knots; otherwise both readers draw from the moved
distinctions. Every placement is tried in which no knot holds both a distinction of reader 1 and one of reader 2.
- **R1, the signed count.** P(a, b | s, t) is the signed sum of weights over the completions of the reading (x_s = a,
  x_t = b) divided by the signed sum over all states.
- **R2, squared sums.** P(a, b | s, t) is the square of that signed sum, divided by the sum of the four squares (A144's
  squared weights, with every unread distinction summed before squaring).

Two differences from the earlier census, recorded for every hit: readers' holders may meet here (`forbid.py` skipped a
placement when a holder of one reader shares a distinction with a holder of the other), and G3 is on single values, not
complete records. Every hit is also marked **on the reads only** when its weight is a function of the four read values on
the allowed states: then no two completions of one reading differ in sign, and the hit is the literature's signed
weighting written on the readers' own values, with the pattern supplying only which reads are tied. A hit **through the
completions** is one where two completions of one reading carry opposite signs: the case the question asks for.

**Gates**, in order, as frozen in `BEYOND-REJECTION-20261126-001`: G0 every normalizer nonzero; G1 every entry
nonnegative; G2 the four setting pairs' normalizers equal; G3 each reader's chances unchanged by the other's setting; G4
CHSH above 2. A hit passes all five. Under R1, G2 and G3 hold by construction (every table is a marginal of one signed
weighting); under R2, G1 holds by construction.

**Controls (run before the freeze, code checks only):** C1 the exact quadratic sums equal enumeration on 60 random
parity patterns; C2 a signed weighting known to give the literature's PR box passes every gate with CHSH 4; C3 the
unsigned weighting never exceeds 2 on five small stages (largest 10/27); C4 as in A5. Output: [controls.txt](controls.txt).

## Scaffolds

Each is a choice of ours, entered in the register (A292) and swapped once before any claim:

| Scaffold | Primary | Swapped for |
| --- | --- | --- |
| Which renaming is the swap | every class of swaps | (every class is read; a hit names its class) |
| The lift | minimal | maximal |
| The value read as "holds" (W1) | 1 | 0 (W1c) |
| The reading | R1 | R2 |
| The readers' distinctions | the sides (two-sided swaps) | moved distinctions (all others) |
| One read per reader per trial | a reader reads one of its two distinctions (G1 is on the four pair tables) | not swapped: by Fine every R1 hit has a negative entry in the table of all four reads, so the incompatibility of a reader's two reads is supplied |
| Rounds | 1 and 2 | 0 (the arrangement before growth), and N4's later rounds |
| The law | parity | not-all-equal |
| The weighting of patterns | the census, each arrangement once (FORBID-EDITS) | named cases and one blow-up start |

The model is not expected to replace these: R1 and R2 are readings added to the model, W1 and W2 need A275's cost, and
W3 needs the choice of the twist's nontrivial character. A hit would therefore be read as "a sign supplied on the swap's
own pairs (or sides), under a supplied reading", unless it survives every swap above.

## Predictions (frozen)

Mine, revised after the advisor's review ([question](advisor_question_1.md), [answer](advisor_answer_1.md)); the
advisor's own number in the last column. The advisor derived by hand a hit at one census start before growth: start 3097
(five knots; pairs (0, 1), (0, 4), (2, 3), (2, 4) sharing one distinction, (1, 4) and (3, 4) two; loose 1, 0, 1, 0, 0),
the swap 0↔2, 1↔3, sides of two distinctions each, tied through the sum of all five knots, where W2 is exactly control
C2's weighting. That hit is frozen here as a prediction, not checked before the freeze.

| # | Prediction | Fails when | Advisor |
| --- | --- | --- | --- |
| P1 | A1: every start with a swap at round r has one at round r + 1 where growth goes on (95%) | a start loses its swaps | 95% |
| P2 | A2: no flipped state under a swap that keeps a distinction; none under parity in a stage with a knot of odd places (proved) | any such state (a code error) | 99% |
| P3 | Rings: W5 is unchanged by every swap; on the six-ring's half-turn W3 equals W5 on kept and flipped states, on the four-ring's it does not (90%) | either fails | 90% |
| P4 | R1, parity: no hit for U (Fine); W3, W3m, W5, W1k fail G0 wherever their character is nontrivial (proved); W2 hits at start 3097, round 0, CHSH 4 (85%); some W1, W1c or W2 hit after growth, rounds 1 or 2 (50%); every parity hit has one read of each reader tied (proved by C4 and A5) | a U hit or a G0 pass for a nontrivial character (code errors); no hit at 3097 | W1/W2 hits: about 90%; after growth alone about 50% |
| P5 | R1, not-all-equal: no hit for U (proved); some hit for W1, W1c, W2 or W3 (50%), none reaching CHSH 4 (80%) | — (descriptive at 50%); a CHSH 4 hit | 50% |
| P6 | R2: the 3097 hit appears under R2 too (80%); after growth some R2 hit passes G0 to G3 (40%) | no R2 hit at 3097 | hits likely (P6 as first written: 15%) |
| P7 | Every round-0 hit is "on the reads only" (85%); a hit after growth, if any, is "through the completions" (60%); a hit survives the other lift and the other convention where those differ (60%) | a round-0 hit through the completions | P7 as first written: 30% |
| P8 | N3 and N4: no hit under any weighting and reading (70%) | a hit | 70% |
| P9 | On stages with exactly two classes every swap acts as the identity on the classes (proved); on some stage with four or more some swap does not (60%) | a two-class stage where a swap moves a class (a code error) | — |

**What a result will mean (frozen).** A hit on the reads only says that the pattern supplies the sides and a tie between
the readers' reads, and that the sign written on those reads is ours (the block or pair cost, A275's kind). A hit through
the completions with W1 or W2 is the supplied cost on the swap's own pairs or sides, under a supplied reading: it would
narrow the reordering line's obstruction (the schedule no longer supplied; the cost and the reading still are). Only a
hit with W1k, W3, W3m or W4, whose signs come from the swap alone, would be a sign the model makes once the swap is given;
under parity A5 already excludes W1k, W3, W3m under R1. No hit anywhere, with the arguments, closes the line: every label
a swap gives is trivial (kept and flipped are classes of one permutation and carry no relative sign under the counting
weighting) or supplied (the costs and readings).

## Prior work in the program

Searched before the freeze, `--until 2026-11-26 --exclude SIDE-SIGN-20261126-001`:

`python3 -B scripts/track.py objects "swap of two sides of a meeting pattern" --until 2026-11-26 --exclude SIDE-SIGN-20261126-001`
`python3 -B scripts/track.py objects "graph automorphism involution signed weighting Bell" --until 2026-11-26 --exclude SIDE-SIGN-20261126-001`
`python3 -B scripts/track.py objects "census starts grown by ordinary growth" --until 2026-11-26 --exclude SIDE-SIGN-20261126-001`

- `MEET-GROW-20261118-001` — unrelated (laws of co-knotted pairs on line presentations).
- `NAE-SURFACE-20261111-001` — unrelated: its swaps are rewirings of knots, not renamings.
- `OVERLAP-READ-20261111-001` — unrelated: swap-made overlapping bases (rewirings).
- `TWO-KNOTS-ONE-DECISION-20261121-001` — a relative: it reproduces a quantum table with supplied keepers and signs; this
  study supplies no keeper and asks whether a swap supplies the sign.
- `ENTANGLEMENT-READ-20261120-001` — a relative: with one common nonnegative weighting every CHSH bound holds for separated
  readings (proved); control U here is that case, and this study adds signed weightings made from a swap.
- `SPLIT-KNOT-METER-AND-CLOSING-TRIPLE-20261121-001` — unrelated (a coherent pair cost at one parity closure).
- `LOOK-ALIKE-20261126-001`, `LATE-VIEWS-20261126-001` — same population (census starts under ordinary growth), different
  object (what a local reader sees).
- Also read: `THREEFOLD-SPIN-20261030-001` and `THREEFOLD-SPINSUM-20261030-001` (the knot's own signs on drawn
  three-regular contradictions are Kasteleyn and induce even spin structures; counts are Arf-signed sums of spin sectors):
  the nearest record of a sign from a twist, on supplied drawings, read as counts, not as readers' tables.
  `REORDER-SIGN-20261126-001` (the exchange cost on a supplied schedule carries the three-reader contradiction):
  W1 is that cost on the swap's own pairs instead of a schedule's. `FOLD-SIGN-20261126-001` (no sum over orders).
  `READS-HOLDERS-SOURCES-20261120-001` and `TWO-CLASS-SIGN-20261126-001` (the preserved class sign, not redone here).
- Entering the program: `PROVE-B-20261119-001`, `CENSUS-READ-20261118-001` and `THREE-RIGID-20261119-001` counted
  symmetries of stages for other questions (readings of tables).

## Prior work outside the program

The sign of a permutation; the double cover of a free involution and the literature's one-sided band (Möbius); Johnson
(1980), spin structures as quadratic refinements of an intersection form, whose Arf invariant labels them; quantization
of a space read up to exchange, where the weight of a loop is a character of the exchange group and both characters are
consistent (Laidlaw and DeWitt 1971; Leinaas and Myrheim 1977); signed weightings of joint assignments give every
no-signalling table, the PR box included (Abramsky and Brandenburger 2011); Fine (1982), one nonnegative weighting gives
CHSH at most 2; the marginals of quadratic-phase functions over GF(2) are of the same kind (the stabilizer formalism).

## Not shown (stated before the run)

Signs of degree three or more; reads of functions of several distinctions (the two-distinction read x_d + x_swap(d)
that would read the twist); mixed lifts (some kept pairs exchanged and others not), which are in general neither lift;
the detection loophole of R2's postselection (equal normalizers do not close it); readers whose setting is an edit of the
pattern rather than a choice of what to read; not-all-equal stages with more than 2^22 states; renamings of order more
than two (the five-knot ring's turn) as signs; the classes of the other thread's sign beyond the named rings.
