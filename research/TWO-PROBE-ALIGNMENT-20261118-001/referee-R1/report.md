# Referee report TWO-PROBE-ALIGNMENT-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.** Both halves hold as stated, and the obstruction is stronger than claimed. The fixes are
about saying what kind of evidence each half has and what the rule is given.
- **The obstruction holds for every rule in the declared game, and also for rules with memory.**
  - The study solves the finite game exhaustively over every *stationary* rule (one action per observed table): z3 rank conditions,
    an independent search and a solver-free certificate.
  - The referee solved the same game for rules that remember every earlier table and action, using its own belief-state solver on the
    study's outcome sets. No such rule guarantees the second junction either: 730 reachable beliefs, and the start loses.
  - The two negative controls also lose with memory: tests created together when idle, and automatic erasure.
  - The positive control wins with memory (automatic erase or replace of either or all) in 6 actions, against 15 for the best
    stationary rule.
- **The hand collision is confirmed from scratch.**
  - Testing (111, u) and (000, 111) gives 90 rows on 14 distinctions.
  - All 40,320 permutations of the second test's two ends with the six untouched originals preserve every table entry.
  - In the comparison (011 in place of 111), 100 rows, the test's ends map only to each other.
- **The positive start is confirmed from scratch.** This is the joint-reconfiguration rule through the second junction and its cleanup.
  - The referee followed every member of every action orbit under the automorphisms of the current table: 72 states, 132 orbit members.
  - There were no failures, and all 18 distinct commitments are correct.
  - The clean interface is reached in at most 8 actions, with 32 rows on 12 distinctions, whose projection to the eight originals
    gives exactly their 8 rows.
- **The coordinator's three questions:**
  1. **"Every tie succeeds under renaming".** It is computed, not proved by hand. The first two parts are exhaustive over reduced
     positions. The last 27 joins follow one canonical trajectory, with a symmetry argument for ties. Renaming invariance holds by
     construction and was spot-checked (§2).
  2. **What the rule is given beyond the distances.** A precompiled plan covering the growth law, the probe law, the target's
     incidence and a fixed join order, plus an instrument that clears its own probes without being told which they are (§3).
  3. **The one-probe-at-a-time impossibility.** It is an exhaustive result for every rule in the game, not for the readers tried. The
     referee's check extends it to rules with memory (§1).

## 1. The obstruction: every rule, with or without memory

- **The study's claim.** The theorem is an exhaustive solution of a finite game.
  - The arena has 9,083 named positions in 225 physical types, with 73 observed tables. Every action is taken as a whole orbit under
    the current table's automorphisms, and every resolution is adversarial.
  - Under these rules, no rule that picks one action orbit per observed table, the same on every visit, guarantees the second
    junction.
- **It covers every such rule, not the readers tried.** The study shows this three ways (`check_start.py`, `check_audit.py`):
  - z3 finds no ranking of the reachable types that a rule could follow;
  - an independent search over every uniform partial policy (526 nodes) finds none;
  - a solver-free certificate gives 1,260 partial assignments ending in 1,173 losing leaves.
- **Its scope as written is stationary rules.** The pre-registration defines the policy as "one action orbit on each observed table",
  and step 3 of the proof makes observation-equivalent histories share a decision. The predecessor proof itself notes that a record of
  earlier choices "would change the equivalences used here". So, as written, the theorem does not cover a rule that remembers its
  earlier tables.
- **The referee's extension** (`referee_memory.py`). The study's game is imported read only: its physical types, observations, action
  orbits and outcome sets (`transitions`). The referee's own solver plays the perfect-recall version.
  - A rule that remembers everything it has seen knows a belief: the set of physical types consistent with its tables and actions,
    since names change between decisions.
  - The solver takes every belief reachable under safe actions and finds the least fixed point.

| Game | Reachable beliefs | Beliefs of more than one type | Start wins with memory? |
| --- | --- | --- | --- |
| One probe addressed at a time (the theorem) | 730 | 512 | **no** |
| Two tests created together when idle (a control) | 745 | 522 | no |
| Automatic erase of either or all (a control) | 730 | 512 | no |
| Automatic erase or replace of either or all (positive control) | 755 | 537 | **yes**, 6 actions (stationary: 15) |

- **So the obstruction holds for every rule that sees only the tables, with or without memory.** The positive control shows that the
  solver can find wins where they exist.
- **The hand witness, from scratch** (`referee_collision.py`, no study code):
  - root 000 with outputs u, v; tests (111, u) and (000, 111);
  - 90 rows on 14 distinctions;
  - the table has 80,640 automorphisms;
  - every one of the 40,320 permutations of {p₂, q₂} with the six originals other than 000 and 111 preserves every entry.
  - So "erase the second test" can be resolved as erasing two originals.
  - In the comparison, tests (011, u) and (000, 011), there are 100 rows and 192 automorphisms, and p₂, q₂ map only to each other.

## 2. "Every tie succeeds, even under renaming": what kind of evidence (question 1)

**It is computer-checked, with one symmetry argument, not a hand proof.** The three parts are covered differently.
- **The first part** (seed to the clean second junction, at most 8 actions). Every tied action is followed over the reduced physical
  positions (`check_start.py`, `direct_bulk_policy`). The physical reduction is checked by transporting whole rows.
  - The referee re-derived this part from scratch (`referee_start.py`): the rule as the proof states it, every member of every orbit
    under the current table's automorphisms, with the referee's own tables.
  - 72 states, 132 orbit members followed, no failure.
  - All 18 commitments are correct: a fresh root output with a true neighbour.
  - Every erasure removes one whole probe.
  - The interface has 32 rows on 12 distinctions, projecting to the 8 original rows. The deepest path is 7 actions after the root,
    8 with it.
