# Referee report DEAD-CAP-001-R1 (proof read line by line; own map, radius, growth and recurrences)

**Verdict: confirmed. Lemmas 1 and 2 and Theorems 3 and 4 are correct, and "classified" is earned for the whole class within five
places. No Block.**
- **D4's failure is the estimator's,** now demonstrated, not only plausible.
- **"At least 11 knots"** is argued in the proof only for the smallest skeleton. The referee supplies the general step. **Not a
  block.**
- **One correction to the referee's own earlier remark,** Not a block.

## The points asked

- **Lemma 1's profile bound with dead knots: correct.** Not a block.
  - **The count.** p_k = sh_k + open_k ≥ deg_k + d_k + (open_k − d_k), and d_k = Σ_{B ∋ k} |B| − r_k. A block through k is
    N(w) ∩ live for a neighbour w of k, live or dead, so deg_k ≥ r_k. Dead neighbours do give blocks, and they count among k's
    neighbours.
  - **Groups are pairs.** Under (S4) any valid set of three or more contains a valid triple, by the argument given. So (S3) leaves
    only pairs.
  - **Checked** with the referee's own blocks on 61,694 live knots, in the study's 2,754 regenerated random and skeleton starts and
    the census's 11,510 in-class starts with a dead knot:
    - every profile is within the bound and in Lemma 1's list;
    - every block has at most five points;
    - no two blocks share two points.
- **Theorem 3's pointing with pendant points marked: correct.** Not a block.
  - **The branch equation.** Each other point q of a block is either left out, or taken with its pendant structure. The factors are
    1 + z per spare, 1/(1 − z) for a one-ray pendant and 1 + z/(1 − z)² for a two-ray pendant, each with connected sets in q's other
    branches.
  - **The marked factor e_p⁺.** p itself (e_p), or a forced point in one pendant: z/(1 + z) times the spare's factor, z/(1 − z)²,
    z(1 + z)/(1 − z)³.
  - **The orbit count.** Every point of a cluster belongs to exactly one knot's structure, and a cluster through a pendant point
    must pass through its knot. The deck group is free on points. So each (orbit, marked point) is counted once, and
    [z^{t+1}] Σ r_p / (t + 1) counts orbits.
  - **Checked against growth.** The referee's engine equals the study's exact counts on every round reached (10 to 12) for 60 starts
    with a piece of rank 2 or 3 (11 to 32 knots). The theta follows the series 11, 12, 20, …, 18,375 to round 13.
- **Theorem 4's rank-2 argument: correct.** Not a block.
  - **Strong connectivity.** The dependency of (p, B) on (q, B′), q ∈ B − p and B′ ∋ q with B′ ≠ B, is the non-backtracking walk on
    the incidence graph. On a connected 2-core of minimum degree 2 that is not a cycle, that walk is irreducible.
  - **The rest is harmless.** Hanging trees feed in one way only.
  - **Nonlinearity** comes from a 3-block of Γ-degree 3.
  - **So Drmota–Lalley–Woods applies.** The pendant factors are analytic on |z| < 1, which contains ρ. Pointing makes the orbit
    count ~ ρ^{−t} t^{−5/2}, as stated, and periodic cores are named.
  - **The referee's own radius** (its own system, Newton at fixed z, spectral-radius test) gives the theta 2.38297576779, against
    1/z = 2.38297576791 for 4z³ + 4z² = 1. On all 60 rank-2 and rank-3 starts it is within 10⁻⁴ of the study's estimate, which reads
    low by about 10⁻⁵, as `posthoc_rates.py` says.
- **D4, treated strictly. The failure was reported honestly, and its diagnosis is now demonstrated.** Not a block.
  - **Honest reporting.** D4 is reported as failed as scored, and the diagnosis is marked post hoc. "5 of 6" is the honest count.
  - **The diagnosis was not recorded.** The note quotes 1.3187 at 4,000 iterations and 1.32462 at 200,000. No artifact records the
    second run (`posthoc_rates.py` covers only rank ≥ 2), so in the study the diagnosis was plausible but undemonstrated.
  - **The referee's test.** It regenerated all 30 rank-1 exponential pieces with the study's own seeds. On each:

    | | Pieces |
    | --- | ---: |
    | The referee's radius of the branch system equals the root of W(1/x) = 1 (to 10⁻⁶) | **30 of 30** |
    | The study's estimator at 4,000 iterations reads below the root | 30 of 30 (1.318659 for 1.324718, 1.709476 for 1.711071, …) |
    | … at 40,000 iterations it moves up towards the root | every one tried (16; for example 1.324176, 1.710968) |
    | The referee's own growth has an exact minimal recurrence whose rate is the root | 16 of 16 where the rounds sufficed (orders 3 to 7) |

    The other 14 reach only 14 to 25 rounds within the referee's junction cap. Their last ratios approach the root from below.
  - **So the theorem's rate is right, and the estimator stops early.** It mistakes slow divergence beyond the pole, a linear
    system's iteration crawling past the singularity, for a finite solution. The referee's own first radius had a similar fault, an
    absolute residual test near the pole, which it corrected before the final run.
  - **"D2's exact counts carry the denominator 1 − W"** is the theorem's statement, not something D2 measured. D2 compared at most
    20 rounds. The referee's recurrences supply the measurement on the 16 pieces.
