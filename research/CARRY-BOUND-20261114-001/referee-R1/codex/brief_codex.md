# Independent recomputation and critique: CARRY-BOUND-20261114-001

You are an independent referee's assistant. The study's code is agent-written, so your recomputation must be **fresh code** from
the notes and the mathematics.

## Rules for this task

- **Do not open or import any `.py` under** `experiments/CARRY-BOUND-20261114-001A/` or `proofs/CARRY-BOUND-20261114-001Z/`. You
  may read their data (JSON/JSONL results, gates), `research/CARRY-BOUND-20261114-001/{carry_bound.md, preregistration.md,
  codex_spec.md, codex_spec2.md, advisor_review*_answer.md}`, the census records
  `artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz`, and the earlier referee
  code under `research/CENSUS-FORGET-20261114-001/referee-R1/codex/` and `research/FREE-TARGET-20261114-001/referee-R1/codex/`
  (fresh per-call relations, the target inventory, and a direct exact bond search with no relation code; reuse them).
- Write **only** inside `research/CARRY-BOUND-20261114-001/referee-R1/codex/`. No git commands that change state; no publishing.
- At most 3 processes and 10 GB; each command under about 15 minutes; the whole task under about 75 minutes. Another referee job is
  running, so keep the load at that. Use `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`. No network.
- Deliverable: `research/CARRY-BOUND-20261114-001/referee-R1/codex/codex_report.md`, plus scripts and JSON outputs there.

## Points to check (in order of value)

1. **Try to break Lemma G.** For at least 8 of the 632 "grow" families (smallest first, including some where a carried port is
   constrained above but unread below), compute **exactly, with no relation code**, the least bond from a top port to an own
   distinction of any covered copy at depth s, with members anywhere, for s = 1..6 or as far as cheap, and compare with
   2 + ⌊s/r⌋ (or the shifted bound for wrappers). Then judge the lemma's proof: when a coordinate no knot reads is deleted, does the
   stretch relation really factor, including when the carried value is constrained above?
2. **Lemma W on a sample.** For about 15 of the 5,074 "bounded" families (different bounds 2, 3, 4, both kinds, including the order
   label and ties), exhibit and verify, by your own direct satisfiability, a bond of the claimed size at several depths, and check the
   window certificate's claim "at every large depth" with its exact depth threshold. Judge Lemma W's exactness and the merging of
   identities in the window.
3. **Scope.** Check that the 58.0 / 39.6 / 2.4 split of census first-ray growth, and the 5,789 in-scope families, use the covered
   target scope of CENSUS-FORGET's referee (copies of S reached through S calls; no other recursive definition with own
   distinctions; no delayed S), and how out-of-scope families are counted.
4. **The two undecided-by-rule families** with complete window bounds: does the frozen cap rule correctly leave them undecided?
5. **The two logged corrections** (a Narrowing of TIE-CYCLE's reading, and a Not-a-block on the pre-registration's Lemma G fixed
   point): are their verdicts right?
6. **Wording.** "Bounded at every large depth" with its threshold; "proved per family" against computed; nothing beyond scope.

## Report format (`codex_report.md`)

A verdict line (Confirmed / Confirmed with fixes / Refuted), one short section per point, fixes each marked Block, Narrowing or Not a
block, and the files you wrote.
