# Independent replay of the funded starts and ring baselines

All eleven principal builds have two classes and one bit beyond the span of the single-knot class reads at both ordinary rounds. Their named parities agree with the exploration table. On a shared knot only the sum of the ring parities works. Through a shared distinction or a chain, none of the sums of the ring parities works, and the parity of all old shared distinctions does. The ten-knot tree has two classes after one round and the same result under an extra loose distinction at every knot. The parity of all nine old shared distinctions labels both tree preparations. [Funded results](built_baselines_funded.json)

| Built preparation | Replay through the reported rounds |
| --- | --- |
| Joined rings | Among 30 recipe rows, 22 give two classes and eight give one at both rounds. The one-class cases are the six joins of 3+3 and 3+5 rings by a shared knot, shared distinction, or one-knot chain, and the two joins of 3+5+7 rings by a common knot or two successive shared distinctions. The 30 rows describe 29 starts because three five-knot rings with a shared knot occur in both scripts. |
| Rings kept apart | The eight recipes give a class bit for each ring of size four or larger. Thus 3+3, 3+5, and 3+5+7 have respectively one, two, and four classes at both rounds. The classes factor because shortest changes through a distinction stay within its connected piece. |
| Funding swap | The eight historical controls have two classes and the same stated label in each arm. The four-knot ring owes one distinction per knot, so its historical arms both supply two. In the additional control, raising its supply from two to three adds four births in the first round, from six to ten. There are still two classes, with the same old shared parity as their label and no single knot able to read it. |

The 41 principal and supplementary recipe rows represent 40 starts when distinction names are ignored and knot order is fixed. The 82 ordinary grown rows represent 80 different meeting patterns under that convention. All 82 preserve the original allowed changes. With the 41 source rows and 22 first-round forbidding controls, 145 measurements represent 139 different meeting patterns. Sixteen measurements, representing 14 patterns, exceed 64 ties at one or more distinctions. The total is 881 occurrences of an over-cap distinction, or 677 with each pattern counted once. The highest count through a single distinction is 450. Applying the original tie order with its cap of 64 preserves the move span on every measured row, hence every class and read. The historical funding controls use a cap of one million and peak at 288 ties. The 22 forbidding controls all have a positive fresh count at every birth, so they offer no case where a zero-fresh constraint could remove old states. [Original examples](../layers.py) · [Supplementary builds](../explore_more.py) · [Funding inputs](../checks_tree_and_funding.py) · [Funded results](built_baselines_funded.json)

The parity comparisons cover all 66 profiles in the earlier referee's round-two ring replay, sizes 3–13 with two loose distinctions per source knot at rounds 0–2, with stage-loose values free and pinned. All eight archived motion preparations at sizes 5 and 31 match on ranks and counts of classes and shortest changes. The original counts for moves shortest through each distinction and shortest overall match at sizes 3–12 with two loose distinctions per source knot at rounds 0–1, with loose values free. Comparison to each original canonical and fold archive covers sizes 3–9 with one or two loose distinctions per source knot, in both pin choices at rounds 0–1, with 54 recorded profiles or no-growth entries matched per archive. The two free first-growth entries skipped under the original rank cap, at sizes 8 and 9 with two loose distinctions, each give two classes. Canonical growth was rebuilt independently and the fold archive was compared to those results. [Two-class sign results](built_baselines_sign.json) · [Earlier ring referee](../../TWO-CLASS-SIGN-20261126-001/referee-R1/report.md)

The read and change distances were rebuilt for 126 profiles, sizes 4–12 at rounds 0–6 in both pin choices, with two loose distinctions per source knot. All 1,122 comparable archive fields agree. The odd rings with a class attain both minima at their start size, and the smaller minimum stays at or below the start size throughout the even-ring grid. A single minimum can exceed it. The committed archive has six unavailable read distances. The replay resolves them with that many disjoint odd changes, matching the size of a read witness. [Distance results](built_baselines_long.json) · [Earlier distance study](../../BOTH-LONG-20261126-001/README.md)

| Source knots | Rounds | Stage-loose values | Rebuilt read distance | Rebuilt change distance |
| --- | --- | --- | --- | --- |
| 8, 10, 12 | 6 | Pinned | 13 each | 8, 10, 12 respectively |
| 12 | 4, 5, 6 | Free | 12 each | 11, 13, 15 respectively |

The checker implements the ordinary rule from the documented operator and the built examples from their declared inputs. It reconstructs the shortest allowed changes through each distinction in the incidence representation with every tie, then checks ranks and single-holder reads by binary linear algebra. For the distances, it searches the two parity copies of the incidence representation for the shortest odd closed change. It certifies minimal reads by a packing of disjoint odd changes or exact cardinality decisions over translates by the knot equations. Literal enumeration checks every allowed assignment on 29 ring profiles and every equivalent read on seven. The archived outputs serve as comparison targets. [Checker](built_baselines.py) · [Ordinary operator](../../ORDINARY-DYNAMICS-20261120-001/end_operator.md)

Run from the repository root using one process with a 2 GiB address-space cap. Add `--pilot` to the same command before a full run. Funded, sign and distance runs took 0.79/1.94, 0.04/0.08 and 0.26/2.48 seconds respectively for pilot/full. The highest observed resident memory was 31,780 KiB.

```bash
R=research/LAYERS-20261126-001/referee-R1
for part in funded sign long; do
  prlimit --as=2147483648 -- /usr/bin/time -f 'elapsed=%e peak_rss_kib=%M' \
    .venv/bin/python -B "$R/built_baselines.py" --part "$part" \
    > "$R/built_baselines_$part.json"
done
```

**Narrowing.** Qualify the joined and separate-ring rows in the exploration table by the actual examples including the three-knot controls. Qualify the funding swap as unchanged at size four in the original and sustained under a genuine swap in the referee check. The guide's general class claim per connected piece is already contradicted by the frozen result. The earlier distance study's text counts five unavailable read distances where its archive contains six. [Exploration table](../README.md#what-the-exploration-found-computed-not-frozen--layerspy) · [Funding disclosure](../decision.md) · [Guide lesson 12.2](../../../publication/knotlab/INTUITIONS.md) · [Distance study](../../BOTH-LONG-20261126-001/README.md)

**Not run.** Separate reconstruction of the fold engine, not-all-equal growth, later rounds of these joined builds, other funding changes, and the earlier studies' census and sampled-start reruns in this replay.