- **The block** (22 actions). Every operand tuple of every pattern is followed over 42 reduced positions: 78 operand choices and 49
  transitions (`check_block.py`). This is exhaustive over the reduced positions. The referee did not recompute it.
- **The tail** (the last 27 joins, 33 actions). It follows **one canonical trajectory** (`check_tail.py`, `trace`). At each step it
  checks that the rule's admitted operands lie within the "source ties": loose, untested outputs of the same parent.
  - Ties are then covered by the argument that exchanging two such outputs is an automorphism of the whole relation, so every tied
    future is isomorphic and the renaming-invariant rule acts the same.
  - The referee's reading is that the argument is sound: the junctions are even-parity relations, symmetric in their outputs; the
    outputs are loose and untested; and the held distinctions are fixed.
  - But it is an argument, not an enumeration. The pre-registration itself says "one canonical trajectory [is] insufficient". The
    note should say the tail rests on this symmetry step.
- **Renaming.** The rule dispatches on an isomorphism-invariant signature (iterated colour refinement of the table) and picks
  operands by colour class. So it is renaming-invariant by construction, as long as the signature is.
  - This was spot-checked on random renamings: one per start checkpoint, two per tail step and 91 composite tables.
  - It was not checked for every renaming, and it need not be, if the refinement is canonical.
  - The cross-phase check (no two parts share a dispatch signature) is what lets one function serve all three parts.
- **Fair wording.** "Every tie is followed exhaustively in the first two parts. In the tail, ties are covered by a symmetry of the
  source fixing the held distinctions, checked on one canonical trajectory. The rule reads only table invariants, so renaming
  changes nothing (spot-checked)." **Narrowing (wording).**

## 3. What the rule is given beyond the bond distances (question 2)

- **At run time:** only the current matrix.
  - It is thresholded at 2 in the first part, at 4 in the block and at 5 in the tail, with larger values merged.
  - The rule gets no names, no history, no tested middles and no stage signal.
- **By construction:** the rule is a finite lookup compiled offline from the designers' model. It encodes:
  - **the growth law:** a parity root junction with two fresh outputs, ordinary junctions with three, and one literal source junction
    per step;
  - **the probe law:** B(p, a, q) and B(p, b, q);
  - **the target:** the literal 105-distinction aligned round, its 35 junctions and their incidence;
  - **a fixed join order:** the tail's program lists the joins in order;
  - **the probe count:** at most two.
  - The 75 dispatch signatures (10, 32 and 33) are table fingerprints from that plan.
  - This is a legitimate stationary policy under the pre-registration. But "bond distances alone" means the observation alone, not
    a rule that discovers the target.
- **The capability that matters.** The joint operation discharges or reconfigures the instrument's own probes without being told
  which distinctions they are.
  - That is exactly what the obstruction says the rule cannot do with the table alone: name the probe ends.
  - The study's own controls locate the boundary:
    - automatic clearing without reinstalling still loses;
    - "clear all and install one chosen test" in one action wins (15 stationary actions; 6 with memory, the referee).
  - So the positive result is about the instrument, not the observation: two probes suffice if the instrument can replace its own
    probes in one action.
  - The note says this ("the instrument can replace the whole pair … without telling the rule the identity of any temporary
    endpoint"). The quoted summary's "bond distances alone can guarantee alignment if the rule can set or clear both probes together"
    is fair once the clear is read as the instrument's act. **Not a block.**

## 4. Other points

- **Validation level.** The study's checks are separate algorithms within one task (V1, as stated). The referee's are fresh, independent
  code (V2) for three things:
  - the collision witness;
  - the first part of the positive rule;
  - the memory game, solved by the referee on the study's outcome sets.
  - The block and the tail were not recomputed.
- **Novelty** is unassessed, as stated.
- **The open question stands:** what is the weakest instrument that suffices?

## Fixes for the thread (listed for the owner, not folded in)

1. **The obstruction's quantifier.** Say "every rule deciding from the tables (stationary, proved by exhaustive solution); also rules
   that remember every earlier table and action (referee, perfect-recall belief game on the study's outcome sets)". **Not a block;
   it strengthens the result.**
2. **The tie claim's evidence.** As in §2: exhaustive in the first two parts; the tail on one canonical trajectory plus a symmetry
   step; renaming by invariance, spot-checked. **Narrowing (wording).**
3. **What the rule is given.** State the precompiled plan (growth law, probe law, target incidence, join order, at most two probes).
   Say that the positive result's ingredient is the instrument replacing its own probes in one action. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, the proof and the predecessor's proof, and read `check_start.py`, `check_tail.py`,
    `check_compose.py` and the results;
  - wrote `referee_collision.py`: the cube relation, root, probes, bond tables and automorphism search, all from scratch;
  - wrote `referee_start.py`: the first part of the positive rule, with every orbit member followed, from scratch;
  - wrote `referee_memory.py`: the perfect-recall belief game, solved by the referee. It imports the study's `check_start.py` read only,
    to build its game.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_collision.py`, `referee_start.py` and `referee_memory.py`.**
- **The matching `.json` outputs.**

Reproduce, from `research/TWO-PROBE-ALIGNMENT-20261118-001/referee-R1/` (under a minute in total):

```sh
for p in collision start memory; do ../../../.venv/bin/python -B referee_$p.py > referee_$p.json; done
```
