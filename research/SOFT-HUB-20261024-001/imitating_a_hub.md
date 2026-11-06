# Can native emergence imitate a hub?

Epic `SOFT-HUB-20261024-001`, closed 2026-10-25.

## The question

The owner asked to continue the recommendation made at the close of `NATIVE-APPROX-20261024-001`.
- **What was known.**
  - Deciding native networks needs a hub as well as a knot (`NATIVE-HARDNESS-20261024-001`).
  - Approximate counting is settled for 28 knots and open for six, the twisted Fibonacci knots (`NATIVE-APPROX-20261024-001`).
- **The question.** Can a network without hubs imitate one: a three-leg gadget whose weight on 000 and 111 dominates, strongly enough
  to carry the six into bounded-degree counting, where approximation is hard unless NP = RP?
- **Intuitions this epic targets:**
  - the complexity side of the thesis: does hardness need genuine reuse, or can emergence fake it?
  - what is real is the binding between loops: the foundation already refuses to count a hub as a contact.

**The evidence:**
- [Hub ratios of the settled knots](../../proofs/SOFT-HUB-20261024-001A/SOFT-HUB-20261024-001A-P001_hub_ratios_of_settled_knots/proof.md)
  (A, proof; the windable bound is given McQuillan);
- [Searching for strong hubs among the open knots](../../experiments/SOFT-HUB-20261024-001B/SOFT-HUB-20261024-001B-E001_strong_hubs/contract.json)
  (B, frozen-contract experiment, supported;
  [result](../../artifacts/SOFT-HUB-20261024-001B/SOFT-HUB-20261024-001B-E001_strong_hubs/result.json));
- [Tree gadgets of the open knots have bounded hubs](../../proofs/SOFT-HUB-20261024-001C/SOFT-HUB-20261024-001C-P001_tree_gadgets_have_bounded_hubs/proof.md)
  (C, proof, with the obstruction for gadgets with cycles);
