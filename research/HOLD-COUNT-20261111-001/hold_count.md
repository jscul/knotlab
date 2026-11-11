# What it takes to hold a count

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a drawn knot pattern; a knot world is a drawn knot pattern. Results are unchanged;
the earlier text is in git history.

Epic `HOLD-COUNT-20261111-001` (backlog B152, G8 with G15; program mathematics), 2026-11-11, at the coordinator's go-ahead after the
owner's question about knapsack. Pre-registered in [preregistration.md](preregistration.md), frozen in commit `29121e4e7` before the
census ran. Proof family: `proofs/HOLD-COUNT-20261111-001A/`.

## The question

The owner asked whether solving a pseudo-polynomial problem is "statistical", some choices leading to the solution faster, and whether
knapsack could be "an emergent representation of what's happening at the logical emergence scale". Knapsack's table is fast because
every partial choice is summarised by one running total. A total is a magnitude, and the knot's own law, not-all-equal, has no preferred
value. So: which counts can a drawn knot pattern with that law hold, with and without one fixed value supplied by the world, and how small can
the space be?

## The answer

**The knot law writes a count in binary, and only in mirror pairs.**

- **The mirror lemma (proved by hand, refereed by fresh code).** A drawn knot pattern whose floor states are closed under flipping every point
  reads a count of n held points mod m (n ≥ m − 1) only when m is even and n is odd, and the codes of c and n − c are complements. So it
  never counts three held points mod 3 without a reference, and it holds their count mod 4 exactly as a full adder.
- **The full adder at the least size (exact).** The 8-point parity torus (2, 0, 4) is already a full adder: hold points 0, 1 and 4, and
  point 5 reads their parity while point 6 reads the negation of their majority, the two binary digits of their count. 13 of the 1,128
  spaces hold one (200 triples); every parity triple in a space of 8 or 12 points is a full adder; the 16- and 18-point tori count
  parity without majority.
- **One reference point buys nothing here (exact in the range).** With a fourth point held at 0, no space holds the count mod 3 or
  mod 4; parity with a reference appears only on three 18-point tori, against 20 spaces without one.
- **Why (computed after the run, exact in the range).** A self-dual map that uses all four of four held points is of one of exactly
  four kinds: the weighted majority [2a + b + c + d ≥ 3]; maj(a, b, a ⊕ c ⊕ d); a switch that reads parity of three points when a fourth
  agrees with one of them and their majority otherwise; and a ⊕ NAE(b, c, d), the knot's own relation read against a fourth point. Only
  the last two can give, against a reference, a bit that a count mod 3 needs. The spaces show 6,783 of the first, 74 of the second and none of the other two.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Counts mod m only for even m and odd n; mod 4 of three = the full adder | proved by hand; refereed by fresh code (90 cases of its core; 32,424 classes closed under flipping every point) |
| The 8-point parity torus is a full adder; 13 spaces hold one | exact census of 1,128 spaces |
| No count mod 3 or mod 4 with one reference point | exact census of 1,128 spaces |
| Exactly four kinds of self-dual map use all four of four held points; the spaces show two | the four kinds by exhaustion of the 256 self-dual maps; the census of 4,634,517 free four-point sets after the run |

## Against the pre-registration

- P0 held, as proved. P1 held, at the smallest size possible. **P2 failed:** I predicted a count mod 3 with one reference somewhere in
  the range, and there is none. P3 and the measure criterion cannot be evaluated without an instance of P2.
- My first guess after the run, that counting needs the held points to fix every point, was wrong: only 48 of the 804 parity triples
  do. The second pass found the reason above.
- Control C1's summary lists the 3-point torus (3, 1, 1) as read by only one epic: `PARITY-NEEDS-20261111-001` stored its empty tally as
  nothing. Both epics count zero there, so the control holds. No defect in the census code; nothing was dropped or re-run.

## What it changes

