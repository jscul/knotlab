Advisor answer for EVENTUAL-R-20261126-001. I read `ops.py`, `part_a.py`, `part_a_out.txt`, `part_b.py`, `part_c.py`, `forbid.py` lines 1–125 and `rival_growth.py` in full; I ran nothing. Everything below is `unverified` unless I cite a line. As frozen, B2, B3 and C are entailed by the code or by a short argument, and B1 is the only prediction at risk.

## What the engine fixes (bears on questions 1 to 4)

Read in `rival_growth.py`:

- **Line 81**: `assert paid == Counter(bit for row in loose.values() for bit in row)`. A funded round consumes every loose distinction of every live knot.
- **Line 71**: a birth takes at most one distinction from each parent.
- **Lines 86–87**: every distinction of the new stage has one or two holders.
- **Lines 39–40**: with no live knot the status is `closed`, so `part_b.grow` stops there.

Read in `forbid.py` line 73: census starts are connected. Births hold their parents' distinctions, so every stage is one component.

Consequences, by argument:

- After a funded round, only the newest births hold loose distinctions.
- A pair of distinctions (a, b) can become co-held only while both are loose. So every pair settles one round after both exist.
- The commutation of two knots is final unless both were born in the last round.
- Two knots born in round T change commutation at T + 1 by the parity of their number of common children. Nothing else about stage-T knots changes.

## 1. Is the whole's R well defined on an open structure?

Yes, pair by pair, as long as growth stays funded. What is provisional is narrower than you wrote: only pairs of fresh distinctions of two different newest births.

R1 of the whole is one-sided. A settled anticommuting pair of knots is final and refutes a state for good; R1 can never be confirmed for an open component.

- **Scaffold I would use instead of plain truncation:** give each knot pair one of three values (settled commute, settled anticommute, open) and report R1 on settled pairs only. Your truncation silently reads "open" as "anticommute".
- **Second choice:** your T against T + 1 count, restricted to newest pairs, checked against the common-children formula. A flip anywhere else is a bug.
- **Counterexample to expect:** two knots with no co-held pair of places anticommute exactly when both place counts are odd. Ordinary births mostly have three places, so every open component should have a settled anticommuting pair by round 2 or 3.
- **What that would mean:** under R the open structure has no state, finally and not provisionally. I think this is the main finding to test, and it is not among your predictions.
- **Small case to try for "holds at T, fails at T + 1":** two start knots sharing one distinction, with 4 and 3 places and no third knot holding one place of each. They commute at round 0 (6 anticommuting pairs). If one birth has both as parents, they anticommute from round 1 on.

## 2. Is B2 an engine property?

Yes: lines 81 and 86–87 above. But B2 as coded cannot be nonzero for two further reasons:

- `part_b.py` line 36 keeps only components whose distinctions all have two holders at the end, so a later holder would have removed the component from `closed`.
- The structure is one component, so "closed" means the whole structure closed and `grow` has already stopped. There are no later knots.

Move B2 out of the predictions and cite the engine lines.

## 3. Is B3 the right formalisation?

It is entailed. `laws(..., use_t)` and `laws(..., c)` use the same values, knot operators and signs, and products of knots in `use_t` are a subset of products of knots in `c`. When the knots commute, the stage laws are a subgroup of the whole's with identical signs. So "sign differs" and "contradiction" are zero by construction.

The conflict test at lines 71–72 also only compares basis elements with the same support, so it could not see a conflict written in two different bases.

Readings that are not entailed:

- **The GF(2) reader.** A reader who signs products by summing knot signs predicts the closing knot even and meets odd. This is part A's 104 read sets, and it is the only place a later layer contradicts an earlier record of laws. State it as the answer to the owner's question.
- **Commutation claims overturned.** Compare stage-R knot-pair commutation with the whole's and count flips in both directions. It needs no laws and runs on all 300 starts, not just the closers.
- **Record survival.** A reader's record is a word on a read set. A later read of a distinction not co-held with a recorded one anticommutes with it, so that record no longer predicts. Count how many recorded values survive an outward reading.

## 4. B4 on the fixture: contradiction or absence of a state?

Neither exactly. On the ring of three, knots (0,1,2) and (1,3,4) have two settled anticommuting pairs (0–4 and 2–3) and one open pair (2–4). They commute only if some later knot holds 2 and 4 together.

