# Independent referee report on signed parity rules
**Confirmed with fixes. No Block.**

The three claims used by the new epic on readings without a whole state (`NO-WHOLE-STATE-20261126-001`) hold. All **115 operator certificates and 58 unrestricted refutations** replayed. On six knots and nine distinctions, the supplied operator reading wins **9/9**, the best classical local responses win **8/9**, and each reader’s complete record has the same distribution for every distant setting. Ordinary parity growth can close **121 of 173** sharing patterns from some connected lawful open start. **79 of those 121** admit operators after one sign is supplied. The smallest has five knots and ten distinctions. One secondary growth count needs a shorter observation limit, and two passages need more precise probability language. [Decision](../../FOUR-READINGS-20261120-001/decision.md) · [Study results](../results.md) · [Hand-off](../referee_handoff.md) · [Assumption A140 on the supplied reading](../../../docs/ASSUMPTIONS.md#a140--a-shared-distinction-can-be-given-one-operator-in-each-rule-that-holds-it)

## What was rebuilt

| Knots | Sharing patterns | Admit operators | Reached by growth | Reached and admit operators after re-signing |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 1 | 0 | 1 | 0 |
| 5 | 3 | 1 | 2 | 1 |
| 6 | 19 | 10 | 10 | 6 |
| 7 | 150 | 104 | 108 | 72 |
| **Total** | **173** | **115** | **121** | **79** |

**Certificates and weighting.** Seed 20261126 gave one uniformly sampled type in each nonempty group defined by knot count and operator verdict. All seven sampled types passed before the full replay. The positive check multiplied signed Pauli factors, tested every local commutator and verified both eigenvalues for each distinction. The negative check started with the actual local equations, rotated only words equal to scalars, multiplied equations, and cancelled adjacent identical involutions. Each of the 58 reductions ended at **I = −I** and hence excludes operators in every dimension. Moving the odd sign to every possible knot gave 1,183 checks. A deliberately corrupted certificate failed on each of the 173 types. [Seeded sample](certificate_sample.json) · [Complete replay](certificate_full.json)

Each type in the table has one vote. A separate enumeration of all labelled subsets of meetings agreed by size with disjoint sets of relabellings of the stored types. Under that weighting, **141,386 of 238,811** admit operators. An independent search for the required connected groups matched every operator verdict. Both marker collisions reproduced. Six three-place knots with nine distinctions can match on arities, charge and loop count yet have opposite verdicts. With ten distinctions the mismatch survives matching on the presence of an odd-length loop. The literal Fano pieces require a third holding. Under not-all-equal the intact Fano rules admit 0/128 assignments and the six-knot comparison admits 102/512. The classification for arbitrary size comes from the cited theorem. [Census and marker replay](census_parts.json) · [Arkhipov, Theorem 21](https://arxiv.org/pdf/1209.3819#page=14)

**Complete records.** Applying the local measurements directly to the supplied preparation gave 72 probabilities of 1/8 and 504 zeros across the nine settings. All 18 complete marginal distributions gave 1/4 to each legal triple. Reweighting compatible answers by doubling the weight on shared bit 1 changed the maximum total variation to 1/6 in both directions. Enumerating 512 assignments gave **5/6** rules satisfied or **6/9** wins when both readers must use the same assignment. Of 4,096 legal setting-dependent classical response lists, 144 attained **8/9**. A perfect classical list would assign consistent values to all nine distinctions, contradicting the odd total sign. [Game replay](games.json)

All 64 subsets of the six rules were rebuilt. Retaining zero through six rules gave respectively 512, 256, 128, 64, 32, 16 and 0 scalar assignments per subset. The canonical forgetting check agreed on every nonempty subset. The six one-rule subsets were exactly those that passed all three knot gates. With five retained rules the omitted triple took all four words of the opposite parity. Across the larger census, each single-rule deletion had a scalar witness. Full opposite parity at the omitted knot is a stronger conclusion. When two four-knot all-pairs patterns share one knot, omitting that common rule permits only 16 of the 32 opposite-parity words there, as the archive records. [Projection and deletion checks](census_parts.json)

For the eight-knot comparison, each of the twelve meeting settings had eight legal, agreeing pairs of answers at 1/8. Each of the four disjoint settings had sixteen pairs at 1/16. Every complete marginal again gave 1/4 to each legal word. I also checked the exclusion argument for general local measurements. Perfect agreement transfers each bit operator between readers on the preparation. Reversing words gives a common closed span on which the bit operators are involutions. The compressed joint measurements have projection marginals, so each knot's operators commute and have its prescribed product. In each of the two four-knot groups, multiplying the same four matched operators in the same order cancels the internal factors in adjacent pairs. One group forces +I and the other forces −I. The twelve meeting inputs already give the contradiction. For four knots given to either reader, 32 equally weighted instruction lists reproduced the twelve distinct-input tables exactly. Adding full-word agreement on equal inputs identifies the two copies of each distinction and forces the separate signed contradiction. [Rebuilt tables](games.json) · [Transfer argument reviewed](../derivations.md#why-the-eight-knot-table-has-no-quantum-realization)

**Ordinary growth.** I counted each candidate last knot once in each stored representative. Removing it leaves its distinctions loose at their old knots. Testing the old local relations and running the forward grouping, payment and fresh-distinction rules gave **397 exact restorations, 42 growing steps, 737 stalls and 7 inadmissible starts** out of 1,183. The 397 restorations preserved the actual paid distinctions and the number of scalar states. Counting symmetry-equivalent marks only once gives 202 restorations out of 685 marked types. Neither weighting samples the frequency of closure from random starts. [Marked choices and ordinary steps](growth.json)

Four mutually meeting knots, each with one loose distinction, fund one four-place birth with no fresh distinction. Summing the old equations forces the newborn's sign to be even, preserving all **64** scalar states. Supplying an odd sign afterwards leaves **zero** scalar states and admits the verified operator reading. The only possible nine-distinction positive pattern has two sets of three knots with every cross-meeting. At any puncture its parents each owe two payments and hold only one loose distinction. Five mutually meeting groups require at least ten shared distinctions, and two threes with all cross-meetings require at least nine. The failed nine-distinction case therefore proves the ten-distinction minimum. The twelve-knot, eighteen-distinction all-three-place witness also regrew. Its even and re-signed counts were **128** and **0**. The lower-bound check included the four-knot exception and all 37 completions of the forced seven-knot part at sizes eight and ten, including repeated old meetings. Suppressing a final two-place tie preserves the operator verdict. In the forward check, none of the nine subdivisions of the six-knot example regrew the tie, and all ten subdivisions of the five-knot example did. The resulting minimum is six holders and eleven distinctions. One initial knot with four distinctions also suffices, reaching a sixteen-knot closure before re-signing. [Growth and size controls](growth.json) · [Size arguments reviewed](../derivations.md#reaching-a-closed-holding-pattern)

**Source samples.** The twelve tree starts (seed 202611200131) gave seven stalls and five funded starts under each law. Through three steps two closed under parity and zero under not-all-equal. The three archive starts, each with weighting 1/3 in a separate sample, gave birth counts of (8,12,15), (10,16,26) and (15,27,56) under each law. The six-knot singleton chosen for its recorded later increase gave **10, 16, 27** under each law and ended with 59 knots and 227 distinctions, 107 loose. Each initial knot projected to its full local rule. The constructed controls have their own observation limits, corrected below. [Source replay](stress.json)

## Fixes to the record

1. **Narrowing — observation limit for the twelve constructed controls.** The results say “Nine closed under parity and none under not-all-equal.” The experiment summary says “The physical census and every numerical comparator reached their frozen stop.” The design calls for three ordinary steps, or an earlier stall, closure or cap. The constructed controls instead used limits of two through six steps. The nine observed parity closures occurred at steps 2, 3, 3, 4, 4, 4, 5, 5 and 6. Report **3/12** at the common three-step limit and **9/12** over the recorded limits. Fourteen of the 24 law-specific histories exceeded three steps. Three others ended open after step two. I advanced those three to step three and all remained open. The not-all-equal count is **0/12** in each comparison. The experiment summary should give the constructed controls their actual limits. The census, punctures and seeded tree sample keep their reported counts. [Exact results sentence](../results.md#which-closed-structures-does-ordinary-growth-produce) · [Experiment summary](../../../experiments/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/result.md) · [Frozen design, item 5](../preregistration.md#frozen-objects-and-questions) · [Replay](stress.json)

2. **Not a block — which projector trace is an integer.** The results say “The integer trace of the two joint outcome projectors verifies every entry, including zeros.” The derivation says “The trace is zero on disagreement and 1/2 on agreement.” For the actual projectors, `Tr(PQ) = 1/2` precisely when **both triples are legal and agree**. It is zero otherwise. For example, on settings (0,3) the answers (000,001) agree on their shared bit, but the second word violates its local even rule. The integer in the archive is `Tr((8P)(8Q))`, either 32 or 0. Dividing by 256 gives the reported probability. [Results sentence](../results.md#six-knots-nine-distinctions-two-complete-records) · [Derivation sentence](../derivations.md#the-six-holders-under-free-settings) · [576 rebuilt weights](games.json)

3. **Not a block — what receives equal weight in the eight-knot game.** The results say “For each meeting, assign 1/8 to each of the eight compatible ordered triples and zero to the other 56.” The derivation says “For uniform local supports in the eight-holder comparison, the same counts give 1/8 on meeting pairs.” The eight events are **ordered pairs of complete answer triples**, and their equal weighting is supplied. Uniform local marginals alone leave the joint weights undetermined. Within each shared-bit value, assign the four compatible pairs weights (3, 1, 1, 3)/16 in the two-by-two answer table. This gives every legal local triple probability 1/4 and preserves all eight compatible pairs. [Results sentence](../results.md#a-non-signalling-table-that-no-quantum-state-produces) · [Derivation sentence](../derivations.md#the-six-holders-under-free-settings) · [Weighting control](census_parts.json)

## Replay and limits

The checkers were written for this review. The twelve main output hashes, the contract and both design hashes matched. Use the commands below from the repository root. Each pilot uses the same program, interpreter and limits as its full run. Each full check took under two seconds and used less than 50 MiB of resident memory in this review.

```bash
ulimit -v 2097152
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
review=research/FOUR-READINGS-20261120-001A/referee-R1
.venv/bin/python -B "$review/certificates.py" smoke
.venv/bin/python -B "$review/certificates.py" sample
.venv/bin/python -B "$review/certificates.py" full
.venv/bin/python -B "$review/games.py" --sample
.venv/bin/python -B "$review/games.py"
.venv/bin/python -B "$review/growth.py" --pilot
.venv/bin/python -B "$review/growth.py"
.venv/bin/python -B "$review/census_parts.py" --pilot
.venv/bin/python -B "$review/census_parts.py"
.venv/bin/python -B "$review/stress.py" --pilot
.venv/bin/python -B "$review/stress.py"
```

**Read only / not run.** The all-size classification was read in its source. The original certificate generators were not rerun. The singleton's 386 and 28,065 births at steps seven and eight were read from its archive. Those steps, the separate unbounded-growth proofs for other sources, a census beyond seven knots, and optimization of the imperfect eight-knot quantum score were not run. The tested twelve-knot witness is a specific construction beyond the census.

| Scope | Verdict | Why |
| --- | --- | --- |
| Signed parity referee check | Successful with fixes | All three principal claims reproduced |
| Local direction, ordinary closure | Confirmed | Actual forward steps and signed controls agree |
| Broader work on readings without a whole state | Finite evidence available | Uniform complete marginals occur with opposite operator verdicts |
| G18, comparing growth laws | Capability checked | Growth supplies an even closure |

**Next step:** Continue — No next action selected. STOP at the requested referee hand-off.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Obtain the odd sign from growth | 3/3 | 1/3 | Specify an ordinary operation → test its sign on the five-knot closure | Alternative · deferred |

**Corrections:** One narrowing of the observation limit and two probability-wording fixes. No Block.

**Goals:** The census and reached example support the finite premise used by the study of readings without a whole state.

**Assumptions:** A140 specifies the supplied operator reading, independent settings and answer weighting.

**Scaffolds:** The choice of an open start, subsequent odd sign, operators, preparation, reader roles and weighting enter separately.
