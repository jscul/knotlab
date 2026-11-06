# Every four-place knot

Status: Proved

Ticket `FOUR-PREFER-20261101-001A`, 2026-11-01.

## Question

- **Already settled.** `FOUR-PLACE-20261031-001` settled the four-place knots with no preferred value.
- **This ticket.** It lists all four-place knots, the ones that prefer a value included, and settles the one that never fails.

## Dependencies

- **`FOUR-PLACE-20261031-001`.** The library `four_lib` and the value-free classes.
- **External.** Schaefer (1978); Tovey (1984), for the matching argument; Hall's theorem.

## Lemma 1 (knots are independent sets)

**Statement.** A four-place relation R is a knot (K1–K3) iff its excluded states E = {0,1}⁴ ∖ R form a non-empty independent set of
the 4-cube.

**Proof.**
- A three-place projection (forgetting place j) misses a pattern iff both of its extensions, which differ only at place j, are excluded.
- K1 says E ≠ ∅. K3 says R ≠ ∅, which is automatic since an independent set of the cube has at most 8 states. ∎

**Counting.** The 4-cube has 743 independent sets, so there are 742 four-place knots.

## Lemma 2 (the catalogue)

Under flips and permutations of the places, the 742 knots fall into 20 classes (check 1, with the full table in `result.json`).
- **Value-free:** four classes, which are the four of FOUR-PLACE A: 0 parity, 3 not-exactly-two, 11 twelve, 18 not-all-equal.
- **Preferring a value:** sixteen classes.

Classes are numbered by sorting their canonical relations by size and then by states.

## Lemma 3 (Schaefer)

Only parity is closed under a tractable polymorphism (check 3). Every other signed class is NP-complete with unbounded occurrences.

## Proposition 4 (the clause never fails)

**Statement.** Class 19 consists of the relations excluding exactly one state. With any signs, it is solvable on every 4-regular
4-uniform system.

**Proof.**
1. **The forcing value.** A relation excluding v is satisfied as soon as one place j takes 1 − v_j. So every place has a forcing value.
2. **The matching.** The incidence graph is 4-regular bipartite, so by Hall it has a perfect matching of lines to points.
3. **The solution.** Give each matched point the forcing value of its line. Each point is matched once, so this is consistent, and every
   line is satisfied by its matched point. ∎

This is Tovey's argument. No other class has a forcing value at every place (check 3).

## Checks

`check.py` (`result.json`, about 3 s):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings. | pass |
| 1 | 742 knots = 742 non-empty independent sets; 20 classes; the table. | pass |
| 2 | The value-free classes match FOUR-PLACE A. | pass |
| 3 | Schaefer: only parity. Forcing values at every place: only the clause. | pass |
| 4 | The clause: the matching construction solves 200 random signed systems (5–40 points); every signing of the systems with n ≤ 5 is solvable. | pass |

## What this does not establish

- **The other fifteen classes that prefer a value.** Ticket B shows ten of them are NP-complete; ticket C covers the remaining five.

## Novelty

- **Elementary.** The independent-set lemma and the 20-class census. No source was found.
- **Classical.** The clause argument is Tovey's.

## Files

- `prefer_lib.py`: the catalogue, the clause construction, SAT helpers, realizations and lifting, regularization for link pieces of any
  size (used by B), and the exact search for failing signings (used by C).
- `check.py`, `result.json`: the checks.
