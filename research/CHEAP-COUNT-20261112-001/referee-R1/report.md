# Referee report CHEAP-COUNT-R1 (lean, Codex-assisted)

**Verdict: Confirmed with fixes: one Block (the rarity headline), three Narrowings, three Not a block.**
- **Every computed number reproduces** with independent code.
- **The ten-knot lower bound now holds for every number of helpers.** It needed an argument the study lacked, and searches at 7 to
  11 helpers.
- **The Block.** "Counting is astronomically rare" does not follow. The mass of the counting descriptions found is a lower bound on
  the mass of counting, and rarity needs an upper bound.
- **A Narrowing Codex did not raise.** The Answer's "the cheapest NAE counter needs a four-place parity of at least 10 knots" is
  proved only for counters built on a parity gadget.

**How the work was split.** The background referee thread owns the verdict.
- **Codex.** The Codex command-line tool, at the owner's choice of model and effort, did the independent recomputation and critique
  from a brief of repository material only (`codex/brief_codex.md`). It wrote everything in `codex/`, starting with
  `codex/codex_report.md`, in about 12 minutes, and changed nothing outside that folder.
- **The referee.**
  - Read the study.
  - Checked the soundness of Codex's reduced and symmetry-broken encodings.
  - Ran its own plain-encoding checks (`ref_bound.py`): f = 3 at 11 knots and f = 4 at 9 knots, both unsatisfiable, in agreement.
  - Stopped its own unreduced query at f = 11 after 54 minutes without an answer. Codex's reduced version decides it in 17 seconds.
- **Advisor.** The advisor model was not consulted.

## 1. What reproduces (Codex, checked)

| Item | Study | Codex's recomputation |
| --- | --- | --- |
| m*(f), f = 0..6 | none, none, none, 12, 10, 10, 10 | the same, each with unsatisfiability one below |
| minimal gadgets at f = 3 | 168 | 168 labelled; 28 classes up to relabelling helpers; 3 classes up to permuting named and helpers (sizes 24, 72, 72) |
| rule 60 / 90 / 150 / 102 / hop, depths 1..64 | as in `s2.json` | identical; the gadget-built rule 60 and hop equal the exact parity at every depth |
| mutations | 240: 3 same parity, 169 constant, 68 eventually constant | identical, every sequence equal to 64 |
| description bits | 105.62 (h = 3, m = 12), 103.63 (h = 4, m = 10); log2 mass of 504 = −96.64 | identical |

**The synthesis encoding is right.** Odd named states are refuted by a chosen knot for every helper assignment. Each even state has
its own existential helper assignment. Knots on three named distinctions are rightly excluded, since they forbid 0000.

**Completeness at f = 3 is right.** Blocking a 12-knot set blocks only that set at a bound of 12.

**The collision handling is right.** Two slots on one distinction at a row end are joined through a fresh copy tied equal.

## 2. The ten-knot bound for every number of helpers (Codex caught this; the referee checked it)

The note states "a parity takes at least 10 NAE knots" without restriction, but its search stopped at six helpers.

**The argument.** It is Codex's, and the referee derived the same one independently.
- **Helpers seen once can go.** A helper in only one knot never constrains: for any values of the other two, it can be chosen. So
  that knot and the helper can be deleted without changing the projection.
- **The count.** In what remains, every used helper lies in at least two knots and every named distinction in at least one. So
  4 + 2f ≤ 3m, and m ≤ 9 needs at most f = 11.

**The searches.** Codex's reduced searches at m ≤ 9 are unsatisfiable for f = 7, 8, 9, 10 and 11.

**The referee's check of soundness.**
- **Representatives.** Codex uses representatives with the first named distinction at 0, which is valid because everything is
  closed under complement.
- **The reduction.** It requires every helper to be used at least twice, so each f is run exactly. That is valid by the argument.
- **The flip condition.** For each named distinction there must be a chosen knot holding it and two helpers. This is necessary:
  flipping one name of 0000 must create a violation, and a knot with two named distinctions cannot become all-equal by that flip.
