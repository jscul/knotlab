# What every one-strand test can recover

November 14, 2026 (Pacific). Goals G3 and G16.

## The question

How much of a table of possible pairs is determined by all equality tests on one strand after any word in the crossing and its inverse? Compare finite exact memory with the first ambiguity for prime alphabets.

## Prior work in the program

`scripts/track.py objects "braid reader" --until 2026-11-14 --exclude BRAID-READOUT-20261114-001 --limit 3`

`scripts/track.py objects "separable code" --until 2026-11-14 --exclude BRAID-READOUT-20261114-001 --limit 3`

`scripts/track.py objects "ternary strand" --until 2026-11-14 --exclude BRAID-READOUT-20261114-001 --limit 3`

- `CHEAP-COUNT-20261112-001` studied Description length and code mass of the counting descriptions found. The present table consists of ordered pairs of field elements, tested at crossing powers.
- `LEVEL-RETURN-20261113-001` studied Automatic states of alternating addressed patterns at every level of one parity. The present table consists of ordered pairs of field elements, tested at crossing powers.
- `SHORT-DESC-20261112-001` studied Finite not-all-equal patterns sampled by short descriptions with reuse and self-substitution. The present table consists of ordered pairs of field elements, tested at crossing powers.
- `SHIFT-LOCK-20261112-001` studied Harmony copies on two copy shifts bound by the mixed knot. The present table consists of ordered pairs of field elements, tested at crossing powers.
- `HARMONY-ARITH-20261112-001` studied Allowed state periods and antiperiodicity of one-shift harmonies under four laws. The present table consists of ordered pairs of field elements, tested at crossing powers.

The finite stop-or-undo comparison in STRAND-RETURN-20261114-001 motivates the question. The crossing and its semantics are defined afresh. BRAID-ACTIONS-20261114-001 and BRAID-REUSE-20261114-001 study learning and reuse. The earlier proof NATIVE-HARDNESS-20261024-001C settles decision for twice-used Boolean distinctions; reproducing it was dropped before a proof family was opened.

## Prior work outside the program

Kautz and Singleton, Nonrandom Binary Superimposed Codes (1964), https://doi.org/10.1109/TIT.1964.1053689, supply the classical pair-intersection bound in coding terminology. The exact ternary observation classes and classification of minimum disjoint ties for these crossing tests are the local target. The scan is calibration; all claims below require direct proofs. No field priority is claimed.

## Evidence and stopping rule

Check every one of the 512 ternary tables. Independently count every class by inclusion–exclusion and check the next prime on a bounded sparse roster. For the uniform question use affine functions of the crossing exponent, compare disjoint and common-state tables, and try to refute the threshold. A field of prime size and one equality are explicit hypotheses. A different test or assignment size invalidates comparisons. Stop after the two classifications or a reproducible counterexample.
