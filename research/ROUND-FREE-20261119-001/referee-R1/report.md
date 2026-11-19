# Referee report ROUND-FREE-001-R1 (fresh code; one size past where it matters)

**Verdict: confirmed, with two Narrowings on the order-free claim. No Block.**
- **serial.py's present-state law is a fair serial reading of the policy.**
- **The order effects reproduce** with the referee's own implementation of that law.
- **The Part C shares reproduce exactly** by the referee's own brute force on the cover.
- **The order-free closure law does reach one structure in every order.** In 20 random orders on two starts it made the same set,
  equal by size to the growth's rounds.
- **But the claim needs two qualifications** before John hears it as the answer to "time doesn't have ticks":
  1. **The law reads the whole unrolled map in advance.** That map encodes every future join, so it supplies exactly the look-ahead
     the rounds supplied; it is not a law that reads only what is built.
  2. **It reproduces the rounds only where the cluster rule holds.** CLUSTER-ALL's overlapping sunflowers put two junctions on one
     cluster; there the closure law builds something other than the rounds, however it is ordered.

## 1. Is serial.py's present-state law a fair serial reading of the policy? (the owner's first point)

**What it does**, from reading `serial.py`:
- **Groups.** The groups are the complete-round policy's own: maximal valid sets plus uncovered candidate pairs. They are computed
  among all junctions that still hold loose distinctions.
- **Joins.** A join is any group not already joined by one junction.
- **Offshoots.** An offshoot is a one-parent move for a junction holding more loose distinctions than its groups use.
- **Fresh distinctions.** The new junction gets the fewest count max(d, 3 − p, 1). Here d is its number of groups in the present
  state (the new junction plus the live ones). The count is 0 when it takes every loose distinction and d = 0.
- **The implied test is the policy's.** For a connected presentation, a set of loose distinctions is a parity consequence only when
  it is empty or all of them, so "takes every loose bit" is the same test as GF(2) implication.

**It is fair as the present-state reading.** It changes exactly what the study says changes: d is read now, while the rounds read it
one round ahead, when all of the junction's partners exist. Two further differences are inherent to any serial law, and the note
does not hide them:
- groups can mix junctions of different ages;
- one schedule ("joins first") is only one of many.

**Replicated with the referee's own implementation** (`serial_mine.py`, on JOIN-GROWTH-R1's lean data structures, 40 orders each):
- **Two touching three-place knots:** 12 of 40 orders close (at 8 or 9 junctions) and 28 pass 400 junctions. The study has 4 of 20
  die and 16 pass 400.
- **A lone four-place knot** (which closes under rounds): 38 of 40 orders pass 400. The study has 19 of 20 keep growing.
- **So the order decides survival, as stated.** The referee's random sequence differs from the study's, so only the phenomenon is
  compared.

## 2. The Part C shares, by brute force on the cover (the owner's second point)

`referee_free.py partc` uses the referee's own enumeration, written for RING-PAIR-R1. It is a Redelmeier enumeration of connected
vertex sets in the lazily built cover, each cluster labelled by the parts it lies over. Orbits are counted as Σ over roots of
(clusters containing the root) / size, for sizes 1 to 13.

| Join | Totals equal the exact orbit count | Split equals the study's, every size | Single-part counts per size | Spanning two or more parts at size 10, 11, 12, 13 |
| --- | --- | --- | --- | --- |
| 5–7 by a distinction | yes, sizes 1 to 13 | **yes** | ring of five: 5; ring of seven: 7 | 0.9938, 0.9969, 0.9985, 0.9993 |
| 5–5 through a path of one knot | yes | **yes** | 5 and 5 | 0.9945, 0.9973, 0.9987, 0.9994 |

**Not checked:** the third join, the ring with a hanging pair. It needs CLUSTER-ALL's pendant chains, which the referee's cover code
does not draw.

**"Each part alone keeps exactly its stand-alone growth" holds.** A ring unrolls to an endless chain, which has one arc of each length
per starting knot.

