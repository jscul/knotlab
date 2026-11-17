# Referee report KEEP-REACH-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **What holds.**
  - Theorems K and F′ and Lemma E are correct.
  - `two_orbit.py` is a faithful copy of the refereed every-depth routine, with only the property changed. An independent SAT
    computation of the two-orbit bonds agrees with it in all 145 cells checked.
  - Actual-value forgetting holds at every remaining depth for all 14 patterns that claim it.
  - The two finite cut-offs the owner worried about (level 16, and s = 13..16) cover the sequences' cycles.
- **What needs fixing** is wording. Three summaries say more than was shown about the 25 patterns that never forget even on actual
  values, whose boundedness is exactly what Conjecture C′ leaves open.

## What holds

- **Theorem K (proved; Not a block).** The joint of two orbits is the exact projection of P_N onto them (Theorem W). So a set inside
  the two orbits is constrained, or free, in P_N exactly when it is in the joint. A bond of the joint that meets both orbits is
  therefore a bond of P_N meeting levels k and k + s, and L_N(k, s) ≤ b_N(k, s). The every-depth computation is the refereed routine
  with its property read changed.
- **Theorem F′ (proved; Not a block).** The referee rechecked the splice against Theorem F's proof (`BLOCK-REACH-20261116-001A`).
  - **The splice.** Take a window of r groups between an orbit O and a descendant orbit O′, with B's members on both sides and none
    inside. Then α (realizing B's upper part) and β (its lower part) take values α|O ∈ P_O and β|O′ ∈ P_O′.
    - Because the joint J(O, O′) is the product P_O × P_O′, some state γ has γ|O = α|O and γ|O′ = β|O′.
    - The window region (path orbits with their side subtrees) meets the rest of the pattern only at O and O′ (Theorem W).
    - So α outside, γ on the window and β below is a state, and B would be free.
  - **The windows used.** Case 1 uses windows whose top orbit lies at a level ≥ k. Case 2 still has s − 1 groups below level k on the
    path. So the count 2 + ⌊(s − 1)/r⌋ = 1 + ⌈s/r⌉ needs the product property only from level k.
- **Lemma E (proved; Not a block).** With x and y exposed by T and T′ and the pair (x, y) missing, no state has x's values on T and
  y's on T′, so T ∪ T′ is constrained. T and T′ are free, so a minimal constrained subset meets both orbits and is a bond of at most
  |T| + |T′| members.
- **(a) `two_orbit.py`'s copy of the routine.**
  - **Line by line**, `every_depth_cross` is `window_tree.every_depth_pairs`: the same S0 construction, the same first-coordinate
    filter, the same advance and periodicity, the same remaining-depth tiers and the same finite-N branch through `pair_joints`.
    Only the property differs: the least cross bond, minimized over pair types, in place of the tie and three-member flags.
    `least_cross_bond` tests constrained-with-every-(size − 1)-subset-free, which suffices since freeness is closed under subsets.
  - **Independently** (`referee_two_orbit_sat.py`, `.json`), the referee recomputed b_N(3, s) at N = 8 by SAT:
    - P_N is the census's `pattern(key, N)`, the object under study;
    - orbits are the referee's own components of each level under the used words;
    - every joint comes from CaDiCaL extension checks of every assignment of the two orbits;
    - the least two-orbit bond is the referee's own search.

    This covered s = 1..5, so remaining depths 4 down to 0, for 29 patterns: the four census ones, all 13 "products" mutants and
    all 12 "hidden" ones. All 145 cells equal the routine's value. Examples: ca1efb37ad88 4, 6, 6, 6, 6; 8db5da810c00 3, 4, 5, 5,
    5; its mutant -73 3, 4, 5, 5, none; bace53f8f952-111 3, 5, none, none, 5. The four census values settle at 6, 4, 5 and 4, as P1
    says.
- **(b) Actual-value forgetting, to level 16 with r ≤ 10.**
  - **The cut-off is enough** (`referee_cutoffs.py`, `.json`). For all 39 third-class patterns, the sets of orbit states enter their
    cycle at level 3 or 4 with period 1 or 2, so levels ≤ 16 cover every level.
  - **Every remaining depth is covered.** All 14 "forget on actual values" patterns have r₀ = 0, so the stable depth used by
    `analyze_third.py` is every remaining depth, as F′'s hypothesis requires.
  - **Independently, by SAT at N = 8** (r = 1 for one pattern, 2 for 13), every joint of an orbit at level j ≥ 3 and an orbit r
    levels below inside its subtree is a product, at every level up to N − r and remaining depth down to 0. There are 0 non-products
    in 14 of 14.
- **(c) The "hidden" verdict, read at s = 13..16 only.** The pair-state sequence from level 3 starts its cycle by s = 5 (s = 3 for
  two), with period 1 for the 12 hidden patterns and 2 for the 13 product patterns. So s = 13..16 covers every eventual pair state,
  and the verdict stands at stable depth. The absence of a two-orbit bond at some s also holds at finite depth, by the SAT check:
  none at s = 5, N = 8 for the hidden ca1efb37ad88 and bace53f8f952-58 families; none at s = 3 and 4 for bace53f8f952-111 and -147.
- **The certified depth-11 values.**
  - **What the engine guarantees.** The census engine returns an integer L only from a completed increasing-size search
    (`optimality_proved: True`); budget expiry gives "undecided". So the integers 3, 4, 5, 5, 6, 6 and 3, 4, 5, 5, 5, 5 are
    certified by its semantics.
  - **What the files show.** `exact_third.py` records `bond` and `optimality_proved` as null, because it reads them at the row's top
    level, not from `row['anywhere']`. The certification is not visible in the files.
  - **What the referee did.** These two searches were not repeated, and the pending depth-13 stress test is not refereed.

## 1. What is shown about the 25 that never forget on actual values (Narrowing, wording)

**What is shown:**
- **The 14 "forget on actual values" patterns grow at every depth** (F′, with the product property checked). They never forget on
  all assignments, so "never forgets on all assignments does not imply a bounded reach" is proved by them.
- **The other 25 never forget even on actual values, and lack a two-orbit bond from the top at some s.** Their boundedness is open:
  it is Conjecture C′'s open direction.
  - *The 13 products.* One, 8db5da810c00-73, exceeds its parent's bound at depth 11 (6 against 5 at s = 5 and 6). That is not shown
    to be unbounded, and the other 12 were not read deep.
  - *The 12 hidden.* The census search decided none of their cells past s = 2 at depth 11.

**Three summaries say more than this:**
- **The proof note:** "'Never forgets', even on actual values, does not imply a bounded reach." No pattern that never forgets on
  actual values has been shown to have an unbounded reach. Fair: "does not imply a two-orbit bond from the top; whether it implies a
  bounded reach is Conjecture C′'s open case".
- **The goals checkpoint:** "never forgetting does not keep the top bound in 39 of 2,380". Fair: "in 14 (growth proved by F′); the
  other 25 lack a two-orbit bond from the top, and their boundedness is open (one exceeds its parent's bound at depth 11)".
- **The intuition entry:** "keeps the top bound only when it starts at the top and its dependence is exposed ... proved". The "only
  when" is C′'s open direction. What is proved is the "when" (Theorem K), with the converse proved only where F′ applies.

The note's own "Conjecture C′ ... proved in one direction (K) ... open on the 25" and "So the mutant has passed the parent's bound"
are accurate.

## 2. Smaller points (Not a block)

- **Records.** Have `exact_third.py` write `row['anywhere']` (L, bond, `optimality_proved`, the certificate summary) so the
  certification is in the record.
- **The census counts.** The classification (2,380 alive small-orbit patterns; 1,081, 1,260 and 39; 14, 13 and 12) was not
  recomputed. The referee checked the routine and the two read-outs it rests on.
- **Words.** "Exposed" and "hidden" are new words for the two kinds of dependence. They are defined in Lemma E, but should be run past
  the advisor before they enter the glossary.

## Fixes for the thread (listed for the owner, not folded in)

1. **What is shown about the 25.** Narrow the three summaries in §1: the proof note's "even on actual values, does not imply a
   bounded reach", the goals checkpoint's "does not keep the top bound in 39", and the intuition entry's "only when ... proved".
   **Narrowing.**
2. **The record.** Record the certificate fields of the depth-11 searches. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the predictions, the proof, `two_orbit.py`, `classify.py`, `analyze_third.py`, `exact_third.py`, the refereed
    `window_tree.py`, Theorem F's proof and the census engine's search;
  - wrote an independent SAT check of two-orbit bonds and of actual-value forgetting (`referee_two_orbit_sat.py`);
  - wrote a cut-off check (`referee_cutoffs.py`).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- `referee_two_orbit_sat.py`, `.out` and `.json`: b_8(3, s) by SAT for 29 patterns against the routine; product joints for the 14.
- `referee_cutoffs.py` and `.out`: the cycle starts and periods behind the level-16 and s = 13..16 cut-offs.
