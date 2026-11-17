# Referee report SPACE-ORDER-R1 (fresh code, no Codex)

**Verdict: the lemma and every frozen number are confirmed; the headline reading "only through steps apart" is a Block.**
- **The lemma holds** (Not a block).
- **Every one of the 426 registered cases recomputes exactly** with the referee's own propagation code.
- **The planted not-all-equal process** is adequate for the readings that use it.
- **A96's own challenge, run, overturns A96.** Rewiring 0.2% of the weave's knots keeps 99% of its short cycles and cuts its
  largest steps apart five-fold (256 to 52 at L = 384), but the phase count does not move (260 to 252). So the phase count
  follows the weave's local structure, not steps apart. The 27-fold ratio between weave and twin is the loss of short cycles.
  - **Block** on "space forces order, and only through steps apart; the price is exactly steps apart" and on the explanation of
    SEQUENTIAL-WALL's easy random patterns.
- **The post hoc finding.** It holds on the plain weave as a close linear relation, not an identity, and is unlabelled in five
  published places (Narrowing).

## What holds

- **Order.** The freeze, `6995ef26a`, is at 17:09:44 UTC; the run was created at 17:09:52 and ended at 17:14:24. No study code
  changed after the freeze. `posthoc.py` is labelled post hoc in its own docstring.
- **The lemma (proved; Not a block).** For an atom law, a distinction set in phase t is either the head of a start (both premises
  set before t) or the head of a two-place rule from an atom one of whose premises was set before t. For not-all-equal, likewise
  from a knot with two members set, or one. Either way it shares a knot with a distinction set before t. By induction, every
  distinction set by phase t is within t steps of the held set, so P ≥ D.
  - **Two remarks.**
    - The argument is the light cone of a local rule. The literature's names are the locality bound of the LOCAL model (Linial
      1992) and the finite speed of propagation of cellular automata, here with instantaneous chains along what is set.
    - The phase of a distinction equals the least label of the rule "g(i, j) = max(i, j) if i ≠ j, else i + 1" over its
      derivations. So the study's gate "Strahler number = phase" is a theorem, not only a check. The referee's code computes
      phases this way.
  - **The check.** P ≥ D holds in all 852 k* and k* − 1 readings recomputed (the study's 2,130 include the fixed fractions).
- **Every registered case recomputes exactly** (`referee_core.py`, `referee_recompute.py`, `.json`).
  - **Method.** The instances were rebuilt with the study's generator and seeds. Everything measured on them is the referee's
    own: the atoms, k* by incremental closure, rounds and phases as least labels by generalized Dijkstra (not the study's
    reachability phases), steps apart, avalanche and free share.
  - **The match.** All 426 cases agree with the stored results in k*, the set size, R, P and D, at k* and at k* − 1: 0
    mismatches.
  - **Every verdict input matches the note.** T1: P slopes 0.95 and 1.01, R slopes 0.91 and 0.94, P*/R* 0.49, k*/n 0.016 to
    0.0016. T2: k*/n 0.091 to 0.086, R ratio 2.45, P* 5 to 9.5. T3: 26.9. T4: 3.7, 5.5 and 6.3 (failed, as stated). O1 to O3,
    N1 and N2. N3: 0.292 to 0.295.
- **The twins are what the note says.** On the study's own R6 instances (`referee_swap_invariants.py`, `.json`; L = 24, 48 and 96,
  five samples per law):
  - every distinction keeps its count of knots in each role, and every slot keeps its role;
  - no knot repeats a distinction, and no knot is duplicated;
  - the planted state stays not-all-equal on the not-all-equal twin.
- **What the twin changes.** Two things, at once:
  - *steps apart:* the largest falls from 2L/3 to 4 or 5;
  - *short cycles:* on the weave every co-knotted pair lies in two knots, one of each orientation; on the twin at most 1.1% do.
  The weave and twin samples use different draws (different seed labels), so they are compared by medians, not paired.
- **The planted not-all-equal process (Not a block)** (`referee_planted.py`, `.json`).
  - **It is valid.** It keeps every knot not-all-equal, and the free share is 0.289 to 0.298.
  - **It is not the uniform ground state at large scale.** The three-class order parameter falls from 0.667 at the start to only
    0.32 to 0.36 after its 30 sweeps. After 3,000 of the referee's sweeps it is still 0.23 to 0.35. Zero-energy flips relax the
    large scale slowly.
  - **The readings do not depend on it.** With 100 times the mixing, they are unchanged on 11 instances at L = 48, 96 and 192:
    k*/n 0.32 to 0.34 against 0.32 to 0.33, P* 2 to 4 against 2 to 4, avalanche at most 0.007.
  - **The note's limitation** "a declared process, checked only by its free share" is accurate. Adding "it keeps part of the
    three-class order of its start" would make it complete.
