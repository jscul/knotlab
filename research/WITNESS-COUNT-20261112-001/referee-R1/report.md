# Referee report WITNESS-COUNT-R1 (lean, as asked)

**Verdict: Confirmed with fixes: one Narrowing, two Not a block.**

**Every least count recomputes exactly by a second method with no SAT at all.** A copy's three ends separate its insides from the
rest, so the least number of witnesses inside a copy is a table over its end states, built depth by depth.
- **The match.** The table gives w at T, T+1 and T+2 for all 798 families the census read: w 798 of 798, N 798 of 798, and B 593 of
  593.
- **Further.** It also covers the 95 families the census could not read, and runs to depth T+6.
- **SAT agrees.** My own SAT check confirms the joint query on 262 families (262 of 262 agree), and that no state has fewer than w
  witnesses at any depth.

**The table also locates the excess.** It comes from distinctions shared between copies, and it is decided by a finite table.
- **The mechanism.** A copy's least count depends on its three ends.
- **The constraint.** The ends of a copy's calls are its own distinctions, tied by its knots, so the calls cannot all sit at their
  cheapest end states.
- **The check.** Every one of the 524 non-multiplicative one-definition families has a least count that varies with the end state.
  No family with a constant table fails to be multiplicative.

So "not a sum of local needs" overstates it. The need is a sum over copies of an end-dependent need, minimised over the shared
distinctions of the copy that makes them.

Referee: the background referee thread, 2026-11-12.
- **Code.** `ref_wc.py`, my own. It uses LIMIT-ONLY-R1's bitset relations and LIMIT-STATE-R1's expansion and SAT encodings, and
  imports neither census.
- **Advisor.** The advisor model was not consulted.

## 1. The table (a second, exact method)

**The recursion.** Let f_{i,d}(s) be the least number of witnesses at relative depth d inside a copy of definition i whose ends are
in state s.
- **The rule.** f_{i,d}(s) is the minimum, over assignments of the copy's own distinctions with ends s, its knots satisfied and every
  callee's ends in the callee's limit relation, of the sum of two terms:
  - over its SELF calls, g_d(callee ends), with g_1(e) = [e all equal] and g_d = f_{i,d−1} for d ≥ 2;
  - over its calls of earlier definitions j, f_{j,d}(callee ends).
- **The answer.** w_t = min over s of f_main,t(s).
- **Why it is exact.** Given the copy's distinctions, the copies it makes share nothing else. The limit relations are exactly what
  extends below, by the fixed point.

| Item | Census | Referee (table) |
| --- | --- | --- |
| w_T, w_T+1, w_T+2 | 798 families | 798 of 798 equal |
| N_t | 798 | 798 of 798 equal |
| B_t (one-definition families) | 593 | 593 of 593 equal, as max over s of c^s · w_{t−s} |
| families readable | 798 (92 over 60,000 knots, 3 over 20,000 calls) | 893 (all but the recurrent family) |
| joint attainment | 107 of 798 | 262 checked by the referee's SAT, 262 agree (40 joint) |
| a state below w at any one depth | none (gate) | none, on the 262 |

**B's recursion is right.** For one-definition families it reduces to B_t = max over s ≥ 1 of c^s · w_{t−s}, the antichain at one
level, where c is the number of SELF calls. It equals the census's tree recursion on all 593.

**The totalizer search is right.**
- **The indexing.** rhs[k] means "at least k + 1", so −rhs[ub] bounds the count by ub.
- **The search.** The doubling stops at the first feasible ub, and the binary search on [max(1, B), ub] keeps hi feasible.
- **The guard.** The bound check at B − 1 is exactly the gate.

**The amendment changed memory only.** The table, which uses no totalizer, gives the same w on every family.

**The joint query is right as built.** It asks for a state at w at every depth together. My SAT, a different encoding (sequential
counters), agrees on all 262 families it could encode within 1.5 million clauses. I stopped it there, as the check is lean.

## 2. Where the excess comes from

**Two values or more.** In one-definition families, w_{T+1} = B_{T+1} = c · w_T exactly when some assignment of the top copy's
distinctions puts every one of its c copies at an end state of least f_T.
- **The non-multiplicative ones.** In all 524 of them, f_T takes two or more values across end states: 2 values in 214, 3 in 217 and
  4 in 93. None with a constant table is non-multiplicative.
- **The multiplicative ones.** Among the 69, 43 have a constant table. The other 26 have a varying table but can still place every
  copy at a cheapest state.

**An example.** In family 6, a copy needs 1 witness at depth T with some ends and 2 with others. The top copy cannot give all three
of its copies the cheap ends, so w_{T+1} = 4 against B = 3.

**Which ends are cheapest.** All-equal ends are the cheapest in 217 of 593 tables, and ends not all equal in 376.

**So the excess is a property of one definition's body,** decided by an 8-entry table per depth. It comes from the copies sharing the
calling copy's distinctions (its ends and its own distinctions are the ends of several calls). It is not interference spread across
the whole pattern.

**The joint failures (P2)** are the same effect across depths. Each depth's table may be minimised by different assignments of the
shared distinctions.

**The growth law to T+6** (by the table, 892 branching families):
- **The share.** The median w/N is 0.020, 0.027, 0.029, 0.030, 0.030, 0.030 and 0.030 from T to T+6, so it levels off.
- **Change from T to T+6.** The share changes by a factor of 2 or less in 775, rises more in 99 and falls more in 18.

## Fixes for the thread

1. **The Answer and the Reading.** "Not a sum of local needs" and "placed as a whole, across depths and branches, not part by part"
   overstate it.
   - **What holds.** Given its three ends, a copy's need is local and the copies are independent. The least count is a sum over
     copies of an end-dependent need, minimised over the distinctions of the copy that makes them, which is an exact table of 8
     entries per depth.
   - **Where the excess comes from.** Every non-multiplicative family has an end-dependent need (524 of 524).
   - **Direction #1** ("where the extra witnesses sit") is answered in kind by this.

   **Narrowing** (settled by a finite table).
2. **The nested share.** The 9.6% comes from one jointly least state per family, chosen by the solver. It is not canonical, so say
   so or take the range over least states. **Not a block.**
3. **The growth law.** The table extends the census to the 95 unread families and to depth T+6, where the median share levels at
   0.030. Say the law is settled in kind by the table. **Not a block.**

## Files

| Command | Output | What it does |
| --- | --- | --- |
| `WC_NOJOINT=1 ref_wc.py run W 6` | `dp_*.jsonl` | the table for every family, compared with the census |
| `ref_wc.py run W 12` | `result_*.jsonl` | the same plus the referee's SAT for the joint query (stopped after 262 checked, by choice) |
| `ref_wc.py summary` | `result_summary.json` | the counts |
