# Codex specification addendum: EVERY-RAY-20261113-001A (second hand-off)

Frozen 2026-11-13 after the first hand-off, before any class share was seen (only gate results). It answers the eight ambiguities
in `codex/REPORT.md` and adds the carried-port split frozen in the pre-registration (commit 5e003342c). Where it differs from
`codex_spec.md`, this addendum wins. The Rules of `codex_spec.md` apply unchanged (write only in CODEX, at most 3 processes, under
about 8 GB, no git, do not read the TRUE-BOND or TRUE-RATE experiment folders, **do not run the full job**).

You are computing, not designing: if anything is still ambiguous, write it under "Ambiguities" in `REPORT.md` and skip only that part.
Start by reading `codex_spec.md`, this addendum, and your own `REPORT.md` and code in CODEX; extend that code, do not rewrite it.

## A1. The start ranges over every entry (fixes G-last)

The first spec's "start block unchanged" was a flaw: it fixed the first step. **L_path minimises over main's entry too.** When main is
S, the start block chooses which of S's SELF calls makes C_1 (the others read as G[S]), exactly like a middle step but with W any
non-empty subset of main's distinctions containing at least one of main's ports. When main is not S, the start chooses which of
main's calls to S makes C_1 (the others read as G[S]). Every other part of the start is as in the census.

## A2–A4. The independent brute force (G-brute)

- **Paths.** For depth s, enumerate every descending path: a start entry, then s − 1 choices of SELF call. For each, build the ray
  CNF along that path as the census's brute force does (`brute_check.py`, generalised): knots as NAE clauses; every non-chosen SELF
  call of every copy on the path, and every SELF call of C_s, as the clauses of G[S] (or G[T] for another self-holding T).
  Members are restricted to the path's distinctions.
- **Endpoint (A4).** A member among main's ports (as the census) and one among C_s's own distinctions.
- **Value.** The least bond for that path by enumerating the CNF's satisfying assignments (at most 22 distinctions; skip a path with
  more and say so) and member sets by size up to 7. L_brute(s) = the minimum over paths. It must equal the DP's L_path(s) wherever
  every path at that depth was enumerable; a DP value over 7 agrees with "none up to 7".
- **Depths (A2).** s = 1..s_max, with s_max = min(8, max(3, onset + period)) when the family has an exact residue certificate (the
  census code's `depth_threshold` and `period`), else s_max = 4.
- **Panel.** 120 families from the full run's eligible set (c ≥ 2, not S1/S2/S3) chosen by `random.Random(7)` among the smallest
  blocks: at least 10 per over-paths class where available, at least 40 with several definitions, at least 20 with c ≥ 3. Since the
  classes come from the DP, select from the smoke run's records (A9 below); report the quotas met.

## A5. Fixed-index rays with several entries

A fixed-index ray is a pair (entry e, SELF call i), held at every level. `mixed_path_needed` is true iff the family is bounded over
paths and no fixed-index pair is bounded.

## A6. Equivalent SELF calls

Two SELF calls of S are **equivalent** if their argument tuples are equal, or one is the other's image under a permutation of S's
three ports that maps the set of allowed assignments of S's flat block (all its distinctions; own distinctions fixed; side calls by
their relations) onto itself. A grower over paths counts for P2 when it has at least two inequivalent SELF calls.

## A7–A8. Population and bootstrap

- **Population.** Families whose over-paths class is grows, bounded or mixed by residue, plus the unresolved ones that are not
  S1/S2/S3. Unresolved count against a class (low) and for it (high). Over-paths none and lost are outside the population and are
  reported as counts.
- **Bootstrap.** Resample draws from the whole archive (all 223,261) with replacement, 2,000 times, from one `random.Random(20261113)`
  stream; in each replicate recompute every cell's population and shares, in the order all, forever, limit-only, then P1's tables.
  Use linear quantiles at positions (n − 1)p.

## A9. Carried and uncarried (from the pre-registration's clarification)

- **Port maps.** A SELF call with arguments (a_0, a_1, a_2) sends the child's port j to the parent's port a_j when a_j is a port.
  T_1 holds the positions of C_1's ports that hold a port of main (for main = S, the positions j with a_j a port for the entry
  call). T_{k+1} = {j : a_j ∈ T_k} for the call chosen at that level. The census's `carried_split.py` (in the REACH-CENSUS
  experiment folder, read-only) has the fixed-ray version.
- **Extended DP.** Add T (eight values) to the node of the min-over-paths DP. L_path^unc(s) accepts at depth s only when T_s is
  empty. On that graph, compute the same classes as on the plain one.
- **Split.** A family bounded over paths is **bounded, uncarried** if its uncarried class is bounded. Otherwise it is **bounded,
  carried only**. Also record the first-ray carried flag, and the uncarried class itself.
- **Summary.** Add P1 read on uncarried boundedness. Add the population's bounded share split into carried only and uncarried. Add
  growers over paths split by whether the uncarried graph also grows.

## What to run in this hand-off (then stop)

1. The fixes A1, A5, A6 and A9, in your code.
2. G-reg (500 one-self-call families; the start fix changes nothing there), G-node, and **G-last on 60 of the 224** (sorted
   `gate_last_keys.json` order, plus the six families whose earlier comparison failed). The runner must run G-last on all 224
   first in the full run, as the census runner did its gate.
3. The smoke on 300 families (`Random(1113)` as before, the first 300 of your frozen selection), with the extended DP.
4. G-brute on the A2 panel from the smoke records. This is the main independent gate. Give it at most about 60 minutes in total
   and report how many of the 120 it finished.
5. Update `REPORT.md` and `gates.json`. Do not interpret results, and write smoke class shares only to their file.
