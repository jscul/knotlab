# What does the growth build when joins come one at a time, without rounds? Pre-registration

Epic `ROUND-FREE-20261119-001` (`FRESH-COUNT-20261118-001#1`, serial growth testing A104; the coordinator's go-ahead, the
round-free test promised to the owner: "Time doesn't have ticks"), 2026-11-19. Written after a pilot of three orders per start
(disclosed, fitting) and the advisor's answer, before the 20-order runs. The canonical K1–K3 test is unchanged. No inside clock is
built: no law below reads a junction's rank or size.

## The question

Rounds (A104) are an outside tick. Without them:
1. Does adding one join at a time, in any order, build the same thing?
2. Do the ratios survive in a form that never mentions rounds?
3. Do parts of one start grow at different speeds, said as how much each part has grown?

## Two kinds of serial law

- **Naive laws (Part A).** These read only the current presentation. A move is one of the policy's groups among the junctions now
  holding loose distinctions (less sets already joined), or an offshoot for a loose distinction in no current group. A new
  junction's fresh count is the fewest rule, with its demand read from the current state. Two schedules: uniform over all moves,
  and joins first.
- **The closure law (Part B).** A junction for a cluster of the unrolled candidate map (`RING-PAIR-20261119-001`,
  `CLUSTER-ALL-20261119-001`) may be added once all its parents exist; nothing else is a move. It reads the map, not ranks or
  sizes.

## In standard terms

Asynchronous versus synchronous (step) semantics of a growth rule: whether every interleaving is a linear extension of one partial
order (confluence), and the graded poset that results.

## Prior work in the program

`python3 -B scripts/track.py objects "serial growth one join at a time order independence rounds" --until 2026-11-19 --exclude ROUND-FREE-20261119-001`
`python3 -B scripts/track.py objects "asynchronous joining rule trees order of growth" --until 2026-11-19 --exclude ROUND-FREE-20261119-001`

- `FRESH-COUNT-20261118-001` — the same growth under rounds; its direction #1 is this study.
- `CUBIC-FROM-A-KNOT-20261117-001`, cited there: "the asynchronous moves also admit a tree".
- `MEET-TWIST-20261118-001` — a relative: KF3 growth, where presentations grow by one law and the number of orders differs; a
  different law.
- `JOIN-GROWTH-20261118-001` — the starts' growth under rounds.
- `RING-PAIR-20261119-001` and `CLUSTER-ALL-20261119-001` — the cluster map the closure law reads.
- Codex's reader line (`VARIABLE-OUTPUT-READER-20261118-001`) works under its own serial two-or-three-fresh law. That is a
  different law, not tested here.

## Settled by construction or by a short argument

**Part B (the advisor's argument).**
- Building a cluster never disables another move, so the families reachable are exactly the parent-closed families. Every order
  is a linear extension of one partial order, and the limit is the whole cluster family.
- In every chain of parents below a cluster, each step removes one point, so every chain has length size − 1. So "rank" equals
  size − 1 in every order, though no law reads it.
- The counts by size are then the round counts wherever the cluster rule holds. That was tested in RING-PAIR and CLUSTER-ALL, not
  here.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| P1 | **Naive laws are order-dependent.** On each growing start (two touching three-place knots, two touching four-place knots, a chain of three three-place knots, the rings 4,4,4,4,5 and 5,5,5,5,5, a ring with a hanging pair, two joined rings of five), under each naive schedule, the 20 orders (to 400 junctions or closure) build at least two different structures: different counts by rank, or a different (parents, fresh) histogram | some start and schedule with all 20 orders alike |
| P2 | **Naive laws miss the rounds.** No order of either schedule reproduces the rounds' counts of ranks 0 to 3 on any growing start | one order does |
| P3 | **Order decides survival.** Under the uniform schedule, the two touching three-place knots (which grow forever under rounds) close in at least one of the 20 orders and grow past 400 junctions in at least one other | either fails |
| P4 | **Part shares by size (Part C, computed from the cluster map).** Seen before the freeze (fitting): in the bare ring with a hanging pair and in two joined rings of five, each part alone keeps a fixed small number of clusters per size (each ring 5 per size), and nearly all clusters span both parts. Frozen for three joins not yet computed: rings of five and seven by a shared distinction, two rings of five through a path of one knot, and the ring 4,4,4,4,5 with a hanging pair (surplus 2 and 1, golden ratio). In each, every part alone keeps a number of clusters per size that does not grow exponentially, and the share spanning two or more parts exceeds 0.9 from size 10 | any fails |

The lone four-place knot is run as a closing control, with no prediction.

## Runs and stop rule

`job.py` through the shared runner (328 cases); `merge.py` scores; Part C by `parts.py`. Minutes. Stop at the read-out.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze.
- **The closure law.** It gave the law and the argument that it is order-independent, never stalls and has the round's result.
- **Why naive laws depend on order.** It named three readings of the current state that make them so: the fewest count fixed at
  creation, offshoots enabled by absence, and groups among mixed-size live junctions.
- **An impossibility template.** No bounded-radius law that commits at creation can match the rounds in every order. It needs a
  concrete witness pair, which is not produced here.
- **The wording of size.** Size counts what a junction spans, not when it is made.
- **Speeds.** It advised freezing shares by size and not a random-order point prediction (Pólya-urn behaviour).
- **Not run.** Its three-cause repair test (P3 there) is not run here and is recorded as a direction.
