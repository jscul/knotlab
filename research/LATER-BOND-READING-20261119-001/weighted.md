# Exact bounds for weighted two-terminal cores

No triple reading changes after a decrease in the exterior separating cost in the tested **306,057 admissible two-terminal cores**. The comparison covers every permutation of the actual core distinctions fixing the exterior, including permutations that split parallel classes. It covers an unchanged core and a connected exterior meeting it at exactly two junctions. [Frozen design](preregistration.md)

| Core junctions | Maximum multiplicity per meeting | Admissible cores up to terminal-preserving renaming | Cores requiring an exact current-cost comparison | Exact current-cost comparisons |
|---:|---:|---:|---:|---:|
| 2 | 3 | 3 | 0 | 0 |
| 3 | 3 | 20 | 0 | 0 |
| 4 | 3 | 756 | 0 | 0 |
| 5 | 3 | 72,968 | 860 | 8,897 |
| 6 | 2 | 229,776 | 8,691 | 99,676 |
| 7 | 1 | 2,534 | 233 | 2,651 |
| **Total** | | **306,057** | **9,784** | **111,224** |

Each multiplicity can be zero. The core is connected, each nonterminal has arity at least three, and deletion of any junction keeps the core connected with a virtual connection between the surviving terminals. These gates include every eligible connected core of the stated sizes and multiplicities in a connected exterior of the specified type. The graph calculation uses junctions as vertices and distinctions as edges. Terminal swaps and permutations of the other junctions select canonical weighted incidence. Independent orbit counts using Burnside's lemma match every roster before applying the intrinsic gates. [Population and certificates](../../artifacts/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/weighted_core.json)

The separate multi-attachment family gives a reached failure at 104 current junctions. [Asymmetric branch construction](../../experiments/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/weighted_shield.md)

## Which costs must be compared

For core marks $X$, let $B(X)$ be the least bond size keeping the two terminals together, using the exterior for connectivity, and let $L(X)$ be the least cost of a connected core cut separating the terminals and containing $X$. Both have a separate infinity value. If the exterior has least separating cost $\lambda$, a pure core reading is $K_\lambda(X)=\min(B(X), L(X)+\lambda)$. A reading using both pieces instead adds the marked separating costs of the two pieces. Consequently the entire old pair and triple observation, for a permutation supported in the core, is equivalent to all pure $K_\lambda$ pairs and triples plus all $L(X)$ for one or two marks. For necessity of the latter, query $X$ with a fixed exterior distinction on a minimum separating cut. Mixed readings at any later exterior stay invariant under the same map because they still use only those marked core costs. [Two-terminal substitution](../../experiments/GROWN-END-READING-20261119-001/GROWN-END-READING-20261119-001-E001_readings/graft_check.md)

Consider two triples matched at cost $\lambda$. If their $L$ values agree, their minima agree at every lower cost. If $L_1<L_2$, their equal current value $h$ must equal $B_2$ and satisfy $B_1\ge h$. At cost $\mu<\lambda$ their readings differ exactly when $L_1+\mu<h$. Thus a difference at any positive integer lower cost is still visible at cost one. For a potential break with $L_1+1<B_2\le B_1$, a current tie is possible only at $\lambda=B_2-L_1$ when $B_1>B_2$, or at that cost and higher when $B_1=B_2$. With $W$ core distinctions, all finite $B$ values are at most $W$. Beyond $W$ the equality pattern stabilizes, including where $B$ or $L$ is infinite. Testing costs $2$ through $W+1$ therefore covers all positive integer decreases.

The search first computes the full group preserving $L$ through two marks. If its generators preserve every $L$ triple or every $K_1$ triple, the entire group satisfies that certificate. Otherwise the engine lists candidate tie costs from triples with the same restricted separator data and stable unary colors. At each remaining cost it builds the exact group preserving both $L$ through two and $K_\lambda$ through three, and checks $K_1$ on a complete stabilizer generating set. The group search uses the individual distinction labels. A connected cut crosses an entire parallel class, so its value uses that class's multiplicity and remains exact even when different labels in that class have different images.

## Controls

The five-, six-, and seven-junction searches include maps preserving $L$ through two marks and changing $L$ on a triple. Independent replay by inclusion-minimal XOR supports confirms the named cases. The simple seven-junction case gives finite separating costs six and five on the indicated triple and its image. The same-terminal costs for those marks are infinity and six. These are controls for the initial separator reading, and the complete current group test rejects transport-breaking maps at every possible cost.

Two explicit cheapest-count histories lower the exterior cost from two and three respectively to one around the five-distinction core known in graph theory as a diamond. The full old pair table is invariant, and four old pair readings separate on the successor in each case. The full old triple table already rejects the swap, with 88 and 100 differing triple entries respectively. Literal growth, the fixed live supports, exact minima including infinity, and the measured exterior costs are all checked. An artificial table with a tie at cost two and different minima at cost one also exercises the search's positive reporting branch. [Literal and abstract controls](../../artifacts/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/weighted_core_controls.json)

## Replay

From the repository root, use C++20 and the shared runner. The two completed runs cover 137 shards each and agree byte for byte.

```sh
family=experiments/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future
scratch=$(mktemp -d)
.venv/bin/python -B "$family/weighted_core.py" prepare "$scratch/weighted_core"
for panel in 2:3 3:3 4:3 5:3 6:2 7:1; do
  order=${panel%:*}
  maximum=${panel#*:}
  .venv/bin/python -B scripts/longrun.py launch "$family/weighted_core.py" \
    --out "$scratch/panel$panel" --unit "later-weighted-n$order-w$maximum" \
    --workers 6 --case-timeout 180 --case-mem 250M --mem-max 3G --prepare-only \
    --param engine="$scratch/weighted_core" --param order="$order" --param maximum="$maximum"
  .venv/bin/python -B scripts/longrun.py run --out "$scratch/panel$panel" --foreground
done
.venv/bin/python -B "$family/weighted_core.py" collect "$scratch"/panel* > "$scratch/summary.json"
.venv/bin/python -B "$family/weighted_replay.py" "$scratch/summary.json"
"$scratch/weighted_core" --abstract-control
```
