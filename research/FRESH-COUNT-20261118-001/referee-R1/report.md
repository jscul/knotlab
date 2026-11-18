# Referee report FRESH-COUNT-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.** Every theorem checks by hand and every frozen reading replays one size past. One wording
fix matters: the headline "a growth rule that reads only bond distances cannot settle its own dimension (proved)" is wider than what
is proved.
- **The theorems hold.**
  - T1 is Birkhoff's construction: the pattern is the down-closed sets of the descent order.
  - T2: one count is forced to the seed's size.
  - T3: the cap of three.
  - T4: the fewest counts close the 2^a pattern and conserve the chains they are handed.
  - Lemma 0 and T6 also check by hand.
  - T5 (balls r^a) carries over the CUBIC-FROM-A-KNOT argument, which the referee checked earlier. It was not recomputed here.
- **Replayed one size past with the referee's own simulator** (`referee_fresh.py`, built from the policy's statement):
  - **One count** at a = 3..9 (study 3..7), c = 1..a + 3, capped and uncapped: all 126 cells agree with T2 and T3.
    - It runs forever exactly at c = a uncapped, and at c = a = 3 capped.
    - Every stall comes at the predicted round, and the junction counts are C(t + a − 1, a − 1).
  - **The fewest counts** at a = 3..8 (study 3..6) give the 2^a pattern:
    - counts C(a, j);
    - every junction has a distinctions;
    - the GF(2) rank is 2^a − 1;
    - no forced distinction.
  - **Blind counts** at a = 3, 4, K = 2..6, run to round 14 (study 10): 2,000 of 2,000 stall.
    - The study's three survivors at round 10 match the referee's three exactly, and those stall at rounds 11, 12 and 13.
    - So "1,997 of 2,000 by round 10" becomes "every one by round 14".
  - **300 hand-overs:** T4(b)'s constancy holds in every one.
  - **Crossed starts** at a = 3..7: a chains, with junction counts matching the study's for a = 3..6.
  - **T1's ideal check** passes on every run checked.
- **The coordinator's two questions:**
  1. **"Cannot settle" is proved only for count rules under the complete-round joining rule (A104), and only for some count rules.**
     - Uniform counts (T2), uniform counts with the cap (T3) and the fewest rule (T4) are proved.
     - For count rules in general, T1 proves the structure: the count rule chooses only the descent order. "It can only copy the
       number from its start or its own text" is an interpretation, not a theorem.
     - "Distance-only" is proved only for the uniform count (T6). The other rules read demands from the junction pattern. §1.
     **Narrowing (wording).**
  2. **"Forced to the first knot's size" has no exception within its scope.** The scope is a single seed of a ≥ 3 places, the
     uncapped policy and one count for every join; T2 was checked by hand and on 126 cells. Outside it:
     - the cap of three (a ≥ 4 stalls even at c = a);
     - starts of several knots, where the forced number is the open count. A touching pair needs a − 1, and a knot with one open
       distinction fits every count, as FIRST-KNOT's Theorem 2 states.
     So the general form is "forced to the seed's number of open distinctions". **Not a block (wording).**
- **Folklore** is cited once with "what this adds", as it should be: Birkhoff (Stanley 3.4.3), event structures, the cube condition and
  Dilworth.

## What holds

