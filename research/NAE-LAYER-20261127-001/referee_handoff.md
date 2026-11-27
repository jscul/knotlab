# Referee hand-off: NAE-LAYER-20261127-001

The note is [README.md](README.md) (frozen at `643e5a85a9` before the runs); the decision is [decision.md](decision.md).

| # | Claim | Evidence class | Code | Data |
| --- | --- | --- | --- | --- |
| 1 | T7: 4,374 states; 510 of 512 loose patterns; (g0, g1, g2) 25 of 27 triples, missing all + and all −, every pair free | computed, frozen | `t7.py` | `t7.json` |
| 2 | The ring control (11 renamed 9): all 128 loose patterns | computed, frozen | `t7.py` | `t7.json` |
| 3 | Growth: T7 stalls; with 15, 16, 17 added, 55,566 states, 4,094 of 4,096, and every loose pattern after one round | computed, frozen | `t7.py` | `t7.json` |
| 4 | Census: one class under single changes, no ties, loose patterns 2^m − 2 on tree-shaped starts and 2^m otherwise; every pattern after one round on 500 starts; parity 2^(m − 1) | computed, frozen | `census.py` | `census.jsonl` |
| 5 | The reading: under not-all-equal a fact held by the whole is a composition over a ring-free part, the first layer read through relays; rings and growth erase it; no second layer | argument (the advisor's lemmas F, G, R) and the computed checks | README.md | |

**Points to press.** The advisor's lemmas (forcing, gluing, rings erase) as stated in its answer; whether "which values
occur" is the right test of a fact here (a weighting of states could carry correlations, the advisor's reading (c));
whether the composed relation is "the first layer read through relays" in every case; the small number of tree-shaped
census starts (15); starts past the census and later rounds.
