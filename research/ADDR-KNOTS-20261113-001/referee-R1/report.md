# Referee report ADDR-KNOTS-R1 (lean, Codex-assisted, fresh code)

**Verdict: Confirmed with fixes: one Block (a false sentence about tail classes), several Narrowing, two Not a block.**
- **The prior-work line passes** the objects gate.
- **All 48 returns are certified.** Each has a checked unsatisfiability certificate for a dead level and a verified state for a
  later live one. All 84 levels of the 7 alternating descriptions are certified.
- **The rest reproduces.** The sampled patterns, the relative classes and the joining counts all match.
- **Lemma A and the finite-types remark hold.** Each needs one clarifying line.
- **The Block.** One sentence in the proof note and the decision note is false: "a tail class's inner knots are the same for every
  tail". Codex found a counterexample, which I confirmed with my own code. The census does not rest on the sentence.

**How the work was split.** The background referee thread owns the verdict.
- **Codex.** The Codex command-line tool, at the owner's choice of model and effort, recomputed from fresh code. It was barred from
  the study's implementation and the thread's recheck script, and opened neither. It took about 45 minutes at up to 3 processes.
- **What it wrote.** `codex/codex_report.md` and its evidence. It also wrote its own reverse-unit-propagation checkers (Python, plus
  a compiled one).
- **A disclosed slip.** It notes one deviation: early proof files were written to the system temporary folder before it noticed.
- **The referee.**
  - Checked points (a) and (b) by hand.
  - Confirmed the tail-class counterexample with its own code.
  - Judged the classes.
- **Advisor.** The advisor model was not consulted.

## 1. Prior work (the objects gate)

`track.py objects-gate` on the pre-registration reports `prior-work line: ok`. The section lists six searches and their hits, and
states that no earlier study placed knots by automaton maps.

## 2. The certified returns (point d; Codex)

**The method.** A fresh pattern builder (addresses, automaton maps, words applying r then q, placements) and a fresh NAE CNF.
- **Live levels.** Every live level has a satisfying assignment checked against every knot.
- **Dead levels.** Every dead level has a DRUP certificate checked by Codex's own reverse-unit-propagation checkers. These never call
  a solver, and they are tested on controls, including invalid and truncated proofs.

**The results.**
- **All 48 returns certified:** a certified dead level followed by a verified live one.
- **The seven alternating descriptions.** All 84 levels are certified, 53 live and 31 dead, matching the records (for example
  `110101010101`).
- **Overall.** 346 live and 218 dead levels are certified, with no conflict. 12 levels are uncertified (budget), and they do not
  affect any return.

**Narrowing.** F2 records an observed dead-then-live pair, not a permanent pattern. The thread's Glucose recheck left 26 levels
undecided, so its "agree" does not certify all twelve levels.

**Storage.** The certificates are 96 MB, too large to commit. They stay on disk in `codex/certificates/`, with their hashes in
`certificate_hashes.json`, and replay without a solver as described in Codex's report.

## 3. Lemma A with list members that are ports (point a; the referee)

The profile is sound.
- **The key fact.** A seen member that is not one of the copy's ports lies outside the copy's distinctions, since it was enlisted
  by an ancestor. So it can never be bound to a child's port.
- **The counts.** Going down, the capped counts only grow: a parent's non-port members stay non-port for the child, and a parent
  port not passed down joins the child's counts. The cap of 3 therefore suffices.
- **Ports.** Ports that are members are tracked by their list sets and values, so list knots that skip a coinciding member are
  decided correctly.
- **The fix.** Step (ii) of the proof should state the key fact explicitly. **Not a block.**

## 4. The finite-types remark (point b; the referee)

With depth as the number of unfoldings, the tuple of all definitions' denotations at depth t is a fixed function of those at depth
t − 1, on a finite set, so life is eventually periodic in t.
- **The advisor's view.** Its objection uses another depth, the longest chain of nested copies, which higher-order schemes can make
  grow like 2^t. Along that, fates need not repeat. Both statements are consistent.
- **The fix.** The remark should name its depth measure. It stays "my argument", by hand. **Narrowing.**

