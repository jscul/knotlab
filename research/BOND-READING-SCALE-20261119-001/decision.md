# How many distinctions must be read together?

On a reached stage of complete cheapest-count parity growth, the worst-case order needed to carry every later bond reading grows linearly with the number of junctions, and lies between square-root and linear growth in the number of distinctions.

A reading through order \(r\) includes every set of at most \(r\) distinctions, including the answer that no common bond exists. A single renaming fixes every distinction at every live junction. A successful renaming must extend coherently across all subsequent complete rounds. The bounds are worst cases over reached stages of at most the stated size. Current sizes below exclude the exterior junction and include all loose distinctions. Distinct junctions may meet more than once unless a row says otherwise. The study was frozen as an exploratory search. The optimizing constructions and the sharper upper bound were obtained during the investigation. [Frozen scope](preregistration.md)

## Finite minima and witnesses

A later reading can reveal a fixed old equation on a larger set even if all future pairs continue to agree. Requiring a pair to reveal the difference is a stronger test. In the first data column the examples for \(r\ge3\) first differ at order \(r+1\) and preserve every reading through \(r\) at every later age. The other outcomes in the table are witnessed by old pairs. [Small-stage proof and replays](lower.md) · [Old-pair replays](../../experiments/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/low.md) · [Higher-order pair controls](high.md)

| Present order \(r\) | Any later reading, fewest junctions found \((J,n)\) | Any later reading, fewest distinctions found \((J,n)\) | A later pair, fewest junctions found \((J,n)\) |
|---:|---:|---:|---:|
| 2 | **(5, 11), proved minimum** | **(5, 11), proved minimum** | (9, 21), two rounds later |
| 3 | (13, 91) | (15, 67) | (96, 368) |
| 4 | (16, 454) | (23, 197) | (315, 1,360) |
| 5 | (19, 897) | (28, 275) | (472, 2,063) |
| 6 | (22, 1,568) | (40, 365) | (739, 3,316) |
| 7 | (25, 2,515) | (45, 481) | (1,132, 5,708) |
| 8 | (28, 3,786) | (44, 634) | (1,589, 7,830) |

The first minimum is simultaneous in the two measures of size. Its permutation swaps distinctions 8 and 10. A four-distinction set is itself a bond, while its image lies in no bond after growth. Under meet-once the joint minimum is six junctions and eleven distinctions, and three old distinctions suffice to expose it. In both histories all future pairs continue to match. For the separate immediately-next-pair test, the exact least width is 21 with repetitions allowed, attained at (10,21), and the meet-once minimum is (12,23). The (9,21) history agrees on every pair for one more round before a pair breaks. Universal all-age pair safety is exhausted through width 15. [Small witnesses and the all-age exclusions](lower.md) · [Immediate and delayed controls](../../experiments/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/low.md)

For \(r=3\) an old quartet and its image read no bond versus a minimum bond of size 24 at (15,67), or no bond versus 38 at (13,91). At (96,368) two old pairs and their images have minimum sizes 30 and 30, then 28 and 30. A two-attachment example at (39,210) has every successor pair preserved and an old triple reading 37 versus 40. For \(r\ge3\) the smaller-junction formula \(J=3r+4\), \(n=8r^3-6r^2+9r+2\), gives an unrestricted-order witness at every order. The compact branch of this formula has its first discrepancy at \(r+1\). A second choice and an independent family both give width \(O(r^2)\). Bounded parameter searches and reachability controls extend to order 14. Their examples and their exact parameter ranges are recorded separately. The unrestricted minima for \(r\ge3\) are open. At (16,454), independent enumeration of all 17,816 bonds and 163,185 four-distinction holder-class sets verified the compact construction directly. An old five-distinction set reads no bond versus a minimum of size 214. [Direct four-mark verification](../../artifacts/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/compact_check.json) [All-order construction](lower.md) · [Exact small family and orders through fourteen](static.md) · [Two-attachment triple](scaling.md)

## Size and attachments

Let \(R_{\rm all}\) denote the least order sufficient to carry all later sets for every marked stage within a size budget. Reading through \(J\) suffices. At any exhausted junction, choose one distinction for each different adjacent junction. A bond containing this selection must contain the whole junction equation, and hence equals it. An additional test distinction tells whether it belongs to that bond. There are at most \(J-1\) neighbors. The growing end provides the remaining equations. Conversely there is a family with \(J=3r+4\) where order \(r\) loses a later reading. There is also a family with \(J\le137r+280\) where a set of the **same** order \(r\) first exposes growth one round later. Thus \(R_{\rm all}(J)=\Theta(J)\). [Upper bound](limiting-reading.md) · [Fixed ambiguity](lower.md) · [Newly exposed ambiguity](scaling.md)

