# Referee report WALL-READ-001-R1 (proof read line by line; partnered starts grown on actual distinctions; Lemmas 2 and 3 tested)

**Verdict: confirmed. Theorem 1, Lemmas 2 and 3 and Corollary 4 are correct; `rosterlib` is the program's rule. No Block. One
part is a stress test pending (stopped at the owner's request).**

## The points asked

1. **Theorem 1: correct.**
   - **Round 1.** With pair blocks, every transversal of O_n (n ≥ 3) is a valid group. Every non-partner pair is covered, and each
     point is in 2^(n−1) transversals, its open count. So there are no offshoots and no stall, and N₁ = 2^n.
   - **The induction (F1)–(F4) holds:**
     - two valid transversals meet unless complementary;
     - the blocks B_v are transversals, distinct (some valid U holds v and ū) and of equal size, hence all maximal;
     - the pair coverage uses 2^(m_t − 2) ≥ m_t > m_(t−1) − 1.
   - **Fresh counts.** Fresh = demand = 2^(m_t − 1) − m_(t−1), since p ≥ 3 and no junction takes every loose distinction.
   - **(F4)** follows from 2^(m − 1) > 2m − 1 for m ≥ 4.
   - **The eight-place minimum is right.** A live knot lies in 2(n − 1) maximal blocks, each needing a different neighbour, plus
     2^(n−1) open distinctions: 8 at n = 3.
   - **Checked by the referee's engine**, on actual distinctions, from its own hub realization:

     | n | Built rounds: (parents, fresh) × count | Form (F1)–(F3) at every built stage | Next round's groups by the rule | Largest live places |
     | ---: | --- | --- | ---: | ---: |
     | 2 | (2, 2) × 4 in each of 10 rounds | yes | 4 | 4 |
     | 3 | (3, 5) × 8; (4, 12) × 10; (5, 2,043) × 24 | yes | 4,086 | 8 |
     | 4 | (4, 124) × 16 | yes | 248 | 14 |
     | 5 | (5, 32,763) × 32 | yes | 65,526 | 24 |

   - **Controls.** Open count 2^(n−1) − 1 stalls in round 1, and 2^(n−1) + 1 makes exactly 2n offshoots (n = 3, 4).
2. **Corollary 4's counting: correct.**
   - **The bound used.** The number of connected k-sets through a vertex of degree at most Δ is at most (eΔ)^(k−1). This is the
     classical bound.
   - **Why it applies.** A regular cover keeps the degree, every deck orbit meets the fibre over one of the b base members, so
     N_t ≤ b · (eΔ)^(s(t)). With log₂ N_t ≥ N_(t−1)/2 − 1 this forces s(t) ≥ c · N_(t−1).
   - **The scope line** (partnered and faster-than-exponential starts only) is right.
3. **Lemma 2's lone-point term: correct.**
   - **Why.** A maximal clique held by no block is a group unless it is a lone point. A 2-clique is a candidate pair, which is
     always held. A held maximal clique equals its block, and the injection of maximal cliques is the folklore one.
   - **Checked,** on 2,374 stages of about 1,000 of the referee's random starts within eight places (one past seven), rounds 0–6:
     with W = all live points and a random W of 12, the bound held on every stage; and 8,392 partnered sets of order ≥ 2 held too.
4. **Lemma 3's disjointness: correct.**
   - **Why.** A block holds at most one transversal of W. Q(T) ∩ W = T, since partners are not candidates. A point in
     Q(T) ∩ Q(T̄) would be a candidate of all of W, which is excluded.
   - **Checked** on 8,046 partnered sets with no outside common candidate: every construction held, including the count
     ≥ 2^(k−1) − |ℬ|.
5. **`rosterlib` is the program's rule: confirmed by reading.** Its candidates, valid maximal cliques, uncovered pairs, stall test,
   one offshoot per leftover distinction, blocks {children of v}, lookahead demand and max(d, 3 − p, 1) all match. Its implied
   clause applies when the round makes one junction holding every live point, each with open count 1. Under the structural test
   that is exactly when a junction takes every loose distinction.
6. **B2's post hoc double count: confirmed exactly by the referee's engine.**
   - **Round 7.** Start-03 has 386 junctions with open sum 993,164.
   - **Round 8** by the rule: 28,064 groups (largest 109; 28,008 with three or more parents), one offshoot, 28,065 junctions and a
     parent sum of 993,164, with no stall.
7. **Start-04's round 9: confirmed.** The rule's groups on its round-8 stage are 304,590 pairs (MERGE-BURST-R1).

## Stress test pending

- **What is missing.** Lemma 2 and 3 on the 16 explosive starts' stages, and one of the nine random cases (eight knots).
- **Why.** Both were stopped at the owner's request.
- **How to rerun.** `job_wr.py`, cases LEM-06 and LEM-09.

## How the work was split

- **The referee:**
  - read `proof.md`, `rosterlib.py`, `wall_read.md`, the post hoc scripts and the advisor's answer;
  - wrote `job_wr.py`, with its own engine, realization, partnered-set search and lemma checks.
- **`rosterlib` was read, not run.**
- **Where it ran.** Under `scripts/longrun.py`: `runs/referee-wr` and `runs/referee-wr-b2`.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
