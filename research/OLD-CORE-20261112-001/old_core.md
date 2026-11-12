# The old core's own end

Epic `OLD-CORE-20261112-001` (sub-goal B170, from `LIFE-JUMPS-20261112-001` direction 1; G17, with G7), 2026-11-12, at the
coordinator's go-ahead. Pre-registered in commit a813eb17d before the registered run. The canonical K1–K3 test is unchanged.
**Referee pending** (handed to the referee thread).

## Words

As in the guide's glossary and `RANDOM-FATES-20261112-001`. The **core** C_k is the knots whose three distinctions are all among the
oldest k; the **dying core** is C_k* for the least k* at which it allows no state; **peeled** removes, repeatedly, distinctions in at
most one knot. X(q) is growth with new distinctions and closings anywhere; O growth grows along co-knotted pairs (global or local
closings).

## The question

Growth that keeps adding distinctions ties a rising share of itself in its most knotted distinctions before it ends
(`LIFE-JUMPS-20261112-001`). Does it end when its oldest distinctions, read as a pattern by themselves, reach the end of uniform knots
(about 2.1 knots per distinction, a known threshold), or does something else end it? The weighting is each named process (A71).

## The question in standard terms

For grown random 3-uniform hypergraphs, is the first non-2-colourable prefix of the arrival order a near-critical uniform random
hypergraph, is its non-2-colourability explained by its degree sequence, or neither?

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **The dying core is far below the uniform end.** In every process the dying core has 1.55 to 1.74 knots per distinction (medians; X(0.3) 1.55, X(0.35) 1.67, O global 1.66, O local 1.74), and uniform patterns with its size and knots never end (median share of 20 resamples allowing no state: 0 in every process). For X this sits at the arithmetic of growth: the oldest distinctions' mean-field density, (1 + q/2)/(1 − q), is 1.64 at q = 0.3 and 1.81 at 0.35. | computed, frozen | L1 failed |
| 2 | **Peeled, the overlap growth's core reaches the known threshold; the expanding growth's does not.** With distinctions in at most one knot peeled away, O growth's dying core has 2.05 (global) and 2.10 (local) knots per distinction, and uniform patterns of that size and knots end in 23% and 43% of resamples: near-critical, at about the known value. X growth's peeled core has 1.70 and 1.81 and uniform patterns of that size never end. | computed, frozen | L1p failed (O global 0.225, X 0) |
| 3 | **Degrees end the overlap growth, not the expanding growth.** Patterns with the dying core's degree sequence end in every resample for O growth (median 1.0, tenth percentile 0.29 to 0.68), and in none for X growth (median 0; ninetieth percentile 0.07 at q = 0.3, 0.31 at 0.35). So O growth ends through its degrees (the few distinctions in very many knots), and X growth ends through something its degrees do not carry: which distinctions share knots, by arrival, as in grown random networks, whose giant component appears below the degree-matched static one (Callaway, Hopcroft, Kleinberg, Newman and Strogatz 2001). | computed, frozen | L2 failed (X 0; O 1.0) |
| 4 | **Age is a proxy for degree.** Ordering distinctions by their final knots instead of their arrival finds a dead prefix at least as early in 82 to 88% of endings, in every process: the referee's degree-weighted null for `LIFE-JUMPS-20261112-001` holds here too. | computed, frozen | L3 held |
| 5 | **The dying core is set by the killing knot.** k* equals the floor, the killing knot's largest index + 1, in the median ending of every process but X(0.3) (1.17 times the floor), so "the oldest k*" is mostly "everything up to the newest distinction of the last knot"; k* is 0.44 to 0.72 of the distinctions at the end. | computed, frozen; the floor by definition | reported |
| 6 | **Where X growth ends.** X(0.25) ends within 6,000 moves in 8 of 100 growths, X(0.3) in 87, X(0.35) in all 100 within 2,000: its closing rate for ending lies between 0.25 and 0.3, where the whole pattern has only 1.33 to 1.43 knots per distinction, far below the uniform end's 2.1. | computed, frozen | reported |

## Answer

No. A growth that adds distinctions does not end when its old core reaches the uniform end. Its dying core sits at 1.55 to 1.74 knots
per distinction, where uniform patterns of the same size never end, and the oldest distinctions matter only because they carry the
most knots. The two growth processes end for different reasons. Growth along co-knotted pairs ends through its degrees: patterns with
its dying core's degrees always end, and, peeled of its loose distinctions, that core sits at the known threshold. Growth with closings
anywhere ends through more than its degrees: neither uniform nor degree-matched patterns like its dying core end, so which old
distinctions share knots, which only growth makes, is what ends it, at closing rates between 0.25 and 0.3, about half of the 0.52 at
which the whole pattern would reach the uniform end's 2.1 knots per distinction.