- **Prior work.** `objects-gate` was ok at the freeze.

## 1. A96's challenge, run: the phase count follows short cycles, not steps apart (Block on "only through steps apart")

A96 says the twin "removes steps apart and nothing else that matters", and names its own test: "a weave with a few random
rewirings ... see whether the phase count follows steps apart ... or the cycles". The referee ran it (`referee_rewire.py`,
`.json`). The setup:
- the two-demand law on the weave, with the referee's own generator, swaps and seeds;
- eps · m of the twin's role-preserving swaps, from eps = 0 (the weave) to eps = 5 (the study's twin);
- 3 to 4 samples per cell; role counts kept in every case.

| L = 384 | Pairs in two knots | Largest steps apart | k*/n | P* | R* | P* / trigger's steps apart |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| weave (eps = 0) | 1.000 | 256 | 0.0010 | 260 | 543 | 1.02 |
| eps = 0.002 | 0.989 | 52 | 0.0011 | 252 | 530 | 4.3 |
| eps = 0.01 | 0.949 | 27 | 0.0023 | 134 | 303 | 4.5 |
| eps = 0.05 | 0.778 | 15 | 0.0006 | 115 | 295 | 7.7 |
| eps = 0.25 | 0.345 | 9 | 0.036 | 48 | 212 | 5.3 |
| twin (eps = 5) | 0.000 | 7 | 0.086 | 10 | 244 | 1.4 |

L = 96 and 192 show the same pattern. At eps = 0.002, L = 192: steps apart 43, P* 128 against 130.5 on the weave. At eps = 0.01,
L = 96: steps apart 21, P* 63 against 64.5.

- **With 99% of the short cycles kept, steps apart falls five-fold and the phases do not.** The kernel still forms (k*/n
  unchanged) and still needs about 250 phases. A shortcut sets a distinction far away, but the two-demand law cannot grow there
  without local support, so the kernel keeps growing only through the weave-like part.
- **The post hoc relation breaks.** Phase against steps from the trigger has correlation 0.04 to 0.21 at eps = 0.002, against 0.99
  on the weave.
- **The phases fall only as the short cycles go,** from 0.99 to 0.35 to 0, and reach the twin's mean-field 10 only when almost none
  are left.

**What this changes.**
- *What stands.* The lemma's lower bound P ≥ D. On the plain weave, the kernel's growth distance and the steps apart coincide,
  so the frozen T1 to T3 and the post hoc reading stand as measured.
- *What does not stand.*
  - The reading "space forces order, and only through steps apart ... the price is exactly steps apart".
  - The goals line "Space forces order exactly through steps apart, the program's ruler distance on weaves".
  - The intuition entry's "its price is steps apart".
  - The position row "Yes, through steps apart only".
- *A fair reading.* "Phases are at least steps apart from the held set (proved). On the weave, the law that grows a kernel needs
  one phase per step of its growth through the weave's local structure (every co-knotted pair in two knots). Long-range shortcuts
  that collapse steps apart do not shorten it, and the twin's 27-fold drop is the loss of that local structure."
- *The explanation of SEQUENTIAL-WALL.* "Random patterns were easy because everything there is within about log n steps" has the
  same problem. A pattern with everything within 27 to 52 steps still needed 134 to 252 phases. They were easy because they have
  no local structure for a kernel: a mean-field jump.
- *A96* is overturned by its own challenge.

**Block** for those interpretive claims, judged against the epic's theory (space forces order through steps apart). It is not a
block on the lemma or on any frozen number.

## 2. The post hoc finding: a close linear relation, unlabelled where published (Narrowing)

**What holds, recomputed on every registered sample** of two-demand on the weave (15, 10 and 6 at L = 96, 192 and 384):
- P* is 254 to 257 against the trigger's largest steps apart of 256 at L = 384 (127 to 136 against 128 at L = 192; 64 to 77
  against 64 at L = 96);
- phase against steps from the trigger has correlation 0.87 to 0.99 and slope 0.88 to 1.06. One sample at L = 96 has 0.62 and
  0.70; at L = 384 all are 0.99 and 0.97 to 1.01.

**But "each distinction's phase is its steps apart from where the kernel began" is not literal.**
- Phases are exactly the steps apart for only 4 to 18% of distinctions.
- The median offset is +2 to +6 in the four samples examined at L = 96 to 384.
- The 10th to 90th percentiles of the offset run from about −4 to +17 at L = 384.

So read it as "phases grow about one per step from the trigger (correlation 0.99, slope 0.99 at L = 384), a few phases above the
steps apart".