## 3. Does every order reach the same structure? (the coordinator's question for John)

**Run.** `referee_free.py closure` builds every rooted cluster up to size 9 on two starts, then applies the closure law in 20 random
orders: make a cluster once all its parents exist, where a parent is the cluster less one point that leaves it connected. The two
starts are the ring 4,4,4,4,5 (492 rooted clusters) and the 5–7 join (16,124).

| Start | Every order made the same set | Every cluster made | Orbits by size 1 to 9 against the growth's junctions by round 0 to 8 |
| --- | --- | --- | --- |
| ring 4,4,4,4,5 | **yes** | yes | 6, 6, 7, 8, 9, 10, 11, 13, 15 against 5, 6, 7, …: equal from size 2. At size 1 the closure law also counts the spare distinction's pendant point, which is not a junction |
| 5–7 by a distinction | **yes** | yes | 12, 16, 26, 44, 76, 138, 261, 502, 975: **equal at every size** |

**The argument is correct as stated.** The law only ever adds, and an enabled move stays enabled, so it is a monotone closure: every
fair order reaches the same completed set, and a junction's size less one is its round.

**What it does and does not answer.** For "time doesn't have ticks", three qualifications:
- **Only a partial order is left.** A junction comes after its parents, and nothing else is ordered. Partial structures at a fixed
  number of moves differ between orders; only the completed structure, size by size, is order-free.
- **The law reads the map.** The unrolled candidate map is a global object computed from the whole start, and it says in advance
  which junctions will join which. So the closure law does not show that a law reading only what is built can do without the tick.
  Part A shows the opposite: the two such laws tried here depend on the order. What it shows is that the tick can be traded for
  knowledge of the map.
- **It equals the rounds only where the cluster rule does.** In CLUSTER-ALL's overlapping-sunflower falsifier, the referee's own
  growth makes two round-3 junctions on the same four start knots, each with three parents. The closure law, with one junction per
  cluster, makes one, in every order. There it is order-free and wrong.

## 4. Is Codex's serial law one of these, or a third thing? (the coordinator's question)

**A third thing.** Codex's law (the VARIABLE-OUTPUT-READER line) is a nondeterministic menu, not a growth policy:
- a new junction takes one loose distinction from each of one, two or three junctions, with a common neighbour for each pair and none
  for all three;
- it makes two or three fresh distinctions, freely chosen;
- its object is the set of all reachable arrangements.

It differs from both present-state laws here in two ways:
- **Any legal parent set is a move,** including a pair inside a valid triple. Here only the policy's groups are.
- **Its fresh counts are free (2 or 3) and never read demand.** The present-state laws set them from present demand and can give 1,
  or 0 when implied, which Codex's law forbids.

So neither family of outcomes contains the other. Codex's law has no order question: it describes every history at once, as a menu.

## 5. The ratios by size

**This follows from rank = size − 1 wherever the cluster rule holds,** which RING-PAIR-R1 confirmed against the referee's own growth.
The ratios are the golden ratio, 1.1347 and the two-ring 2.6075. The referee did not recompute 2.6075 separately.

## Corrections for the owner (listed, not folded in)

1. **"Every order reaches the same structure."** Qualify: the completed structure, size by size, for a law that reads the unrolled map
   in advance; it equals the rounds only where the cluster rule holds, and it fails at CLUSTER-ALL's overlapping sunflowers.
   **Narrowing; not a block.**
2. **The way it is said to John.** The rounds can be replaced by the partial order "after its parents" only by giving the law the
   map. The present-state laws here cannot replace them. **Narrowing (interpretation).**

## How the work was split

- **The referee:**
  - read `round_free.md`, `serial.py`, `job.py`, `parts.py` and `partc.py`;
  - wrote `referee_free.py` (partc, closure) and `serial_mine.py`, on its RING-PAIR-R1 cover code and JOIN-GROWTH-R1 lean engine.
- **No study code was run.**
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