So the reader's record, plus the demand for a state, predicts the next layer: the closing knot must hold 2, 4 and 5 together. That is a conditional claim about what comes next.

- **Proposed B5:** at each stage, solve over GF(2) for the open pairs so that all stage knots commute. Record whether a solution exists, whether it is unique, and whether the next round's births realise it.
- This is not entailed, and it is the one place R could say something about growth.

## 5. Part C

The bound holds, but your argument covers only one case. For the counting state each correlation is ±1 if the signed product is a law and 0 otherwise.

- **All four observables commute:** three laws force the fourth with sign s11 = s00·s01·s10, so CHSH is at most 2. This is your "−1 in the group" argument.
- **B0 and B1 anticommute:** then A0B0 and A0B1 anticommute and cannot both be laws. At most two correlations are nonzero, so CHSH is at most 2. The same holds when A0 and A1 anticommute.

The proof needs only Hermitian Paulis with each Alice observable commuting with each Bob observable, so it holds for products of places too. "Largest CHSH exactly 2" is a theorem plus a trivial attainment; move it out.

What reaches 4 is three readers. On census type 0 (knots (0,1,2), (0,3,4), (1,3,5), (2,4,5), forced odd) take readers {0,5}, {1,4}, {2,3}. The four knot laws are +, +, +, −, which should give the three-reader Mermin value 4 against 2 for a list of values. That equals the quantum maximum for three readers, so it does not exceed it. Run this as the part C test.

Nothing lets a value above the quantum limit through while a state exists and readers' observables commute, because it is then a quantum model. The routes by which 4 could appear are all errors:

- signing by rule (i) or (ii) instead of (iii);
- calling `laws` on knots that do not commute (the sign then depends on the order in `mul`);
- mixing a table from stage R with one from the whole's R.

A referee will press this first: under R, two values commute only if one knot holds both. Readers with no common knot (the `meets` sense in `forbid.py` line 106) therefore have no joint table at all. Every table under R is read inside knots; it shows contextuality, not separated readers.

## 6. The predictions

| Prediction | Status | What to do |
|---|---|---|
| B1: under one third | At risk | The sample is the starts that close within four rounds. Small closures are mostly R1 (census types 0, 2, 3 all are), so the share under the uniform weighting on census starts may exceed one third. Count closers first and stratify by closure size. |
| B2: zero | Entailed three ways | Move out. |
| B3: zero sign differences, zero contradictions | Entailed | Move out. |
| B3: "more laws later" at least once | Nearly entailed | Holds whenever one commuting closer has an earlier stage. |
| B4: stage knots often fail to commute | Expected from odd place counts | Replace with the flip count and the common-children formula. |
| B4: "some read set differs" | Has content | Supports are identical; only signs can differ, and only through newest-pair relations. |
| C: largest CHSH exactly 2 | Theorem | Replace with the three-reader value on type 0. |

Predictions worth adding: every open component has a settled anticommuting pair by round 3; B5; the flip formula holds with no exception.

Two smaller points:

- The docstrings cite a `README.md` that is not in the study folder.
- Stalled starts stay at round 0 and are scored as open under truncated R. Report them apart.

## 7. Known constructions

From memory, not checked against sources:

- **Arkhipov's magic arrangements** (2012): each observable in exactly two contexts, which is your two-holder condition with knots as contexts. The state-independent parity proof exists exactly when the intersection pattern is nonplanar. Yours is the state-dependent version (knot operators fix a state and are not themselves ±1), which is why type 0, planar, still forces odd. Cheapest test: planarity of the 173 types against R's forced sign.
- **Binary constraint system games** (Cleve and Mittal): the knot laws are such a system, and its operator solutions require commuting only within a constraint. R adds "anticommute everywhere else".
- **All-versus-nothing arguments for stabiliser states** (Abramsky, Barbosa, Carù, Perdrix): "no whole word, every part allowed" is their setting.
- **Quasi-Clifford algebras** (Gastineau-Hills): generators that commute or anticommute by a given pattern, which is what `realise` builds.
- **Kochen–Specker partial algebras**: jointly readable exactly when in a common context. R is the strongest completion of that.

Hivemind: one consultation entry and one standing fact (the engine lines 71, 81, 86–87) added to `docs/ADVISOR_HIVEMIND.md`; nothing else touched.
