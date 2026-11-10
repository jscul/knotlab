# Closure of learning in handles

Status: Proved

Ticket `LEARN-HANDLES-20261109-001Z`, 2026-11-09.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/LEARN-HANDLES-20261109-001/learn_handles.md`; the pre-registration is
  `research/LEARN-HANDLES-20261109-001/preregistration.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A law and a state are free of dissonance (no violated line, no over-agreeing face, no even face) only on a surface of Euler characteristic 0: on the sphere learning cannot remove the forced dissonance, and at genus 2 or more every state over-agrees. | known-with-delta; proved | A |
| 2 | On a torus whose Kasteleyn law is in a class no state satisfies, a state with one violated line has exactly one over-agreeing face; on the Fano tori and the thin tori of even index up to 40 points such states exist (70 per Fano torus, n² per thin torus up to 20 points, computed). | known-with-delta; proved and computed | A |
| 3 | With the state fixed, learning at the dissonance resolves that pair, leaving no even face; every process that resolves it, whatever the state does, changes the law by a cycle of nonzero homology class, so it winds around a handle. Checked by 96,732 walks into every other class. | known-with-delta; proved | A |
| 4 | The cheapest walk into each class costs exactly the smallest cycle of its class change on every torus tested; a local rule with an outside distance to the over-agreeing face resolved all 9,608 starts, against the pre-registered expectation. | computed (exploratory) | A |
| 5 | `RESIGN-STEER-20261107-001B`'s local rule holds one size past: 300 of 300 targets on K_14 and K_16, 2,698 of 2,700 on nine non-octahedral spheres. | stress test (computed) | A |

## Answer

Yes. Learning carries what no change of state can: the law's class, two bits on a torus. On a class-forced torus it removes the
dissonance completely, and only by going around a handle.

## Recommendation

**Continue, awaiting the coordinator's go-ahead:** a native target for learning (backlog B61). The decision note gives the two tables.
