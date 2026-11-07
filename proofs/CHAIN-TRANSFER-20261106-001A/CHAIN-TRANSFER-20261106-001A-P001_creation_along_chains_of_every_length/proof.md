# Creation along chains of every length

Status: Proved (a reduction to finitely many chain profiles, with the profiles and their verdicts computed exhaustively)

Ticket `CHAIN-TRANSFER-20261106-001A`, 2026-11-06.

## Question

- **Background (PENDANT-LINE C).**
  - **Exact contraction.** In a Fano tree, a line creates at another exactly when it does in the chain of their atoms.
  - **Up to distance two.** The touching rule holds up to distance two.
  - **Distance three.** It held at 18 places on 16 four-atom paths, but only as a computation.
- **The question.** Does the touching rule hold at every distance? The chain grows without bound, so a finite proof needs something
  finite that a chain carries from one atom to the next.

## Dependencies

- **`PENDANT-LINE-20261106-001A`.** The two-round rule and its local engine (`local_lib.py`).
- **`PENDANT-LINE-20261106-001C`.** Exact contraction in Fano trees (its item 3).
- **`TWO-BIT-SCREEN-20261105-001B`.** The block lemma, and the two-atom chains (`chain_lib.py`).
- **`BRACE-TREE-20261105-001B`.** Places in the tight-cut decomposition (`dict_lib.py`), used to read the built trees.
- **`NATIVE-GENUS-20261104-001A`.** The creation map and the splices (`genus_lib.py`).

## Setting

- **Fano trees.** These are spaces built from Fano atoms alone by the creation map's splices.
  - An atom minus a line, spliced at a point, emits.
  - An atom minus a point, spliced at a line, receives.
  - Every splice has the standard twist and any port permutation.
- **Creation.** It is the creation map's: knots of up to three points, against the four census far sides. "a creates at b" means that
  removing a creates a new knot at b for some far side.
- **Touching.** A line b touches its atom's cut toward another atom when its atom emits at that cut, or when b passes through the point
  its atom lost there (b is a cut line).

## Theorem

**In every Fano tree, a line a creates at a line b of another atom exactly when b touches its atom's cut toward a's atom.** With the block
lemma (lines of one atom create at each other), the whole creation relation of a Fano tree is fixed by its tree.

*Proof.*

1. **Reduction to chains.** By PENDANT-LINE C, a creates at b exactly when it does in the chain of their atoms.
2. **Chains are words.** Read the chain from a's atom A_0 to b's atom A_k. It is A_0, the Fano plane minus the removal a, followed by k
   splices, each at an element of the last atom:
   - **At a point.** The next atom loses a line and emits.
   - **At a line.** The next atom loses a point and receives.
   - **Letters.** Each splice is a letter: the element, the next atom's lost element and the port permutation. Every combination is
     allowed, so every chain is a word.
   - **No other choices.** All signs are zero (the Fano atom's). Relabelling and complementing points change no creation.
3. **Creation at b is decided at b.** By PENDANT-LINE A, a crossing knot is new exactly when the two-round rule does not reach it. The
   rule's verdict on a knot reads only the near side's relations on b's three points together with one or two further near points.
4. **The profile.** Stop the chain before a splice. The prefix meets the rest only at the element's three ports: a point's three copies,
   one on each of its lines, or a line's three points. Its profile is its solutions projected onto:
   - the ports (the port relation);
   - the ports and one further point (singles);
   - the ports and two further points (pairs).
   - **Why it is enough.**
     - The rest meets the prefix only at the ports. So the next profile is a function of this one and the next letter: a join over the
       ports, then a projection.
     - For the same reason, the near side's relations on a line of the last atom, with up to two further points, are a function of the
       last profile and the last letter.
   - **What can be forgotten.**
     - Complementing or swapping the further points of a single or a pair changes no constrained set.
     - Permuting the ports is absorbed by the next letter's permutation.
5. **Finitely many profiles (check 4).**
   - **Start.** Every removal and first element gives one of 3 profiles.
   - **Closure.** Closing under every letter adds 13, 24 and 7 profiles at the next three splices, and none after.
   - **So.** Every chain, of every length, ends in one of 47 profiles.
6. **The verdict (check 5).** Take each of the 47 profiles, every last atom (its lost element and permutation) and each of its lines.
   The two-round rule creates exactly when the line touches the last cut: 12,894 of 12,894. ∎

## What the profiles show

- **Free ports.** Every profile has the full port relation: all eight patterns.
  - **What it means.** At every cut between the removal and b, the removal's side of the chain shows all eight patterns on the cut's three
    ports.
  - **Where the constraint comes from.** A removal frees the ports of every cut beyond it, at every distance. What the near side shows
    there is decided by the intact side beyond the cut.
- **Creation is decided in the receiving atom.** Compute the verdict from the last atom alone, with free ports and no point behind its
  cut. It equals the full verdict in all 12,894 cases. Points further down the chain never add or remove creation.
- **Far sides.**
  - Cut lines receive creation from all four far sides.
  - Emitters' lines receive it from the Fano plane and census 58 always, from census 6 in 1,848 of 5,544 cases, and never from
    K4^(3).
  - Intact lines receive it from none.

## Validation

- **Check 1. The reduction at the gluing line.** On every two-atom chain, creation is computed from the near side's relations on the
  line and up to two further points. It equals the creation map at all 45,864 removal–line pairs, far side by far side.
- **Check 2. The automaton on built chains.**
  - **The chains.** Random chains of two, three and four atoms, built by the creation map's own splices.
  - **The verdicts.** At every line of the last atom, the automaton's verdict equals the creation map far side by far side.
  - **The ports.** At every cut, the prefix shows every pattern on the points it shares with the rest of the chain. When the removal is
    itself a cut line, the third port lies on no other line of the prefix, which leaves it free.
- **Check 3. Whole trees.** On random Fano trees of three and four atoms, of any shape, the exact creation map equals the block lemma
  with the touching rule at every pair of lines.
- **Further replays.** Ticket B computes the exact creation maps of trees of six and seven atoms.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The reduction at the gluing line, on every two-atom chain | 45,864 of 45,864 removal–line pairs equal, far side by far side |
| 2 | The automaton on 240 built chains of two to four atoms | 1,557 of 1,557 last-atom lines equal; all 480 cuts free (74 sharing two points); solutions equal to SAT enumeration on all 240 |
| 3 | The whole relation on 20 random trees of three and four atoms | 8,904 of 8,904 pairs (2,294 in one atom, 6,610 in different atoms) |
| 4 | The reachable profiles | 3 initial, then 13, 24, 7 and 0 new: 47 profiles, all with free ports |
| 5 | The touching rule on every profile and last atom; the last atom alone decides | 12,894 of 12,894; last atom alone 12,894 |
| 6 | Controls: simpler rules disagree | "every line receives" agrees in 8,694, "only cut lines" in 7,350, "only emitters' lines" in 9,744 |

## What this does not establish

- **Other far sides, and knots of more than three points.**
- **Spaces with plane glue or non-Fano handles.**
- **Other twists.** Twists other than the standard one: by TWO-BIT-SCREEN B check 1, the other twist that keeps a knot space differs
  from it by complementing a side.

## Novelty

- **New here.**
  - The profile automaton and its closure.
  - The touching rule at every distance.
  - Free ports.
  - Creation decided in the receiving atom.
- **Method.** Carrying a bounded interface along a decomposition is the classical finite-state method for tree-like structures. Its use
  here is standard; we know of no prior statement of these results.