**Labels.**
- The note labels it in its lemma section and its post hoc table. It does not label it in "The answer" ("256 phases ... the
  weave's largest steps apart (2L/3)"; "each distinction's phase is its steps apart ... correlation 0.99").
- Five published places give it without a label, and three of them under "computed, frozen":
  - the final report as sent;
  - the intuition entry;
  - the goals' Stands-on line;
  - the objects row ("P* = 16.5..256 = about 2L/3 (the weave's largest steps apart)");
  - and, as said, the note's answer.

The frozen T1 tested only slopes (P and R like L); the identity with 2L/3 and with steps from the trigger is post hoc.

## 3. Known mathematics to name (Not a block)

- **The lemma** is a light cone: a local rule moves the settled set one layer per step. Linial (1992) is the standard locality
  bound in distributed computing. The note names the light cone; adding the name of the locality bound would place it.
- **"Phases grow linearly with distance on the weave"** is, for rounds, the known time of bootstrap percolation after nucleation:
  a supercritical droplet fills the torus in time linear in L. See Balister, Bollobás and Smith, "The time of bootstrap
  percolation in two dimensions" (Probab. Theory Relat. Fields, 2016), and, for dense initial sets, Bollobás, Holmgren, Smith and
  Uzzell (Ann. Probab. 42, 2014).
- **The phase version** is the same front growth saturating the light cone. Nothing found names it for Newton-type phases, as the
  pre-registration says.
- **2L/3** is the diameter of the triangular torus for 3 | L (elementary; checked at L = 24 to 384).

These should be named beside the post hoc finding, together with the bootstrap literature the pre-registration already cites.

## 4. Smaller points (Not a block)

- **A96's Why.** "role-preserving swaps keep every distinction's counts in each role and destroy short cycles and steps apart"
  already says the twin removes both, so the scope statement "and nothing else that matters" was never consistent with it.
- **Words.** "kernel", "steps apart" and "rim" are used for the program's objects. "Rim" is a near-spatial word for the boundary of
  the settled set: see the common-verbiage skill (an advisor check before a new word).

## Fixes for the thread (listed for the owner, not folded in)

1. **"Only through steps apart."** Withdraw "space forces order, and only through steps apart / its price is exactly steps apart"
   (note's answer and position row, goals' Stands-on line and checkpoint row, intuition entry, final report).
   - **The replacement.** The lemma's lower bound, plus "on the weave, phases count the kernel's growth through its local
     structure; shortcuts that collapse steps apart do not shorten it".
   - **The other changes.** Withdraw the explanation of SEQUENTIAL-WALL's easy patterns by steps apart. Mark A96 Overturned, with
     the rewiring table. **Block** (on these readings only).
2. **The post hoc finding.** Label it post hoc in the note's answer, the intuition entry, the goals line, the objects row and the
   final report. Restate it as "about one phase per step from the trigger, a few phases above the steps apart (exact for 4 to
   18%)". **Narrowing.**
3. **The planted state.** Add to its limitation that it keeps part of the three-class order (0.32 to 0.36), and that 100 times the
   mixing leaves the readings unchanged. **Not a block.**
4. **Known mathematics.** Name the locality bound and the bootstrap-percolation time literature beside the phase-growth finding,
   and the triangular torus's diameter 2L/3. **Not a block.**

## How the work was split

- **The referee:**
  - read the pre-registration, the note, `weaves.py`, `job.py`, `summarize.py`, `posthoc.py` and the atom library's phase
    definitions;
  - wrote an independent propagation library (`referee_core.py`), recomputed all 426 cases and the post hoc reading, and checked
    the twins' invariants;
  - ran A96's rewiring challenge and the planted-state mixing check;
  - checked the labels and the literature.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- `referee_core.py`: the referee's weave, swaps, atom laws, least-label rounds and phases, and steps apart.
- `referee_recompute.py`, `referee_recompute_runs.jsonl` and `referee_recompute.json`: all registered cases.
- `referee_rewire.py`, `referee_rewire_runs.jsonl` and `referee_rewire.json`: A96's challenge.
- `referee_planted.py` and `.json`: the planted state.
- `referee_swap_invariants.py` and `.json`: the twins.

## Addendum (from the LAYER-RANK referee check)

The equality "phase = least Strahler number of a derivation", which the gate checks and the remark under "The lemma" derives, is a
known theorem: the k-th Newton approximant of a fixed-point equation over an ω-continuous semiring collects exactly the derivation
trees of dimension (Strahler number) at most k (Esparza, Kiefer and Luttenberger, "Newtonian program analysis", J. ACM 57(6),
2010). Name it beside the lemma; the one-step lemma itself is the elementary light cone. **Not a block.**
