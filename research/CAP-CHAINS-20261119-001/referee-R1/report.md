# Referee report CAP-CHAINS-001-R1 (proof read line by line; own constructions, enumeration, reading and growth)

**Verdict: confirmed. Lemmas 1 and 2, Theorem 1, Corollary 2 and Theorem 3 are correct. No Block. Two wording points, both Not a
block.**
- **Lemma 1 is correct, including the six-cycle step.**
  - **Triangle and four-cycle.** As written, by (S3) and (S4).
  - **A six-cycle is induced.** With no three- or four-cycle, a chord of a six-cycle would make a triangle (a chord two apart) or two
    four-cycles (three apart).
  - **a, b, c are pairwise candidates** through x, y, z.
  - **No common neighbour.** A common neighbour w of all three would make a–x–b–w a four-cycle, since x is not adjacent to c in an
    induced cycle. So {a, b, c} is valid, against (S3).
  - **The count.** The partners of k are the knots two apart from it, distinct over w by (S4) and none adjacent to k (no
    triangle). Every candidate pair is a group, so d_k = Σ (deg_w − 1).
- **Lemma 2 is correct, and so is the step asked about** ("no knot can touch three knots that themselves touch others").
  - **The count.** Each non-leaf neighbour w of k adds deg_w − 1 ≥ 1 to d_k, so d_k ≥ m_k, and deg_k ≥ m_k. By (S0) and
    sh_k ≥ deg_k, p_k ≥ deg_k + d_k ≥ 2m_k. With p_k ≤ 5 this gives m_k ≤ 2.
  - **The shape.** Removing the leaves keeps the knot graph connected (three or more knots), so the core has degree at most two:
    a path or a cycle.
- **Theorem 1 is correct, including step 5.** A ray needs d_k ≤ 1 and open_k ≤ 2 (the two cases listed).
  - **A cycle core.** Every knot has d ≥ 2, so there are no rays. Every piece holds a cycle of blocks: an even core has length ≥ 8,
    so each parity class closes up. So no piece is finite and no relay is added.
  - **A path core: step 5.**
    - An inner core knot has two non-leaf neighbours, so d ≥ 2.
    - A leaf on an inner knot, or on an end with two or more leaves, sees a neighbour of degree ≥ 3, so d ≥ 2.
    - At the end c₁ the only knots with d = 1 are its single leaf (when it has exactly one) and c₁ itself (when deg c₂ = 2). These
      two are adjacent, so they lie in opposite parity classes.
    - Each parity class therefore gets at most one ray from each end. On the path of four, for example, each class gets two.
  - **The pieces of a tree** are its parity classes, and a relay goes only on a finite piece, which has no ray. Hence at most two
    rays per piece.
- **Theorem 3's constructions and values are correct.** The referee built S_R and T_h from the proof's text and recomputed every
  value:
  - **S_R:** branch d = 3, p = 6; connector d = 4, p = 6; the arm's middle d = 2, p = 4; leaf d = 1, open 2, one ray.
    The knot counts are 4R − 5: 7, 11, 15 and 19.
  - **T_h:** member d = 2 + 1 = 3, p = 5, open 3, no pendant point; connector d = 0 (the hub is dead), open 1, a piece of its own
    with two rays; end d = 1, one ray. The knot counts are 10 and 31, with 1 and 4 dead hubs.
- **The C1 enumeration is complete,** for the reason the hand-off gives, and the referee's own enumeration agrees.
  - **Why it is complete.** Both conditions pass to subgraphs: cycles can only disappear, and deg_k + Σ(deg_w − 1) can only fall.
    Every connected graph has a knot whose removal keeps it connected, a leaf of a spanning tree. So adding one knot at a time,
    joined to any set of old knots, reaches every graph.
  - **The referee's enumeration** joins the new knot to any set of old knots, with no limit of five. It agrees with the networkx
    atlas to 7 knots.
  - **The count.** It gives 86 graphs to 12 knots, the study's number, and 149 to 14 knots. Every core is a path (107), a cycle (36)
    or a star or less (6).

## The machine checks, re-run with the referee's own code (`job_cap.py` under `scripts/longrun.py`)

