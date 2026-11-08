# TWO-BIT-20261108-001B-E003: interpretation

**The forcing route stalls at its first step on all 12 sampled survivors.** The control passed (the probe's product gives exactly
E001's 964 / 1,620 / 60 after arc consistency, at a 0.76 GB peak).
- **Parents are forced** in all 12: in no core collar can the central tile's children carry a label vector other than some s(a).
- **Arc consistency leaves off-law parent collars in all 12:** 177 to 996 pinwheel collars with labels the product's law does not
  list, and 0 to 270 non-pinwheel collars. One product, 01101/10001 x 10001/00010, keeps no non-pinwheel collar (only 209 pinwheel
  collars with other labels); one keeps a single one (00111/10000 x 11101/00001).
- **The torus searches found no crystal.** For the first three products in sample order, 20 seeds each: on two of them no seed grew a
  patch from which periods could be read, so no lattice was tried; on the third, 124 lattices were tried (103 invalid for the seed,
  21 exhausted). The run does not record whether a failed patch died or ran out of steps, so it says nothing about those seeds.
- **What it shows.** As for one bit, local consistency does not settle these products: their off-law parents survive it. Whether any
  of them forces the pinwheel stays open; the product that keeps only label defects is the sharpest candidate.

**Process notes.** The run is the epic's stress test TWO-BIT-B1 (ticket B retired into it at the preliminary closure), under unit
two-bit-b3 with a 16 GB cap; 782 seconds. The factors' level-one collars run from 925 to 1,318,912 (the one-bit decoration 01001/01011
has the most), and arc consistency cuts every factor to 235–976.
