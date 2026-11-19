<!-- modelUsage: claude-fable-5-2 -->

I did not open the epic's code or the cluster-map definition; this rests on your description alone. Three places to check are marked **Check**.

## 1. Serial law: yes with monotone moves, no with the pilot's readings

**Why the pilot laws depend on order.** They read the current state in three ways that a later move can change:

- **Fewest count at creation.** It counts future joins, so partners not yet made are missed and the junction gets too few bits.
- **Offshoot for a loose bit "in no current group".** This is enabled by absence, and absent now is not absent for ever. It would explain the lone 4-place knot growing past 300.
- **Groups among whatever is live.** Serial orders keep junctions of different sizes live together, so the policy makes joins the rounds never make. It would explain closing after 8–10 instead of 16.

**The law that works.** A cluster may be built once all its parents exist; nothing else is a move.

- **Order-independent.** Building never disables or pre-empts another move, so the built sets are exactly the parent-closed families and every order is a linear extension of one partial order.
- **Never stalls.** A smallest unbuilt cluster always has all its parents.
- **Same result.** The limit is the whole cluster family, so the counts by size are the round counts.

Your "bits on demand plus complete sibling set" is this law, with two costs to state:

- **Fewest does no work.** With arity on demand, the fewest count holds of the finished thing and is automatic at every stage. The group test carries everything.
- **The floor needs a rule.** A junction passes through one and two places, which is not a knot. Either create it with three places and grow from there, or claim knots only of the limit. "This floor bit is never taken" is again an absence, so decide it from the map, not from the state.

**Check:** is a junction's cluster identity readable from the presentation, through kept ancestry, or only from the unrolled map? If only from the map, the law reads the map and you should say so.

**The impossibility you could state.** It holds for bounded-radius laws that fix arity at creation or fire offshoots on absence, and that never stall.

- Take two starts that agree within radius r of a junction J, where a partner of J arrives in one and never arrives in the other.
- Delay the partner. The law must commit at a finite stage on the same local view in both, so it is wrong in one.
- It is not true of laws that read the whole presentation, since those can simulate the rounds.

**Check:** you need a concrete pair of starts as the witness. Without one, this is a template, not a result.

## 2. Is size an inside clock?

It is a clock only if the law reads it.

- **Rank is a logical clock.** Rank = 1 + max parent rank is a Lamport timestamp. A law that says "join only equal-rank siblings" uses an inside clock, which is the thing the owner rejects.
- **The closure law reads only which parents exist.** Size then follows as a theorem: every chain of parents below a cluster has the same length, size − 1, because each step removes one point.

Suggested wording: "Size counts what a junction spans, not when it is made. The law never reads it, and junctions of different sizes are made in any order. What is fixed is only that a junction comes after its parents." Say plainly that this partial order remains. It is a before-and-after, but it has no ticks.

## 3. Speed statement to freeze

Freeze shares by size, plus each part's growth ratio of counts by size. Both are free of order.

I would not freeze the uniform random order as a point prediction:

- **It is a scheduler.** "Each buildable cluster equally likely" supplies an input, and a different measure, such as each junction at rate 1, gives different numbers.
- **Equal-ratio parts behave like a Pólya urn.** Their shares converge to a random limit set by early luck, not to a number.
- **Unequal ratios give a slow takeover.** The faster part's share goes to 1, but only polynomially in N.

Run it as an exploratory arm and report the spread over orders. The tree analogy behind the urn claim is only indicative, because clusters need all their parents.

Also record what 2.6075 means for the two-ring join. Independent parts with sizes adding would give the golden ratio, the larger of the two. Parts multiplying at equal size would give its square, 2.618. The value sits just under the square, and the "both" share by size will show why.

## 4. Predictions and falsifiers

| # | Prediction | Falsifier |
| --- | --- | --- |
| P1 | Closure law, 20 orders per start: the built set is always a parent-closed part of the round growth. Completed sizes match 2,4,6,8,10; 1,4,6,4,1 (closing at 16 in every order); 5,6,7,8,9; 5,10,15,25,40. | One order with a different count at a completed size, a junction outside the cluster family, or a stall. |
| P2 | In every order, rank equals size − 1 for every junction. | One junction whose rank differs between two orders. |
| P3 | Each naive law's first divergence from the cluster family is one of the three events in section 1. Removing all three restores order independence; removing any two does not. | A divergence of a fourth kind, or independence restored by a partial repair. |
| P4 | Ratios by size are the round ratios in every order. No claim is made about counts per serial step. | Follows P1. |
| P5 | In connected joins the "both" share by size tends to 1. Each part's own ratio equals its stand-alone ratio. | A part's ratio shifted by the join. This would be the more interesting result. |
| P6 | Random order, exploratory: shares vary across orders at fixed N for equal-ratio parts. | Shares concentrating on one number. |

P3 is the cheapest discriminator and I would run it before the 20-order freeze in (A). It turns "order-dependent" into "order-dependent for these three reasons".
