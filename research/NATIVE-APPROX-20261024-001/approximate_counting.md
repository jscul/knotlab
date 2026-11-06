# Approximate counting of native emergence

Epic `NATIVE-APPROX-20261024-001`, closed 2026-10-24.

## The question

The owner asked to continue the recommendation made at the close of `NATIVE-COUNTING-20261024-001`.
- **What was known.** Exact counting of native networks is easy for the four topological knots and #P-hard for the other 30, given
  Backens's dichotomy, although deciding is easy for every knot (`NATIVE-HARDNESS-20261024-001C`).
- **The question.** Is emergence hard to count exactly but easy to approximate?
- **Intuitions this epic targets:** the complexity side of the thesis; the growth of emergent information, read as a count of
  witnesses.

**The evidence:**
- [Windable knots count approximately](../../proofs/NATIVE-APPROX-20261024-001A/NATIVE-APPROX-20261024-001A-P001_windable_knots_count_approximately/proof.md)
  (A, proof; the approximation scheme is McQuillan's theorem, cited);
- [The open knots are twisted Fibonacci knots](../../proofs/NATIVE-APPROX-20261024-001B/NATIVE-APPROX-20261024-001B-P001_open_knots_are_twisted_fibonacci/proof.md)
  (B, proof);
- [Correlation decay on native trees](../../experiments/NATIVE-APPROX-20261024-001C/NATIVE-APPROX-20261024-001C-E001_tree_decay/contract.json)
  (C, frozen-contract experiment, refuted; [result](../../artifacts/NATIVE-APPROX-20261024-001C/NATIVE-APPROX-20261024-001C-E001_tree_decay/result.json));
- [Two-way forcing freezes native trees](../../proofs/NATIVE-APPROX-20261024-001D/NATIVE-APPROX-20261024-001D-P001_two_way_forcing_freezes_trees/proof.md)
  (D, proof; explains C);
- [bounded scan](scan.md) (windability, canonical paths, bounded-degree counting, two-spin uniqueness);
- **scoping (scratch, not evidence):**
  - a soft-hub search on gadgets of up to seven knots;
  - a tree probe with uniform boundaries only, which missed the freezing found by C.

## Outcome in one paragraph

**Emergence is easy to count approximately for 28 of the 34 knots. The six left open are the Fibonacci knot with one or two places
negated, and both standard approximation methods stop there.**
- **K2 is the terraced condition (A).** The knot axiom K2 is the "strictly terraced" hypothesis of McQuillan's winding method.
  - A knot is windable exactly when it excludes at most two tuples or is a parity knot: 26 knots.
  - Given McQuillan's theorem, each of them has a fully polynomial randomized approximation scheme.
  - With the four topological knots, which count exactly, 28 knots are settled. For 24 of them emergence is hard to count exactly and
    easy to approximate.
- **The six left open are twisted Fibonacci knots (B).**
  - They form one orbit under relabelling: the Fibonacci knot (no lone 1) with one or two places negated.
  - Their native networks are Fibonacci networks in which some edges carry a disequality, a *twist*.
  - In the Fibonacci knot's own basis a twist is a reflection with one negative entry, so the count is a signed two-spin sum.
- **Correlation decay fails for them too (C and D).**
  - On native trees without pins, boundary values can force the root edge either way at every depth. The experiment saw width 1 on
    every tree up to depth 16 and refuted the predicted decay.
  - The reason is elementary (D). A knot freezes every native tree exactly when its excluded tuples take both values at every place.
    That holds for 14 knots, including the six, not-all-equal and parity.
  - So freezing does not signal hardness: not-all-equal freezes and is approximable.

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Compare K2 with McQuillan's hypotheses | K2 is "strictly terraced" | Proved (A, Lemma 1) |
| Test windability on all 34 knots | 26 windable; the non-windable knots exclude three tuples | Proved (A, Theorem 2); inequality and exact linear feasibility agree |
| Identify the six left open | One orbit; Fibonacci with negated places; twists | Proved (B, Theorems 1 and 2); 1,000 networks |
| Write a twist in the Fibonacci basis | A signed reflection; the count is a signed two-spin sum | Proved (B, Proposition 3) |
| Scoping: soft hubs | No gadget of up to seven knots concentrated more weight on 000 and 111 than elsewhere for the six | Scratch |
| Scoping: tree decay with uniform boundaries | The six appeared to decay | Scratch; misleading |
| Worst-case boundaries on random native trees | No decay without pins; with pins, decay of about 0.43 per level, slower than predicted | Refuted (C) |
| Explain the refutation | Two-way forcing freezes trees; 14 knots | Proved (D) |

## What was proved

| Result | Content |
| --- | --- |
| A, Lemma 1 | Every knot, both pins and the free unary function are strictly terraced. |
| A, Theorem 2 | Windable ⟺ at most two excluded tuples or parity: 26 knots. |
| A, Corollary 3 (given McQuillan) | Each windable knot has an approximation scheme for native counting with pins. |
| B, Theorems 1 and 2 | The six open knots are Fibonacci with one or two negated places; their networks are twisted Fibonacci networks. |
| B, Propositions 3 and 4 | A twist is a signed reflection in the Fibonacci basis; winding, Fibonacci holography and weighted Fibonacci gates stop at twists. |
| D, Theorem 1 | A knot freezes every native tree without pins ⟺ its excluded tuples take both values at every place. At a one-way place the root marginal stays on one side of 1/2. |
| D, Proposition 2 | Exactly 14 knots are two-way forcing: four antipodal pairs, eight knots excluding three tuples, two parity knots. |

**What was refuted (C).** On random native trees, the worst-case influence of the boundary on the root edge did not fall below the
pre-registered thresholds for the six open knots.
- **Without pins** it stayed at 1 on every tree.
- **With pin probability 0.2** the median width was 0.0014 to 0.0025 at depth 12 against a threshold of 0.001. It fell by about 0.43
  per level, against 0.23 to 0.30 for the decaying controls and 0.59 for not-all-equal.

## What this changes

- **Exact and approximate counting split.** For 24 knots, emergence is hard to count exactly and easy to approximate. The boundary
  of exact counting (topological knots) is not the boundary of approximate counting.
- **The frontier is one twist.**
  - The six open knots are the Fibonacci knot, which counts exactly, with a negated place.
  - The negation is what the standard methods cannot absorb. In the Fibonacci basis it is the same kind of sign that the Fibonacci
    rule needed in three dimensions (`HUB-DIMENSION-20261024-001B`).
- **Native complexity, as it now stands:**
  - deciding is easy for every knot;
  - refuting can need exponential size only with parity;
  - exact counting is easy only for the four topological knots;
  - approximate counting is easy for 28 knots and open for six.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| Hard to count exactly means hard to count approximately | Reading of `NATIVE-COUNTING-20261024-001` | **False for 24 knots.** They are #P-hard exactly (given Backens) and approximable (given McQuillan). |
| A probe with uniform boundaries measures decay | The scoping behind ticket C | **False.** Worst-case boundaries freeze the trees that uniform boundaries made look decaying. |
| Freezing signals hardness | Implicit when persistence is read as difficulty | **False.** Not-all-equal and parity freeze native trees and are easy to approximate or to count. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A, Lemma 1 and Theorem 2 | K2 read against McQuillan's definitions; the split pairs of a knot | Census and the K2 reading: `candidate-local-delta`, folklore risk medium |
| A, Corollary 3 | McQuillan's theorem | Classical theorem applied; conditional |
| B | The Fibonacci knot from `NATIVE-COUNTING-20261024-001A`; negating places | `candidate-local-delta`, folklore risk medium |
| C | Exact interval propagation on random trees | A recorded computation (refuted) |
| D | Forcing from excluded tuples and K2 | Elementary; the obstruction to strong spatial mixing is classical; folklore risk high |

**Did the perspective do real work?** Partly.
- **What it supplied.**
  - K2, the program's knot axiom, turned out to be the hypothesis of the winding method. This is the third complexity result it
    supports, after the width bound and the half rule.
  - The topological lens named the six: Fibonacci, the fusion rule, with a twist.
- **What is classical.** The approximation scheme is McQuillan's, and the decay obstruction is classical.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: approximate counting of native emergence | **Status:** Successful in part | 28 of 34 knots settled; the six open knots identified as twisted Fibonacci knots; tree decay refuted and explained. |
| Local direction: standard approximation methods | Practically exhausted | Winding fails (not windable) and decay uniform over pins fails (two-way forcing) for the six. |
| Broader exploration: complexity program | Known alternatives | Hubs simulated by gadgets; Markov chains beyond winding; signs. |
| Long-term goal: the complexity side of the thesis | Capability gained | Deciding, refuting, exact counting and approximate counting are now mapped for native networks of every knot, except approximate counting for six. |
| Next recommendation: can native emergence simulate a hub? | **Next step:** Continue, with a fresh epic | See below. |
| Interest: that recommendation | **2/3: promising** | It decides whether hardness of approximate counting, like hardness of deciding, needs a real hub, for the only knots where this is open. Main uncertainty: a gadget search may stay inconclusive. |
| Execution | Deferred to the owner | Bound: one epic. |

**The next step in more detail.**
- **The question.** Can networks of the six open knots, with pins, make a *soft hub*: a three-leg function that puts more weight on 000
  and 111 than on any other value?
- **Why it matters.**
  - Deciding needs a real hub as well as a knot (`NATIVE-HARDNESS-20261024-001`).
  - An amplifiable soft hub would carry the six to bounded-degree counting with pins. The six are neither affine nor built from
    implications, so that problem has no approximation scheme unless NP = RP (Dyer, Goldberg, Jalsenius and Richerby, degree at
    least 6).
  - A proof that no gadget makes one would point toward approximability instead.
- **A lead (scratch calculation, not evidence).**
  - In the Fibonacci basis every gadget of the Fibonacci knot has one spin, so its three-leg function is α v₀^⊗3 + β v₁^⊗3.
  - Non-negativity then forces the hub ratio to be at most 1: no untwisted gadget makes a soft hub.
  - A twist lets the spins differ, which is where a soft hub could appear. The small search found ratio 1 for the six.
- **First discriminators.**
  - A search of twisted Fibonacci gadgets up to about twelve knots in the signed two-spin form, maximizing the hub ratio.
  - An attempt to extend the ratio bound from untwisted to twisted gadgets.
- **Stop if** no ratio above 1 appears up to twelve knots and no bound can be proved (record the obstruction), or if a ratio above 1
  appears but cannot be amplified.

**Alternatives:**
- **Twists in three dimensions (1/3).** Can a native twist supply the negative weight that the Fibonacci rule needs in three dimensions
  (`HUB-DIMENSION-20261024-001B`)? It is on the space intuition, but speculative.
- **A Markov chain beyond winding for the six (1/3).** Mixing experiments would be evidence only.
- **A note on native complexity (1/3).** It would collect deciding, refuting, exact and approximate counting; magnitude moderate,
  folklore risk medium to high.