- **"Two or more cycles need a dead knot and at least 11 knots": the dead knot is proved, the 11 only for the smallest skeleton.**
  - **The dead knot.** With every knot live, CAP-CHAINS and RING-CORES leave only paths, stars and rings, so every piece has rank at
    most 1. The proof's own route ("a 3-block of degree 3, and so a dead knot") skips that step.
  - **The proof covers the minimal skeleton.** It shows the theta skeleton (5 blocks, 6 points) needs 11 knots: each point has
    profile {2, 3} and two neighbours, so no point is a block's knot.
  - **The referee's general step.** Any rank ≥ 2 piece has two 3-blocks A = N(w_A) and B = N(w_B) of Γ-degree 3.
    - Their six points are distinct and have degree 2. w_A and w_B have three or more live neighbours, so they are not among them.
    - Each point's 2-block knot u has exactly two live neighbours, so it is not w_A or w_B.
    - u can be one of the six points only as a mutual pair across A and B, which forces w_A and w_B live.
      - Two mutual pairs make a cycle of three blocks (w_A, y₁, y₂ through N(x₁), B, N(x₂)), which is outside the class.
      - One mutual pair leaves a dead 2-block knot with two places. A point of profile {2, 3} cannot touch twice, so that knot
        needs another dead knot.
    - Every other u serves at most two of the six points.

    So there are at least 6 + 2 + 3 = 11 knots, and longer paths only add points. With this step folded in, the claim is proved;
    without it, it was proved for the smallest skeleton and observed for the rest. **Not a block.**
- **"Classified" is earned for the whole class, not only the sampled starts.**
  - **The classification is proved for every in-class start within five places.**
    - Rank 0 is polynomial or closes, by RELAY-IDENT.
    - Rank 1 is rational, constant if bare and exponential otherwise.
    - Rank ≥ 2 is exponential at an algebraic rate.
  - **The counts are proved exact** (Theorem 3).
  - **What stays open or is not independent:**
    - The rank ≥ 2 rates are the singularity of each system, computable but not given in closed form.
    - The ceiling 2.3830 is a conjecture, stated as one.
    - D3's agreement with `dims.predict` is not independent: it is the same structural reading, as in RING-CORES' K6.
- **The referee's earlier 1.2288 against the theta's 2.3830.**
  - **That figure was from the touch census** (at most five knots), and every start that reached it is outside the class (S3).
  - **The census holds no exponential in-class start** with a dead knot: all its 10,549 in-class dead-knot starts are trees.
  - **Rank ≥ 2 needs 11 knots,** so that test could not contain the theta. Rank-1 pieces with dead knots already reach 1.7111 (D4),
    above φ.
  - **So the referee's RING-CORES-R1 remark was uninformative.** "The wider claim is not contradicted where tested" was true of its
    test but said nothing about dead knots beyond five knots. The RING-CORES fold's Narrowing ("nothing within five places" was
    false) is right.

## Points for the owner (listed, not folded in)

1. **Record D4's diagnosis as an artifact.** The 200,000-iteration value quoted in the note has no file. The referee's runs
   (`referee_dead.json`) supply it now. **Not a block.**
2. **Corollary 5 and the note: the 11-knot step.** "Nothing of rank 2 is smaller" is argued only for the 5-block skeleton; add the
   general step above. **Not a block.**
3. **The referee's own correction.** RING-CORES-R1 said the golden-ratio ceiling's wider reading was "not contradicted where
   tested". Its test was the census, which cannot contain the dead-knot eddies that exceed φ. It should have said the test was
   uninformative beyond five knots. **Not a block** (the fold already narrowed the claim).

## How the work was split

- **The referee:**
  - read `dead_cap.md`, `proof.md` line by line, `deadlib.py`, `job.py`, `merge.py`, `posthoc_rates.py` and their outputs;
  - wrote `job_dead.py`, with its own map and blocks, its own branch-system radius and the profile checks. It uses its FIRST-KNOT-R1
    engine with the program's rule (CAP-CHAINS-R1's structural-implied variant) and BREAK-EDDIES-R1's exact recurrences.
- **Run only to regenerate the study's starts:** the study's samplers (`sample_rand` and `sample_skel`, same seeds).
- **Run as the object under test, labelled:** its `rate_of`, `branch_rate` (at 4,000 and 40,000 iterations) and `exact_counts`.
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap (peak 2.3 GB). A session drop at 17:32 UTC killed the first
  runner after 4 of 15 cases. Those cases were rerun with the corrected radius (`runs/referee-dead3`).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