- **For the owner's knapsack question.** The drawn knot pattern does hold a running total, natively and at its least size: in binary, as the
  full adder that digital circuits use, not as a table of every total. It holds only counts that look the same from both sides of the
  mirror, so a count mod 3 needs a fixed value supplied by the world, and in spaces up to 20 points even that is not enough: a point
  would have to read whether three held points are not all equal, the knot's own relation, and none does. Nothing here bears on P versus
  NP; the lemma is classical in substance (Post's self-dual functions; spin systems without fields, Whitfield, Faccin and Biamonte 2012).
- **For composition (sub-goal B148).** A single space gives the two binary digits of three held points for free, so composing tori would
  give binary counters; counting mod 3 would need composition to supply the switch or a ⊕ NAE, which no single space here does.

## Assumptions

A65 (a held reference point is supplied by the world) added for this epic and used by P2; status unchanged. Relied on: A47, A58.

## Corrections

None.

## In the owner's words

A drawn knot pattern can keep a running total, and it keeps it the way a computer does: three held points come out as two binary digits, a
parity and a carry, in the smallest space that counts at all. It only keeps counts that look the same from both sides of the mirror,
so counting in threes needs a fixed value from outside. Even with one, no space this small does it, because it would have to read
the knot's own relation, whether three things are not all equal, and none can.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — what it takes to hold a count (B152) | **Status:** Successful | lemma refereed; full adder at 8 points; no count mod 3 with a reference |
| Local direction — counts held by one drawn knot pattern | Continue | the two missing four-point maps are a sharp target |
| Broader exploration — arithmetic and learning lines | Known alternatives | composing counters (B148), phases, a native reference |
| Long-term goal — G8 From spacing to arithmetic and sets | Capability gained | binary counting is native; odd moduli need an input |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Does a drawn knot pattern read its own relation? | 2/3 — Substantial | 2/3 — Testable | four-point maps on lattice tori of 21 to 24 points by SAT, and a proof attempt → a ⊕ NAE or the switch found, or a reason none occurs | Selected · awaiting go-ahead |
| 2 | Binary counters from composed tori (sub-goal B148) | 3/3 — Major | 2/3 — Testable | two (2, 0, 4) tori wired so that the carry of one feeds the next → a count of more held points in binary, or the wire unties | Alternative · awaiting go-ahead |
| 3 | Totals carried as phases in signed laws | 2/3 — Substantial | 1/3 — Stated | a signed law whose phase carries a count mod 3 | Alternative · deferred |
| 4 | A native reference (challenge A65) | 2/3 — Substantial | 1/3 — Stated | a space or learned frame fixing one value in every floor state | Alternative · deferred |

- **#1** asks whether the absence of the two maps that could count mod 3 is a property of the knot law or of small spaces; a proof
  would say the knot law counts natively only in binary, at any size. It reuses PARITY-FIVE's SAT tools on the tori of 21 to 24 points
  and the after-run classifier here, so it is a few hours at most. The uncertainty is whether a proof exists at all.
- **#2** is the learning line's sub-goal, raised by the full adder: the parity torus already carries the carry. It stays the owner's
  call while that line is paused.
- **#3** would follow the Fourier route that makes subset sum pseudo-polynomial; it waits on the interference reading the owner has
  not decided. **#4** is A65's challenge; no mechanism for a native reference is in sight.

**Corrections:** none. **Goals:** G8 checkpoint (capability gained; no goal change). **Assumptions:** A65 added (Assumed), history line
for its use here. **Basket:** #1 recorded for a go-ahead; B148's entry notes the full adder; B152 taken.

## Final report as sent

Sent to the owner in the project thread on 2026-11-11 (about 19:00 UTC): the three results above (the mirror lemma proved and refereed;
the 8-point parity torus a full adder; P2 failed, with the two missing four-point maps as the reason), the position table and the
next-directions table of this note with #1 selected and awaiting a go-ahead, and the Corrections, Goals, Assumptions and Basket lines.
