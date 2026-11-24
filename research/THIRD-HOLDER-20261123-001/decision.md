# What a third holder gives: decision

Epic `THIRD-HOLDER-20261123-001`, 2026-11-23, on the owner's go-ahead for direction 1 of
`REVIEW-LEADS-20261123-001`. Two studies, frozen after a cold review by the advisor model, implemented by Claude Opus
sub-agents and checked by the thread with separate code and by reading the argument; and one note by the thread.
Every result is referee pending. [Referee hand-off](referee_handoff.md)

## What was found

| Record | Verdict | Finding |
| --- | --- | --- |
| [Ticket A](../THIRD-HOLDER-20261123-001A/result.md), the 18-knot structure checked in full | Supported | 20/9 with both complete records hidden, by full enumeration. At weight ratio ρ the largest hidden score any distribution can give is 4(1 + ρ²)/(1 + ρ)², by argument, reached only with equal totals. Two and three births per setting give 68/25 and 260/81; the second is above the quantum limit. A setting keyed to an old value changes the far record by up to 2/9 |
| [Ticket B](../THIRD-HOLDER-20261123-001B/result.md), the smallest structure | Supported, one prediction failed | If the setting birth may take a distinction already held twice, 7 knots of both laws with no distinction held three times give 19/9, hidden; 8 knots give 20/9; none with 6 or fewer within the census. With loose observer distinctions and at most three holders none was found |
| [Note](third_holder_moves.md), which moves give a third holder | Argument and reading of the record | Parity knots with two holders hand a value on once and never twice. The Fano pattern less one knot hands a value to three places and has distinctions held three times. No recorded growth move gives a third holder to a value not already tied |

## What it says

**The excess is the weighting's; the structure only has to hide it.** With every present word weighted equally, an old
word's weight depends on both settings. The ceiling shows how much that can give with hidden settings, and it is
reached.

**One move is missing from ordinary growth, and it is small.** Under ordinary growth a loose distinction is taken by
one birth and is then shared; nothing takes it again. A birth that takes a distinction already held twice is enough:
seven knots, both laws in one structure, nothing else out of the ordinary. Requiring the birth to take a loose
distinction pushes the smallest known structure to 18 knots with two distinctions held four times.

**Nothing here stops at the quantum limit.** The score rises with the number of births a setting triggers and passes
2√2 at three. A setting keyed to an old value sends a message; ordinary growth cannot key a birth to a value.

**What is still supplied.** The weighting; the settings, which are births chosen from outside; the move itself; and
both laws in one structure, which no recorded growth has made.

## Records

- Freeze commit `3378865bd6`. Advisor question and answer: `advisor/`.
- The tracker rows of this epic were written without a commit, like those of the epic before it.

## Final report as sent

Sent to the owner on 2026-11-24 00:14 UTC.

Direction 1 is done. A hidden excess needs one move that ordinary growth lacks: a birth that takes a distinction already held twice. With that move seven ordinary knots are enough, and the most any structure can reach under this weighting is now known exactly. Both studies are referee pending.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — what a third holder gives | **Status:** Successful | The structure is verified in full, its ceiling is proved, the smallest structure is found and the missing move is named |
| Local direction — a hidden excess under equal weight on every present word | Practically exhausted | The largest hidden score at every weight ratio is known and reached |
| Broader exploration — rival growth laws | Known alternatives | No recorded growth move gives a third holder; a birth that re-takes a shared distinction is a new one |
| G18 Comparing growth laws | Capability gained | The first structures with a hidden excess, and the one change that allows them |