| # | Referee's run | Result |
| --- | --- | --- |
| C1 | own enumeration, every subset joined; atlas to 7 | 86 graphs to 12 (as the study), 149 to 14; every core a path, cycle or star |
| C2 / Theorem 1 | every assignment open_k ∈ [max(1, d_k), 5 − deg_k], read by the referee's own classification and X⁺, relay counted | 200,597 to 12 knots (as the study), **433,939 to 13**: every one in the class, none with more than two rays in a piece |
| C3 | every simple all-live start, sizes [max(3, deg_k + 1), 5], the referee's reader | 2–9 knots exactly the study's: 150,355 stall; 1,864 / 9,259 / 1,098 one-dim / two-dim / exponential; **10 knots too (472,392)**: none three or more |
| C4 | atlas graphs of 6–7 knots, girth ≥ 5 with a six-cycle, every all-live size within five, no cap filter | 3,159 starts: 1,377 out by (S3), 1,782 stall, none in the class |
| C5 | the census's 12,473 in-class arrangements | 963 with no dead knot, none with more than two rays in a piece; **with dead knots too (11,510), none either**, so "no in-class census start carries three chains" holds exhaustively |
| C6 | S_3–S_6, T_1, T_2 built by the referee | all in the class; most rays in a piece 3, 4, 5, 6 and 3, 6; read as that many dimensions; the referee's growth equals its relayed model per round to round 8 |
| C7 | the referee's engine, exact minimal recurrence (Berlekamp–Massey over Q) | (x − 1)^R exactly: per-round counts of degree R − 1 for S_3, S_4, S_5 (24 rounds), T_1 (24), T_2 (18); S_6 by differences, below |
| C8 | the ring of seven with one leaf, at bare sizes (largest 5) | in the class, read exponential, equal to the relayed model to round 8; the counts obey **a_t = a_(t−7) + a_(t−8)** exactly from round 8 to round 60 |

**S_6:** to round 20 its sixth differences are 0 over the last six values and its fifth differences are 1 over the last seven, so its per-round counts have degree 5 (19, 27, 40, 60, 91, …, 29,496 at round 20). The rounds were too few for the exact recurrence to certify order 6 with the referee's margin, so this one is the study's own criterion. A 28-round run was stopped at the referee's memory limit.

- **The regrowth.** The spider S_3 is three-dimensional (7, 9, 10, 14, 20, 27, …). The 19-knot S_6 is six-dimensional. The dead-hub
  trees T_1 and T_2 grow in three and six dimensions within five places. The bare rings of 5, 7 and 8 are one-dimensional, with
  constant counts.
- **The long runs** used the referee's engine with the implied test read structurally (a junction is implied exactly when it takes
  every loose distinction; PARENT-RULE Lemma 2) to save memory. It equals the full GF(2) engine wherever both ran, to round 6 on
  every family.

## Points for the owner (listed, not folded in)

1. **"The ring of seven with one knot hung on it grows … at about 9% a round"** understates it slightly. Its counts satisfy
   a_t = a_(t−7) + a_(t−8) exactly to round 60 (computed), so the rate is the real root of x⁸ = x + 1, 1.0970: about 10% a round.
   The quoted counts are the referee's too, but "1,096 at round 52" is at round 53 if round 0 is the start (2,086 is at round 60).
   **Not a block.**
2. **C4's count of 2,187 starts** comes after a cap filter (deg_k + d_k ≤ 5 on the graph). The filter is harmless, since an in-class
   all-live start within five places passes it by Lemmas 1 and 2. Without it the referee finds 3,159 starts, with the same 1,377
   out by (S3) and none in the class. **Not a block.**

## How the work was split

- **The referee:**
  - read `cap_chains.md`, `proof.md` line by line, and `machine_check.py` with its output;
  - wrote `job_cap.py`. It uses its own constructions, graph enumeration, WEIGHTINGS-R1 bare sizes, DOUBLE-IDENT-R1 classification
    and X⁺ reading, RELAY-IDENT-R1 growth keys and relayed model, its FIRST-KNOT-R1 engine with the program's rule (and a
    structural-implied variant for long runs), and BREAK-EDDIES-R1's exact recurrence.
- **Read as data:** the touch census's arrangements in `runs/touch-census`.
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap. The first family run reached the 3 GB case cap on the long
  growth with GF(2) elimination and was redone with the structural test.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
