# Learning a six-bit constraint and using it again

In this finite experiment a supplied learner discovered, through its own attempted changes, that `xyz` could take exactly six values. Two copies of its stored reading then ruled out two new combinations on four fresh distinctions. The learner received neither a target triple nor an example labeled “not all equal.”

The [four original constraints](../../proofs/OVERLAP-READ-20261111-001B/OVERLAP-READ-20261111-001B-P001_what_nae_forces/proof.md) put not-all-equal on `abc`, `ayz`, `xbz` and `xyc`. Their 18 joint states and the bond on `xyz` were already known. G16 asks what a system can learn about its rules. This test concerns learning what the rules together allow and reusing that reading.

## What was placed in the base

The original six distinctions have a static relation. For this experiment the enlarged system has a state with six sensed values, a memory, and a controller for trying reversible single-bit changes. A proposed change takes effect if the four constraints permit it. The controller sees only the resulting values. Its choices and its stopping condition belong to a supplied, deterministic update rule. The computer running the rule makes no choices of examples or moves during an episode. This is an operational model of the enlarged system. The four original knots supply no update rule, memory, or upper wiring of their own.

For each of the twenty triples the learner starts with eight empty memory entries. A visit to a state sets the entry for the three values present. In symbols, for a triple T and a word w, the update is M[T,w] ← M[T,w] OR [T shows w]. The order of the six ports, access to all six, the choice to record triples, and the eight-entry form of the record are supplied. An individual entry reads only its three bits. The controller also remembers which full assignments it has visited and which flips it has tried, and physically undoes a move to return. It stops when it has explored its entire reachable component. The guarantee is relative to that component. The scorer separately checks whether it is the whole base.

From **every one of the 18 legal starts**, the learner visited all 18 assignments, making 77 forward trials and 17 return moves. Eight triples, including the four written triples and four others, had just the six unequal words. The other twelve had all eight words. On the first run all six words of `xyz` had appeared after 40 trials. The learner waited until its exploration was complete at trial 94 before using absence as evidence. It stored a table of values, which in this case is exactly the not-all-equal relation.

## What the stored reading did

Every finished triple table went through the same supplied connection. Two copies of a table M constrained fresh triples `pqh` and `hrs` through one shared distinction `h`. Once the memory was acquired the upper system received only that table. Its rule for four visible bits is

```text
(p,q,r,s) is allowed if some h satisfies both M[p,q,h] and M[h,r,s].
```

This is a constraint on the upper states. Each table entry can equally be used as a Boolean memory bit: for each three-bit word w, impose “if this triple takes w, then M[w]” on each copy. Pin the eight memory bits to the acquired reading, then forget them and h. The canonical `knotlab check` on those constraints returned fourteen states and passed K1–K3 for `p,q,r,s`: the whole is constrained, every proper part is free, and a state exists.

| Change to the acquired `xyz` reading or its use | Excluded upper words |
| --- | --- |
| Use both copies as learned | `0011`, `1100` |
| Admit `000` in the first copy only | `1100` |
| Admit `111` in the first copy only | `0011` |
| Erase the acquired restriction, leaving both tables free | None |
| Give the two copies separate hidden distinctions | None |

For example, `p=q=0` requires `h=1`, while `r=s=1` requires `h=0`. This rules out `0011`. Admitting `000` in the first copy lets `h=0` satisfy both copies in exactly that case. Thus changing one bit of the stored reading has a specific consequence upstairs. The four-bit queries were never training observations.

## Controls and scope

- Removing any one original constraint gave 26 legal states. The same learner then acquired all eight words on `xyz`, and its upper connection allowed all sixteen words. A free six-bit base also gave a free reading.
- The complementary four original triples allow the same 18 states. On matched starts they gave identical action-and-observation traces and identical readings. With a permutation and two reversed bits, the readings followed the changed values. The interface can learn a relation even when it cannot distinguish two presentations that give it.
- A control base requiring only `a=b` has 32 states in two components. Every run visited 16. Its report about triples involving `a` or `b` could describe only its starting component. This is why global coverage was checked separately in the six-bit example.
- In the original base, none of `a,b,c` is a function of `xyz` on all 18 states. The six-bit relation permits a history that repeats one assignment indefinitely if no further rule on changes is imposed. It therefore gives no guarantee that the readings needed for discovery will occur.

The study was exploratory and deterministic. The nine panels contain 254 separate cold starts and 27,812 attempted moves. The implementation is ordinary exhaustive exploration with a table of observations. Its interest here is the passage from a relation on the original distinctions, through a retained reading acquired without labels, to a new restriction that depends on the content of the memory. Whether the six-bit base or a larger pattern can itself form such a learner and its wiring remains open.

The [frozen contract](../../experiments/SIX-BIT-REUSE-20261111-001/SIX-BIT-REUSE-20261111-001-E001_witness_memory/contract.json) records what was given and what the learner could see. The [learner](../../experiments/SIX-BIT-REUSE-20261111-001/SIX-BIT-REUSE-20261111-001-E001_witness_memory/learner.py), [runner](../../experiments/SIX-BIT-REUSE-20261111-001/SIX-BIT-REUSE-20261111-001-E001_witness_memory/run.py) and [saved readings and trace digests](../../artifacts/SIX-BIT-REUSE-20261111-001/SIX-BIT-REUSE-20261111-001-E001_witness_memory/result.json) reproduce the experiment. The first completed transfer took about 0.0006 seconds and the full measured run took about 0.10 seconds on CPU. The retained state and exhaustive exploration are part of the cost.

A [separately written check](../../experiments/SIX-BIT-REUSE-20261111-001/SIX-BIT-REUSE-20261111-001-E001_witness_memory/check.py) directly joined pairs of whole six-bit states and matched all twenty lower and upper readings for every run. It checked the first walk's 18 memory snapshots, checked the upper knot against the canonical test and rejected three deliberate changes to the recorded results. Replaying the producer reproduced every byte. The [verification record](../../artifacts/SIX-BIT-REUSE-20261111-001/SIX-BIT-REUSE-20261111-001-E001_witness_memory/verification.json) gives the scope of this separate same-task check (V1). All nine panels completed. The exploratory decision rule passed, which closes this finite test. The dominant work before the first transfer was specifying and implementing the learner and its observation interface.
