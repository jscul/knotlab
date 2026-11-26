# The advisor's answer (26 November 2026, extra-high effort, read-only in the repository)

# Advisor's answer: what the model is missing for the quantum part

**Proposal B is not new.** The record ran it on 20–23 November, more fully than the test in item 5, and no decision or README of 26 November cites those studies (searched by name, no matches). They already show that part counts overshoot the quantum set. What they leave open is my answer to (A): the program assumes every two distinctions have a joint value even when no knot holds both.

Status marks: *read* = I opened the file at that line; *by hand* = argument or trace, no run; *not found* = a search, not a proof.

## B.1 What the record already has (all *read*)

- **`FOUR-READINGS-20261120-001A/results.md`** is the nine-distinction square with one odd sign.
  - Lines 21–31 count all 64 parts: 512, 256, 128, 64, 32, 16, 0 states.
  - Lines 33–42: two readers win 9/9 against a classical 8/9, with complete local records unchanged by the far setting.
  - Lines 46–58: the operator test on 173 closed patterns; 115 admit a signed reading.
  - Lines 68–83: ordinary growth closes 121 of these types, and 79 admit after one sign is reversed. The smallest reached is five knots on ten distinctions. The square itself is not reached (its five-knot part stalls; my trace of `freelib.groups_among` agrees).
- **`ERASURE-AND-CLOSING-SIGNS-20261121-001B/closing_law.md`**, lines 9–25: growth forces the closing sign even. Reversed, no word is left and "a post-step read probability on that set is undefined".
- **`REVIEW-LEADS-20261123-001A/result.md`**, lines 45–46: 91 closed parity parts met in growth; one admits (8 knots, 14 distinctions).
- **`proofs/ENTANGLEMENT-READ-20261120-001A/.../check.py`**, lines 103–138 and 330–337: both contradictions with local tables, overlap agreement asserted, zero common assignments, 8 and 16 after any omission.

The referees of the first three are pending as written there.

## (A) The missing ingredient

**Values that need not commute where no knot holds both distinctions.**

- **Where it sits.** The implied test sums knot rows over GF(2) (`startlib.py` line 48; `closing_law.md` lines 9–11). That inference is valid only if all values commute.
- **What the record shows without it.** The stored witnesses satisfy every older knot while the closing knot's product is −I (`FOUR-READINGS-…A/results.md` line 58). So the even closing rule is not entailed at operator-positive closures (79 of the 121 reached types), and is entailed at the rest.
- **What it is in the program's words** (*by hand*). The closing sign is the cost of reordering the closing sum: each distinction occurs twice, and bringing the two together costs −1 per pair that does not commute.
- **Counting survives** (*by hand* from `closing_law.md` line 37). The two-reader table is tr(P·P)/D, which for commuting values is the plain count of allowed words. Of the supplied list (odd sign, operators, preparation, weights), only the non-commuting values are irreducible.
- **Not A126.** Under even parity the all-zero word is allowed under every law, including the forbidding rivals (`FORBIDDING-JOIN-20261120-001/decision.md` line 17; `freelib.py` line 3 stores knots as supports only). The whole word exists because of the even sign and commuting values.
- **Register.** I found no entry for "values commute" (searched `commut`, `joint value`, `definite value`; two long lines, 4030 and 5733, not read).

**Cheapest test (no new machinery).** From `census.json` and `arbitrary_operator_refutations.json` of `FOUR-READINGS-…A`:
1. At the five-knot closure, confirm the four older knots multiply to +I, the closing knot's places commute, and its product is −I.
2. At the four-knot and eight-knot closures, confirm the sign is forced.
3. Confirm the growth engines use only GF(2) rows (`freelib.py` lines 44–61, *read*: they do).

This shows the entailment depends on commuting. It does not show that any law chooses the odd branch.

## B.2 Growth

- An odd sign survives only in a closed component; a loose distinction absorbs it (`results.md` line 19; `closing_law.md` line 15).
- A closed component has no births and no loose distinction, and `startlib.py` lines 21–22 refuse a third holder. So no later-born knot can read it. The record's readers there are outside keepers (`closing_law.md` line 41).
- **One candidate, *by hand*:** where the even rule is not entailed, the closing birth is not implied, so `floored` would give it one fresh distinction, which carries the sign. In the commuting reading that distinction is forced (`forced_bits`, `freelib.py` line 192), so the candidate is unlawful by the present test and lawful only with non-commuting values.

## B.3 Weighting

- **Parity.** Counts within the two read knots give 1/8 on the eight compatible pairs, with no signalling (`results.md` line 33). Another weighting on the same support signals, with total variation 1/6 (line 42).
- **The part matters.** With five of six rules kept, the omitted triple has the opposite parity (line 31). So "counts within the part" needs the rule "the part contains the knot that holds what is read".
- **Not-all-equal.** Not automatic:
  - Counts changed the old marks in 221 of 233 placements (`ENTANGLEMENT-READ-20261120-001/decision.md` line 53).
  - *By hand:* one knot gives a shared pair 1:2:2:1; two knots sharing that pair give 1:4:4:1.
  - With at most two holders a whole state always exists, so B has no counterpart there. The Fano pattern, 0 of 128 states, needs three holders (`results.md` line 62).

## B.4 Overshoot

- **Nothing in the reading stops it.** The same part-count table on the eight-knot closure is non-signalling and "no quantum state produces" it (`results.md` lines 90–94).
- **Smallest illustration, *by hand*:** four two-place parities around a ring of four, one odd, scores 4.
- **What separates the cases** is whether the whole has a state with non-commuting values, which is the record's operator test.
- **The roles of the readers decide** (`results.md` line 96).
- **CHSH is the wrong target.** With reads and changes, two-reader correlators are 0 or ±1, so CHSH stays at 2 (`SIDE-SIGN-20261126-001/decision.md` lines 59–61). Use the agreement game and the three-reader game.

## B.5 What to freeze instead

The proposed test would repeat `six_parts.json` and `check_contexts`. One new small case, *by hand*:

- **The fixture.** The ring of three with one loose distinction each closes in round 1 on an implied birth (traced through `freelib.py` lines 67–176). Check: `startlib.grow([[0,1,2],[1,3,4],[3,0,5]], F.fewest, 3)` should return `closed`, with the last knot `[2,4,5]` and no fresh distinction.
- **The identity.** The result is four mutually meeting knots on six distinctions, the holder pattern of `ghz` in `check.py` line 330.
- **The readers.** The six distinctions fall uniquely into three pairs that no knot holds together. Give each pair to one reader.
- **Prediction.** With the closing sign odd, and the rule "a knot's law where one knot holds the read triple, free otherwise", all 64 probabilities of `FOUR-SETTINGS-PARITY-20261125-001` are reproduced.
- **Control.** Reading a scored triple from the three knots that do not hold it gives the opposite parity.
- **Would show:** the record's smallest reached closure carries the three-reader contradiction, below the five-knot minimum, although the census marks it operator-negative (`results.md` line 52). I found no mention of three readers in either study's folder.
- **Would not show:** a native odd sign, native roles, or any two-reader excess.

## What a referee would press first

1. The uncited prior work.
2. Which of the sign, the roles and the part rule is supplied.
3. The 79 of 121 as a count of types, not a weighting.

**Hivemind:** one standing fact (the prior work, with lines) and one consultation entry added, both `unverified` except the lines read. Nothing here touches the publication hold.
