# Referee report, group 1 of 2026-11-20: bare growth (four studies)

Covers ORDINARY-DYNAMICS, BOND-CLOSURE, FRESH-DEMAND and SERIAL-REPAIRS (all -20261120-001). The referee wrote its own code,
`job_g1.py`, using its EXPLOSIVE-R1 engine (the program's rule with the structural implied test) and its exact least-bond MILP.
No study code was run.

**Verdict: all four stand. No Block, no new correction. The Narrowing that SERIAL-REPAIRS logged is right.**

## ORDINARY-DYNAMICS: a knot cannot see whether its next join closes. Stands.

The four-knot pair was regrown with the referee's engine:

| | No spare at the centre | One spare loose distinction |
| --- | --- | --- |
| Births per layer | 3, then 1, then closed | 4, 3, 4, 6, 8, …, 58 (30 layers, linear) |
| Least bond on two of the y's, and on all three | 3, 3 | 4, 4 |

- **The chain variant at length 6** (one past the four registered lengths) gives the same triple fresh counts, 0 against 1. The
  extra birth is **7** ordinary steps from the pair births, and the bonds read 3 against 4.
- **The sharp general control** (radius two needed) holds: the birth {u, a, b} gets fresh count 2 or 1 as the distant knot x has 0 or
  1 loose distinction.
- **Scaffold note.** The obstruction rests on parity's closing exception, an implied last birth that writes no fresh distinction.
  Under not-all-equal both starts continue, as the study says. So this is a result about the parity law with complete rounds,
  which is how the study states it.

## BOND-CLOSURE: closure is read from the inputs. Stands, proved.

**The claim.** A join of three or more parents closes exactly when the least bond on p − 1 of its inputs has size p. For three
parents, that means when a pair of its inputs reads bond distance 2.

**The proof was read line by line and is correct.**
- The key step is the bridge lemma: one shared crossing cannot divide a legal group. Its case analysis is complete.
- The cost argument then gives b = p exactly when the inputs exhaust the loose distinctions.

**Checked** on every birth of three or more parents in 300 random starts of 6 to 10 knots (rounds 0 to 3):
- 5,520 births, with 4,616 of three parents, 901 of four and 3 of five;
- the criterion agrees on all of them, including the closing births (the four-knot and chain controls, and one random).

## FRESH-DEMAND: what fixes a birth's fresh count. Stands.

- **Formula (1)** computes the demand from the parents' child lists alone. It equals the engine's lookahead demand on all
  **10,980** births of the same stages.
- **Not checked:** the information lower bounds and the fixed-map finite counts (lighter).
- **The fairness qualification** that SERIAL-REPAIRS logged applies to its infinite orders.

## SERIAL-REPAIRS: present holdings and fairness. Stands; its logged Narrowing is right.

**The impossibility proof was read.** Under weak fairness after strict global joins-first, no fixed radius guarantees completion.
- **How.** The prefix-extension, freeze-one-piece and projected-run argument is sound.
- **Why.** A waiting one-parent birth on the frozen piece is never continuously on the filtered list, so weak fairness does not
  force it. Strong fairness would.

**The Narrowing logged against the round-free claim** ("every order reaches the same completed structure under the fixed map") is
correctly a Narrowing of a quantifier: finite orders finish and the fixed-map counts stand.

**Not rebuilt:** the seven repair tests and the 4-step local rule (lighter).

## How the work was split

- **The referee:** read the decision notes, `end_operator.md`, `criterion.md`, `demand_proof.md`, `present_proof.md` and the
  correction entry, and wrote `job_g1.py`.
- **Where it ran.** Under `scripts/longrun.py`: `runs/referee-g1`, with the record in `referee_g1.json`.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
