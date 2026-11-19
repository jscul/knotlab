# Prove that a round's junctions are the clusters of the unrolled candidate map

Epic `RING-IDENT-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `RING-PAIR-20261119-001#2`. Goal
G17. **Refereed:** report [R1](referee-R1/report.md), the theorem confirmed line by line, no Block; three presentation points
folded into the proof on 19 November (see Referee).

**Record.**
- **The proof:** [proof.md](../../proofs/RING-IDENT-20261119-001A/RING-IDENT-20261119-001A-P001_identification/proof.md), ticket A.
- **Its machine check:** [machine_check.py](../../proofs/RING-IDENT-20261119-001A/RING-IDENT-20261119-001A-P001_identification/machine_check.py),
  with output in
  [machine_check.json](../../proofs/RING-IDENT-20261119-001A/RING-IDENT-20261119-001A-P001_identification/machine_check.json). It is
  a separate algorithm in the same task, and it runs in seconds.
- **The advisor** checked the statement and every step before the freeze ([question](advisor/question_1.md),
  [answer](advisor/answer_1_fable.md)).

## The answer

**In the owner's terms.**
- **The rule is now a theorem.** Draw which knots can join which, open every cycle of that map out into its endless branching form,
  and count its clusters. The junctions the cheapest growth makes in round t are then exactly the clusters of t + 1 points, each
  counted once however often it repeats.
  - It is proved for every round, not only checked.
  - A junction's parents are the points the cluster can lose and still hang together.
  - A junction's open distinctions are the points just outside the cluster.
- **It needs one condition RING-PAIR did not state: the knot graph must contain a cycle.**
  - When the knot graph is a tree, the map of joins falls into finite pieces. A piece that finishes while others still have loose
    distinctions is not implied, so the floor gives it one fresh distinction, a relay, which starts a chain.
  - Two stars joined at their centres, inside RING-PAIR's stated scope, grows 6, 6, 2, 2, 4, 6, 8, … where the rule says 6, 6, 2, 0.
  - The machine check and the advisor found this independently. The correction to RING-PAIR is a Narrowing, logged; every start
    RING-PAIR grew has a cycle.
- **Why it works.** Everything rests on one fact about the unrolled map. In scope, no loop of the map of joins passes through fewer
  than four of its knots:
  - two blocks never share two knots (no two knots have two common neighbours);
  - three never close up (round 1 has no group of three).
  So a cluster and any shifted copy of it can only sit together inside a cluster at least four points larger. That one inequality
  makes:
  - every group of the growth the set of a cluster's removable points;
  - every pair of candidates belong to exactly one cluster;
  - every junction use exactly its open distinctions.
- **Where the wider rule needs more.** CLUSTER-ALL's rule is exact on a wider class. Each extension breaks a named step:
  - relays break the counting step, and are the condition above;
  - the floor's endless chains break the same step;
  - first-round groups of three break the girth step: a loop of three blocks gives only three new points. Both of CLUSTER-ALL's known
    breaks sit there.

## Referee

Report [R1](referee-R1/report.md), 19 November 2026, by the coordinator's background referee thread, read line by line, with its own
growth, lazy cover and cluster enumeration. No study code was run.
- **Confirmed.** The theorem, its lemmas and the induction. Its own check: all 45 in-scope starts with a cycle at 3 to 7 knots agree,
  81 of 81 sampled at eight knots, girth at least 8 on all 332 starts with (S3) and (S4). Two stars joined at their centres regrown
  (6, 6, 2, 2, 4, 6, 8, 10, …), so (S5) is needed and RING-PAIR's Narrowing is confirmed.
- **Folded in (presentation, not gaps).** The implied rule stated as the code has it (exactly d, no floor), with both readings equal
  under (S5); round 1's fresh counts and liveness written out in the base; the t = 1 surplus case in Lemma 4(iii) step 2 spelled out.

## Known results, and what this adds

- **Known, cited once.**
  - Hyperbolic automorphisms of trees (Serre, *Trees*).
  - Block graphs (Harary).
  - Site animals on Bethe lattices and Husimi trees (Fisher and Essam 1961; Harary and Uhlenbeck 1953).
  - Reverse search over connected induced subgraphs (Avis and Fukuda 1996).
  - Halved graphs.
- **What this adds.** For the cheapest parity growth, the exact identification of every round with the clusters of a tree-like
  cover. It holds with parents and open distinctions, under a stated scope whose last condition is shown necessary.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: prove the identification | **Status:** Successful (proved, with one added condition shown necessary) | Every round, parents and open distinctions, from one union lemma on the cover |
