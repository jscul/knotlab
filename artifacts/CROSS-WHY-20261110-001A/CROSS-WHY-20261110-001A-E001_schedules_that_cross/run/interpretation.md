# Interpretation: why stages fail, and schedules that cross a border

Run of the frozen contract `CROSS-WHY-20261110-001A-E001` (exploratory, not blind: its exploration is disclosed in the contract),
2026-11-10, launch `cross-why-a1`. Parts M, S and V finished in 78 minutes; part X (one size past, 96 × 96) runs on in the background
as CROSS-WHY-A1 and is folded into the decision note when it finishes. Readings exact.

## The hypotheses

| Hypothesis | Verdict | Evidence |
| --- | --- | --- |
| W1: every schedule in which an original ring hears ring (0, 0) has an unbalanced stage within two doublings of the crossing | **Refuted** | At g = 3, 21 schedules of three runs cross a border and keep every stage balanced through 48 × 48 (`S.json`); the first two in S's order, [1, 28, 1] and [1, 28, 12], are balanced at every doubling on the full state by `BIRTH-RULE-20261109-001A-E001`'s `readings()` (`V.json`). |
| W2: crossing is the mechanism, so every failure at the second doubling comes after a crossing | **Refuted** | Failures with no crossing by the stage lag: P = 4, 5 at g = 2; 3, 5, 6, 7 at g = 3; 2, 3, 4, 6, 7, 8, 9 at g = 4 (`M.json`). |

The contract's decision rule: W1 is refuted, so part X says whether balance continues one doubling further, and the result is computed
for these schedules only.

## What it shows

- **Two kinds of failure, neither needing a crossing (M).** At the second doubling, after one run of P = 1 to 24 lags, there are 11
  failures at g = 2, 17 at g = 3 and 13 at g = 4. Internal ones, where a ring's parts on its own cells alone already fail, number 5, 6
  and 4: at g = 2 exactly P = 5, 9, 13, 17, 21. The rest are heard: those parts bind, and parts held by other rings cancel them. Stages
  balanced right after a crossing: 10, 4 and 9. No ring born at the stage's doubling fails (ticket B, Lemma 2).
- **At g = 2 one run keeps balance with a period of four (M, S).** Balanced at the second doubling exactly for P = 1 and P ≡ 2 or 3
  (mod 4); P ≡ 0 fails by hearing and P ≡ 1 (P ≥ 5) internally, to P = 24.
- **Crossing with every stage balanced (S).** g = 3: one run keeps balance for P = 1, 2, 4, 12, 13, 16, 19, 27 to 30 and 32 to 34, all
  from P = 12 on after a crossing at lag 8; two runs, 39 schedules (29 crossing); three runs after a crossing, 21 schedules, among them
  [12, 1, 1], [12, 1, 2], [19, 1, 1], [28, 1, 1], [28, 4, 4] and [1, 28, 1]. In 11 of the 21 every original ring hears all eight others
  (on the 3 × 3 tube, the four nearest and the four diagonal), in the other 10 the four nearest. g = 2: 114 two-run schedules balanced
  at 24 × 24, 97 crossing; g = 5: 98, 55 crossing.
- **The controls fail where exploration said (V).** [12, 2, 1] and [28, 28, 28], balanced at 12 × 12 and 24 × 24, are unbalanced at
  48 × 48 on the full state. A uniform pause of 28 lags at g = 3 crosses and stays balanced twice, then fails.

## Nonclaims

- One tube (3 × 3), g = 2 to 5, the frozen ranges; balance to 48 × 48 (96 × 96 pending), computed, not proved; plain dependence;
  declared rings (A45); open births (A44). The schedules are declared, found by search, not chosen by the network.