In literal distinctions the best general bounds obtained here are
\[
c\sqrt n\ \le\ R_{\rm all}(n)\ \le\
\min\left(1+\left\lfloor(2n-1)/5\right\rfloor,\
          1+\left\lfloor(2n+9)/7\right\rfloor\right)
\]
for all sufficiently large \(n\) and some constant \(c>0\). The construction proving the square-root lower bound can change a **next pair**, even under meet-once. For carrying a next pair alone the junction bounds are \(\Omega(J^{2/3})\) and \(O(J)\). The exponents \(2/3\) in junctions and \(1/2\) in distinctions are sharp for the shrinking-branch construction analyzed here. Both unrestricted sharp exponents for next pairs remain open. The construction forces a quadratic cost by requiring many independent routes; a general square-root upper bound would need an argument encompassing differently connected junctions. [Upper bounds and their scope](limiting-reading.md) · [Pair constructions and their cost](scaling.md)

| Supplied attachment between a connected unchanged part and a connected changing part | What a fixed renaming of the unchanged part can carry |
|---|---|
| Two shared junctions | Reading through \(k+1\) now carries readings through \(k\) at every later round. The extra distinction is necessary in the worst case for every \(k\). |
| Three shared junctions, or any fixed larger number | For every current order \(r\), an example matches through \(r\) and changes a pair of old distinctions in the next round. Each of the prescribed attachment junctions is necessary to separate the changing part from the moved distinctions. |
| Three shared junctions with exactly one crossing distinction apiece | For the connected replacements retaining those three named distinctions, readings through \(k\) carry all later readings through \(k\). |

With two shared junctions one mark in the changing part measures the conditional cost of separating them. Three shared junctions can carry arbitrarily many shared distinctions. In the failing examples small current readings group the three together, while growth later makes separating them on one side cheaper. In an admissible wired stage, removing one junction cannot separate two nonempty interiors. [Full attachment theorem and literal replays](attachments.md)

## The limiting reading

Write \(K(S)\) for the size of the least bond containing \(S\). The one bit \(K(S)=|S|\) identifies precisely those nonempty \(S\) that are bonds. Subtract a contained bond from any nonzero parity equation and its support strictly decreases. Repetition expresses it as a sum of the detected bonds. With the growing end one can restrict those equality tests to **sets of shared distinctions**. All exhausted junctions have their entire equation on shared distinctions, and the supplied live junctions give the remaining equations. Another proper family avoids a single fixed loose distinction and uses one supplied live equation containing it. The recovered equation span and growing end transport coherently to every later round. This specifies all implied equations and allowed states. Distinct lists of generating junctions can define that same span. [Proof and converse](limiting-reading.md)

## Evidence and outstanding questions

- **Proved for every size.** The junction size law, the distinction bounds, the attachment rules with their stated hypotheses, the reconstruction from a proper family, and the persistence of a hidden equation on an old support. These calculations concern the parity growth law and the specified renaming.
- **Exhausted to a bound.** All reached stages through 18 distinctions pass the three-mark test for every later order. At width 18 the static superset included 62,195,994 rooted allocations. Its 7,665 residual allocations were settled by 57,770 normalized marked maps. For the immediate pair-to-pair test all 438,040 weighted predecessor allocations through 20 distinctions passed. The separate computation attaining the global two-mark minimum and its junction lower bound is in the small-stage proof. Counts refer to the declared presentations. [Width exclusions](lower.md) · [Immediate width panel](../../experiments/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size/low.md)
- **Family searches and sampled controls.** The higher-order small examples are constructive upper bounds. The old-pair search exhausts its stated mark profiles and candidate parameter panels through order eight. The separate two-hub comparison exhausts its listed integer ranges through order seven, with a sufficient-certificate search through fourteen. Independent implementations replayed complete rounds on selected literal examples. Initial and later equations were checked directly on small stages. The three-single-distinction replacement identity was independently tested on 61,384 queries. [Higher-order panels](high.md) · [Other finite panels](static.md) · [Attachment controls](attachments.md)
- **Open.** The exact unrestricted growth rate by literal distinctions, a sharp junction rate for the next pair alone, and the unrestricted minimum sizes at each \(r\ge3\). The most direct discriminator for the size exponent is whether any change of equation invisible through \(r\) must consume \(\Omega(r^2)\) distinctions beyond the independent-route family, or whether alternate arrangements compress that cost. The in-task checks are complete. Independent program referee pending.