- **The 18-knot structure holds in full.** Each of its four finished structures has 1,152 allowed words out of 2^28 assignments. The score is exactly 20/9 and both complete records are hidden. Three computations agree.
- **The ceiling is proved.** With hidden settings and weight ratio ρ, no distribution and no outcomes can score above 4(1 + ρ²)/(1 + ρ)², and reaching it needs the four totals equal. The structure sits exactly on it. The implementer found the argument; I read it step by step and found no gap.
- **Nothing stops at the quantum limit.** Two births per setting give 68/25 = 2.72, below 2√2 ≈ 2.83. Three give 260/81 ≈ 3.21, above it. Both are hidden. The three-birth case was checked by side tables and backtracking, not full enumeration.
- **A setting keyed to an old value signals.** It changes the far observer's complete record by up to 2/9. Ordinary growth cannot key a birth to a value.
- **The smallest structure has seven knots.** If the setting birth may take a distinction that already has two holders, seven knots of both laws give 19/9 with hidden settings, and no old distinction is held three times. Eight knots reach 20/9. None with six or fewer exists within the census.
- **With loose observer distinctions, three holders were not enough.** Nothing was found in sides of up to 5 knots (4.03 billion pairs scored). The 18-knot structure has two distinctions held four times.
- **Why two holders fail, for parity.** The ends of a two-holder parity part satisfy only their total parity, so such a part hands a value on once and never twice. For parts with a not-all-equal knot the evidence is the census.

The excess comes from the supplied weighting, where an old word's weight depends on both settings. The move only lets a structure hide it. The settings are still births chosen from outside, and the seven-knot structure mixes both knot laws, which no recorded growth has done.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A growth law in which a birth may take a shared distinction | 3/3 — Barrier | 2/3 — Testable | Freeze one rule: a knot with no loose distinction pays with a shared one → classed on survival, the recorded sources and the pace limit, or shown equal to a recorded rival | Selected · awaiting go-ahead |
| 2 | Both laws in one grown structure (B232, B254) | 3/3 — Barrier | 3/3 — Ready | Grow mixed starts by ordinary growth → the seven-knot structure's old part is reached, or a reason it cannot be | Alternative · deferred |
| 3 | Check the ceiling against the literature and write it up | 2/3 — Substantial | 3/3 — Ready | Compare with the relaxed-independence bounds → known, or a note with the knot structures that reach it | Alternative · deferred |
| 4 | Loose observer distinctions with three holders: a structure or a proof of none | 2/3 — Substantial | 2/3 — Testable | Extend the parity argument to parts with a not-all-equal knot → a proof, or the first structure | Alternative · deferred |
| 5 | Independent referee of both studies and of the six before them | 2/3 — Substantial | 3/3 — Ready | Replay from the hand-offs → confirmed or a failing case | Alternative · deferred |

1. This is the move the result points to, stated as a law. It would also remove the stall, since a knot short of loose distinctions could still pay. It is a new objective with a choice among rules, so I have not started it.
2. The seven-knot structure needs parity and not-all-equal knots together; whether ordinary growth with mixed laws makes its old part is a finite question.
3. The argument is of the kind the literature has for relaxed measurement independence. Nobody here checked whether this exact form is published.
4. The census is a null for its sizes and the parity argument covers only parity parts.
5. My checks used separate code and a close reading, by the same designer.

**STOP** on direction 1's question: the move is named, the smallest structure is found and the ceiling is proved. Direction 1 above is a new objective and waits for you.

**Corrections:** One, a narrowing, logged in `docs/CORRECTIONS.md`: my last report said the 18-knot structure works "once a distinction may have a third holder". It has two distinctions held four times, and three holders were not enough when the observer's distinctions are loose. What is enough is the narrower move above.
**Goals:** Checkpoint row added; G18 gained a results line. No goal changed.
**Assumptions:** A225 to A227 record the scaffolds: a birth that takes a shared distinction, the pooled reading of a value-keyed setting, and the size order.
**Scaffolds:** The weighting; births as supplied settings; the two classes of observer distinctions; the 18-knot and 9-knot structures written by hand.
**Basket:** Direction 1 of the earlier epic is taken and settled. The postulates basket still leads with B254, B255 and B260.

**Housekeeping.**
- Commits: `3378865bd6` (the freeze), `37ba5db174` (the epic, 303 files), `b66fec1151` (goals lines and the correction). Publication to knotlab succeeded.
- Not committed: this epic's tracker rows, like those of the epic before it. The shared tracker files still hold other threads' pending rows; one integration commit remains your call.
- Sub-agents: Opus 5.5 at extra-high effort for both studies. Fable 5.2 reviewed the designs before the freeze.
- The decision note is `research/THIRD-HOLDER-20261123-001/decision.md`.
