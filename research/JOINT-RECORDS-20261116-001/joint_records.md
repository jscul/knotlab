# Joint records where they can matter

Epic `JOINT-RECORDS-20261116-001`, 16 November 2026, by Claude; takes `CARRY-STRANDS-20261116-001#1`. Goal G3. Refereed:
`JOINT-RECORDS-R1`, confirmed, no Block and no fix needed ([report](referee-R1/report.md), commit `4dbbd04df`).
Pre-registration: [preregistration.md](preregistration.md), frozen in `8fa8b0697` before its one computation. Proof:
[Theorems 1–2](../../proofs/JOINT-RECORDS-20261116-001A/JOINT-RECORDS-20261116-001A-P001_record_law/proof.md).

## The answer: it reduces

Carrying joint records of up to w distinctions through not-all-equal satisfiability and counting, the place where a joint record
can hold more than separate ones, is dynamic programming over a tree decomposition. The least w that works is the treewidth + 1 of
the pattern, by construction (bucket elimination: Freuder; Dechter and Pearl; Samer and Szeider for counting). So no stage count on
small weaves can say anything a decomposition does not, and by the stop rule the study closes on the proof. The owner's braid,
carried to where joint records matter, is the classical separator table. It explains nothing beyond treewidth and the known
algebraic and matching escapes:

- affine records for parity;
- Pfaffians for counting on drawn knot patterns (`HANDLE-COUNT-20261106-001`);
- Petersen's theorem for deciding on a zero-pair weave, which is always satisfiable.

One tidy fact is the program's own. What a seam of s shared distinctions must report is a relation closed under flipping every
value. Every such relation occurs, 2^(2^(s−1)) of them (the referee checked this directly: every one is the projection of a
not-all-equal pattern, all 4 at s = 2 with three hidden distinctions and all 16 at s = 3 with two). Pairwise reports suffice for one or two shared distinctions. At three they
fail for exactly 4 of the 16 reports: not-all-equal and its three single-flip variants, which are knots. The first seam reports
that pairwise reports cannot capture are the knots themselves, the foundation's two/three boundary (computed; the general fact,
two-place shadows determine a Boolean relation exactly when it is majority-closed, is Baker–Pixley). At four shared distinctions,
50 and 226 of the 256 reports are fixed by two- and three-place shadows, and the hierarchy never stops.

## The connections

- **The Codex seam finding** (`GUARD-CHOICE-SEPARATION-20261115-001`, developed in `TWO-CHOICE-IMPLICATIONS-20261115-001`, whose
  exact two-port reports number 13 for positive implications) is the level below. Separate bit supports on two shared choices miss
  a contradiction. Its pair ({10} against {00, 01, 11}) is not closed under flipping, so it cannot arise in pure
  not-all-equal patterns, where one shared distinction reports only satisfiable or not.
- **The braid studies' finding**, that separate strand records lose what the joint record keeps, is the separator's joint
  projection against its shadows.
- **Forcing in atom patterns** needs only width-1 local consistency, which is why joint records added nothing in
  `CARRY-STRANDS-20261116-001`.

## Checks (frozen S1 to S4, all held)

S1: 2, 4, 16, 256 complement-closed relations at s = 1 … 4. S2: 2, 4, 12 determined by two-place shadows; the four failures are
knots. S3: the four-place not-all-equal is not fixed by its three-place shadows. S4: counts by a record-carrying run equal brute force
on the tetrahedron (6), octahedron (18) and icosahedron (72). [Census](../../proofs/JOINT-RECORDS-20261116-001A/JOINT-RECORDS-20261116-001A-P001_record_law/seam.json)

## Advisor

Consulted before the freeze. It agreed the reduction is an identity, corrected three statements, all adopted:

- width on weaves is O(√n), not Θ(√n);
- "least w" is about this law, and beating treewidth is excluded only under ETH;
- balanced combination needs about three times the width.

It added the Petersen escape, separated the Codex finding (one-place against two-place) from this one (two-place against three-place),
and proposed the seam table.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: joint records in not-all-equal patterns | **Status:** Successful (refereed, confirmed) | It reduces, as the stop rule asked to test; the seam hierarchy computed |
| Local direction: carrying records, the braid picture | Practically exhausted | Forcing: pebbling. Satisfiability and counting: treewidth. Escapes: known algebra and matchings |
| Broader exploration: parallel and record-based methods for knot laws | Known alternatives | Width, Pfaffians, Gaussian elimination, Newton/Strahler cover what this line found |
| Long-term goal: G3 Hardness at three places | No demonstrated advance | A restatement in the program's words, plus the seam census |

**Next step:** Research directions. No next action selected in this line.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Why layered random circuits need about d^0.4 phases | 2/3, explains how order built into a meeting pattern forces nesting | 3/3 | Solve the rank-distribution recursion → it matches within one, or fails | Alternative · deferred |
| 2 | Not-all-equal propagation phases on the program's own weaves and three-regular contradictions | 2/3 | 3/3 | Count phases from held pairs over three sizes → a clear trend | Alternative · deferred |

**Corrections:** none.

**Goals:** G3 checkpoint (no demonstrated advance); no goal changed.

**Assumptions:** none new; A87's challenge (measure a record by its allowed joint states) is answered here. Measured that way, the
law is the width method.

**Basket:** read; nothing in it is this question.

## Final report as sent

Posted to the owner's project thread on 2026-11-16 at about 23:03 UTC:

**Result:** joint records reduce to known mathematics, as expected, so I closed the study on a proof. Carrying joint records of several distinctions through not-all-equal satisfiability and counting is dynamic programming over a tree decomposition. The fewest records that work is the pattern's treewidth plus one. Your braid, taken to where joint records hold more than separate ones, is the classical separator table, and the known escapes (parity algebra, Pfaffians, Petersen on spheres) are already known.

One fact is the program's own. What a seam of shared distinctions must report is a flip-symmetric relation. Pairwise reports work for one or two shared distinctions. At three they fail for exactly 4 of the 16 possible reports, and those 4 are the knots: the two/three boundary appearing at the seam. The Codex "two shared choices" finding is the level below this.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: joint records in not-all-equal patterns | **Status:** Successful (referee pending) | It reduces; seam census computed |
| Local direction: the braid / record picture | Practically exhausted | Forcing → pebbling; satisfiability and counting → treewidth |
| Broader exploration | Known alternatives | Width, Pfaffians, Gaussian elimination, Newton/Strahler |
| G3 Hardness at three places | No demonstrated advance | A restatement plus the census |

**Next step:** no next action in this line. The best remaining options are why layered circuits need about d^0.4 phases (2/3 payoff, 3/3 concreteness), and not-all-equal phases on the program's own weaves (2/3, 3/3).

**Corrections:** none. **Goals:** G3 checkpoint. **Assumptions:** none new. [Decision note](https://github.com/jscul/knotlab/blob/main/research/JOINT-RECORDS-20261116-001/joint_records.md)
