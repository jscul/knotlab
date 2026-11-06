# Mutual selection at four places

Status: Proved

Ticket `FOUR-PREFER-20261101-001D`, 2026-11-01.

## Definition

As in `PINNING-20261031-001C`, a law is *mutually selecting* on regular systems when:
- **(M1)** its failing systems form a non-empty class recognisable in polynomial time; and
- **(M2)** counting its solutions is #P-hard in general.

## Theorem

**Statement.** Unless NP-complete problems are polynomial, a mutually selecting four-place knot on 4-regular 4-uniform systems must lie in
one of five weak classes: 13, 14, 15, 16, 17. These prefer a value and exclude two or three states. None of them failed on any system
examined.

**Proof.** The 20 classes (ticket A):

| Class | States | Status | Mutually selecting | Evidence |
| --- | --- | --- | --- | --- |
| 0 parity | 8 | count 2^{n−r} or 0 | no: (M2) fails | FOUR-PLACE D |
| 3 not-exactly-two, 11 twelve | 10, 12 | NP-complete on 4-regular systems | no unless P = NP | FOUR-PLACE C |
| 18 not-all-equal | 14 | never fails | no: (M1) fails | FOUR-PLACE B |
| 19 clause | 15 | never fails | no: (M1) fails | A |
| 1, 2, 4, 5, 6, 7, 8, 9, 10, 12 | 9–12 | NP-complete on 4-regular systems | no unless P = NP | B |
| 13, 14, 15, 16, 17 | 13–14 | never failed in any search | open | C |

**Why NP-completeness rules out (M1).** NP-completeness of the decision makes the failing class coNP-complete. If it were recognisable in
polynomial time, then P = NP. ∎

## Reading

- **Three places against four.**
  - At three places one law has recognisable failures and a hard count: not-all-equal, the knot. It is rigid, so it cannot pin and its
    pieces build no equality, yet it fails on its Pfaffian spaces.
  - At four places every class that fails builds a link, and with it equality, so its failures are as hard to recognise as
    unsatisfiability. Every class that cannot fail either way is weak. Its constraints exclude so little that the law never fails
    (proved for not-all-equal and the clause; observed for the other five).
- **Rigid against failing.** At four places nothing found is rigid and still failing.
  - The three-point core, three points on four lines, realizes the twelve class from nine different classes. Through it, almost every
    four-place law builds equality.
  - So three is the only arity found with a law that both fails and stays rigid. Here this holds for all four-place knots, not only the
    value-free ones (FOUR-PLACE).
- **In the owner's terms.** The two/three boundary holds at the next arity for every law, not just for laws without a preferred value.
  Five weak classes are the one gap.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings. A and B Proved and passed, C Complete, FOUR-PLACE B–D Proved. | pass |
| 1 | The assembled table: every class appears once; 15 settled, none mutually selecting; 5 open. | pass |

## What this does not establish

- **The five weak classes.** Whether any of them ever fails (C).
- **Counts.** Not needed here.
- **Arities five and above.** Not classified.

## Novelty

- **New.** The statement and the full four-place table. No source was found.
- **Classical ingredients.** Schaefer, Tovey, Seymour, Thomassen.
