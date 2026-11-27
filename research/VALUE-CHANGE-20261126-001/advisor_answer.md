The hivemind has one consultation entry and one standing fact from this call; nothing else was touched. Everything below is by hand with no run, so it is `unverified` unless marked "read".

## What I read

- `css.py` and `rings.py` in full, and the three check outputs.
- `repro.py` lines 29–80 (`rings_start`), `forbid.py` 1–135, `rival_growth.py` in full.
- `sides.py` 196–295.
- `FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A/results.md` and `growth_motion.md`.

`css.py` computes what its docstring says (read): `kernel`, `subspace_within`, the three treatments and the pairing rank are correct for the CSS form. There is one hazard at line 99: `sum(1 << idx[d] for d in k)` gives the wrong vector if a knot ever lists a distinction twice. Add `assert len(set(k)) == len(k)` or use XOR.

The docstrings cite `README.md` and `preregistration.md`, which are not in the folder yet.

## 1. The separability argument

I found no counterexample; the argument closes as follows.

- **The split.** A change x allowed and supported on A + B splits into x_A and x_B, both allowed, because each knot meets at most one reader.
- **e = 0.** For any value certainty z on A + B, x|A · z|A = x_A · z = 0, since x_A is in S and z in S⊥.
- **Separable.** Each reader's parts of the certainties commute among themselves, so the reduced state is diagonal in a product basis. It is a mixture of product states, so no read of any kind gives an excess.
- **No quotient needed.** Local certainties give zero rows and columns of the pairing.
- **Middle read for values.** The same split applies, and the state given the record is pure with e = 0, so it is a product: the readers are independent given the middle's values.

Two general identities follow, for any parity structure and any disjoint A, B, separated or not:

- e(changes) = dim(S⊥ on A + B) − dim(S⊥ on A) − dim(S⊥ on B). This is the number of independent parity relations between A's values and B's values under the counting weighting, i.e. their classical mutual information in bits.
- e(values) is the same expression with S for S⊥, and e(unread) ≤ min of the two.

**Check:** compute both rank expressions on every row and compare with `css.ebits`. This tests the code independently, and it says what "changes" measures: the readers' value correlation, read again.

**Where the claim is weaker than worded.** In every family the two connecting knots of a pair share a distinction directly (`repro.py` line 62, read). So the holders of ring r's and ring s's distinctions meet: the readers are apart in `sides.py`'s meaning but not in `forbid.meets`'. Taking each reader as the ring's own shared and loose distinctions (attachments to the middle) makes them apart in both meanings; by hand e is unchanged (0, 1, 0). Run both.

## 2. Is e the right quantity

For two readers, yes, with two additions.

