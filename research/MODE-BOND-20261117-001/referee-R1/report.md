# Referee report MODE-BOND-R1 (fresh code, no Codex)

**Verdict: Confirmed. No Block.**

The 13 descriptions (5 distinct patterns) grow linearly, as claimed. The pieces:
- **Lemma J** is correct.
- **Theorem G on a component** is correct, including the owner's points (a) and (c).
- **The block reading** that puts the self-similar type outside the top's component holds at every depth: it is a statement about
  types, and a referee union-find at depths 9, 11 and 13 agrees.
- **"All 583 decided"** is exact. No group of identical descriptions mixes classes, so 244, 323 and 16 are exact counts, not
  inferred ones.

There are two wording points, and a recommendation on the TWO-ENDS reading (a lesson and a status update, not a correction of a
false claim).

## What holds

- **Lemma J (proved).**
  - Two components share no knot, so the states of P_N are the product of the components' states.
  - A set split across two components then projects as a product. So if it is constrained, one part is, and it is not minimal.
- **Theorem G on a component (proved; the owner's points (a) and (c)).**
  - **(a) The joined-path lemma.** Let O be an orbit of a bond's skeleton below level k. O holds a member or lies above one.
    - If O's step from its parent were unjoined, O's subtree would meet the rest of the pattern only through the parent's block.
      That block holds no knot on O, so the subtree would be disconnected.
    - Every member under O would then be in a component lying inside that subtree, not in the top's component C.
    - By Lemma J the bond lies in C, so every skeleton step below level k is joined. Every crossing of a member-free window
      therefore runs along joined steps.
  - **(c) Unjoined children.** An unjoined child's subtree touches nothing above it, so its feasibility constrains only its own
    assignment. Quantifying it leaves the parent's composite unchanged. Here F holds every assignment anyway (r₀ = 0). Nothing more
    is needed.
  - **The rest.** Theorem G's factorisation (TWO-ENDS-R1, item (c)) then applies to the joined composites.
- **The self-similar type never meets level 3, at every depth (the coordinator's first question).**
  - **Proved from the type table** (`growth13.json`), and the referee rechecked the logic:
    - in types 4, 5 and 7, only child 0 is joined;
    - type 7 occurs only as child 1 of types 4 and 5, and as either child of type 7.
  - **How a type-7 component runs.** It goes up only along joined first children of type 7. It stops at a type-7 orbit that is an
    unjoined child, at level 4 or below. Downward, it follows first children only.
  - **Why this holds at every depth.** The type table does not depend on N, so the statement holds at every depth.
  - **The referee's union-find** (`referee_mode.py`, item 1) on the knot triples of `pattern(key, N)`, for the 5 distinct patterns
    at N = 9, 11 and 13:
    - all level-3 addresses lie in one component;
    - the carrying orbit [3, 7, 9, 15] at level 4 (the one whose line TWO-ENDS-R1 found non-product) and every one of its
      descendants lie outside it;
    - the top's component holds 2, 4, 8, 12, 20, 28, 44, 60, 92, 124, 188 and 252 addresses at levels 1 to 12 (N = 13), the same for
      all 5 patterns.
- **On the top's component the long composites are products** (the owner's point (b)).
  - **Pair projections** (item 2, SAT on P₁₁). For every orbit at level 3 or 4 in the top's component and every orbit 5 or 6 levels
    below it, inside its subtree and the component: 92 of 92 joints are products, for each of the 5 patterns.
  - **Outside the component**, 328 joints are products and 2 are not, the carried line. That is where TWO-ENDS's non-product
    composite lives.
  - **Composites directly** (item 5): the projection of the knots inside O's subtree alone, with nothing above O, onto O and an orbit
    5 levels below in the top's component.
    That projection is the saturated composite. All 38 are products for each of the 5 patterns (N = 11).
  - This agrees with `growth13.py`'s joined automaton (ℓ₀ = 5) and with the study's own gate.
- **Lemma J's sanity** (item 3). Both certified bonds of 7 at depth 12 lie in one component, the top's.
- **"All 583 decided" is exact** (the coordinator's second question; item 4).
  - The 2,380 descriptions form 583 identical-pattern groups at N = 9. No group mixes verdict classes.
  - By distinct pattern:
    - 244 forget, so they grow by Theorem F;
    - 323 have a two-orbit bond at every s, so they are bounded by Theorem K;
    - 16 are third class: 6 grow by F′, 5 are bounded by K\* and 5 grow by this study.
  - The note's 323 was inferred ("if every group carries one verdict"); it is now checked.
  - So every pattern of the population is decided. In every bounded one, the reach is held by a bond in bounded pieces at the two
    ends: two-orbit, block or stem bonds.
  - "C\* with two ends fits the whole population" is fair as scoped to this population.

## 1. Wording (Not a block)

- **"It did not point to the disconnection, nor did the two referees or the earlier studies."** That is accurate. TWO-ENDS-R1
  (this referee) found the split link by SAT on whole-pattern pair projections and did not check components.
  - That report's fix 4, "add the split channel to direction 1's search", is now moot: no bond meeting level 3 can use either link.
- **"Proved with finite checks (SAT gate at depth 11)".** The disconnection is proved from the type table for every depth. The SAT
  gate and the union-find are checks, not the proof. Say "proved from the block types; checked at depths 9 to 13".
- **The ca1efb37ad88 controls (MODE-BOND-A1)** are pending and not refereed. Nothing rests on them.

## 2. The TWO-ENDS reading: lesson or correction? (the coordinator's third question)

- **What TWO-ENDS said.** For the 13:
  - "one carried mode blocks the test";
  - "a bounded bond … would need a piece near the top that forces such an orbit to be all equal";
  - in the proof note, "A bond across a long stretch must use that mode";
  - in the intuition entry, "Reach stays bounded only if the top can tie itself to such a frozen strand".
- **What MODE-BOND shows.** The mode lies in components that never meet level 3, so no bond with a member at level 3 can use it.
- **Is any statement false?**
  - "The test fails" is true, for the whole-pattern product test.
  - "The 13 remain open" was true when written.
  - "Would need a piece near the top …" and "must use that mode" are true as implications, vacuously, since no bond meeting level 3
    crosses a long member-free stretch.
- **But they were read as live possibilities.** They steered the selected direction and the referee's fix 4.
- **Recommendation.** Log it as a lesson, with a status update ("superseded by MODE-BOND: the mode never meets the top") beside the
  four TWO-ENDS sentences, not as a correction of a false claim. If the program prefers a record in `docs/CORRECTIONS.md`:
  - verdict Not a block;
  - lesson: "check that a carrier shares a component with the end before reading it as a route".
- **The stale summaries.** TWO-ENDS's "the 13 remain open" in its intuition entry and goals line should point to MODE-BOND.

## How the work was split

- **The referee:**
  - read the note, the proof, `growth13.json`, `gate_growth.json` and the predictions;
  - checked Lemma J, Theorem G on a component and the type argument by hand;
  - wrote its own union-find components, SAT pair joints and subtree composites, the bond check and the population count
    (`referee_mode.py`), reusing its own SAT tools from `CARRIER-R1`.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_mode.py` and `.json`:**
  - 1, components at N = 9, 11, 13;
  - 2, pair joints at N = 11;
  - 3, the bonds of 7;
  - 4, the population by distinct pattern;
  - 5, composites on the top's component.

Reproduce, from `research/MODE-BOND-20261117-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_mode.py > referee_mode.json
```
