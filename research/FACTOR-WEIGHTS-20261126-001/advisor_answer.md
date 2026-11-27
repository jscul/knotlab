**Advisor answer, `FACTOR-WEIGHTS-20261126-001`.** Nothing was run; everything below is by hand from the files read and is `unverified` unless a line is cited. No counterexample to (a) or (b) as you mean them, but both need a narrower statement, check 1 cannot fail as designed, and (b) misses the treatment where the count does change.

## (a) The two countings

**Holds, with one exact hypothesis.** For one history, counting from the start is a constant times one factor per knot when the knots of each stage have disjoint private fresh sets (`TWO-COUNTINGS` definitions 1.5). The lines:

- **Canonical engine:** `freelib.py` 165–169 gives each fresh distinction one holder.
- **Arms:** `rival_growth.py` 63–64, 74, 81, 86–87: inputs are old names, and every loose distinction is consumed once.
- **Waiting engine:** `eng.py` 533–535, 560, 602–608: a waiting member keeps what it holds, and inputs are loose distinctions plus takes, all held when the round starts.
- **Every stage extends there:** `eng.py` 596 with 86–115 and `rations.py` 26–28: no fresh distinction only at an implied birth.

Not read: `ring_line.py`'s REC-ONE-FEWER body, whose docstring (lines 8–9) says "none at least where three places are given".

**Cut arms.** A cut birth's factor is its law on its inputs, so the product form survives. Three things change:
- Counting from the start is undefined as worded (definitions 3.2); you need the renormalised one (3.4).
- "The start's uniform weighting times one factor per birth" is no longer true of the start's marginal.
- The factor is no longer a division.

Under parity the code's start weighting is the uniform one times a constant (`counts.py` 46–49).

**Where the product fails.**
- **Example E4 of the definitions (8.2):** two setting knots share their fresh z. At z = 1 the weights on (x, y) each in {00, unequal} are 1, 1, 1, 1/2, and 1 · 1/2 ≠ 1 · 1.
- **The whole growth as one stage:** "each start word's weight divided equally among all its finished completions", which your wording allows. Under not-all-equal at two rounds, take b1 = nae(x_u, x_v, g), b2 = nae(x′_u, x_w, h) and their round-2 join nae(g, h, z). The completion count is 6, 3, 3, then 1 or 2. With all else fixed, the weights on (x_v, x_w) are 1, 1/3, 1/3, 1/6. No knot holds both.
- **Supplied weightings:** `sides.py` 215–232: W1, W2 and W4 are not products over knots. W3, W3m and W1k live on the states the swap keeps, so joint parities are fixed with no value fixed.

**The 20/9 sentence.** Counting from the finish also factors (law indicators), so factoring does not part the two countings. `SETTING-AS-REREAD` decision 74–75 says the finish gives 20/9 and the start at most 2. So the 20/9 is an excess under a factoring weighting. It is possible because the four setting pairs are four structures, and the setting knots' factors are not divisions (1 or 2 completions). Part A covers one state only. The property that gives "at most 2" is division at each birth, not factoring.

## (b) Restricting to a fact's value

**Shorter proof.** Restricting to f = v adds one knot, whose places may be any representative of f modulo the laws. Each of R, S, T, P, Q has a representative on one ring, so some representative misses one reader and part A applies unchanged.

One correction: changes on ring 0's distinctions alone can flip P and Q together; only R, S, T are flipped by none.

**Your criterion is exact for one treatment only.** For readers no knot joins, the change in e is:

| Middle | Change in e |
| --- | --- |
| values read | +1 exactly when every representative meets A and every one meets B (your criterion) |
| unread | the same, and some representative lies on A + B |
| read for changes | [a representative on A + B] − [one on A] − [one on B] |

**Predictions on the referee's three rings** (carriers read at `ring_overlap.py` 99, attachments at `growth.py` 249–260):
- Unread and values: 0 for every ring pair and every sum of the five facts. This is entailed by where the carriers are, so it is not a test.
- Changes, T fixed: rings 0 and 1 go from 1 to 2, with the square. T is, modulo laws, the four attachment distinctions of ring-0 and ring-1 knots 1 and 3.
- Changes, one connecting knot's attachment parity fixed: that pair goes from 1 to 0.

**Restrictions to a fact's value already in the record.**
- A cut birth with no fresh distinction (`rival_growth.py` 25–32). `BUILT-BINDING` referee fix 4 (report line 40) records seven constraints on start values, where "only deleting the middle law frees the triple".
- `sides.py` W3, W3m, W1k.
- Example E5 of the definitions.
- Any table sorted on a combined read.

Ordinary growth has none: a birth with no fresh distinction is implied (`freelib.py` 163–164).

## The checks

1. **Check 1 is an identity.** `counts.py` 28–33 and 51–55 already compute the start weighting as that product. Replace it with the test part A uses: for readers no knot joins, with all else fixed, W(a,b)·W(a′,b′) = W(a,b′)·W(a′,b). Add the two failing controls above (E4, whole-growth division).
2. **Check 2:** run all three treatments by appending the fact's carrier as one more knot to `css.ebits`. Only the changes column can move.
3. **Check 3** gives 1 under all three treatments, so it tests the code, not the criterion. Add two controls:
   - f = a + b + m, with m a loose distinction of a third piece: values 1, unread 0, changes 0.
   - Readers holding only {a} and {b}: changes 1, values 0.
4. **Check 4:** report four counts: pairs, separated pairs, those with e ≥ 1, those with e ≥ 2. Start knots with a common neighbour are never separated. I expect the same counts at rounds 0, 1 and 2 under the ordinary count, so run the cut arms beside it.

## Is "every recorded weighting factors over knots" provable?

Not as worded: the supplied weightings and the stage choice above are exceptions. The provable form is: for one history, with stages no larger than a round, the finish, start (renormalised) and from-stage-s countings are products of one factor per knot. A referee would check the lines cited under (a) and `counts.py` 28–33, 51–55.

A referee would press first: that check 1 is an identity, the stage choice, and the changes treatment.

The hivemind has one consultation entry and one standing fact added; nothing else was touched.