- **Symmetry breaking.** It uses lex-leader constraints for adjacent transpositions of helpers, and also of named distinctions,
  under which parity is symmetric. These are necessary conditions for each orbit's least member. The chain variables are only
  forced true while the prefix is equal, so they do not over-constrain.

**The result.** The bound holds for every f.

## 3. The rarity headline (Codex caught this)

**Conclusion 3 and the Answer.** They say "astronomically rare", "weight about 2^−97". That is the total mass of the 504 counting
descriptions found, all built on one template (a parity gadget per position, rules 60, 90 and 150).
- **Why it does not follow.** That mass is a lower bound on the mass of all counting descriptions. Rarity would need an upper bound
  over every way the language can count, including longer gadgets, other rules and other mechanisms.
- **What else the bits depend on.** The bits are also conditional on the frozen decoder: the global reference, the missing positions
  read as it, the closing, and the equality copies, all at zero cost.
- **The verdict.** Withdraw the rarity claim, or restate it: "the cheapest counting descriptions found in this template take about
  104 to 106 bits; no bound on counting mass is shown". **Block** for that conclusion as stated. No other number is affected.

## 4. "The cheapest NAE counter needs a parity" (Codex missed this)

The Answer says the cheapest NAE counter needs, at every position, a four-place parity built from at least 10 knots.
- **What is proved.** That any NAE definition of a four-place parity needs at least 10 knots and 3 helpers.
- **What is not.** That every NAE counter must contain one. A counter could count by some other relation, or with helpers shared
  across positions.
- **The fix.** Scope it: "the cheapest counter built on a four-place parity gadget". **Narrowing.**

## 5. Honest reporting (Codex, checked)

**P3's failure is stated plainly.**
- **Hop.** Its evidence is death from 12 to 64, not a proof of permanent death, so "does not count" should say "within 64".
- **Rules 90 and 150.** They are "unexplained within 64" in the data. The note's "count too" needs either that wording or an
  all-depth argument for this closing.
- **Other bounded readings.** Codex also notes that "settle" for mutants is a bounded reading.
- **The verdict.** **Narrowing.**

## 6. Settled by construction or known

- **Deletions.** No deletion from a minimal gadget can keep parity, by minimality. A replacement that keeps it is another minimal
  gadget, by definition. The three replacements found and the growth classes are the measured part.
- **The gadget-built growth.** It equals the exact parity by composition, once the local projection and collisions are right, so
  G checks the implementation.
- **Known.** Counting by additive rules (Martin, Odlyzko and Wolfram 1984) and NAE's co-clone (Böhler, Reith, Schnoor and Vollmer
  2005).
- **New.** The exact minimal sizes and the counts.

## Fixes for the thread

1. **Withdraw or restate the rarity conclusion.** The found mass is a lower bound, and the bits are conditional on the frozen
   decoder. **Block** (Conclusion 3 as stated).
2. **Scope "the cheapest NAE counter needs a four-place parity"** to counters built on a parity gadget. **Narrowing** (the
   referee's; Codex missed it).
3. **Give finite verdicts as finite.** Write "unexplained within 64" for rules 90 and 150, "dead from 12 to 64" for hop, and say
   that the mutant classes are bounded readings. **Narrowing.**
4. **State the decoder conventions the bits assume,** and keep ideal bits apart from a shortest complete description. **Narrowing**
   (folded into 1).
5. **Add the bound for every f** (the helper argument and the searches at f = 7..11) to Conclusion 1. **Not a block.**
6. **Add the three classes of minimal gadgets** (24, 72, 72). **Not a block.**
7. **Note that deletions failing follows from minimality.** **Not a block.**

## Files

- **`codex/`.** Codex's brief, report, scripts and outputs: `s1_recompute.py`, `growth_mutations.py`, `weights_claims.py`, and
  their JSON.
- **Referee.** `ref_bound.py`, `result_bound_*.json`, plus the referee's plain-encoding checks.
