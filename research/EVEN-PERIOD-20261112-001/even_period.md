# Why the knot law's harmonies are even

Epic `EVEN-PERIOD-20261112-001` (`HARMONY-ARITH-20261112-001` direction 1, G8 with G1; program mathematics, group arithmetic),
2026-11-12, at the coordinator's go-ahead. Pre-registered in [preregistration.md](preregistration.md), frozen in commit `8f4b693b8`
before the census ran. Proof family: `proofs/EVEN-PERIOD-20261112-001A/`.

## Words

As in the guide's glossary and the pre-registration: harmony (A70), period, orbit, word, residue pairs, compatible, flippable,
certificate.

## The question

`HARMONY-ARITH-20261112-001` found that every not-all-equal harmony has even periods only, on every base of up to three knot kinds
to span 12. Why, and is it true at every span and with any number of kinds? The coordinator asked first what the law's symmetry gives
by itself, and why no harmony has a state such as 001 repeating, which satisfies the knot kind (0, 1, 2).

## The answer

**No not-all-equal harmony has a state of odd period up to 29, at any span and with any number of knot kinds; the mirror is not
why.**

- **The mirror alone (proved).** Flipping every value keeps the law, and an orbit of odd period is never its own flip, so odd orbits
  come in mirrored pairs. That is all the symmetry gives: it forbids nothing.
- **What does forbid them (proved).** For 001 repeating, flipping one of its 0s gives a state that every base allowing 001 also
  allows, because no knot kind that 001 satisfies sees the change. That state does not repeat, so no base allowing 001 is a harmony.
  In general a word has a flip certificate when a word compatible with it has a position whose flip no compatible knot sees; a
  certificate rules out every harmony that allows the word.
- **And nothing else could (proved).** A word of odd period p without a certificate would itself make a harmony: the base of all knot
  kinds of span less than p that it satisfies would allow only states of period p. So the even-period rule for period p holds exactly
  when every word of period p has a certificate. This equivalence was suggested by the advisor model and proved here.
- **Every odd period to 29 is covered (computer-assisted, refereed).** All 25,328,938 words of odd period 3 to 29 have certificates:
  most are their own, and 560 are certified by another word, from period 17 on. None of the 11 words of known harmonies has one, as
  the lemma requires.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| The mirror pairs odd orbits but does not forbid them | proved by hand (lemma 1) |
| A flip certificate rules out every harmony allowing a word | proved by hand (lemma 3) |
| A word of odd period without one would give a harmony of span less than its period | proved by hand (lemma 4, from the advisor's suggestion) |
| No not-all-equal harmony has a state of odd period at most 29 | computer-assisted: lemmas 3 and 4 with an exhaustive census of 25,328,938 words, refereed |
| Every odd period | not proved; words with one pattern of residue pairs are always their own certificate |

## Against the pre-registration

E1, E2 and the control held. The census took 38 minutes inside its 2-hour cap. The fresh-code referee recomputed periods 3 to 19 by
brute force (identical counts), checked all 534 certificates listed at periods 21 to 29, sampled 300 words at each of those periods
(none needed another word's certificate, so the sample did not exercise that path), and checked lemma 3 on 1,188 actual bases. The
independent session's report is below. Lemma 4 was found after the freeze, with the advisor; it changes no frozen prediction but
makes E1 decisive, since a word without a certificate would have been a counterexample harmony.

## Review

An independent session (a fresh model session that did not see this work's reasoning, `independent_referee/report.md` in the proof
family) found lemmas 1 to 4 correct, recomputed the census to period 21 with identical counts, verified all 560 listed
certificates, sampled each of periods 23 to 29, and confirmed the control. Its caveat stands: at periods 23 to 29 the full census rests
on this epic's run, with every listed certificate and the samples checked.

## What it changes

- **For the owner's harmonies.** The knot law's own repeats are even not because of the mirror but because an odd repeat always leaves
  one value that can flip unseen, so the law cannot pin it down. Up to 29 that is proved; beyond it, the question is now a precise one
  about words.
- **For the count line.** Even periods, the mirror's pairing of offsets (`HARMONY-ARITH-20261112-001`) and counting only modulo an even
  number (`HOLD-COUNT-20261111-001`) are three faces of the same two-sidedness, and here the first is shown not to follow from the
  mirror alone.

## Assumptions

A70 used; status unchanged.

## Corrections

None.

## In the owner's words

The knot law's repeating patterns all have even length, at least up to 29, and the reason is not the mirror. A pattern of odd length
always has a spot that can be flipped without any knot noticing, so the law never holds it in place. If some long odd pattern had no
such spot, it would itself be a harmony; up to length 29 none does.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — why the knot law's harmonies are even | **Status:** Partially successful | proved to period 29 and reduced to words; not proved for every odd period |
| Local direction — flip certificates | Continue | a proof for every odd period or a counterexample is now a question about words |
| Broader exploration — the count line | Known alternatives | antiperiodicity, two shifts, signed knots |
| Long-term goal — G8 From spacing to arithmetic and sets | Capability gained | the law's own repeats are even, for a reason other than the mirror |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Certificates for every odd period | 2/3 — Substantial | 2/3 — Testable | search pattern sets, not words, at periods 31 to 45 (the advisor's route), and seek a construction for words with several patterns → a proof, or a counterexample harmony | Selected · awaiting go-ahead |
| 2 | Why unsplit harmonies are antiperiodic | 2/3 — Substantial | 1/3 — Stated | an analogue of certificates for even words that are not antiperiodic, on unsplit bases → a lemma, or a counterexample | Alternative · deferred |
| 3 | Harmonies along two shifts | 2/3 — Substantial | 2/3 — Testable | as filed by `HARMONY-ARITH-20261112-001` | Alternative · deferred |

- **#1** either proves the rule for every odd period or finds the first odd harmony, which by lemma 4 would have span less than its
  period; the advisor expects candidates near periods 21 to 35 among words with three or more patterns, and the census has already
  seen such words certified up to 29.
- **#2** is the other half of `HARMONY-ARITH-20261112-001`'s rule; certificates cannot address it, since they rule out split bases too.

**Corrections:** none. **Goals:** G8 checkpoint (capability gained, with G1; no goal change). **Assumptions:** A70 used, unchanged.
**Basket:** #1 to #3 recorded. **Advisor:** consulted once on the general proof; its equivalence became lemma 4.
