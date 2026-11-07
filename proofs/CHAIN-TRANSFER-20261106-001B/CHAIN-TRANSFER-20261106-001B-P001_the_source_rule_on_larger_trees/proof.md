# The source rule on larger trees

Status: Proved (the source rule holds on every Fano tree of at most five atoms and fails on a tree of six; both by ticket A's theorem, the
failures also by exact computation)

Ticket `CHAIN-TRANSFER-20261106-001B`, 2026-11-06.

## Question

- **The source rule (BRACE-TREE B).**
  - **Blocks.** Within each piece of the creative part, take the maximal blocks of mutual creation.
  - **Blind sets.** A line a is blind to c when c creates at a and a does not create at c.
  - **Keeping.** Keep a block when one of its lines is blind to every line that any other line of the block is blind to.
  - **What it predicts.** The kept blocks count the Fano atoms, and so the genus.
- **The evidence so far.** It held on every space without a non-Fano brace that was computed: 47 in BRACE-TREE B and 110 fresh ones in
  BRACE-TREE C, of up to 26 points. A Fano tree of 26 points has at most four atoms.
- **The question.** Ticket A makes creation on any Fano tree a function of the tree. So the rule can now be evaluated on trees of any
  size without computing creation. Does it hold?

## Dependencies

- **`CHAIN-TRANSFER-20261106-001A`.** The touching rule at every distance (`transfer_lib.py`).
- **`TWO-BIT-SCREEN-20261105-001B`.** The block lemma.
- **`BRACE-TREE-20261105-001B`, `BRACE-TREE-20261105-001C`.** The source rule (`dict_lib.source_blocks`) and its evidence.
- **`PENDANT-LINE-20261106-001A`.** The two-round rule, for the exact computations.

## Results

1. **Up to five atoms it holds (check 1).**
   - **Scope.** Every Fano tree of at most five atoms, every splice sequence, up to the choices that leave creation unchanged:
     2 + 52 + 1,976 + 98,800 trees.
   - **Result.** The source rule keeps exactly one block per atom, for the first maximum quiet part and for every one.
2. **At six atoms it fails (checks 2 and 3).**
   - **The tree.** A receiver R takes cuts from two emitters at two of its points. Each emitter feeds a further receiver, its load.
     R emits the line through those two points to a sixth atom.
   - **The result.** The source rule keeps 5 blocks, for every one of the 96 maximum quiet parts.
   - **Exact confirmation.** The exact creation map, computed from all 31,250 solutions per removal by the two-round rule on the real near
     sides, equals ticket A's relation at all 1,332 pairs. The source rule on it keeps 5.
3. **Why (check 5).**
   - **Blindness.** A line of R is blind to a load's intact lines exactly when it passes through the point that load's cut took.
   - **No source.** The one line through both points is the line R emits. So no line of R is blind to everything another line of R is
     blind to, and R's block has no source.
   - **Each ingredient is needed.**
     - Keep that line in R (five atoms), or remove one load (five atoms), and the rule holds.
     - Three loaded cuts at non-collinear points of R (seven atoms) fail the same way. At collinear points the line through all three is a
       source, and the rule holds.
4. **In random trees (check 4).** Among 200 random trees each of 6, 7, 8, 10 and 12 atoms, the rule miscounts on 0, 2, 7, 9 and 19.
   It never miscounted on a path.

## Answer

- **The source rule is refuted.** It fails on Fano trees from six atoms on, and holds on every Fano tree of at most five atoms.
- **What survives.** BRACE-TREE's evidence stands. Its spaces had at most four atoms, where the rule holds.
- **What fails.** Its reading "kept blocks count the atoms" is not a theorem. A source needs a line blind to everything its block's lines
  are blind to, and an atom whose loaded receiving cuts share no line has none.
- **What replaces it.** Ticket C gives a rule that provably reads every Fano tree whose atoms have at most four cuts.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Every tree of at most five atoms (100,830): kept blocks = atoms, for the first and every maximum quiet part; the build's relation equals the tight-cut decomposition's on every 25th (4,036) | 100,830 of 100,830; 4,036 of 4,036 |
| 2 | The counterexamples and their variants | six atoms: 5 kept (96 of 96 quiet parts); seven, non-collinear: 6 (64 of 64); without the emitted line, with one load, or collinear: one block per atom |
| 3 | Exact creation maps of the two counterexamples | six atoms (37 points, 31,250 solutions per removal): 1,332 of 1,332 pairs equal, 5 kept; seven (43 points, 156,250): 1,806 of 1,806, 6 kept |
| 4 | 200 random trees and 200 paths at each of 6, 7, 8, 10 and 12 atoms | trees miscounted: 0, 2, 7, 9, 19; paths: none |
| 5 | The mechanism on the six-atom tree | the receiver's two lines through each point are blind to that point's load; its two other lines to neither |

## What this does not establish

- **Spaces with plane glue or non-Fano handles.** The source rule was also meant for these. Nothing here tests it there.
- **Whether some other block-keeping rule counts every Fano tree.** Ticket C reads the tree a different way.

## Novelty

New here: the exhaustive test up to five atoms, the counterexamples and their mechanism.