| Reading | Referee (fresh code) | Study |
| --- | --- | --- |
| One count, uncapped: survives exactly at c = a; stalls at rounds 2 / 4 / 3 | 63 of 63 cells, a = 3..9, up to 10 rounds | 40 cells, a = 3..7, 8 rounds |
| One count, capped at three: survives exactly at c = a = 3; c = a ≥ 4 stalls at round 4 | 63 of 63 cells, a = 3..9 | 40 cells, a = 3..7 |
| Junctions per round of the survivors = C(t + a − 1, a − 1) | every survivor | every survivor |
| T1 on the survivors (no ideal twice, none missing, parents = lower covers, round = size) | every survivor checked, a ≤ 6 (to 1,716 ideals) | 1,829 runs |
| Fewest from one knot: the 2^a pattern, every junction a distinctions, rank 2^a − 1, no forced distinction | a = 3..8 | a = 3..6 |
| Blind counts: not stalled by round 10; by round 14 | 3 of 2,000; **0 of 2,000** | 3 of 2,000 (round 10 only) |
| Hand-overs to the fewest rule: offshoots per round constant and equal to the first round's demand-1 offshoots | 299 of 299 | 196 of 196 |
| Crossed starts: a chains | a = 3..7 (counts equal to the study's for a = 3..6) | a = 3..6 |

**The referee's simulator.**
- It builds groups, stalls, offshoots and the lookahead demand from the policy's statement.
- Implied parity is tested by GF(2) elimination, not by Lemma 0, so Lemma 0 is checked rather than used.
- The ideal check recomputes I(v) from the parents.
- Valid sets come from a clique search, pruned only where a common neighbour holds every possible extension.

## 1. "Cannot settle": what is proved, and for which rules (question 1)

- **The scope is A104 throughout.** Every theorem is about the complete-round joining policy of CUBIC-FROM-A-KNOT, and the note's
  Limitations say so ("A serial rule never stalls and admits trees; nothing here constrains it"). The headline's "a growth rule that
  reads only bond distances" does not.
- **Inside A104, proved:**
  - **T1.** Whatever the counts, the pattern is the ideals of the descent order Q, so a count rule chooses only where offshoots go.
  - **T2.** A uniform count must be the seed's size, giving ℕ^a.
  - **T3.** With the cap, only a = 3 survives.
  - **T4.** The fewest counts close the seed, or conserve the chains they are handed.
- **Inside A104, not proved:**
  - **No theorem covers count rules in general.** T1 shows that a count rule can realise many descent orders.
    - For example, a rule giving extra surplus at the first round's offshoots grows more chains than the seed has. A distance-only
      rule can recognise the first round, since that table is the seed and its offshoots.
    - The number of chains then comes from the rule's own text, so "copy from the start or its own text" holds of every rule by
      construction. It is a reading of T1, not a theorem.
    - What the study proves is narrower: the natural criteria tried (one count and no stall; the fewest counts) pick no number other
      than the seed's.
  - **"Distance-only" is proved only for the uniform count (T6).**
    - The fewest, surplus and blind rules read demands computed from the junction pattern, not from distances.
    - The threshold reader gives the fewest pattern correctly except one round before the end, where it reads the loose distinctions
      as a junction (P8).
    - It misreads mixed counts (47 of 247 stages).
    - So for those rules the study shows what the rule builds, but not that a reader of distances could run it.
- **Fair wording.** "Under the complete-round joining rule (A104), a count rule chooses only the descent order (proved). One count is
  forced to the seed's size (proved), and the fewest counts close the seed (proved). No count rule tried picks a number its start or
  its text does not hold. Only the uniform rule is shown to run from distances alone." **Narrowing (wording).**

## 2. "Forced to the first knot's size": any exception? (question 2)

- **None within T2's scope.** The scope is a single seed of a ≥ 3 places, the uncapped policy, and one count c ≥ 1 at every new junction.
- **The proof checks case by case:**
  - **Round 1:** a antichain offshoots, each of demand a − 1, so c ≤ a − 2 stalls at round 2.
  - **c = a − 1:** the round-3 triples have demand a > c, so it stalls at round 4. This holds at a = 3 too, where the triple is the
    whole antichain with demand 3.
  - **c ≥ a + 1:** the round-2 pairs need 2s ≤ 1 + s, which fails for s ≥ 2, so it stalls at round 3.
  - **c = a:** every non-principal ideal has demand a and every principal one a − 1 plus one surplus, so Q stays a chains.
- **The census:** all 63 uncapped cells for a = 3..9 agree.
- **Outside the scope there are exceptions, which the wording should name:**
  - **With the cap of three** (T3), c = a ≥ 4 stalls at round 4.
  - **With a start of several knots** the forced number is each knot's number of *open* distinctions, not its size.
    - Two knots touching at one distinction need c = a − 1.
    - A knot with one open distinction fits every count.
    - This is FIRST-KNOT's Theorem 2, checked in its own referee report.
  - So the exact statement is "one count is forced to the number of open distinctions of the start's knots". For a lone first knot
    that is its size.
- **Not a block.** The note's own sentence is correct for one knot.

## 3. Other points

- **T1 (Birkhoff)** checks by hand:
  - candidates are the pairs of round-t ideals meeting in t − 1;
  - valid sets are either sunflowers, with an ideal core and so a common neighbour, or the lower covers of a (t + 1)-ideal;
  - every (t + 1)-ideal of the old order has two or more maximal elements, because principal ideals have size equal to the round.
- **Lemma 0** checks: a cut made only of loose bits is a union of components. The referee tested implied parity by elimination
  instead, and it agreed everywhere.
- **T3's demand count** 3 + 3(a − 4) + 3 = 3a − 6 > a for a ≥ 4 checks.
- **T4(b)** checks: surplus arises only at an offshoot of demand 1. Its child's only candidate is the parent's group, so its demand
  is 1 again.
- **T6's cut bound** 3a − 2 > 2a checks: the last three members bring 3a fresh bits, and there is no triangle.
- **Corollary 2.1** is labelled as added after the freeze, before the read-out. It is correct, since each junction multiplies the
  states by 2^(a−1).
- **Blind counts and implied junctions.** The blind rule can put fresh bits on a junction whose parity is already implied, forcing
  them to one value.
  - The referee saw this in 22 runs to round 14; the study saw 12 to round 10.
  - It is a property of that rule, and the note says so.
- **The "stall at four" sentence** is accurate: four stalls only because of the cap.

## Fixes for the thread (listed for the owner, not folded in)

1. **The headline and the "In the owner's terms" first bullet.** Scope "cannot settle" to count rules under the complete-round joining
   rule (A104):
   - proved for the uniform, capped and fewest rules;
   - T1's structure (the rule chooses only the descent order) proved;
   - "copies the number from its start or its own text" a reading;
   - distance-only operation proved only for the uniform count (T6).
   **Narrowing (wording).**
2. **"Forced to the first knot's size."** Add "(for a lone first knot; in general, the start's open distinctions)", and point to
   FIRST-KNOT's Theorem 2. **Not a block.**
3. **The blind row.** Update to "every one of 2,000 stalls by round 14 (the referee)". **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, the proof, `freelib.py`, `ideals.py`, `job.py` and the results, and checked T1 to T4, T6
    and Lemma 0 by hand;
  - wrote `referee_fresh.py`: its own simulator of the policy, GF(2) implied-parity test, ideal checker and count rules, with the
    census one size past.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_fresh.py`.**
- **`referee_fresh_uniform.json`, `_fewest.json`, `_blind.json` and `_handover.json`.**

Reproduce, from `research/FRESH-COUNT-20261118-001/referee-R1/` (about a minute in all):

```sh
for p in uniform fewest blind handover; do ../../../.venv/bin/python -B referee_fresh.py $p > referee_fresh_$p.json; done
```
