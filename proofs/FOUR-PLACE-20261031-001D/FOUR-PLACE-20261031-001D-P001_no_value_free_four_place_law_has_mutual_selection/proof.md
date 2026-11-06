# No value-free four-place law has mutual selection

Status: Proved

Ticket `FOUR-PLACE-20261031-001D`, 2026-10-31.

## Definition

As in `PINNING-20261031-001C`, a law is *mutually selecting* on regular systems when:
- **(M1)** its failing systems form a non-empty class recognisable in polynomial time; and
- **(M2)** counting its solutions is #P-hard in general.

## Theorem

**Statement.** Unless NP-complete problems are polynomial, no value-free four-place knot is mutually selecting on 4-regular
4-uniform systems. Together with ticket B, the value-free not-all-equal law fails on regular systems only at three places, where its
failures are the knot's Pfaffian spaces.

**Proof.** The four classes of ticket A:

| Class | Fails on 4-regular systems | (M1) | (M2) | Mutually selecting |
| --- | --- | --- | --- | --- |
| parity | yes (A) | yes (linear algebra) | no: count 2^{n−r} or 0 (check 1) | no |
| not-exactly-two | yes (A) | no unless P = NP: coNP-complete (C) | — | no |
| twelve | yes (A) | no unless P = NP: coNP-complete (C) | — | no |
| not-all-equal | never (B) | no: empty class | — | no |

If a coNP-complete class were recognisable in polynomial time, then P = coNP and so P = NP. ∎

## Reading

**Three places against four.**
- **At three places** the knot is rigid: it cannot pin, and its pieces build no equality. It fails exactly on the Pfaffian spaces, which
  are recognisable, and these make two counts easy (PINNING C, KNOT-COUPLING).
- **At four places** no preferred value is common: all 30 value-free knots lack one.
  - The only rigid one, not-all-equal, never fails. This is Thomassen's theorem: digraphs with in- and out-degree at least 3 are even.
  - The others build equality without constants, and that makes them as hard as satisfiability.
  - Parity is easy to count.

**Why three is special.** Mutual selection needs a law that fails and yet stays rigid. Thomassen's degree threshold is the exact point
where rigid laws stop failing:
- a k-place line gives a digraph of degree k − 1;
- that digraph can avoid evenness only when k − 1 = 2.

**In the owner's terms.** The two/three boundary reappears one level up. Among laws that never fix a value, only the three-place one can
fail in a recognisable way. Its failures are global (Pfaffian), which is what the parity correction showed selection needs.

## What this does not establish

- **Four-place laws that prefer a value.** Not classified. At three places they either pin (and are hard) or never fail. A four-place
  pinning theorem is expected to behave the same way but is not proved here.
- **Counts of the four-place laws.** Not needed for the theorem, and not established.
- **Arities five and above.** Only value-free not-all-equal is settled there (B). The other value-free k-place laws are not classified.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; A, B, C and PARITY-CORRECTION B Proved and passed. | pass |
| 1 | Parity's count 2^{n−r} or 0 against brute force on every 4-regular system with n ≤ 7, with four signings each. | 80/80 |
| 2 | The classification table, assembled from the upstream checks. | pass |
| 3 | The Fano plane fails not-all-equal (k = 3), while B rules out failures at k ≥ 4. | pass |

## Novelty

- **New.** The statement. No source was found.
- **Classical.** Its ingredients: Schaefer, Thomassen, Seymour.
- **Proved here.** Everything else, in tickets A–C.
