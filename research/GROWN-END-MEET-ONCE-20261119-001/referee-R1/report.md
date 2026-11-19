# Referee report GROWN-END-MEET-ONCE-001-R1 (Codex; the failures regrown with own code, the census rebuilt to 11 junctions)

**Verdict: confirmed. The meet-once failure is real, and both of Codex's census failures reproduce exactly. No Block. Beyond
GROWN-END-SWAP, this is a further Narrowing of EXTEND-ROUND's direction #1 and HUNT-SHORTEN's reading: meeting once does not
rescue the pair table. One point for the owner, Not a block.**

## The points asked

1. **The smallest reached failure, 12 junctions and 23 distinctions: confirmed.** The referee regrew the seven-junction history
   from its start with its own engine, and the stages equal the literal ones.
   - **The swap 0 ↔ 1** keeps all 253 current pair readings and fixes every distinction of every live junction.
   - **The entries.** K(0, 2) and K(1, 2) are 4 and 4 at round 1, and 3 and 4 at round 2: distances 3, 3 and then 2, 3, as the
     table says.
   - **Under the program's reading R** (live junctions to live junctions, as in HUNT-SHORTEN-R1), all 48 reading-keeping symmetries
     that break the equations fail at round 1.
   - **Under the study's pointwise marking**, the stage has 8 pair-table maps, and exactly 4 extend.
2. **The six-junction history: confirmed.** Regrown from its start, it passes at age 1 (12 junctions, 26 distinctions: 48 such
   symmetries, none failing). It fails at age 2 (19 junctions, 37 distinctions: 48 of 48 fail).
3. **The three joint-minimum witnesses: confirmed.** They come from 7, 8 and 8 starting junctions. Each regrows to its literal
   stage of 12 junctions and 23 distinctions and fails there:
   - under reading R, 48, 8 and 8 symmetries fail;
   - pointwise, 4 of 8 maps fail in each.
4. **The nine-junction construction (every starting junction of three or four places): confirmed.** It fails at 13 junctions and
   24 distinctions, 16 of 16 such symmetries under reading R.
   - The subdivision argument for every larger count was read. Added sites are closed and lie on A's side, so the live groups,
     the two routes at age 1 and the single route at age 2 are unchanged. It is sound.
5. **The least extra reading on the meet-twice example: confirmed.**
   - Of the 48 pointwise matchings, 16 extend.
   - The flip-together bit and the existence of a bond through {x, y, 15} each keep exactly those 16.
   - The flip bit is true for 0, 1 and false for 2, 1. 21 bonds hold {0, 1}, and one holds {2, 1}.
   - The least bond through {0, 1, 15} has 4 distinctions, and none holds {2, 1, 15}.
6. **Codex's two census failures, widths 14 and 15, regrown from their starts: confirmed exactly.**
   - Each age-2 stage (16 junctions) and its successor equal the literal ones as incidence structures.
   - The literal permutation is a table isometry. It keeps reading R, fixes every live distinction, and does not carry the
     equations.
   - **The successor entries on the named old pair and its image** are 3 and 4 at width 14, and 6 and 5 at width 15. These are
     the study's values, distances 2 and 3, and 5 and 4. Both names are old, so no fresh naming can repair them.
   - **The referee's coset search** finds 24 and 16 failing coset representatives. The census counts 3 and 1 failing generators.
     These are different units of the same failing groups.
7. **The census by starting width.**
   - **Start counts.** The referee's own generator gives the same admissible counts as Codex at widths 3 to 8 and 11 to 14: 1, 1,
     2, 4, 6 and 13, then 218, 647, 2,019 and 6,720.
   - **Failures.** It grew those 9,631 starts through every stage of at most 11 junctions, at any age. Among the reading-keeping
     symmetries that break the equations it finds no failure: 52,259 symmetries in 4,675 open stages.
   - **Widths 9 and 10 are still running** (stress test pending; 33 and 81 starts by Codex's count). The referee will fold them in
     when they finish.
   - **The bound.** This agrees with "no counterexample at 11 or fewer current junctions", but only within widths 14 and below.
     The study's claim has no width cap (see point 1 below).
8. **A single starting junction: consistent, but uninformative here.** Starts of 3 to 9 places (study 3 to 7), grown while stages
   have at most 14 junctions, reach only one or two open stages each. At each one the identity is the only pointwise map, so the
   proof carries this claim.

## Narrowing or Block for EXTEND-ROUND and HUNT-SHORTEN, beyond GROWN-END-SWAP

**A Narrowing, not a Block.**
- **What GROWN-END-SWAP left.** It refuted pair-table sufficiency on a reached stage whose junctions meet twice. That left meeting
  once as the obvious repair.
- **Why the repair fails.** This study removes it. A pointwise-fixed growing end is stronger than reading R, and every two
  junctions meet once, yet the pair table already fails at 12 junctions and 23 distinctions. Under reading R the failure reaches
  starts of every size from nine, with three or four places per starting junction.
- **What stands:**
  - EXTEND-ROUND's theorems: Claim B*, transport by the equation span, which carries every map that keeps the equations;
  - HUNT-SHORTEN's census statement, inside its bounds. The referee's census agrees with it to 11 junctions.
- **What must narrow.** Any rule that extends a matching from the pair table alone, with or without meeting once, holds only below
  the census bound. Otherwise it needs a further reading. GROWN-END-READING's triples are the candidate, and its 239-junction
  stage shows that triples need not carry the equations.

## Points for the owner (listed, not folded in)

1. **"No counterexample at 11 or fewer current junctions, with no initial arity or width cap."** The referee checked this only
   within starting widths 3 to 14. The study reaches the uncapped statement through its predecessor sweep, which the referee did
   not rebuild. **Not a block.**

## How the work was split

- **The referee:**
  - read `decision.md`, `proof.md`, `structure.md` and `census.md`, with the artifacts of the named histories and the census;
  - wrote `job_meet1.py`, built on its earlier engine, tables, coset search and stage test (HUNT-SHORTEN-R1, GROWN-END-SWAP-R1,
    CREATED-PAIR-R1).
- **Read as data:** Codex's starts, stages and permutations.
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap:
  - `runs/referee-meet1` (census);
  - `runs/referee-meet1-cw` (the census failures);
  - `runs/referee-meet1-x` (the headline entries);
  - `runs/referee-meet1-smoke` and `-smoke2` (the meet-twice readings and the histories).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
