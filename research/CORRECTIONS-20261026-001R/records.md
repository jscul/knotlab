# Corrected discovery records

Ticket `CORRECTIONS-20261026-001R`, 2026-10-26. Documentation.

**Why.** The owner asked that the outdated discovery records be updated ("Could you update them?"), and that the twisted-triple-product
proofs be reissued.

**How.** Each outdated record is superseded, not edited in place:
- the old record keeps its text, with `status: superseded` and `superseded_by` pointing to the corrected record;
- its scope's disposition lists the supersession;
- the corrected records live in this epic and bind its closure.

| Old record | Why it is outdated | Corrected record | What changes |
| --- | --- | --- | --- |
| `SL23-BOUNDED-20261025-001-D001` | Its last sentence, "the bounded-homology line separates Fitting heights 2 and 3 as far as tested", was refuted the next day: UT₃(F₄) ⋊ C₃ has Fitting height 2 and is #P-hard with H₁ = Z/3 (`TRIPLE-PRODUCT-20261026-001`, reissued as `CORRECTIONS-20261026-001D`). | `CORRECTIONS-20261026-001-D001` | It keeps the SL(2,3) result and replaces the "line" sentence: the line is the twisting (pairwise versus three-way obstructions), not the Fitting height. |
| `CLOSED-H1-20261025-001-D001` | It presents the order-6 quandle equality as proving the 2013 conjecture of Clark, Elhamdadi, Hou, Saito and Yeatman as a new result. Livingston 1995 (Theorems 8–9) already implies it (`S4-LIFT-PRIOR-ART-20261025-001`). | `CORRECTIONS-20261026-001-D002` | It is labelled a re-proof of Livingston's equinumerosity by twisted lifting cohomology, and the conjecture is noted as already implied by Livingston. Its significance changes from frontier change to reusable interface. |
| `HARD-3D-20261025-001-D001` | It presents #P-hardness of counting maps into S₃ as a frontier change. Galindo's 2026 Turaev–Viro dichotomy (arXiv:2605.06984) already implies hardness for every nonabelian G (`DICHOTOMY-3D-20261025-001`). | `CORRECTIONS-20261026-001-D003` | It keeps the explicit chromatic constructions (doubles count pairs of colourings, 2 P(G, 9)/3^\|V\|) as the contribution, and notes the hardness as a case of Galindo. Its significance changes to first construction and reusable interface. |
| `TRIPLE-PRODUCT-20261026-001-D001` | The conclusion stands, but its evidence is the closed proofs, which the independent review `COPRIME-CLASS2-20261026-001A` corrected in presentation. | `CORRECTIONS-20261026-001-D004` | It is rebound to the reissued proofs `CORRECTIONS-20261026-001A/C/D` and adds the knot-group result (+63) and its consequence for Rowell's Conjecture 3.2(b). |

**Unchanged.** The other records of those scopes stay active as they were, including `CLOSED-H1-20261025-001-D002` (S₄ #P-hard on
closed manifolds with H₁ = Z/2).
