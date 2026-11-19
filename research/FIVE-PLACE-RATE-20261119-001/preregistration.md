# Sharp steady growth rate of the five-place branch systems

Does every branch system in DEAD-CAP's within-five class have steady growth at most the eleven-junction theta rate?

Let r be the positive root of 4r²(1+r)=1. Try a common critical majorant for branches through two- and three-member blocks and check the full profile list, including two two-member blocks with a spare distinction, an end with a ray, isolated larger blocks and the pointing identity. Check the rate numerically from the polynomial and with a coefficient control. If the comparison is only at the critical point, distinguish it from coefficient-by-coefficient dominance. Read the WALL-READ direction together with DEAD-CAP's explicit admissible start conditions. Give conclusions outside that class only if separately established.

**Decision.** Proof bounding every within-five branch system by 2.382975... or an explicit faster start.

## Prior work in the program

`python3 -B scripts/track.py objects "five places theta ceiling branch system 2.3830" --until 2026-11-19 --exclude FIVE-PLACE-RATE-20261119-001 --limit 3`

`python3 -B scripts/track.py objects "two and three block profile dead knots rates" --until 2026-11-19 --exclude FIVE-PLACE-RATE-20261119-001 --limit 3`

`python3 -B scripts/track.py objects "pendant rays branch radius theta exact" --until 2026-11-19 --exclude FIVE-PLACE-RATE-20261119-001 --limit 3`

DEAD-CAP proves the branch equations and rank classification, with precise exclusions S0/S3/S4/S6′. Its fastest sampled theta was compared numerically and equality was conjectured. WALL-READ points to the uniform comparison.

Other retrieved records, included with their scope given by the objects index, are `BLOCK-REACH-20261116-001`, `CHAIN-IDENT-20261119-001`, `DEAD-CAP-20261119-001`, `ONE-SIDED-PATH-SKETCH-20261115-001`, `RING-FORMULA-20261118-001`, `TWO-PRODUCT-SKETCHES-20261115-001`.
