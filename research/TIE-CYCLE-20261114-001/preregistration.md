# Is identity the whole story of forgetting: pre-registration

Epic `TIE-CYCLE-20261114-001` (`FORGET-RULE-20261114-001#1`; G17, with G1), 2026-11-14, at the coordinator's go-ahead. Frozen in
two stages: the split now, before the tie status of any family is computed; the rule and the held-out predictions after exploring
the training half. The thread's work, reusing FREE-TARGET's per-call relations. The canonical K1–K3 test is unchanged.

## The question

`FORGET-RULE-20261114-001` proved that a port handed to itself around a cycle of calls prevents forgetting (rule N). In the census,
having no such cycle means forgetting in every chain and in 94% of the other families, and the exceptions carry a value through
knots that force equality. Generalise identity to a tie: at the end of a call word, a port equal or opposite to a start port in
every allowed state. Is "no tie cycle" exactly forgetting?

## In standard terms

For a finite semigroup of complement-closed relations on {0,1}³ × {0,1}³, whether some element has a coordinate equality or
inequality from a start bit to the same end bit (a self-tie). The question is whether the absence of self-ties characterises
eventual rectangularity.

## Prior work in the program

`python3 -B scripts/track.py objects "forced tie along a call word equal or opposite port" --until 2026-11-14 --exclude TIE-CYCLE-20261114-001`
`python3 -B scripts/track.py objects "affine dependence between top and depth ports parity" --until 2026-11-14 --exclude TIE-CYCLE-20261114-001`
`python3 -B scripts/track.py objects "identity cycle prevents forgetting" --until 2026-11-14 --exclude TIE-CYCLE-20261114-001`

- `FORGET-RULE-20261114-001`: rule N (identity cycles) and rule A, the starting point; this study generalises N.
- `TRUE-RATE-20261113-001`: carried top ports, the identity mechanism, a relative.
- `REACH-CENSUS-20261113-001`, `BOND-DEPTH-20261112-001`: the census and the ray bonds, relatives.
- `FAR-BOUND-20261112-001`, `NEST-COUNT-20261112-001`, `BOARD-DIST-20261110-001`: unrelated (other bases and objects).

## Stage 1: the split (frozen now)

A family is **training** when `int(sha256("TIE:" + key).hexdigest()[:8], 16)` is even, otherwise **held out**. This is a fresh salt,
so the halves differ from FORGET-RULE's. The census's forgetting verdicts have been seen in aggregate counts. No family's tie status
has been computed. One- and several-definition families are reported apart.

## Proved before stage 1 (stated, not tested)

- **On single bits a complement-closed relation is full, an equality or an inequality.** Any pairwise dependence a word forces
  between two port bits is therefore a tie.
- **Ties compose.** A tie from port j to port k along u, followed by one from k to l along v, is a tie from j to l along uv, with the
  signs multiplied.
- **A tie cycle prevents forgetting.** Suppose some word w gives a self-tie, port j to port j. Then every power of w carries it. The
  projection on (start j, end j) is an equality or an inequality containing both values, which is never a product. So no power of
  w is rectangular. Rule N is the equality case.

## Stage 2 (to be frozen after exploring the training half)

The rule's exact test (the finite semigroup's elements, checked for a self-tie), any variant found on the training half, the
advisor's view, and the held-out predictions.
