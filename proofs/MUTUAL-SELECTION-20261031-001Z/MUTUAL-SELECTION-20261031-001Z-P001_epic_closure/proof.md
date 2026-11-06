# Closure of the mutual-selection scan

Status: Proved

Epic `MUTUAL-SELECTION-20261031-001` closed on 2026-10-31.
- **What this is.** A ledger: no new claim. All three lanes are documentation tickets.
- **The decision note** is `research/MUTUAL-SELECTION-20261031-001/decision.md`.
- **The lane reports** are `research/MUTUAL-SELECTION-20261031-001{A,B,C}/report.md`.
- **Replay.** Every lane's script was rerun in a temporary mirror of the repository, and the outputs were identical apart from timing.

## Conclusions

| # | Conclusion | Label | Evidence |
| --- | --- | --- | --- |
| 1 | A symmetric three-place law can fail on plain cubic systems only if it excludes both constant colourings. Among the seven symmetric knots only not-all-equal does. | elementary | `…001A` |
| 2 | Exactly-one and exactly-two fail on plain cubic systems but are NP-complete to decide (dual: exact cover by 3-sets, every element in three sets). | classical (Gonzalez 1985) | `…001A` |
| 3 | Signed parity fails exactly on inconsistent linear systems (recognisable), but its whole coupling family is affine, so it selects nothing. Signed cubic clause systems never fail. | classical (linear algebra; Tovey 1984) | `…001B` |
| 4 | The signed Fibonacci laws (the no-lone topological knots) fail on many small cubic systems and are NP-complete to decide there. A five-line gadget pins a value, a pinned point makes a line an equality, equality chains give fan-out, and Schaefer's theorem applies. | complete argument, checked on 60 instances; no overlap looked for | `…001C` |
| 5 | Not-all-equal gadgets with up to five internal points reach only three relations (nothing, everything, itself); Fibonacci gadgets reach fifteen, including pinned values. | computed (58.5 million signed structures each) | `…001C` |
| 6 | The only three-place knots with no preferred value (unchanged when every colour flips) are the signed not-all-equal relations. | elementary (decision note) | `decision.md` |

**Verdict.** Among symmetric three-place laws, mutual selection is special to the knot.

## Challenged assumptions

- **"Topological knots might share the knot's selection."** False for the Fibonacci knots: their failures cannot be recognised unless
  NP = coNP. Parity's failures can, but select nothing.
- **"The Fibonacci law fails only off Pfaffian graphs."** It looked so up to n = 7. The census found a Pfaffian graph with both kinds of
  failure at n = 8.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: the mutual-selection scan | **Status:** Successful | Every symmetric law is classified, and the knot is the only one with mutual selection. |
| Local direction: mutual selection | Continue, widened | Open: the asymmetric three-place knots, and rigidity of not-all-equal gadgets at every size. |
| Broader exploration: the two/three boundary | Known alternatives | Pinning across all three-place knots; rigidity at every size; the counting note. |
| Long-term goal: the two/three boundary as emergence | Capability gained | The knot is the only three-place knot with no preferred value, and the only one whose failures are recognisable and select it back. On regular systems its law can fail only at three places (Thomassen). |
| Next recommendation: pinning across all three-place knots | **Next step:** Continue. Prove that pinning plus non-affinity gives NP-completeness on cubic systems, and find pinning gadgets for every value-preferring knot, asymmetric ones included. | Stop if some value-preferring non-affine knot provably cannot pin. |
| Interest | **3/3: Hot** | A uniqueness theorem for the knot among all three-place laws, in the owner's terms (no preferred value). Uncertainty: gadget sizes for asymmetric knots. |
| Execution | Planned | It awaits the owner's choice. |