- **Citations (from memory, not looked up).** Fattal, Cubitt, Yamamoto, Bravyi, Chuang 2004 covers pure states, which is the "changes" and "values" treatments. The unread case is a mixed state; the normal form (pairs plus a separable rest) is Audenaert and Plenio 2005.
- **e = 1.** Every table of Pauli reads, including contexts and the same-distinction product, has a list (one shared triple x, y, z with the second reader's y negated). CHSH is at most 2 with these reads and 2√2 with a rotated read (Tsirelson).
- **e ≥ 2.** The two-reader game of certainty is Cabello 2001 / Aravind 2004.

**Addition 1: the excess needs combined questions.** With value reads and change reads only (and products of the same kind), there is a list at every e and for any number of readers:

- Draw an allowed word w and, independently and uniformly, a sum of knot laws p.
- A value read of z answers the parity of w on z; a change read of x answers the parity of p on x.
- Reading one re-draws the other along what was read.

This is the rebit result of Delfosse, Allard Guerin, Bian, Raussendorf 2015. So an excess needs combined questions read together (a change on one part times a value on another, with its mirror), not only e ≥ 2. Parts B and C as designed cannot tell the coherent state from this pair of words.

**Addition 2: three readers.** Ring r, the chain and ring s should share one certainty that no pair's certainties generate. The change {a loose distinction of r, an attachment, the link c, an attachment, a loose distinction of s} is not a sum of changes each supported on two of the three. With the middle as a third reader with two settings, a three-reader game of certainty exists at e = 1. It needs the same-distinction product read. Freeze "two readers, the middle's setting fixed".

## 3. Prediction 3, and what the run will show

All four predictions are fixed by hand on these families. No birth has parents of two rings:

- The connecting knots hold no loose distinction, so they are never live.
- Every group is the children of one knot.
- `rival_growth.py` 81–85 (read) consumes every loose distinction and gives surplus ones single-parent births.

A cross value law modulo local ones is the sum of the laws of a set of middle knots closed under sharing middle-only distinctions and holding no loose one. Each dead chain gives exactly one. Any middle knot born later is joined to the newest births, which hold loose distinctions. So growth cannot add a cross value law while it is funded and does not close.

| Read | unread | changes | values |
|---|---|---|---|
| Every pair of rings, every family, rounds 0–2 | 0 | 1 | 0 |
| Control, round 0 | 1 | 1 | 1 |
| Control, rounds 1 and 2 | 0 | 1 | 0 |

**Prediction 4 fails as worded.** After round 1 each loose distinction of the two control knots is held by a birth whose other places lie outside A + B, and no birth has both knots as parents. No allowed change is then supported on A + B, so e(unread) = 0. Say "round 0", or freeze 1, 0, 0.

**"No two-reader game of certainty" is a product of the choice of readers.** Cheapest case, no new start: on the three-ring families at round 0, one reader holds rings 0 and 2 and the other ring 1.

- `css.ebits(knots, region[0] + region[2], region[1], 'changes')` should be 2, with unread and values 0.
- The two chains' law sums are independent cross laws, because the attachment values are free.
- The game of certainty is then available with combined questions, sorted on the middle.

Two more cheap cases:

- **A control that can fail:** `middle_loose=True` should give e(changes) = 0 for the first pair and 1 for the others at round 0.
- **A smaller middle:** reading only the change of the one distinction the two connecting knots share, the rest unread, should already give e = 1.

## 4. What carries a read of a change

- **Prior work.** The rule is already `FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A` (read, `results.md` 15–25). Its counts for a change T with values on disjoint U are the coherent counting state's. Under parity its f is 0 or 1 whatever the word. It records "the six-rule parity win is 1" with the order of combined questions supplied. Cite it; parts B and C add the separated arrangement and e.
- **A function of two words in the record.** That study's "unordered pair {s, s+T}" (line 19) is one, and it is supplied. Its selected and deferred next step is "a holding record that reveals the unordered pair". `growth_motion.md` §4 (read) found the exact flip of a funded parity birth's inputs has freedom zero, and no recorded event gives a freely chosen second question.
- **A second one.** `sides.py` R2 (lines 281–285, read) squares signed sums over completions, which is a sum over pairs of completions. By hand it is exactly "every unread distinction read for its change, sorted on the record all plus".
- **Your intended sentence is too strong.** Under parity a change read's answer depends on no word: certain if x breaks no law, a coin otherwise. What must be carried is the coin's agreement across readers. A second classical word p does that without coherence, and p is an allowed word of the exchanged pattern of `SECOND-CHECK` and `RECURSION-LEAD` (even on every smallest change). Coherence is forced only by combined questions or rotated reads.
- **Suggested wording:** "a change read needs a second word and a rule by which reading one re-draws the other; the record has the exchanged pattern but nothing that holds its word, and the exchange does not commute with growth."
- **Growth.** It carries the coherent state forward by copying parities, with each fresh distinction's change certain. It neither makes nor destroys the difference between the state and the counts.

## 5. The middle reader whose record sorts

It is the event-ready arrangement (Żukowski, Zeilinger, Horne, Ekert 1993, from memory). It is not communication, on three conditions:

- the middle's setting is fixed;
- its record does not depend on the readers' settings;
- the classical bound is applied within each record.

It is a three-reader table, and unsorted it is the unread table (e = 0). Print both, and check the middle's record against the readers' settings.

What it supplies is a third reader, the change read, and the pooling by record (the kind of scaffold A226 registers). Note also that the middle in `rings.py` includes the third ring's whole lineage and its loose distinctions; the one-distinction middle above avoids that.

**What a referee would press first:** every prediction is entailed, prediction 4 fails after round 0, and the "e ≤ 1" conclusion reverses when a reader holds two rings.
