# Starts where both distances grow: what stands

Epic `BOTH-LONG-20261126-001` (G18, at the coordinator's go-ahead after `SECOND-CHECK-20261126-001`; the scaffolds of
A291), closed 26 November 2026. A check by the thread: computed, with an argument; advisor consulted read-only in the
repository; referee pending. [The note](README.md)


> **Refereed (R1, [report](referee-R1/report.md)): confirmed with fixes, no Block.** All 50 ring preparations and 44 from six
> sampled starts matched. **Narrowings:** the ring's size bounds the smaller distance (eight knots, round four: 8/11 free,
> 9/8 pinned); of the 350 sampled starts, 153 reached round four and 75 ever had a class; **"a start with a long cycle is
> rare" is wrong**: cycles of five or more knots occur in 99 of 200 census starts and 85 of 150 extension starts, yet their
> distances stay small, so a long cycle in the start is not enough; the old odd ring attains both minima but so do other
> sets; one sampled start had 128 ties through a distinction, over the cap of 64 (keeping every tie reproduced its
> distances); a recorded reading does use the class character as a supplied weighting; with loose values pinned at
> nonzero values a positive class can still be singled out. Logged in `docs/CORRECTIONS.md`.
## What stands

1. **Ordinary growth makes a class with both distances long, at the start ring's length.** Under parity, a ring of n
   knots grown round by round gains one class; on odd rings (5 to 11) its read and change distances both reach n, from
   about (n − 3)/2 rounds with loose values free or (n − 1)/2 pinned, and stay there to round 6; on even rings (4 to 12)
   one is n and the other grows by two a round. Neither ever exceeds n: the length is the built start's.
2. **Sampled starts do not.** In 350 sampled starts of three to eight knots grown to round 4, the largest min(read,
   change) is 4, at the four-knot ring itself.
3. **The old ring is its own conjugate on odd rings** (the least change and a least label at once, overlapping itself
   oddly), and the class character changes sign under it. But every two-class structure has that character, it is fixed
   only through the all-zero state, it sums to zero, and no recorded reading weights by it: the structure fixes which
   signed function a relative sign would be; no native reading uses it.

**Not shown.** Growth beyond the start's length; rings that meet (the next-layer question); other move rules.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — both distances long | **Status:** Successful (a positive with a scope, and a negative) | Rings grown by ordinary growth reach both distances n; sampled starts do not |
| Local direction — a relative sign set by the structure | **STOP** (obstruction learned; referee pending) | The sign function is fixed by the structure; no reading of the law uses it |
| Broader exploration — rings that meet | Unmapped | Whether ring labels obey a forced parity (a next-layer knot) is the next-layer question |
| Long-term goal — G18 Comparing growth laws | Obstruction learned | The recorded laws make a protected two-valued fact with both distances long, and still no sum that weights it with a sign |

**Next step:** Research directions — #1 proposed (it is the other thread's queued question; the coordinator's call)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Two or three odd rings that meet: do their class labels obey a forced parity (a next-layer knot), and does a least class change change exactly two (a next-layer move)? | 3/3 — would make ring facts the distinctions of a next layer | 3/3 — `distances.py` reads it | Grow meeting rings, read the classes and labels → a forced parity, or free bits | Proposed |
| 2 | The same distances under other move rules | 1/3 | 3/3 | Inclusion-minimal moves give one class; read the rest | Deferred |

**Intuition (an exact link, not evidence).** A grown odd ring holds one bit that only the whole ring can read and only the
whole ring can change, the literature's logical qubit of a code of distance n, with the twist that the reading set and
the changing set are the same, which on n odd makes them anticommute. Such a bit is exactly what a next layer's
distinction would need to be, which is why the meeting-rings test is the next question.

**Corrections:** two logged: my "one distance is always short" in the second-check study holds after one round only; and
that study's referee (no Block; the mutual-duality intuition fails).
**Goals:** checkpoint row added (G18); no goal changed.
**Assumptions:** A291 history (rings: both distances reach n under the move rule).
**Scaffolds:** the ring starts (a built start, named), loose values free or pinned (swapped; the rounds to reach n change,
the endpoint does not), the move rule (A291), one engine. The length n belongs to the start; that both distances reach it
holds under both settings of the loose values.
**Advisor:** consulted read-only in the repository with the skill; its catches (a wrong label flag, the cap by n, the sign
function common to every two-class structure, tie-cap and holder-count checks) were checked and taken.