- [bounded scan](scan.md);
- **scoping (scratch, not evidence; disclosed in B's contract):**
  - hill climbing and annealing on one axis;
  - the first test of the dichotomy;
  - linked pairs on 343 gadgets;
  - compositions;
  - annealing restricted to trees;
  - the search for the cyclic collision.

## Outcome in one paragraph

**Emergence cannot imitate a hub exactly, and as far as anyone can tell, not approximately either.**
- **No exact hub (A).** For every knot, the support of a native gadget excludes at most half its values, so it is never an exact hub.
- **The settled knots are bounded (A).**
  - Gadgets of windable knots have hub ratio at most √3, given McQuillan.
  - Gadgets of parity and the no-lone knots have hub ratio at most 1.
- **The key lemma (A).** Pairs of solutions whose difference does not tie all three terminals together can always be rerouted onto
  off-diagonal values. Only *linked* pairs can make a hub, and for the six open knots they pass through knots that are empty on one
  side and full on the other.
- **The six exceed 1 but stay low (B).**
  - The strongest gadget found, among 336 annealing runs up to 40 knots and 100,000 random gadgets, has ratio 65/53 ≈ 1.23.
  - A gadget never violates the windability inequality on an axis where its ratio exceeds 1.
  - Composing the best hubs never amplified them.
- **Trees are proved bounded (C).** On a tree gadget, rerouting one terminal's arm at the first such knot maps every linked pair
  injectively. This gives hub ratio at most 3.
- **Cycles are open (C).** With a cycle the arm can be rerouted in two ways (an explicit seven-knot collision), so the same bound for all
  gadgets remains a conjecture, true on every gadget tested.

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Supports of native gadgets | Co-independent, so never an exact hub | Proved (A, Theorem 1) |
| Exchange the difference component of one terminal | Separated pairs inject into split patterns | Proved (A, Lemma 2) |
| Settled knots | Windable ≤ √3 (given M); parity, no-lone ≤ 1 | Proved (A, Theorems 4 and 5) |
| Shape of the eight non-windable knots | Closed neighbourhood plus antipode; rigid at the branching knots | Proved (A, Proposition 6) |
| Scoping: search for hubs | The six reach about 1.21; random search up to 7 knots had seen only 1 | Scratch |
| Pre-registered search at scale | Best 65/53; dichotomy holds; linked ≤ M²; compositions do not amplify | Supported (B) |
| One-sided reroute along the tree | Arm inequality, hub ratio ≤ 3 on trees | Proved (C, Theorem 1) |
| The same reroute with a cycle | Two pairs, one image | Proved (C, Proposition 3) |

## What was proved

| Result | Content |
| --- | --- |
| A, Theorem 1 | No native gadget of any knot is an exact hub, on any number of legs from three up. |
| A, Lemma 2 | F(u)F(ū) ≤ s_u + (linked pairs), for every gadget of every knot. |
| A, Lemma 3 | Every linked pair branches at a knot with antipodal local tuples; parity has none. |
| A, Theorems 4 and 5 | Windable gadgets have ρ ≤ √3 (given M); parity and no-lone gadgets ρ ≤ 1 (Fibonacci recurrence f₂ = f₀ + f₁). |
| A, Proposition 6 | The eight non-windable knots are N[c] ∪ {c̄}; only whole difference components can be exchanged. |
| C, Theorem 1 and Corollary 2 | Tree gadgets of the open knots: F(u)F(ū) ≤ s_u + F(u + eᵢ)F(ū) + F(u)F(ū + eᵢ), so ρ ≤ 3; trees reach 12/11. |
| C, Proposition 3 | With a cycle the reroute is not injective (explicit gadget). |

**What was supported (B).** All four predictions held:
- no ratio above √3;
- no axis with both a windability violation and ratio above 1 (13,915 violating axes);
- linked pairs at most M_u² (12,000 axis cases);
- no amplification by triangles, dressings or hubs of hubs.

## What this changes

- **Reuse is a separate ingredient.**
  - Hardness of deciding needs a hub (`NATIVE-HARDNESS-20261024-001`).
  - Native emergence cannot produce one exactly, and on trees not even approximately beyond ratio 3. That is far from the
    near-exact hubs a hardness reduction needs.
  - So the hardness of the thesis's three-literal side comes from emergence combined with reuse, not from emergence alone.
- **Where the six stand.**
  - Their gadgets behave like those of the windable knots: soft hubs exist (65/53 against not-all-equal's 4/3), but no amplification
    appears.
  - The hub route to hardness looks closed, though it is proved closed only on trees. Their approximate counting stays open.
- **The defect picture.**
  - The eight non-windable knots allow 0, 1 or 3 defects relative to a centre, never 2.
  - The rigid knot (no defects against three) is exactly where pairs of solutions cannot be rerouted, and where all hub-like weight
    lives.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| A soft hub above ratio 1 would make approximation hard | The recommendation behind this epic | **Refined.** Ratios above 1 exist even for knots with approximation schemes (not-all-equal reaches 4/3). What matters is amplification, and the evidence and the tree theorem say there is none. |
| Small random searches settle hub questions | Scoping in `NATIVE-APPROX-20261024-001` (gadgets up to 7 knots, ratio 1) | **False.** Annealing finds 65/53. |
| The open knots are more hub-capable than windable ones | Their non-windability | **Not supported.** Their best ratio lies between not-all-equal's values and the windable cap √3. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A, Theorem 1 | Co-independence from `SURFACE-GLUING-20261024-001B` | Elementary; folklore risk high |
| A, Lemma 2 and Lemma 3 | The core of winding: switching whole components | Elementary; folklore risk high |
| A, Theorem 4 | McQuillan's Theorems 4 and 6 | Classical theorem applied; conditional |
| A, Theorem 5 and Proposition 6 | Linear algebra; the Fibonacci eigenbasis; the shape of the eight knots | Elementary, new to the program |
| B | Annealing, sampling, pair classification | A recorded computation |
| C | One-sided path switching along a tree | `candidate-local-delta`; folklore risk medium |

**Did the perspective do real work?** Partly.
- **What it supplied.**
  - The question, whether emergence can imitate reuse, comes from the foundation's distinction between a contact and a common hub.
  - The defect picture (0, 1 or 3 defects) located the rigid knot where rerouting fails, which shaped both the exchange lemma's limit
    and the tree proof.
- **What is classical.** The exchange and path-switching arguments are classical in style.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: can native emergence imitate a hub? | **Status:** Partially successful | No exact hub, for any knot; bounded hubs for 28 knots and for tree gadgets of the six; ratio ≤ 65/53 found everywhere. The bound for gadgets of the six with cycles is open. |
| Local direction: injective rerouting | Practically exhausted for cycles as constructed | One-sided switches hide the arm when a cycle offers two routes. |
| Broader exploration: complexity program | Known alternatives | Bound with cycles; approximation schemes for the six; signs. |
| Long-term goal: the complexity side of the thesis | Capability gained | Deciding needs reuse (proved); emergence cannot fake reuse exactly (proved), nor approximately on trees (proved), and the conjecture covers the rest. |
| Next recommendation: hubs with loops | **Next step:** Continue, with a fresh epic | Decide Conjecture 4 of ticket C. First discriminator: anneal directly for violations of the arm inequality (maximize the ratio of its two sides) up to 40 knots. If none appear, try a fractional reroute that averages over all routes of an arm, or induction on loops by self-gluing with a stronger multi-terminal inequality. |
| Interest: that recommendation | **2/3: promising** | A proof would complete "emergence cannot imitate reuse" for every knot. A counterexample would be the first native gadget beyond the tree bound. Main uncertainty: the proof may need a new idea for one-sided switches. |
| Execution | Deferred to the owner | Bound: one epic; stop if no violation appears and neither proof route closes. |

**Alternatives:**
- **Approximation schemes for the six (1/3).** Mixing experiments for a defect-flip Markov chain would be evidence only, but they would
  bear on the original question directly.
- **Twists in three dimensions (1/3).** On the space intuition, but speculative.
- **A note on native complexity (1/3).** It would collect deciding, refuting, exact and approximate counting, and hubs. Magnitude
  moderate, folklore risk medium to high.