## 5. Patterns, relative classes and joining (point c; Codex)

**Patterns.** 31 stratified records (1 to 5 states, 1 to 9 placements) match in knot counts, joining counts, pattern hashes and fates.
Two independent builders agree on 200 more small cases.

**Relative classes.** 80 units, 20 per class, agree on class and polynomial degree. The check builds independent signed product
automata with inverses, and the action comparisons all match.

**Narrowing (point c).** As frozen, V-rel checks the relative *actions* and V-act-class the letter maps. Neither validates the
inverse-product class computation itself. This audit fills that gap on its sample only.

**Joining.** 20 patterns, 240 level checks, match `join_n`. The registered count uses tails of length k = 1.

## 6. The false sentence about tail classes (Block; Codex found it, the referee confirmed it)

**Where it is.** The proof note (§2, "A class's inner knots are the same for every tail") and the decision note (about line 23).

**Why it fails.** g(uv) = g(u)·g|_u(v): the prefix action ignores the tail, but whether all three images keep the tail v depends on
u. So the set of knots inside a tail class can depend on the tail.

**The counterexample.** sw = [1, 0], d0 = [1, 0], d1 = [1, 1], with one placement of words (1,), (0, 0), (1, 0). At level 4 there are
14 knots. The tail classes 00 and 01 contain no inner knot; 10 and 11 each contain the two knots on prefixes (0, 1, 2) and (0, 1, 3).
My own code (`tail_check`, in the scratchpad) gives the same.

**The fix.** "A map's prefix action is independent of the tail; its section decides the output tail, so both a class's inner knots
and its joining knots can depend on the tail." **Block** for the sentence as published. The census, B0 and the activity upper bound
do not rest on it.

## 7. Wording (point e and the rest; Codex)

**"Bounded joining is rare".** It conflates denominators: 7.87% of the W draws with a knot, 3.66% of W's pattern and class units,
and 3.26% in E. No threshold for "rare" was registered. Give the frequencies and say "a minority". **Narrowing.**

**"Almost every pattern doubles with each level" and "late ends need growing joining".** Exponential activity is an upper bound on
joining, not a lower bound: an exponential-class pattern can join with a constant 4 knots. Give the measured class averages at
levels 10 to 12, and call the late-death link an association within level 12. **Narrowing.**

**"Density decides most of it".** This is an association, and "neither arm dies" should read "few die". **Narrowing.**

**Settlement.** The share is 74.8% under each draw's own flags and 79.9% under the addendum's inherited settlement. Say which.
**Narrowing.**

**Class counts.** They are by (pattern, class) membership: 3,997 memberships over 3,990 patterns in W. Say so. **Not a block.**

**The bounded excess (e).** "2 of 27 against about 9 expected" is correctly marked descriptive. It comes from few automata, as the
note says. **Not a block.**

## Fixes for the thread

1. **Withdraw "a tail class's inner knots are the same for every tail"** and use the corrected sentence. **Block** (the sentence,
   not the census).
2. **Say that the returns are certified,** all 48 and all 84 levels of the 7, and that F2 is an observed pair, not permanence.
   **Narrowing.**
3. **Lemma A, step (ii).** State that a non-port member is outside the copy and cannot be rebound. **Not a block.**
4. **The finite-types remark.** Name the depth measure. **Narrowing.**
5. **The relative-class gate.** Say that it checks actions, not the class. **Narrowing.**
6. **The wording.** Fix "rare" and its denominators, exponential activity as an upper bound only, "density decides", "neither arm
   dies", and which settlement share is meant. **Narrowing.**

## Files

- **`codex/`.** Codex's brief, report and evidence: `fresh_patterns.py`, `recompute.py`, `check_rup.py`, `check_rup_fast.cpp`,
  `replay_certificates.py`, `relative_activity.py`, `joining_check.py`, the per-key `returns/`, `sample/` and JSON summaries. The
  certificates (96 MB) and the compiled checker are kept on disk and not committed (`.gitignore`). Their hashes are in
  `certificate_hashes.json`.