## Reading

**Interpretation, not a theorem.**
- **The owner's "go for a while then die".** Under these weightings what ends a growing pattern is not a density it reaches but the
  structure its history leaves: in growth along pairs, a few distinctions knotted to very many others; in growth with closings
  anywhere, correlations among its oldest distinctions that a pattern with the same counts would not have. Read with the owner's
  "relative to each other": what ends it is how its parts are related, not how many there are.
- **What is known and what is new.** The uniform end near 2.1 is known; that heterogeneous degrees lower thresholds is known; that grown
  random networks differ from their degree-matched static versions is known for components. New: where grown not-all-equal patterns
  end (between 0.25 and 0.3 for X), that their dying core is not uniform-like, that degrees explain the end of one growth process and
  not the other, and that growth with closings anywhere ends through correlations its degrees do not carry.

## Lag cutoffs and census-only claims

Computed under five processes, 100 growths each (O global: 98, two stopped unfinished, below), 20 resamples per ending. The
resamples estimate each ending's chances to 0.05; the predictions use medians over endings. Degree-matched resamples are made by
shuffling stubs and repairing repeats with degree-preserving swaps (every one of the 20 per ending succeeded).

## Stress test and pending

Two O global growths were still resampling after an hour and a half, when every other growth had finished in at most 37 minutes
(the degree-matched repairs are slow on cores with a few very knotted distinctions); the unit was stopped then, and they are not in
the record, which holds 498 of the 500 growths (a deviation from the frozen 100 per process, disclosed). Nothing reported changes
with two O global growths more. One size past: the X processes at q = 0.25 to 0.35 bracket where X growth ends.

## Review

Referee pending (the referee thread). The advisor model reviewed the design cold before freezing and replaced the draft's density
predictions, which were settled by arithmetic, with the matched resamples.

## Literature and provenance

Known: the uniform threshold (Achlioptas and Moore; Achlioptas, Chtcherba, Istrate and Moore; Castellani, Napolano, Ricci-Tersenghi
and Zecchina; Coja-Oghlan and Panagiotou; Ding, Sly and Sun); thresholds under prescribed degrees (Cooper, Frieze and Sorkin; Boufkhad,
Dubois, Interian and Selman; Ansótegui, Bonet and Levy; Friedrich et al.); grown random networks (Callaway, Hopcroft, Kleinberg, Newman
and Strogatz 2001; Bollobás, Janson and Riordan). Not found: the end of grown random NAE patterns and its source. Classification:
known-with-delta.

## Workspace assumptions

A71 (each process one weighting of many), A72 (a growth ends when it allows no state): used, status unchanged.

## Ratio

Substantive: the census of 498 growths and its summary. Administrative: the pre-registration, this note, the closure.

## Corrections

None.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the old core's own end | **Status:** Successful (referee pending) | The uniform-end law refuted; the two growth processes end for different reasons |
| Local direction — why growths end | Continue | X growth's ending structure beyond degrees is unidentified |
| Broader exploration — G17 | Searching | Other laws and weightings untried |
| Long-term goal — G17 Typical and rare meeting patterns (with G7) | Capability gained | What ends a pattern that goes for a while: its history's structure, not a density |

**Corrections:** none. **Goals:** a G17 checkpoint (capability gained, with G7); no goal change. **Assumptions:** A71 and A72 used.
**Basket:** `LIFE-JUMPS-20261112-001#2` (a calibrated forecast), `#3` (larger uniform sizes), `MISSING-KNOTS-20261112-001#1`,
`RANDOM-FATES-20261112-001#3` and `#5`.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | What X growth's degrees do not carry | 2/3 — Substantial | 3/3 — Ready | Resample the dying core keeping its knots among pairs of distinctions (the co-knotted pair counts, which the law reads, OVERLAP-READ) or its arrival-rank kernel, frozen → the correlation that ends X growth named, or none of these | Selected · awaiting go-ahead |
| 2 | Where X growth ends | 2/3 — Substantial | 3/3 — Ready | Scan q from 0.2 to 0.3 with long horizons and fit the ending hazard against size → the closing rate at which X growth ends with certainty, and whether the hazard decays | Alternative · deferred |

1. Payoff 2: it would name what ends the growth with closings anywhere. Concreteness 3: the census's endings regenerate from their
   seeds, and the pair-count resample keeps exactly what the law reads (`OVERLAP-READ-20261111-001`'s lemma).
2. Payoff 2: the critical closing rate of a grown pattern, the advisor's question. Concreteness 3.

**Recommendation.** Research directions, #1, awaiting the go-ahead.

## Final report as sent

(Appended after sending.)
