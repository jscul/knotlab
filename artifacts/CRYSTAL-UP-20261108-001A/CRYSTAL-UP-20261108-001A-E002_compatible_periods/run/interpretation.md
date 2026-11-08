# CRYSTAL-UP-20261108-001A-E002: interpretation

**Primary observable: yes.** Of the 203 off-law parent collars of s = 10101 / 00110 used as seeds, 7 (all non-pinwheel collars)
complete 26 tori whose cut obeys the decoration's law in the run's check: crystals escaping the last one-bit decoration, 8 to 40
tiles per period (one of 8, two of 16, six of 20, three of 24, four of 32, ten of 40; several are larger periods of the same
tilings). The control passed: the constant decoration's rhombus seed completed 35 tori of 4 to 28 tiles that pass the same check.

**Secondary observables.** 198 seeds grew patches (5 grew none in either move order within the budget); 7,934 candidate periods
passed the compatibility filter, spanning 61,069 lattices of n(C) to 48 tiles, of which 31,872 also had every short vector
compatible and were tried (at most 200 per seed). Outcomes: 29,477 invalid (the seed collar has no consistent completion on the
torus), 2,369 exhausted without a torus, 26 completed. No attempt reached its budget. 3,080 seconds with 8 workers.

**What the crystals look like.** In every one, half the tiles have their legs parallel to the seed tile's and half are turned from
them by arctan(4/3), twice the pinwheel's angle arctan(1/2). The smallest (seed 71, 8 tiles, lattice (1, 2), (−16/5, 8/5) in
Euclidean units of the short leg) has four collars that are not pinwheel collars.

**Independence of the verdict.** The run's check (decor_lib's periodic labelling of the plane's cut) shares its library with the
search. The verdict is carried instead by `CRYSTAL-UP-20261108-001B`, whose check rebuilds every collar and the labelled law with
the knotlab note's standalone replay and checks all 26 crystals.

**Process notes.** E002 was frozen after E001 was stopped; its feasibility disclosure names the pre-freeze probe that led to
filtering every lattice vector up to the collar's diameter. The run was registered as CRYSTAL-UP-A2 in the long-running index.
