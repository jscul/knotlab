# The advisor's answer (Fable 5.2, claude-fable-5-2), before the freeze

Advisor's answer for `SIDE-SIGN-20261126-001`, before the freeze. I could not run anything, so every claim below is `unverified` unless I say which lines I read. The main finding is in point 4: I expect P4 and P6 to fail on a named census start.

## The finding to check first: a W2 hit at round 0

By hand, W2 under parity and R1 gives the literature's PR box (CHSH 4) on this census start:

- **The start:** five knots; pairs (0,1), (0,4), (2,3), (2,4) share one distinction; pairs (1,4), (3,4) share two; loose counts (1,0,1,0,0). That is 10 distinctions, every knot has at least three places, so it is in `starts.json`.
- **The swap:** 0↔2, 1↔3, knot 4 kept. Sides are {0,1} and {2,3}, two-sided, and the minimal and maximal lifts coincide.
- **The readers:** each side has exactly two candidate distinctions, so there is one placement. Reader 1 reads s (loose on knot 0) or s₂ (shared by 0 and 1); reader 2 reads their images.
- **The tie:** the sum of all five knot rows is s + σ(s), so x_s = x_σ(s) on every allowed state. I found no other relation among the four reads: a set of knots whose row sum lies in the four reads must be all five.
- **The weight:** W2 = (−1)^((a₀+a₁)(b₀+b₁)) on the set a₀ = b₁. This is control C2's weighting exactly.
- **The tables:** Z = 16; correlations +1, +1, +1, −1; every pair table nonnegative.
- **Under R2:** the same hit, since every pair table has entries 0 or one constant.
- **Scaffolds:** it survives both swaps of P7 trivially. There is no kept twin for the lifts to differ on, and W2 does not change with the value convention when a side has an even number of distinctions.
- **Separation:** the two sides' knots meet only through knot 4, so it also passes `forbid.py`'s stricter criterion.

Run this one start before freezing. If it holds, the freeze should say what such a hit means: W2 on sides of two distinctions is the Abramsky–Brandenburger sign written on the readers' own four reads, and the pattern supplies only the tie.

## 1. A1 (growth keeps every swap)

- **Knot level: I found no mechanism that breaks it.** I read `freelib.py` lines 67–176, `fastlib.py`, `rival_growth.py` and `naelib.py`. Groups are a label-free family; the fresh count depends only on p, D and the implied flag; the implied flag is a property of the structure under both laws. The label-ordered allocation only chooses among one parent's loose distinctions, which `Pattern` cannot tell apart.
- **Distinction level: A1 as worded fails.** A lift need not extend. Test on N1: the five-ring, reflection keeping knot 0. Round 1 joins knots with a common neighbour, so knot 0 is in groups {0,2} and {0,3}, which the reflection exchanges. The extension must exchange knot 0's two loose distinctions; the round-0 minimal lift keeps them.
- **The converse case:** the four-ring, reflection through knots 0 and 2, maximal lift. Knot 0's loose distinctions go to a join and an offshoot, so they cannot be exchanged.
- **Consequence:** W1's pairs and the one-sided or two-sided kind are not carried from round to round. The pre-count's fall in one-sided swaps under the maximal lift (809, 636, 377) fits this.
- **P1 is not yet a prediction.** `precount.md` gives only totals, not a per-start tally, and the pre-count has already run. P1 must also exclude stages that close or stall.

## 2. A2 and A3 (the twist's trace in the states)

- **There is a finer trace: the mismatch x + σ(x).** Kept and flipped are two of its values (nothing, and everything). Under parity it is a linear map from the allowed states to kept allowed states.
- **"Flipped on the moved distinctions" is missed.** States with x + σ(x) equal to all the moved distinctions need only that every knot holds an even number of moved distinctions. A2's emptiness under parity comes partly from requiring the full complement. Count these.
- **The loop claim is true but nearly empty.** What reads the twist is the two-distinction read x_d + x_σ(d), the two ends of an open chain. That is outside the frozen single reads; say so.
- **W1 on kept states needs no A275.** It is the sign of the swap as a permutation of the distinctions the state holds. Under parity it is a character on the kept states.

## 3. A4 (a swap and the classes)

- **Correct for exactly two classes.** A renaming carries H to H and acts linearly on S/H; when S/H has two elements, that action is the identity.
- **The README's argument fails for four or eight classes.** `TWO-CLASS-SIGN` records 24 starts with four classes and 2 with eight. There a swap keeps the class of the all-0 state but can permute the others, and can carry one class sign to another. Check: compute the swap's action on S/H for those 26 starts and for grown stages with more than two classes.
- **P3 compares W3 with W5 at round 0,** where the other thread finds no classes. W5 there is only a character. My hand count agrees with P3: the six-ring's half-turn gives W5 = −1 on flipped states (three pairs), the four-ring's gives +1.
- **A cheap addition to `named.py`:** compare W5 with W1 on kept states.

