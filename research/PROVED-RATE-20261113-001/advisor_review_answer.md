**Verdict:** λ is right as a liminf and as a lower-bound rate, but not as an exact limit in general, and "λ = 0 iff bounded" is too strong as stated.

**Rate computation**
- **Lower bound holds for all s:** any walk is a simple path plus cycles, so L(s) ≥ λ·(s − |V|). So λ > 0 gives linear growth for every s, provided the graph is complete.
- **Upper bound holds only along residues:** fixed length matters. The trimmed graph is not strongly connected, so lengths in some residue classes may be forced through other SCCs with a larger mean. λ = liminf L(s)/s, and the limit may not exist.
- **λ = 0** therefore shows boundedness only along an arithmetic progression. Full boundedness needs a per-residue check, monotonicity of L in s, or the exact vector repeat you already have.
- **Simplification:** zero-mean cycles are exactly cycles of the empty-W map, so λ = 0 iff some empty-W-periodic node is reachable and co-reachable. Karp is only needed for the positive value.
- **Capped graphs:** a partial graph gives λ_partial ≥ λ. A zero is conclusive, a positive value is not.
- **Gate:** it checks transitions, not completeness. Completeness is shown by an empty frontier.

**Settled**
- The 204 exact-repeat families have bounded L_ray.
- Nothing is settled about growth until the graphs are complete.

**True bond**
- Assuming the ray is a restricted witness shape, L_ray ≥ the true bond.
- Boundedness transfers to the true bond; λ_ray > 0 shows nothing about it, because side branches may be cheaper. It only rules out ray-shaped witnesses.

**Thresholds**
- P1 has thin margin: there are 651 families, and the 44 over-cap ones alone are 6.8%.
- P2 and P3 test whether 30 steps predicts the asymptote, not anything about the bond.
- Count P2 only on complete graphs, and P3 per residue.
