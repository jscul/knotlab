# Supplementary referee report on reading values and changes
**Confirmed with fixes. No Block.** The supplied coherent state, combined questions and middle reader who sorts give a no-signalling quantum table. The winning probability is 1 when the score uses the middle record's signs. Pooling the raw answers gives 2/3 on the rebuilt start.

The three supplied pieces are the **coherent counting state** with equal positive amplitudes on the allowed words, the **combined questions** that read a change of one set with a value of another, and the **middle reader who sorts** by the outcomes of one fixed change measurement. The state controls explicitly replace the first piece while holding the other two fixed.

## 1. Can the sorted or unsorted records signal?

With the coherent state, combined questions and sorting middle reader, I rebuilt the direct-link family of three rings of five knots before growth. Reader A holds all distinctions of rings 0 and 2, reader B all distinctions of ring 1. There are 21 knots and 63 distinctions, of which A holds 38, B holds 19 and the middle holds 6. No knot holds a distinction of both A and B. The 21 independent even-parity laws allow exactly $2^{42}$ words. Exact parity expectations account for all of them.

The full table for the coherent state, combined questions and sorting middle reader covers all 9 setting pairs, all 64 middle records and all 8 three-sign records for each reader. Of 36,864 entries, 576 are positive, each with joint probability 1/64 at its setting. The middle distinctions in order are 49, 50, 55, 56, 61 and 62. Writing 1 for a minus sign, the eight supported records have the form $m=(p,p,q,q,r,r)$. Each has probability 1/8 under every setting pair. [Full joint, conditional and pooled tables](tables.json)

| Marginal of the coherent state with combined questions and sorting middle reader | Exact result |
|---|---|
| A or B, pooled and conditional on each supported $m$ | Each of the four triples of the required parity has probability 1/4. Changing the other reader's setting leaves the whole triple's distribution fixed. |
| A with the middle, or B with the middle | Each compatible pair of a local triple and a middle record has probability 1/32, independent of the other reader's setting. |
| A and B conditional on $m$ | Eight answer pairs have probability 1/8 each. All obey the intersection sign specified below. The other pairs have probability zero. |
| A and B with the middle forgotten | For the values-only row, eight pairs have probability 1/8 each. For each of the other two rows, all sixteen parity-allowed pairs have probability 1/16 each. |
| A and B after using $m$ to correct signs | At each setting, eight pairs have probability 1/8 each and agree at the intersection, both within each supported record and after pooling. |

For the coherent state, combined questions and sorting middle reader, these marginals answer both signalling questions in the negative. There is also a direct reason. Summing either reader's complete local measurement over its outcomes inserts the identity, for every setting. This works with the middle projector still present. Summing both readers leaves the middle probability alone. Dividing by its positive, setting-independent probability proves the same independence after sorting. The 56 impossible middle records have no conditional table.

## 2. Which game has value one?

For the coherent state, combined questions and sorting middle reader, let $s_1=(-1)^{p+q+r}$ and $s_2=(-1)^r$. These are the measured middle signs of two allowed changes extending the readers' selected changes. In the first and third game rows, the three raw intersection products are $(s_1,s_2,s_1s_2)$. In the second row all three are +1. A sign of -1 means certain disagreement. The following scores weight the nine setting pairs equally.

| Use of the sorting middle reader's record, with coherent state and combined questions fixed | Score |
|---|---:|
| Sort and score raw equality | 1 in 2 of 8 records, 5/9 in 6 of 8 |
| Pool and score raw equality | 2/3 |
| Apply the record's signs to A's triple and score equality | 1 in all 8 records |

With the coherent state and combined questions, the sorting middle reader's two signs can be given to A before the settings are chosen. A can then play the ordinary game using the corrected answers. Alternatively, a scorer can use the signs afterward and report a record-corrected score. The correction uses A's row and the middle record only. Its three factors multiply to +1, preserving A's required row parity throughout.

The coherent state, combined questions and sorting middle reader admit an explicit quantum realization. In a supported middle record the same game table is realized on two local four-state systems by

$$
  \frac{1}{2}\sum_{u\in\{0,1\}^2}s_1^{u_1}s_2^{u_2}|u\rangle_A|u\rangle_B.
$$

