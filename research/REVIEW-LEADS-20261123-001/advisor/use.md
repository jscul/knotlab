# Advisor review before the six freezes

Claude Fable 5.2 (`claude -p --model claude-fable-5-2 --tools ""`, confirmed in `answer.json` under `modelUsage`) reviewed all six designs cold on 2026-11-23, from `question.md`. Its answer is kept verbatim in `answer.json`. Each pre-registration ends with the strongest objection to its design and the change made. Two points changed more than one design:

- Design C's setting is a payment allocation: which of two loose distinctions a parent pays. Ordinary growth leaves that open, so it is a setting that can arise inside one history, and design E's list of freedoms had left it out. Design C now has an allocation class as its primary class and design E enumerates allocations.
- Several first predictions were false or empty by plain reasoning (one-parent births can more than double and never fail the operator test; the not-all-equal learner answers nothing by construction; a finite donor goes to whoever asks first). They were replaced before the freeze.

**Correction, 23 November 2026.** The first point above is wrong as stated. A payment allocation is open under ordinary
growth, but two loose distinctions of one knot are exchangeable, so the two allocations give one structure with two
names exchanged. It is not a setting. Ticket C's allocation class cannot exceed 2 for that reason, and ticket E's
result note carries the correction. The follow-up design (ticket G) was reviewed separately (`question_g.md`,
`answer_g.json`).
