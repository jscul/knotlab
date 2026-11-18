# Pair distances identify every junction when one presentation uses at most four distinctions per junction

**Standard statement.** Let one reachable finite wired incidence graph for the serial parity rule have ordinary degrees three and four. For pairs of named coordinates use the minimum size of a cocircuit containing the pair. If another reachable graph has the same entries through six under a coordinate bijection, the bijection carries every ordinary vertex star onto an ordinary vertex star. The second graph may use the full set of permitted degrees. The bound reduces to five when exactly two extensions in the first graph introduce three new coordinates.

**Nearest known result.** [The preceding short-equation theorem](../../VARIABLE-OUTPUT-READER-20261118-001F/VARIABLE-OUTPUT-READER-20261118-001F-P001_finite_interval/structural.md#recovering-every-equation-through-size-four) identified the equations of sizes three and four and gave equality of all equations with at most one three-fresh addition. The previous width count allows a rival with an additional independent equation as soon as a second addition makes three fresh distinctions. The present proof rules that rival out using the pair table and removes the number-of-additions restriction altogether. The broader [theory of signed-graph representations](https://arxiv.org/abs/1109.2978) supplies background terminology. The proof here uses the particular serial rule and its finite physical separations.

## What the reader receives

The seed is a single ternary even-parity relation. Each added junction uses one loose distinction from each of one, two or three different current parents and makes two or three fresh distinctions. Each two parents must have an ordinary common neighbor, and three parents must have no common neighbor of all three. The only numerical information supplied is the current pair table with a proposed unordered group marked. The exposed value for distinct bits is \(K=D+1\), where \(D\) is the bond distance. A threshold of \(L\) means that \(K=3,\dots,L\) are read exactly and all greater values give one common answer. A bijection need only preserve these entries. Nothing identifies birth order, the seed, the loose distinctions or the special additions.

## The theorem and sharp bounds

At every finite size, if one compatible presentation has at most four distinctions in each ordinary junction, every compatible rival has exactly its ordinary junction supports under the given renaming when the pair readings through \(K=6\) agree. In particular this fixes the entire allowed-state relation and every permitted one-, two- and three-parent selection. Both output counts remain available for every allowed selection.

| Three-fresh additions in the small-arity source | Sufficient pair reading | Sharpness against unrestricted rivals |
| --- | --- | --- |
| Zero or one | Through \(K=4\), or \(D=3\) | One swap on a seven-site source changes the triple while preserving all entries through \(K=3\). One unary addition gives the one-exception case |
| Exactly two | Through \(K=5\), or \(D=4\) | A width-27 marked pair of presentations agrees through \(K=4\) and gives opposite triple verdicts |
| Each exact count of three or more | Through \(K=6\), or \(D=5\) | A width-26 pair of presentations with three such additions agrees through \(K=5\) and gives opposite triple verdicts. Matched unary additions extend this example to each larger count |

These examples establish the sharp **distance horizon** in the specified nested family of pair readings. Their full tables are different. Their widths have not been minimized for this separate truncated-data question. [Two-addition histories](checks.json) · [Three-addition histories](six_check.json)

## Why a hidden site must change a pair reading

1. Short equations force each physical rival site of size three or four to be a site in the source. A hypothetical missing four-place source site would be the four-bit boundary of several rival sites. Take an innermost such boundary. Its last three sites supply its four boundary distinctions in groups of one, one and two. In the source, ordinary simplicity and bipartiteness leave only one possible distinction connecting the retained inside sites to the rest. Deleting it separates the source in a way the rival cannot match. This test itself needs only pair entries through the largest permitted junction arity. [Identification of the common sites](extension.md#the-low-junctions-are-the-same-physical-sites) · [Bounded separator proof](separator_horizon.md)
2. Once these common physical sites have been identified, the only way a rival could differ is by turning some of the source's loose distinctions into meetings at additional sites. At a five-place rival site, two of its output distinctions lie in its five-bit bond. In the source, any cut through those two must contain both of their holders. Counting the old inputs and outgoing distinctions proves it has at least six bits. [Five-place proof](extension.md#a-five-place-junction-forces-a-discrepancy-of-at-least-one)
3. An earliest six-place rival site has three parents and three children. Either two children still have older parents when the extra sites are removed, or a child has none. In the first case two output distinctions require at least seven bits together in the source. In the second case use that child's output distinction and the input from the latest of the three parents, who already needed two distinct earlier witnesses. This pair also requires at least seven. The rival's six-place star supplies a bond of size six or less in both cases. [Six-place proof](extension.md#the-earliest-six-place-junction-also-forces-a-discrepancy)
4. For exactly two three-fresh additions the equation-space rank can rise by at most one. Any strict rival then makes only two fresh distinctions per join and can have no six-place junction. The separator test works through five and the five-place bound suffices. Equal-rank rivals have identical equation spaces, hence identical full tables, so the general result applies. A separate finite closure checks the same sharp horizons at two and three additions with an unbounded number of two-parent steps. [Rank and independent finite-closure proof](cutoff.md)

One way to read the verdict is to find any matching reachable small-arity presentation for the truncated table and read its site memberships. At a fixed width that search is finite. The theorem says every permitted correspondence gives the same answer, even when the actual realization was allowed larger junctions. Equivalently recover the forced short equations, discard a four-bit sum of adjacent three-place stars, and use the resulting physical stars. A bit held at just one star is loose. A bit in two stars identifies their meeting. Each proposed group can then be tested using the parent rule. No history is an input to either reading.

## Evidence and remaining case

This is a uniform-family theorem with independent checks in the same task. The mathematical upper bounds hold over all finite widths. The finite examples establish the lower bounds for the scalar cutoffs. Reproduce the controls from the repository root with the workspace Python. Each JSON comparison recomputes original lawful histories, pair measurements and legal menus.

```sh
family=proofs/VARIABLE-OUTPUT-READER-20261118-001G/VARIABLE-OUTPUT-READER-20261118-001G-P001_two_three_fresh
set -o pipefail
.venv/bin/python -B "$family/check.py" | cmp - "$family/checks.json"
.venv/bin/python -B "$family/six_check.py" | cmp - "$family/six_check.json"
.venv/bin/python -B "$family/frontiers.py"
.venv/bin/python -B "$family/frontiers_one_three.py"
```

The unrestricted mixed-count inverse remains open for triples when **both** candidate presentations contain a five- or six-place junction. The full-table lower bound of 27 distinctions from the [six-width comparison](../../../research/VARIABLE-OUTPUT-READER-20261118-001F/decision.md) still applies there. The prior [18-distinction smaller-input witness](../../../research/VARIABLE-OUTPUT-READER-20261118-001A/first_three.md) contains a high-arity junction and gives identical full allowed states. Every bond reading computed purely from those states, including readings on three or more distinctions, must agree on its two histories.
