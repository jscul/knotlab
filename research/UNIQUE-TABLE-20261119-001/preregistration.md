# Does the bond-distance table fix every census arrangement it has no symmetry for? Pre-registration

Epic `UNIQUE-TABLE-20261119-001` (`CENSUS-READ-20261118-001#1`, the coordinator's go-ahead; assumption A97, goal G1), 2026-11-19.
Code by the thread. Frozen before any population stage is run; the code was developed on FRESH-COUNT's mixed stages and three toy
starts only. The canonical K1–K3 test is unchanged.

## The question

`CENSUS-READ-20261118-001` found 522 census stages where no two junctions share two distinctions, every exchange of distinctions
that keeps the exact bond-distance table also keeps the set of junctions (all such exchanges enumerated), and yet the name-free
reader misread. Is the arrangement there the only legal arrangement with that table? If yes, the misreads are the reader's
weakness; if a second legal arrangement exists, it is either one with the same allowed states and other junctions, or one with
other allowed states and the same table. This is the sharpest form of the owner's premise now testable: "distances carry
everything but their own symmetries".

## In standard terms

G is a graph on the distinctions (its edges), with one vertex per junction and an outside vertex o ending the loose ones; the
junction stars span the cut space C; the table is T(e, f) = (smallest circuit of C containing e and f) − 1. A rival is another
graph H on the same labelled edges. Question: within a stated class of rivals, is G the only one with T(H) = T?

## Prior work in the program

`python3 -B scripts/track.py objects "table determines arrangement uniqueness up to symmetries second presentation same bond distance table" --until 2026-11-19 --exclude UNIQUE-TABLE-20261119-001`

- `CENSUS-READ-20261118-001`: the source of the population and of the symmetry test; same object, one step further.
- `NAE-GROWTH-20261119-001`: a relative (whether bond-distance tables say who joins whom under the not-all-equal law); not this
  population or law.
- `RING-READ-20261118-001`: the ring, read back exactly (3-connected; only the outside choice left, which the law decides).

`python3 -B scripts/track.py objects "Whitney 2-isomorphism twists same allowed states different junctions" --until 2026-11-19 --exclude UNIQUE-TABLE-20261119-001`

- `FIRST-KNOT-20261118-001`: a relative (the same relation grows differently by presentation: same states, other junctions).
- `MEET-GROW-20261118-001`: unrelated (KF3 growth of line presentations).
- `CENSUS-READ-20261118-001`: as above.

`python3 -B scripts/track.py objects "census stages read back from bond distances symmetry-free" --until 2026-11-19 --exclude UNIQUE-TABLE-20261119-001`

- `CENSUS-READ-20261118-001` and `RING-READ-20261118-001`: as above. `FRESH-COUNT-20261118-001`: the threshold reader and the mixed
  stages, used here only as a development set.

Also: A108 (the cheapest growth reads which junction holds which distinction, not only the allowed states), from the other study:
same allowed states with different junctions is a real difference for the law, and is reported as its own kind here.

## Prior work outside the program

Whitney's 2-isomorphism theorem (1933): graphs with the same cycle (equivalently cut) space on the same edges are related by twists
at 2-separations and by splitting and re-gluing blocks at a vertex. Shih's theorem (1982, as the advisor recalled; not checked
here) on codimension-one extensions of a graphic cut space, which is why the step "a larger code" below is bounded rather than
proved.

## The rival class (the bound)

A rival is an arrangement on the same labelled distinctions in which
- (B1) every distinction lies in one or two junctions, and every junction has at least three distinctions;
- (B2) any two junctions share at most one distinction;
- (B3) every junction's star is a bond of the rival (its vertex is not a cut vertex; the outside vertex may be one);
- (B4) the rival has at most as many junctions as the truth (n).
Junction sizes are not bounded. A rival matches when its own exact table equals T on every pair.

## Method, and what is proved against what is exhaustive

1. **Forcing (proved sound, computed per stage).** For a pair p with T(p) = d and d + 1 ≤ K (the largest true junction), every
   circuit of size d + 1 through p in any matching code has all its pairs at T ≤ d. Candidates are eliminated when they strictly
   contain a forced word, or when the span of the forced words and the candidate holds a word lighter than m(e) = 1 + min over f of
   T(e, f) at one of its edges (impossible: a word through e contains a circuit through e). A pair left with one candidate forces
   it. F = span of the forced words. If F = C, every matching code contains C, and with (B4) every matching rival's code is C.