## 4. A5 (characters give no excess)

- **No counterexample exists, and the proof is shorter than C4.** A character's sums over the completions of the four reads are a character on the image, or all zero. Z is the sum over the whole support, which is 0 unless the character is trivial there, and then the weighting is nonnegative.
- **So W5 and W3 under parity always have Z = 0 and fail G0.** P4's "no hit for W3 or W5" is empty; report it as "G0 fails", not as a test passed.
- **Under R2 a character gives at most 2.** Each pair table is uniform on a subspace of the two read values, so correlations are 0 or +1, and three +1 force the fourth.
- **The pushforward lemma for degree two is right.** I rederived it: the size is constant on an affine support, the sign quadratic.
- **`controls.txt` does not support the cross-tie claim.** It prints only "512 weightings above 2", not "only on eight-word sets with a cross tie". P4's last clause rests on that; make C4 print the breakdown.
- **A lemma for W2 to check.** Its sum over the completions of four reads is nonnegative (so at most 2, by Fine) unless both sides' parities are functions of the four read values. Hits can only come from small sides plus a tie, as in the start above.

## 5. Readings and gates

I found no arithmetic error in `best_chsh`. A referee would press these, in order:

1. **G1 is checked only on the four pair tables.** By Fine's theorem every R1 hit has a negative entry in the table of all four reads. Nothing in the model stops a reader reading both its distinctions, so the incompatibility of a reader's two reads is supplied. It is not in the scaffold table.
2. **The separation differs from `BEYOND-REJECTION`'s frozen design.** `forbid.py` line 273 skips readers whose holders meet; `sides.py` lines 417–420 only require no common holder. Record for every hit whether the holders meet. G3 there was "every complete record", here single values.
3. **R2 is a postselection.** It projects every unread distinction before squaring. Equal normalizers (G2) do not close the literature's detection loophole. Report the retained fraction, and run U under R2 on not-all-equal as a control.
4. **A reader is any two moved distinctions** in the one-sided and several-sided kinds, with nothing tying the two to one reader.

Two practical points:
- **Memory:** `bits()` makes uint64 temporaries of states × D × 8 bytes, about 1.4 GB each at 2²² states and 42 distinctions. Cap the run.
- **Coverage:** census parity stages over 2²² states are "not run" although the exact-sum path could do them. Most round-2 not-all-equal stages will exceed the cap (D reaches 42); report the count.

## 6. Missing candidates

- **Every weighting in the table is unchanged by the swap.** None is odd under it, which is the most literal "sign to the sides". A candidate: +1 when side 1 holds more than side 2, −1 when fewer, 0 when equal. Z = 0 always, so R2 only. At mirrored reads (s, σ(s)) the two readers never agree, and mirrored placements give at most 2 by the symmetry.
- **W1 restricted to kept states** (point 2), and W3 on the moved distinctions.
- **The sign of the swap on all allowed states is already `labels['det']`.** Under parity it is −1 only when exactly two states are kept: an accident of counts. The same holds per reading.
- **A sign from a lift** is W1 on the twin pairs; nothing new.
- **W1c is W1 times the parity of the moved distinctions,** up to a constant. Where that parity is constant on the allowed states, the convention swap tests nothing; count those stages.
- **Mixed lifts** (some twins exchanged, others not) are not conjugate to the minimal or maximal lift in general. Put them under "Not shown".

## 7. My numbers

| # | Chance it holds | Note |
| --- | --- | --- |
| P1 | 95% | For knot permutations, excluding closed and stalled stages |
| P2 | 99% | A2 is a proof |
| P3 | 90% | |
| P4 | U, W3, W5 certain; W1/W1c/W2 about 10% | W3 and W5 by G0, empty. I expect the W2 hit above; at rounds 1 and 2 alone, about 50% |
| P5 | 50% | No exact ties under not-all-equal, so CHSH 4 is out, but values just above 2 are open |
| P6 | 15% | The same start hits under R2 |
| P7 | 30% | The W2 hit survives both swaps trivially |
| P8 | 70% | |

My guess for where hits come from: round 0, two-sided swaps whose sides have two or three distinctions, stages with exactly two loose distinctions exchanged by the swap, W2, with reader 2's reads the images of reader 1's.

The hivemind has one consultation entry and one standing fact (the two separation criteria), both marked `unverified`.
