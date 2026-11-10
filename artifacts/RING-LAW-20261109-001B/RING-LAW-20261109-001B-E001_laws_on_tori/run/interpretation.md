# Laws that see their rings, on the lattice tori: E001, stopped as too slow

Experiment `RING-LAW-20261109-001B-E001` (exploratory), pre-registered in 27192b3a9. It was launched at 23:33 UTC on 2026-11-09 and stopped
after 70 minutes with no output. It was relaunched at 00:43 UTC with progress logging only (a08dfb956) and stopped again at 01:00 UTC as too
slow, with nothing failed. It wrote no result: `progress.txt` beside this note (written as progress.log, renamed so the record keeps it) is its only output.

## What the partial log shows

- **The cost.** Its first reading, R1 (binding for every law), was going through the networks in order. On the line networks a law that
  binds to lag 6 needs 2^|X| copies of the contact's cone at every lag. That took 50 to 117 s per law on the square 4 × 4 line network and
  about 700 s on the 5 × 5. Extrapolated to the 6 × 6 and the triangular line networks (64 copies), the census would have run 10 to 15
  hours.
- **What it read before stopping.** On the square 4 × 4 and 5 × 5 tori every reading of R1 finished quickly, and none was logged as
  binding. On the square 4 × 4 line network 32 laws were logged as binding to lag 6 and on the 5 × 5 line network 10. The log keeps only
  readings over 30 s (and every 500th), so these are not counts, and it does not say which of them see the routing.

## What follows

E002 (same ticket) reads E001's readings in a feasible order. It reads R2 and R3 first, then R1 on the nine tori and on the line networks
of n = 4 and 5. It tests the lines-versus-tori observation as a frozen hypothesis, disclosing this log and the pilots up front. No claim
rests on E001.