2. **Same equations, other junctions (complete by Whitney's theorem, enumerated).** Blocks of G (with o, or without it when nothing
   is loose), each twisted through its Whitney class (closure under twists at 2-separations) and re-glued at one vertex, which (B3)
   forces to be the outside vertex; every combination is filtered by (B1)–(B2). Each rival found is verified directly: its exact
   table equals T and its equations equal C.
3. **When forcing reaches rank n − 1** (one equation missing): every code of rank n containing F is F + ⟨S⟩; all cosets are tested
   by computing the code's own table (exhaustive, up to 2^16 cosets).
4. **Otherwise** the stage is reported undecided.
5. **Table symmetries (a lemma, not searched).** If a rival R = π(G) for an exchange π of distinctions with T(R) = T, then π keeps
   T, so by the population's definition π keeps the junctions, and R = G. So no rival here is a symmetric image of the truth.

Within (B1)–(B4), a stage decided by steps 1–2 is exhaustively settled: either unique, or every same-state rival is listed. Larger
rivals (more junctions than the truth) are outside the bound; the coset test of step 3 covers only one missing equation.

## Settled by construction (stated, not tested)

- A same-equation rival always has the same table.
- At a 3-connected stage the only same-equation rivals are outside choices: the loose set becomes a junction and one junction
  becomes the outside. Legal exactly when the loose set has at least three distinctions and no junction holds two loose ones
  (the advisor's criterion).
- At a closed stage (nothing loose) any junction can become the outside.

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md); `modelUsage` names
claude-fable-5-2). Its points and what I took: forcing is sound (taken); my claim that a larger code forces a vertex splitting is
false in general (Shih's theorem) — taken: the bound (B4) instead of that claim, and its coset test, which turned out too weak on the
development set (most cosets pass) and is replaced by the exact one-missing test; the outside choice is per block, twists need a
closure, closed stages pick per block (taken in step 2); the symmetry lemma (taken as step 5); label each rival by whether its
equations equal the truth's (taken). Its guesses: unique 55–70%, same-states 25–35%, undecided 5–15%, no different-states rival at
3-connected stages; it bet against "nearly all unique".

## Predictions (frozen)

Population: the 522 stages. Controls: the 1,330 symmetry-free stages without shared pairs that the reader read exactly.

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gate: every rival found, on the development set (FRESH-COUNT's mixed stages of at most 10 junctions, run alongside) and on the population, verifies directly (its exact table equals T and its equations equal C) | any fails |
| U1 | Forcing spans C on at least half of the 522 | fewer |
| U2 | No stage has a matching rival with different equations (steps 1–3) | one is found |
| U3 | Every closed stage among the 522 has a same-state rival | one does not |
| U4 | At every 3-connected stage, a same-state rival exists exactly when the loose set has at least three distinctions and no junction holds two loose ones | a stage disagrees |
| U5 | At least half of the decided stages have a same-state rival (the reader's ties are the table's) | fewer |
| U6 | Among the 1,330 controls, at most a tenth have a same-state rival | more |

## Runs and stop rule

`job.py` for the shared runner, one stage per case (522 + 1,330), 10 workers, 600 seconds per case; expected minutes. Readout by
`readout.py`. One run; the study stops at the readout.

## Amendment 1 (2026-11-19, while the main run was under way, before any of its results was read)

- **Population.** CENSUS-READ's referee showed that the 64 stages whose symmetry enumeration stopped at its limit have no
  junction-moving symmetry. The 5 of them R3n misread join the population (527) and the 59 it read join the controls (1,389)
  (`population_unknown.json`).
- **Time.** Cases at ten junctions with hundreds of thousands of candidate circuits time out at 600 seconds in the forcing step
  (one replayed: 560 seconds). The main run's timed-out cases are rerun with a 3,600-second limit (`job_amend.py`, same functions).
- The predictions U1–U6 are unchanged and are scored on the 527 and 1,389.
