# Scoping for CLASS4-PAIRS-20261028-001B-E001 (not evidence)

All on free class 4 on (1, 1) at d = 5, p = 11, slots (1, 1, 2), unless stated; scripts and logs in the session scratchpad.

- **Value-level path test (P3, edges e₀ = (0, 1), e₁ = (1, 2)).**
  - At the full diagonal, every P3 equation equalled the single-edge prediction.
  - With e₀ off-diagonal on its own solutions and e₁ diagonal, every equation was local.
  - With e₁ off-diagonal on its own solutions and e₀ diagonal, vertex 0's and vertex 1's equations changed (30 of 33 rows at a random
    pair, 327 of 363 at a pair-failing difference); private equations and vertex 2 stayed local.
- **Mechanism.** Zeroing e₀'s slot-1 layer-1 data removed the change; zeroing e₀'s slot-2 data did not. For each of e₁'s 11
  solutions (0, 0, t, 6t, 2t), a unique translation (t, 4t) of e₀'s layer-3 slot-2 coordinates made vertex 0's and vertex 1's
  equations equal the local prediction on 40 samples. A canonical gauge (particular solutions vanishing on every reading strand)
  did not remove it. Reading: e₁'s bundle-1 conjugator has a layer-3 part at character 3 outside slot 1's roots; it shifts e₁'s
  zero strands (junctions), and the shift is absorbed upstream as a translation of e₀'s slot-2 leaf.
- **An edge over an isolated vertex** (edge (0, 2), vertex 1 between): vertex 1's equations stayed zero and the edge's equations
  equalled the single edge's, even for random off-variety data. Blocks between moved strands are conjugated uniformly (a gauge).
- **Affine form.** For fixed layer-≤2 data the layer-4 equations are affine in the layer-3 data. Global and assembled local systems
  had equal linear parts and constant parts differing by an element of the column space in 15 of 15 configurations (five shapes,
  three configuration types) for (1, 1) and for (1, 1, 1); partial runs on (0, 1, 1) agreed. The cumulative design failed (linear
  parts equal in 3 of 15, column-space test in 0 of 15).
- **Linear structure.** For (1, 1) the private equations were homogeneous affine in slot-2 data and the endpoint terms additive at
  a diagonal, a random and a pair-failing pair; for (1, 2), slots (1, 2, 3), the private equations were not affine in slot-2 data
  at the pair-failing pair (11 of 11 samples).
