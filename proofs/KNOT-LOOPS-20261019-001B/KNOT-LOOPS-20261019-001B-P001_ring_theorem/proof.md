# The ring theorem: which knots remember a loop

Status: Proved

Ticket `KNOT-LOOPS-20261019-001B`, 2026-10-19. The Lean file is
`RingKernel.lean`, checked by `check.py` with Lean 4.32.2, core only, using
only the standard axioms.

## Setting

A **link** is a relation on Boolean distinctions with three roles:
- one witness passed in;
- one witness passed out;
- d ≥ 1 middle distinctions.

Under the forgetting reading of K1–K3, a knot's excluded states contain no two
neighbours, that is, no two states that differ in one distinction. The kernel
assumes exactly this separation (`KnotLink`), so its results cover knots and
also links that exclude nothing.

For a value m of the middle distinctions, the **transfer** T_m is the 2×2
table of allowed (witness in, witness out) pairs.

A **ring** of copies passes each copy's witness out to the next copy's witness
in, with the last copy passing back to the first. After the witnesses are
forgotten, the ring allows a pattern of middle values exactly when some
witness assignment satisfies every copy, that is, when the composed transfers
have a fixed point.

## Theorems

1. **Transfer cases** (`transfer_cases`). Every transfer of a knot link is a
   permutation (the identity or the swap) or misses at most one pair.
2. **Exclusion** (`ring_excludes_iff`). A ring excludes a pattern exactly when
   every transfer along it is a permutation and an odd number of them swap.
   This holds for mixed rings, where the copies may come from different
   knots.
3. **A knot or nothing** (`ring_one_flip`). Two patterns that differ in one
   middle distinction are never both excluded.
   - So the excluded patterns of a ring contain no two neighbours.
   - With at least three middle distinctions, every ring therefore composes
     into a knot or into nothing.
   - This extends the composition result of `KNOT-FOUNDATION-20261019-001D`
     from one shared distinction to a closed loop.
4. **Parity** (`all_permutations_iff_parity`). A knot link's transfers are all
   permutations exactly when the link is a parity relation: the witnesses and
   the middle values have a fixed parity.
5. **Which lengths are remembered** (`ring_memory`). A ring of k ≥ 1 copies of
   one link excludes some pattern exactly when two things hold:
   - the link has a swap transfer;
   - either k is odd, or the link also has an identity transfer.

   `parity3_every_length` checks the parity knot itself.

## Counting

Statement 2 gives the number of excluded patterns directly. Let a link have S
swap transfers and I identity transfers among its 2^d middle values. A ring of
k copies excludes the sequences of permutation values with an odd number of
swaps. There are ((S+I)^k − (I−S)^k)/2 of them, out of 2^{dk} patterns. Two
cases follow:
- **Parity**, where S = I = 2^{d−1}: exactly half the patterns are excluded
  at every length, so the ring keeps one full bit.
- **Any other link**, where S + I < 2^d: the excluded fraction shrinks like
  ((S+I)/2^d)^k, so the memory of the loop fades exponentially with its
  length.

The counting step is elementary and argued here in prose. The census confirms
the formula exactly on all 9,108 ring placements.

## Proof

- **Transfers.** For fixed m, the excluded (witness in, witness out) pairs
  cannot contain two neighbours, so they are none, one, or a diagonal pair. A
  diagonal pair leaves exactly a permutation.
- **Rings.**
  - When every transfer is a permutation, the composite is the swap raised to
    the number of swaps, so the ring closes exactly when that number is even.
  - When some transfer T misses at most one pair, rotate the ring so T comes
    first. Composition preserves "no empty column", so the rest of the ring
    reaches witness 0 from some y₀ and witness 1 from some y₁.
  - T misses at most one of the pairs (0, y₀) and (1, y₁), so the loop
    closes.
- **One flip.** Changing one middle distinction of one copy changes only that
  copy's transfer. If both patterns were excluded, both transfers would be
  permutations with the same swap parity. But neighbouring middle values with
  permutation transfers must differ: otherwise two neighbouring states would
  both be excluded.
- **Parity.**
  - The swap bit flips with every middle distinction, so it equals a constant
    plus the parity of the middle values (`flip_parity_rule`, by induction on
    the middle values).
  - So the link allows a state exactly when witness in, witness out and the
    middle parity sum to that constant.
- **Lengths.**
  - With a swap value and an identity value, use one swap and k − 1
    identities.
  - With only swap values and odd k, use k swaps.
  - Conversely, an excluded pattern has only permutation values and an odd
    number of swaps. If k is even, at least one of its values is not a swap,
    so it is an identity.

## What is checked

| Check | Result |
| --- | --- |
| Lean 4.32.2 accepts the file with no messages; no `sorry`, `admit`, `axiom` or `native_decide` | pass |
| The six main theorems depend only on `propext`, `Quot.sound` and, for two of them, `Classical.choice` | pass |
| Control: a ring that excludes patterns with an even number of swaps | rejected |
| Control: links without the separation across middle distinctions | rejected |
| Control: memory at every length whenever there is a swap, without the identity condition | rejected |
| Control: parity links with the middle values left out | rejected |
| Agreement with the census `KNOT-LOOPS-20261019-001A-E001` | statements 1, 2, 4 and 5 hold on all 9,108 ring placements, and 2 and 3 also on all 82,824 mixed rings |

## Nearest known results

- **Composing transfer tables is the transfer-matrix method.** A cycle of
  two-place constraints is satisfiable exactly when the boolean product of its
  matrices has a nonzero diagonal.
- **Parity rings are Tseitin's parity contradictions on a cycle, read
  backwards.** An odd number of swaps is a nontrivial Z/2 holonomy. Local
  consistency checking (k-consistency) fails exactly on constraints that can
  simulate linear equations over a group (Barto and Kozik 2009, settling a
  conjecture of Larose and Zádori).

**Novelty:** known-overlap-likely. The mathematics is elementary. The
project's reading is that, among knots, only permutation (group-like)
transfers carry a loop, and only parity carries it at full strength.

## Scope

- Boolean distinctions only, with one witness passed between neighbouring
  copies, in rings. Networks with several loops and many-valued knots are
  ticket C.
- No claim about native recurrences, composed topology, paths, distance, space
  or physics.