| Local direction: an exact model of the cheapest parity growth | Continue | The model is now a theorem on its class; the wider class's failing steps are named |
| Broader exploration: what the cheapest growth builds | Known alternatives | In scope, clusters of a tree-like cover: rational with one cycle, algebraic with more |
| Long-term goal: G17 | Capability gained | The growth of every start with a cycle in scope follows from its map of joins, provably |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Relays and trees: extend the theorem to knot graphs that are trees, by a pendant chain on each finished piece (CLUSTER-ALL's relay) | 2/3 — completes RING-PAIR's scope | 3/3 — the failing step and its fix are named | state the modified count at finished pieces, prove it with the same lemmas → stop at a proof, or at a tree where the relay chain is not a fixed pendant | Alternative · proposed |
| 2 | The floor's endless chains (dropping S1 or S2) as pendant chains of the cover, proved the same way | 3/3 — the census's typical two dimensions would become a theorem | 2/3 — the offshoots hang from clusters, not points, so a new complex is needed | define the chain points and check the union lemma for them → stop at a proof or the first non-invariant step | Alternative · proposed |
| 3 | First-round groups of three: a complex in which the triple is its own block, with its own girth | 2/3 — the home of CLUSTER-ALL's two breaks | 1/3 — the advisor says the tree-of-blocks cover is the wrong object | find the complex whose clusters are the junctions on the sunflower starts → stop at one, or a proof none of this kind works | Alternative · deferred |

## Final report as sent (2026-11-19 13:47 UTC)

**Outcome:** The cluster rule is now a theorem, under one condition RING-PAIR hadn't stated. The junctions the cheapest growth makes in round t are exactly the clusters of t + 1 points of the unrolled map of joins, each counted once. A junction's parents are the points its cluster can lose and still hang together, and its open distinctions are the points just outside. It's proved for every round, provided the knot graph contains a cycle. Closed, referee pending.

- **Why it works.** In scope, no loop of the map of joins passes through fewer than four knots. Two blocks never share two knots, and three never close up. So a cluster and any shifted copy of it can only sit together inside a cluster at least four points larger. That one inequality forces everything else. Every group of the growth is the set of a cluster's removable points, every candidate pair belongs to exactly one cluster, and every junction uses exactly its open distinctions.
- **The condition is necessary.** If the knot graph is a tree, the map falls into finite pieces. A piece that finishes while others still have loose distinctions gets a relay. Two stars joined at their centres is inside RING-PAIR's stated scope, and it grows 6, 6, 2, 2, 4, 6, 8, … where the rule says 6, 6, 2, 0. My machine check and the advisor found this independently. On 3 to 7 knots, all 45 in-scope starts with a cycle agree with the theorem, and 21 of the 43 trees don't.
- **Where CLUSTER-ALL's wider rule would need more.**
  - Relays and the floor's endless chains break the counting step.
  - First-round groups of three break the girth step: a loop of three blocks gives only three new points. That's where both of CLUSTER-ALL's known breaks live.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: prove the identification | **Status:** Successful (proved, with one added condition shown necessary) | Every round, with parents and open distinctions, from one union lemma on the cover |
| Local direction: an exact model of the cheapest parity growth | Continue | The model is a theorem on its class; the wider class's failing steps are named |
| Broader exploration: what the cheapest growth builds | Known alternatives | In scope, clusters of a tree-like cover: rational with one cycle, algebraic with more |
| Long-term goal: G17 | Capability gained | Growth with a cycle in scope follows provably from the map of joins |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Trees: extend the theorem with a relay chain on each finished piece | 2/3 | 3/3 | state the modified count at finished pieces and prove it with the same lemmas → stop at a proof or a tree where the relay isn't a fixed pendant | Alternative · proposed |
| 2 | The floor's endless chains as pendant chains of the cover | 3/3 — the census's typical two dimensions as a theorem | 2/3 | define the chain points, check the union lemma for them → stop at a proof or the first non-invariant step | Alternative · proposed |
| 3 | First-round groups of three: a different complex | 2/3 | 1/3 | find a complex whose clusters are the junctions on the sunflower starts → stop at one or a proof none of this kind works | Alternative · deferred |

**Corrections:**
- **RING-PAIR, Narrowing:** its rule needs a cycle in the knot graph, per the counterexample above; every start it grew has one.
- **JUNCTION-KINDS and NATIVE-SPINE, not blocks (from their referees, both confirmed):**
  - "no exact transfer along parents" now carries its qualifier;
  - "the spine is not in the growth" is now "no rule tried picks it, and nothing forces it";
  - the depth bias is stated as proved.

All are logged in docs/CORRECTIONS.md and knotlab's HISTORY.md (c40dde200), and the line summary is updated.

**Goals:** G17 checkpoint (capability gained). **Assumptions:** none changed; A104 and A107 bound the scope. **Basket:** `RING-PAIR-20261119-001#2` taken. **Advisor:** Fable 5.2, before the freeze, staying within its text. It checked every step, found the tree gap independently and proposed the cycle condition as the fix. It also tightened the union lemma's wording, and located the wider class's failing steps (relays and the floor at the counting step, groups of three at the girth step).

**Referee hand-off.** The proof is `proofs/RING-IDENT-20261119-001A/RING-IDENT-20261119-001A-P001_identification/proof.md`, and the decision note is `research/RING-IDENT-20261119-001/ring_ident.md`. Please check:
- Lemma 2 (the union lemma) and Lemma 4(iii)'s size count;
- that (S3) and (S4) give girth at least 8;
- `machine_check.py`'s cluster enumeration, with each rooted cluster weighted 1/size.
