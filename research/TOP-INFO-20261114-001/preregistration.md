# Is reading the whole rule for the bond: pre-registration

Epic `TOP-INFO-20261114-001` (`READ-RULE-20261114-001#2`; G17, with G1), 2026-11-14. Started at the coordinator's go-ahead, which
put this question before B173. Frozen before any census computation for it. The advisor model was consulted before the freeze
(`advisor_review_answer.md`). Census code by Codex in one hand-off, run by the thread. The canonical K1–K3 test is unchanged.

## The question

`READ-RULE-20261114-001` proved that a carried top port read by a knot, together with an own distinction of the target copy, bounds
the bond, and that the bond is, on each residue of the depth, eventually bounded or at least linear. The coordinator asked whether the
converse completes the rule: **bounded on a residue exactly when some carried value is read there, outside Theorem R's exception;
linear otherwise.** If not, what is the rule?

## The question in standard terms

For iterated hyperedge-replacement NAE instances whose bond to depth s is eventually bounded or linear, a characterisation of the
bounded case by finite windows at the root and at the target.

## Prior work in the program

`python3 -B scripts/track.py objects "top ports correlated with own distinctions of the deep copy bounded bond" --until 2026-11-14 --exclude TOP-INFO-20261114-001`
`python3 -B scripts/track.py objects "order idempotent bounded bond without carried port" --until 2026-11-14 --exclude TOP-INFO-20261114-001`
`python3 -B scripts/track.py objects "converse growth requires unread carried values" --until 2026-11-14 --exclude TOP-INFO-20261114-001`

- `READ-RULE-20261114-001`, `CARRY-BOUND-20261114-001`: Theorem R, the dichotomy, the census split; the immediate predecessors.
- `TIE-CYCLE-20261114-001`: the order label.
- `TRUE-BOND-20261113-001`, `BOND-DEPTH-20261112-001`, `EVERY-RAY-20261113-001`, `TRUE-RATE-20261113-001`: bonds to the first ray and
  over paths; relatives.
- `GROW-FACE-20261110-001`: a lexical hit, unrelated.

## What is already known before any computation

**The rule as stated is false.** The 93 in-scope families of the order label have no identity cycle, so no port of main is carried
to large depths and Theorem R never applies there. Yet all 93 are bounded at every sufficiently large depth (`CARRY-BOUND`, by window
certificates and the path DP). READ-RULE's 9 exception families are bounded too, although on some residue every reading knot meets
the exception. So the census check below measures how far the rule fails, and what replaces it.

**Plain pinning is not the rule either (the advisor's example).** Call depth s **pinned** when, for some covered copy c, main's ports
V and c's own distinctions X_c are correlated: the projection on V ∪ X_c is not the product of the two sides. The complement-closed
relation NAE4(p, q, r, t) × {0, 1}, minus the states (0011, x = 1) and (1100, x = 0), is pinned, but no bond inside V ∪ {x} contains
x. Pinning does not by itself give a bond to the target. Whether a census family realises such hiding is open.

## Statements (to prove in `proofs/TOP-INFO-20261114-001B/`)

**Theorem P′ (bond-pinning, the advisor's).** If at depth s some shattered T ⊆ V and shattered D ⊆ X_c (c a covered copy at depth s)
have T ∪ D not full, then L(s) ≤ |T| + |D|. (A minimal non-full subset of T ∪ D is a bond and meets both sides.)

**Two-block window bound.** Lemma W holds with main's whole block in place of main's ports: the projection onto main's block and the
target copy's block is exact. So every bond found there containing a port of main and an own distinction of the target is a bond of
the pattern, and its least size U₂(s) bounds L(s). It is eventually periodic by the same state iteration.

**Localisation (to prove or leave open with its gap).** If L is bounded on a residue, some least bond on that residue has all its
members within a bounded number of levels of the top and of the target. That is, it crosses one long member-free stretch, and every
other stretch is shorter than a constant of the family. Proof idea: by pumping, a long stretch can be shortened by a multiple of the
period without changing the projection; shorten all but one.

## Census checks (Codex, on CARRY-BOUND's 5,789 in-scope families and the 175 out of scope)

1. **The rule's exceptions.** Per family and residue, READ-RULE's R flag (the theorem's quantifier: some state in which the knot's
   position is carried and the exception fails) against CARRY-BOUND's verdict, after its path DP. List the families bounded on a
   residue where R does not apply, by stratum (order label, the 9, other), and the growing families where R applies (there must be
   none, by Theorem R).
2. **Plain pinning.** Per residue, whether some state of the repeating part is pinned (exact from the window projection of V ∪ X_c).
   Cross-tabulated with the verdicts.
3. **Bond-pinning (P′).** Per residue, whether some state has shattered T ⊆ V and D ⊆ X_c with T ∪ D not full.
4. **Two-block window.** U₂(s) per residue, up to size 6, with the same caps as CARRY-BOUND, for every family not already bounded,
   and for a control sample of 200 bounded families (sha256("TOP:" + key) order).

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | **Gates.** No growing family has a residue where R applies, or one that is bond-pinned at a large depth (Theorem R, Theorem P′). The two-block window never undercuts CARRY-BOUND's lower bound on 100 forgetting families (the first in sha256("TOP:" + key) order), and agrees with the one-block window wherever both bound. A separate brute-force check on 30 families at s ≤ 3 matches the two-block projection. | any fails |
| T1 | **Plain pinning is rare where the bond grows.** Among the 632 growers, no residue is pinned at a large depth. | any pinned residue |
| T2 | **The order families are bond-pinned.** All 93 order-label families are bond-pinned on every residue: their window bonds pair main's ports with an own distinction. | any is not |
| T3 | **The two-block window decides some of the undecided.** It bounds at least 10 of CARRY-BOUND's 83 undecided in-scope families on every residue. | fewer than 10 |
| — | Reported: the rule's exceptions by stratum, the pinning and bond-pinning shares, the two-block window's new bounds, and every undecided family with a non-rectangular long product but no cross bond (the advisor's "hiding"). | — |

**Undecided** (caps) counts as failing in T2 and T3, and as not pinned in T1.

## Runs and stop rule

Codex writes only in `experiments/TOP-INFO-20261114-001A/TOP-INFO-20261114-001A-E001_rule_check/codex/`, without commits, and uses the
shared runner for anything over ten minutes, which the thread launches and registers. Stop after the census check, the proofs of P′
and the two-block bound, localisation proved or its gap stated, a referee hand-off and the report.
