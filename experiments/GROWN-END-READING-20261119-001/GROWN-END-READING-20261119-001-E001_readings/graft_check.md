# Two-terminal substitution preserves the marked readings

Let `G` be the closed ordinary core in the classical holder graph, and let `e` be its distinguished shared distinction with holders `s,t`. Put `H = G − e`. Take a connected graph `Q` meeting `H` exactly in `s,t`, with disjoint distinction names. For the natal construction, `H` is also connected. Write `K` for minimum common bond size, with infinity for absence, and `L_H` and `L_Q` for the corresponding minima over bonds separating `s` from `t`. An empty mark set in `L` gives the unmarked separating cost.

## The complete cut calculation

If a bond keeps `s,t` on the same shore, its other shore lies entirely in one piece. With both terminals unavailable on that other shore, the two pieces have no way to connect it across pieces. All marks and crossings therefore belong to just one piece. For a bond crossing only `H`, the whole of `Q` belongs to the terminal shore; connectivity on that shore is equivalent to the connectivity supplied by the single connector `e` in `G`. Correspondingly, the same-terminal exterior cuts are exactly those of `Q` with a virtual connector between `s,t`.

If a bond separates `s,t`, its restriction to each piece has both shores connected. Every component on one shore must reach its own terminal within that piece before it can enter the other piece. Conversely, any connected separating cuts of `H` and `Q` can be oriented to agree at the terminals, and their union has both global shores connected. Their sizes add. The two-terminal parts are connected, so each contributes at least one crossing. This gives the following formulas for marked sets `X` in `H` and `Y` in `Q`.

| Marked distinctions | Minimum common bond size in `H ∪ Q` |
| --- | --- |
| `X` and `Y` both nonempty | `L_H(X) + L_Q(Y)`, where `L_H(X) = K_G(X ∪ {e}) − 1` |
| `X` nonempty and `Y` empty | The least of the same-terminal minimum in `G` and `L_H(X) + L_Q(∅)` |
| `X` empty and `Y` nonempty | The least of the same-terminal minimum in `Q` with a virtual connector and `L_H(∅) + L_Q(Y)` |

An unavailable cut has infinite cost. The same formulas handle missing bonds and a closed `Q` without an outside holder. If `L_Q(∅) = 1`, the pure interior expression equals `K_G(X)`. For a mixed pair or triple, `X` has at most two distinctions, so `X ∪ {e}` is an available order of core reading. A core self-matching fixing `e` and preserving every pair and triple minimum therefore carries every pure interior and mixed minimum. Fixing every exterior distinction preserves the pure exterior readings.

## Actual growth retains separating cost one

Attach one new ordinary junction `U` to `s` and another `V` to `t`, each by one distinction, and give each two loose distinctions. The old ordinary core has no loose distinctions. In round one, `U` and `V` have distinct sole ordinary neighbours and form no pair. Each gives two offshoots, which then share their own parent. Each offshoot receives two fresh distinctions from the arity floor and its lookahead demand of one. In round two each branch makes one pair junction and two offshoots. Their lookahead demands are two, one and one, respectively. Each receives two fresh distinctions.

Thereafter all live junctions meet only their parents, and every parent belongs to its own branch. Across branches there is no common parent. Each branch produces at least one new junction, so a new junction in either branch takes only a proper subset of the loose distinctions of the whole arrangement. Its parity is nonimplied by the connected-stage criterion and it receives at least one fresh distinction. The lookahead demands keep the following round available. Thus both branches stay open. The outside holder then gives a route between their terminals in `Q`, and the single link `sU` gives a connected separating cut of size one in `Q` throughout. The formulas apply at each age.

## Literal controls and dense replay

The compact core is the classical `K4`. The permutation exchanges its terminal vertices, fixes the name `e`, and keeps every exterior distinction individually fixed when applied to the graft. The production growth engine and an independent round check agree on the literal stages. The exact bond enumeration verifies the formulas and the marked permutation on every entry.

| Compact stage | Ordinary junctions | Distinctions | Pairs checked | Triples checked | Mixed triples with no common bond |
| --- | ---: | ---: | ---: | ---: | ---: |
| Start | 6 | 11 | 55 | 165 | 77 |
| After round one | 10 | 19 | 171 | 969 | 373 |
| After round two | 16 | 31 | 465 | 4,495 | 1,117 |
| Closed exterior path control | 6 | 8 | 28 | 56 | 21 |

The literal 21-index graft independently replays from `(235,635)` ordinary junctions and distinctions to `(239,643)` and `(245,655)`. The marked index exchange fixes every live distinction and preserves every pair-flip bit at the first reached stage, where 206,403 bits were checked. The image of the dark hub's equation lies outside the equation span. One certificate is the allowed state difference with support `{22,23,133,134}`. Every literal junction support meets it evenly, while the image equation meets it only at `134`. The certificate persists in both replayed rounds.

The dense-core pair and triple minima use the separate dense-core proof and the substitution formula above. The literal large replay checks growth, the marked growing end, the pair-flip bits, and the equation obstruction. This combination provides the reached obstruction to reconstructing the equation span from those readings. For this two-terminal graft the marked permutation preserves the pair and triple minima at later ages by the same calculation.

```bash
.venv/bin/python -B experiments/GROWN-END-READING-20261119-001/GROWN-END-READING-20261119-001-E001_readings/graft_check.py
```

[Literal control and dense certificates](../../../artifacts/GROWN-END-READING-20261119-001/GROWN-END-READING-20261119-001-E001_readings/graft_check.json) · [Complete-round reading](../../../research/EXTEND-ROUND-20261119-001/extend_round.md)
