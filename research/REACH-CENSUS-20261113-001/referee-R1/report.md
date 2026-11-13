# Referee report REACH-CENSUS-R1 (lean, Codex-assisted, fresh code)

**Verdict: Confirmed with fixes: no Block, four Narrowing, three Not a block.**

**The census's computations reproduce.** That covers the multi-definition path at shallow depth (including 12-distinction blocks),
the classes on a 49-family sample, every headline share, and certificates for all 131 last-call bounds.

**The correction must change.** "Growth along the first ray is not growth with depth" is largely an identity artefact.
- **Carried by identity.** In 99 of the 131 families bounded along the last-call ray, that ray carries a top port by identity: 77 as
  a fixed point, 22 through a cycle of ports. The bounded bond is then local at every depth.
- **Genuine.** Only 32 are bounded without a carried port.

**How the work was split.** The background referee thread owns the verdict.
- **Codex.** The Codex command-line tool, at the owner's choice of model and effort, recomputed from fresh code. It was barred from
  the study's own folder and did not open it. It took about 15 minutes, with at most 3 processes and under 0.75 GB each, and wrote
  only in `codex/`, starting with `codex/codex_report.md`.
- **The referee.**
  - Checked the carried-port split itself (`ref_carry.py`).
  - Read the published readings.
  - Judged the class of each correction.
- **Advisor.** The advisor model was not consulted.

## 1. The multi-definition path (Codex)

**What Codex built.** Fresh code covers the usual limit, depth-first inlining, S, the entry and ray calls, side relations, and the
block DP. A separate SAT expansion works from the original syntax, with members restricted to the ray's distinctions.

**The sample.** 49 families: 37 with several definitions, seven with 12-distinction blocks, and some with mains of more than three
ports.
- **The checks.** All 147 checks at s = 1..3 agree: 141 exact, 6 at "no bond of size ≤ 7".
- **The classes.** All 49 complete graphs reproduce class, node count, exact cycle mean, residue verdict and L_ray(1..30), which is
  1,470 values.

**The gap that remains.** G3's 11 unfinished largest families leave large multi-definition blocks validated only at shallow depth.
The note states that G3's 11 did not finish. It should not say or imply that every gate passed. **Narrowing.**

## 2. Weights, settled parts, unresolved (Codex)

**The shares are of draws.** Each draw is one sample of the description code, with no second weighting. Codex reproduced 58.40%
(no depth), 3.04%, 79.81–80.17%, 13.88% bounded, 5.95% grows, and the forever and limit-only cells. P1 is 68.79–70.59%
[68.34, 71.03], and P2 and P3 reproduce. The wording "weight" means share of draws. It is used consistently.

**The 70/30 split is not settled by construction.** S1 to S4 are one-line consequences of the definitions. Finite state and the class
implications are method facts, but nothing forces the split. P1's "typical" rests on the conservative lower band (unresolved
counted against), so it is not one-sided.

**The 813 unresolved draws are handled as stated.** They are outside every class numerator, inside the denominators, and below the
5% undecided threshold in each cell (0.93% and 2.09%).

**Small overstatements.** **Narrowing.**
- **"Only because their bonds exist"** is too strong, since the conditional growth bands still differ (29.4–31.2% against
  32.9–35.0%).
- **"Mixed below 0.01%"** holds for classified weight only. The band reaches 0.37%.
- **"Settles at 3 members"** should be "has a certified upper bound of 3". The residue certificate's cost is a bound, not the
  least value (row 262: bound 5, minima 3).
- **"Nothing below the top three distinctions"** should be "no eligible endpoint at increasing depth".

## 3. The crash (Codex)

**It was a resume, not a rerun from scratch.** `run_info.json` records 110,262 records resumed from the pre-patch runner and 14,310
new ones, as the note itself says ("resumed").

**What can be checked.** Recomputing the prefix's summary from the final rows matches the unread partial summary in all 1,830 counts
and bands and all 366 histogram values.

**What cannot.** The pre-patch per-family rows are not available, so "no result changed" is supported in aggregate only. Say so.
**Not a block.**

## 4. The ray dependence and the identity artefact (the referee and Codex)

**The certificates (Codex).** Codex independently certified all 131 last-call bounds, at 3 (96), 4 (32) or 5 (3), and reproduced 48
SAT minima on a sample.

**The carried ports (the referee, `ref_carry.py`).** For each of the 224 first-ray growers I checked the last-call SELF call's
argument map on the ports (child port j = parent's a_j). A cycle in that map means a top port is carried down the ray by identity.

| Last-call class | Carried (fixed point) | Carried (cycle) | Not carried |
| --- | ---: | ---: | ---: |
| bounded (131) | 77 | 22 | **32** |
| grows (87) | 8 | 0 | 79 |
| lost (2) | 2 | 0 | 0 |
| none, unresolved (4) | 0 | 0 | 4 |

**What the 99 mean.** In those families the top distinction is itself a port of every copy on the last-call ray, so the bounded bond
is local at each depth. It says nothing about the law's reach across depth. This matches the other thread's 99.

**The correction's class.** The broad reading ("the law's reach measures depth there, as on a ruler", PROVED-RATE's Reading; "counting
inside ... appears in more than a third", BOND-DEPTH's Answer) is contradicted only in the 32 families bounded without a carried
port.
- **Codex's view.** Codex proposed a Block against that broad reading on all 131.
- **Why I classify it as a Narrowing.** With the identity artefact removed, the counterexamples are 32 of 224 (14%). The technical
  statements of both studies were restricted to one ray from the start. So the broad reading narrows rather than falls.
- **The condition.** It must not be used without the ray and carried-port qualifiers.

**How the Narrowing should be worded.** In at least 32 of the 224 first-ray growers, another ray reaches depth s with at most five
members without carrying a top port, so growth along the first ray is not growth with depth there. In 99 more the other ray's
bounded bond is local, because that ray carries a top port by identity, and reach should not be read from it.
- **Where to make the change.** REACH-CENSUS's Conclusion 7, its Answer ("in most of the families where it was proved ...") and the
  in-place narrowings of PROVED-RATE and BOND-DEPTH should say this.
- **What follows.** A80's challenge should be restated with this split, and A81 (bonds starting from a carried port) is the right
  companion.

**Narrowing.**

## Fixes for the thread

1. **Reword the ray-dependence correction with the carried-port split,** as in section 4: 32 genuine, and 99 local by identity.
   Restate A80's challenge accordingly. **Narrowing** (not a Block, since the genuine counterexamples are a minority and the
   technical claims were ray-restricted).
2. **State that large multi-definition blocks are validated only at shallow depth.** That is G3's 11 unfinished, plus the referee's
   37 multi-definition families at s ≤ 3. **Narrowing.**
3. **Fix the small overstatements:** "only because their bonds exist", "mixed below 0.01%", "settles at", and "nothing below the top
   three distinctions". **Narrowing.**
4. **The crash.** Say that 110,262 rows were resumed from the pre-patch runner and only the aggregate is shown unchanged. **Not a
   block.**
5. **Weights.** They are shares of draws, worded consistently. **Not a block.**
6. **Unresolved.** These are handled as registered. **Not a block.**

## Files

- **`codex/`.** Codex's brief and report, `fresh_recompute.py`, `bounded_certificate.py`, `verify_referee.py`, `weights_crash.py`
  and their JSON.
- **Referee.** `ref_carry.py` and `result_carry.json`.
