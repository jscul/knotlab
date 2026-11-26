# Independent referee report on signed counts
**Refuted. Block on the claim that only squared readings use cancellation. The count-weighting result is confirmed.**

## What holds

**Rebuilt.** Each knot binds two consecutive shared distinctions and one loose distinction by the not-all-equal rule. Bob adds one fresh loose distinction used only by his knot. Alice reads +1 when her two shared distinctions agree and −1 when they differ. Each table entry gives the counts **(agree, differ)** under the stated weighting. Deletion keeps Bob's original loose distinction free.

| Start | Original | Bob's knot deleted | Edited | Total, original → edited | Alice's mean, original → edited |
| --- | ---: | ---: | ---: | ---: | ---: |
| Three knots | (10, 16) | (12, 24) | (22, 40) | 26 → 62 | −3/13 → −9/31 |
| Four knots | (26, 56) | (36, 72) | (62, 128) | 82 → 190 | −15/41 → −33/95 |
| Five knots, one size beyond the study | (82, 160) | (108, 216) | (190, 376) | 242 → 566 | −39/121 → −93/283 |

For each old word satisfying the other knots, the fresh distinction has two completions if Bob's old values differ somewhere and one if they are all equal. A word failing another knot contributes zero throughout. Thus **edited = original + deleted** for each old word and for every event made from those words. The code verified all 64, 256 and 1,024 old words respectively. For four knots the edited distribution mixes the original and deleted distributions in proportions 82/190 and 108/190. The signed count on three knots changes from 27 − 1 to 63 − 1. On four knots it changes from 81 + 1 to 189 + 1. The expansion preserves the whole table. [Independent rebuild](rebuild.py)

## Fixes