The generator $X_j$ flips bit $j$, and $Z_j$ reads its sign. Their products give the combined questions. All three reads in each requested row or column commute, and the readers act on separate factors. The literature calls this the Mermin–Peres square game. The row products are $(+I,+I,+I)$ and the column products $(+I,+I,-I)$. Direct multiplication of the local projectors reproduced every entry. Winning probability cannot exceed 1. A fixed list must fail on at least one intersection because the total row and column parities disagree. A can answer all plus signs, and B can use one minus sign in the last column, attaining 8/9. The excess over that classical maximum is fully accounted for by the quantum realization. [Gisin, Méthot and Scarani on the square game](https://arxiv.org/abs/quant-ph/0610175)

## 3. Does counting supply the coherent state?

The combined questions and sorting middle reader distinguish preparations with identical count data. For the $N=2^{42}$ allowed words, counting fixes the diagonal entries $1/N$. The coherent state adds the off-diagonal entries $1/N$ as well. The uniform mixture sets them to zero. More generally, amplitudes $e^{i\theta(w)}/\sqrt N$ give exactly the same counts for every choice of phases. Requiring every allowed change to have outcome +1 would select the equal-positive state. Changes translate any allowed word into any other, so the amplitudes must agree. That is an extra requirement.

| Preparation supplied in place of, or as, the coherent state | Score with the same combined questions and sorting middle reader's original signs |
|---|---:|
| Equal positive amplitudes | 1 |
| Uniform diagonal mixture of the allowed words | 2/3 |
| Multiply each amplitude by $(-1)^{w_{15}}$ | 1, identical full table |
| Multiply each amplitude by $(-1)^{w_0}$ | 5/9, or 1 with the additional known sign reversal |
| Multiply each amplitude by $i^{w_0}$ | 7/9 |

With the combined questions and sorting middle reader fixed, distinction 15 is an open loose distinction outside both selected changes. The sign $(-1)^{w_{15}}$ genuinely varies across words and preserves the entire coherent-state table. By linearity, even a half-and-half mixture of those two preparations gives the same full table. Distinction 0 is a shared distinction flipped by the first selected change. Its quarter-turn phase makes four intersection products uncertain with the original questions and signs. The uniform mixture is a mixture of product words even conditional on a middle record, so no choice of local questions can recover a perfect game from that mixture. All five scores in the table were rebuilt.

## Fixes to the study's wording

**Narrowing — state how the game is scored.**

> Built from the readers' own reads (changes, values and combined questions on their own distinctions), all nine cells of the square are certainties of the sorted state on all 18 rows, and each row's and column's reads commute on the first reader's side: the readers win the square's game with certainty, where any list of values wins at most 8 of 9. [README, part C](../README.md#L82)

> One reader holding two rings and the other the third share two pairs (e = 2) on the three three-ring families without a loose chain, at every round read, and all nine cells of the literature's square are certainties: the game is won with certainty, where a list of values wins at most 8 of 9. [Decision, item 4](../decision.md#L21)

For the coherent state, combined questions and sorting middle reader, replace the win clause with “after using the middle record's two signs to label one reader's answers, every intersection agrees.” The study checked membership among the certainties and commutation on A. The rebuilt raw scores distinguish sorting from relabelling in six records. The no-signalling claim holds for both.

**Narrowing — state what counting supplies.**

> Under parity a change read's answer depends on no word: certain where the change breaks no law, an even coin otherwise. [README, part B](../README.md#L48)

> The least state that carries it is the *coherent counting state*: every allowed word weighted equally and every two related equally (the literature's equal superposition over the allowed words; a stabiliser state whose certainties are the knots' laws, read as values, and the allowed changes, read as changes). [README, part B](../README.md#L51)

> Nothing native reads a change; these are the least additions under which a change read means anything, and the regions follow the structure's own lineage. [Assumptions register, A300, “Why”](../../../docs/ASSUMPTIONS.md#a300--values-and-changes-both-readable-the-coherent-counting-state-combined-questions-and-a-middle-reader-who-sorts)

Qualify the certainty rule with “in the supplied equal-positive state” and describe the coherent state, combined questions and sorting middle reader as sufficient for this table. In the equal-count mixture, every nonempty allowed change has two equally weighted outcomes. A different relative phase even reproduces the entire winning table. A300 already identifies the coherent state as supplied.

**Not a block — retain all three supplied pieces in the interpretation.**

> The square's certainty for readers who share no knot is then the same certainty the four-readings study found with a supplied preparation; here the preparation is the coherent counting state on a grown structure, and the supplied part has moved into the middle's reads. [Decision, intuition paragraph](../decision.md#L50)

The coherent state remains supplied alongside the combined questions and sorting middle reader. Replacing it by the mixture drops the score to 2/3 with the same questions and sorting.

## Reproduction and limits

[The physical-table calculation](rebuild.py) rebuilds the knots from the direct-link construction. It reads the actual question supports chosen by the study's [selector](../css.py#L132). The signs, state expectations, probabilities and marginals are computed afresh. The convention is $X^x Z^z$ with a minus sign on the last cell for both readers, which gives the row and column products above. For the coherent state, the expectation of a signed product vanishes unless its change preserves every law and its value mask is a sum of laws. Inverting the 4,096 commuting product expectations at each setting gives the probabilities of all combined questions and the sorting middle reader's full record. [The second calculation](check_realization.py) uses explicit four-by-four local projectors and matches all 36,864 entries, including zeros, and both pooled tables.

From the repository root, run each command with one process. The one-setting pilots used the same 512 MiB address-space cap as the nine-setting runs. Pilot times were 0.10 s and 0.02 s, giving nine-setting estimates of 0.90 s and 0.18 s. Measured full times were 0.42 s and 0.03 s, with peak resident memory below 17 MiB in each.

```sh
r2=research/VALUE-CHANGE-20261126-001/referee-R2
prlimit --as=536870912 .venv/bin/python -B "$r2/rebuild.py" --pilot
prlimit --as=536870912 .venv/bin/python -B "$r2/rebuild.py" --tables
prlimit --as=536870912 .venv/bin/python -B "$r2/check_realization.py" --pilot
prlimit --as=536870912 .venv/bin/python -B "$r2/check_realization.py"
```

**Not run.** Other families, later growth rounds, the restriction to distinctions held only within a reader's rings, a second middle setting, a census of phases, and the whole-study replay. The 18 cases in the quoted study result were read. One of them was rebuilt for this supplementary check.