**1. Block · Squaring is not required.** The handoff says, “A signed sum that is not a count exists only in supplied readings that square it (SIDE-SIGN's R2; the four-settings calculations).” The decision uses that assertion to exclude all other readings that cancel. Three archived prescriptions contradict it. Each supplies its reading. None derives a signed weighting from ordinary growth. [Handoff](../referee_handoff.md#L8) · [Decision](../decision.md#L13)

- **Direct normalization, rebuilt.** In the side-swap study, the reading called R1 divides the signed sum for an outcome by the signed total. On its eight-word control, setting 00 gives ordinary counts (2, 2, 2, 2) and signed sums (2, 0, 0, 2). Across the four settings the signed correlations are (1, 1, −1, 1), giving a CHSH score of 4. Unit weighting on the same words gives 1. All reported probabilities are nonnegative and each single reading is balanced. Calling R1 a “signed count” describes subtraction of completions with opposite signs. It changes observable probabilities while the ordinary counts stay fixed. The separately supplied squared reading R2 also gives 4 here. [Reading definitions](../../SIDE-SIGN-20261126-001/README.md#L144) · [Control](../../SIDE-SIGN-20261126-001/controls.py#L37)
- **Absolute weighting, rebuilt.** The three-reader calculation sums signed contributions before applying one of three weightings. For the signed preparation all 64 entries agree under uniform weighting on nonzero sums, absolute weighting and squared weighting. The unequal-magnitude control separates them. At setting 011 the sums in word order are (3, 1, 1, 3, 2, 0, 0, −2). Outcome 001 has probability **1/6, 1/12 or 1/28**, respectively. Absolute weighting genuinely differs from squaring. [Recorded prescriptions](../../WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001/verify_laws.py#L60) · [Magnitude control](../../WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001/results.md#L56)
- **Nonzero signed support, read and rebuilt.** An adopted reading allows a visible word when its signed witness sum is nonzero. In the recorded three-copy not-all-equal example, words 000 and 111 each have four ordinary completions and signed sum zero. Word 110 has three ordinary completions and signed sum −3. The other five words each give +3. This reading decides which words are allowed, without assigning probabilities. [Adoption](../../INTERFERENCE-20261029-001/canonical_correction_request.md#L18) · [Three-copy example](../../../proofs/INTERFERENCE-20261029-001B/INTERFERENCE-20261029-001B-P001_signed_laws_survive_native_coarse_graining/proof.md#L145) · [Independent checks of all three prescriptions](readings.py)

**2. Narrowing · Which edit is far.** The handoff says, “Under a count weighting the signed form of a count is only a rewriting: on the ring of four and the ring of three (`signed.py`, `signed_out.jsonl`), a far edit moves the near reader's statistic, and the edited count is the unedited count plus the count with the far knot deleted (its own distinctions free).” The original four-knot example has disjoint reader knots. In the three-knot example Bob's knot contains one of the two distinctions Alice reads. Both means change. Of the two published examples, only the four-knot one demonstrates the effect for disjoint reader knots. [Handoff](../referee_handoff.md#L5) · [Recorded starts](../signed.py#L66)

**3. Narrowing · Events on the old distinctions.** The note says, “An edited not-all-equal knot has 2 − [its other places all equal] = (not-all-equal) + 1 completions, so for every event the edited count is the unedited count plus the count with Bob's knot deleted (its own distinctions left free): checked exactly on both starts (190 = 82 + 2 × 54; the same for Alice's sum).” Specify events on the old distinctions after summing out the fresh one. The event “the fresh distinction is 1” has no original count. The completion argument above proves the identity on that domain for any one such edit. [Study note](../README.md#L24)

**4. Not a block · Relative contribution.** The note says, “The far setting does move the near reader's statistic under this weighting (the edit changes how many states each old state counts for), and in the signed form it shows as the loop terms through Bob's knot contributing less (on the ring of three, a positive term cancelling a third, then a seventh, of the direct term).” In Alice's unnormalized sum the term through Bob stays **+3** on three knots and **−3** on four. The direct term changes from −9 to −21 and from −27 to −63, respectively. The term through Bob falls relative to the direct term and after normalization. [Study note](../README.md#L21)

**5. Narrowing · Event probabilities and signed means.** The note says, “Every reader statistic under a count weighting is a ratio of nonnegative counts; any signed expansion sums to the same numbers; a far dependence it shows is the counts' own, visible to the reader only as a change of its own statistic, which is signalling when the far setting is free, never a correlation the counts do not give.” The ratio applies to event probabilities. Alice's original four-knot mean is (26 − 56)/82. Her negative mean is determined by those two nonnegative counts. [Study note](../README.md#L28)

**6. Not a block · Parity convention in the code description.** The opening description says, “Parity's indicator is (1 + s1 s2 s3)/2 on three places, so its expansion has no negative coefficient, and a character sum over its allowed space is 0 or the size.” Label this **even parity**. On odd parity the product of the three signs is −1 on all four words, so its sum is −4. The study note already gives the correct general statement for a character on a nonempty parity system. [Code description](../signed.py#L5) · [Study note](../README.md#L32)

## How it was checked

The state count tests the two fresh values directly. A separate calculation sums the loose distinctions first, expands the resulting constants and shared-pair products, and sums each product over all shared distinctions. Its totals and Alice numerators match enumeration. The record search followed **after** this rebuild. The two-reader control, the three-reader prescriptions and the signed-support example were already present at the study's closing commit `741bd25a81`. In the threefold counting proof, Lemma 2 puts the signed correction into a two-way counting identity. The proof specifies no reader for that correction. This last finding was read, not rerun. [Counting proof](../../../proofs/THREEFOLD-AMPLITUDE-20261030-001C/THREEFOLD-AMPLITUDE-20261030-001C-P001_one_amplitude_for_every_non_colourable_cubic_system/proof.md#L47)

From the repository root, run each linked script with `.venv/bin/python -B`, first with `--pilot` and then without it, under `ulimit -v 262144`. Each run used one process with a 256 MiB address-space cap. Timing the first eighth of each count and the first setting or visible word of each reading at that configuration projected under 0.01 seconds of computation in total. The completed checks also used under 0.01 seconds in their timed sections. They enumerate the stated cases exactly, without sampling.

**Not run:** the original programs, a growth or sign census, the full threefold proof checks, or an exhaustive archive search. The targeted search establishes the counterexamples above and leaves open which further readings the archive contains.

| Scope | Verdict | Why |
| --- | --- | --- |
| Count weighting | Confirmed | Exact word-by-word identity |
| Square-only conclusion | Refuted | Archived unsquared readings |
| Supplied signed readings | Rebuilt | Direct, absolute and support readings |
| G18 Comparing growth laws | Unresolved | These examples supply their weighting |

**Next step:** Research directions. Stop this referee pass at the counterexamples.

| Direction | Payoff | Concreteness | First step and stop | Status |
| --- | --- | --- | --- | --- |
| Correct the square-only conclusion in the study record | 3/3 | 3/3 | Retain the count identity and name the unsquared readings | For the study owner |

**Corrections:** one Block, three Narrowings, two wording fixes classified Not a block.  
**Goals:** no change.  
**Assumptions:** no change.  
**Scaffolds:** the count weighting, the chosen starts and single fresh distinction, and the supplied signed readings.
