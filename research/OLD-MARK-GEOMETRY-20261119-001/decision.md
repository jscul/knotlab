# Does a stored ring change the distance between old distinctions?

Yes. Loading the five shared distinctions of the ring once changes the **bond distance between the same two old background marks**. The number of ordinary steps between those marks stays fixed. The marks, the initial incidence and all initial loose values were the same in both histories. The only preparation difference was the ring's stored state. This uses the existing feedback law, which lets cold knots join and vetoes a group containing an active parent. [Design and predictions fixed before measurement](definitions.md)

## The same pair can respond in either direction

The 17 original background knots have 16 successive shared marks. Label them `e0` through `e15` for the reading. The ring attaches between `e3` and `e4`. One ordinary mark step passes through a holder. Bond distance is the size of the smallest bond containing both distinctions, less one. Such a bond constrains its distinctions together and becomes free when any member is forgotten.

| Pair of original marks | Ordinary steps at every size | Source bond distance, quiet / loaded | Layers 1–3 | Layer 4 |
| --- | ---: | ---: | ---: | ---: |
| Two on the same side, e0 and e2 | 2 | 5 / 5 | 5 / 5 | 5 / 5 |
| Across the attachment, e2 and e5 | 3 | 15 / 15 | 13 / 15 | 13 / 12 |
| Meeting at the attachment, e3 and e4 | 1 | 7 / 7 | 7 / 7 | 7 / 4 |
| Far away on the same side, e8 and e12 | 4 | 9 / 9 | 9 / 9 | 9 / 9 |

For the crossing pair the quiet first layer can use a new knot holding four fresh distinctions. Loading the ring makes that join supply six. By layer four the loaded knot at the attachment has a different way of meeting the rest, through four original distinctions and just one continuing distinction. These give a five-distinction bond for the adjacent pair. Matching lower bounds prove its distance stays **4 loaded and 7 quiet at every later size**, including when a second ring is independently loaded. The crossing pair's reversal is certified at layer four. The quiet stage then has 291 knots and 1,238 distinctions, the loaded stage 250 knots and 709 distinctions. In a single history every allowed old assignment still extends, so every old bond is still available. Its minimum can stay constant or decrease as new knots form. Comparing two histories at the same layer can give either sign. [Proof of the old bond minima](distances_proof.md) · [Exact values and witnesses](bond_distances.md)

## Does the effect fall off?

There is an exact answer for the first layer on an arbitrarily long version of this background. Add p ordinary background knots on the left and q on the right, keep the four end spares, and always mark the two outermost shared distinctions before growth. Their quiet bond distance is 37 + 2p + 2q, and their loaded distance is 39 + 2p + 2q. **The absolute change stays two even as both marks move arbitrarily far from the ring.** Its fraction of the total distance tends to zero. At that same layer two marks wholly on either side have exactly equal bond distance in both histories. This answers a joint reading across the loop and explains how a small neighborhood at either end can stay fixed. This corollary is a proof following the registered panel, with no added measurement. [Arbitrary path length and exact endpoint offsets](padded_path.md)

## What changes over the background

- **Reach of the bond reading.** At layers one and two exactly 33 of the 120 original background pairs have bond distance two greater under loading. The affected pairs are precisely `e0,e1,e2` paired with any of `e5` through `e15`. This includes nine pairs with both endpoints at least three original knot steps from the attachment. There are 72 same-side pairs, all equal at these layers. The farthest straddling pair reads 37 quiet and 39 loaded. Across all 210 original pairs, including the ring marks, 75 lengthen by two and 135 agree. All 56 previously settled comparisons stand. The former 154 unresolved comparisons divide into 75 longer and 79 equal. The local bond balls previously measured through radius five answer a different question. [All 210 comparisons](bond_distances.md)
- **Shortest routes.** The ordinary length of every initially shared background pair stays fixed at every size. Any trip between two parents through their new child can be replaced by one of equal length through an older common neighbor. Repeating this replacement removes all newly born knots. All original routes remain available. Loading changes route counts for 44 of the 48 crossing pairs, including nine with both endpoints far away. The counts for all 72 same-side pairs agree at all later sizes. The marks 15 steps apart have 610 quiet versus 356 loaded shortest routes in layer one and 3,432 versus 2,220 permanently from layer seven. At each positive layer each of the 44 affected quiet pairs has a shortest route through offspring of the attachment. In the loaded history **no shortest old-background route traverses offspring of any originally loaded ring knot**, including the attachment. Each such part meets the old arrangement only back at the holder where it began. No route on the named single and double controls ever uses offspring of an exclusive ring knot even when quiet. Originally loose marks require a separate statement because they can acquire another holder. [Ordinary steps and their proof](ordinary_formula.md) · [All route counts](routes.md) · [Last possible new shortest route](last_routes.md)
- **Knots around a midpoint.** We counted each knot once within each incidence-hop radius of the set of all shortest-route midpoints. We also kept the original midpoint fixed. On the three-step crossing pair at layer two the two midpoints together have 14 quiet versus 16 loaded knots within two hops. The original midpoint alone has nine in both. At six hops both readings give 58 versus 71. A same-side pair's midpoint has two fewer loaded knots within five hops and three more within nine. There is no single monotone falloff in these counts. The archived table gives every radius through saturation in each physically reached stage. [Radial profiles and conventions](routes.md) · [Read any measured pair](../../experiments/OLD-MARK-GEOMETRY-20261119-001/OLD-MARK-GEOMETRY-20261119-001-E001_marks/read_pair.py)
- **How much is loaded.** The unmodified ring permits only zero or all five shared distinctions active when every loose distinction is quiet. To vary the amount on one fixed source we duplicated each of its five shared meetings and exhausted all 64 allowed assignments. For the three-step crossing pair the first bond distance is 13 plus the number of the attachment's two ring neighbors carrying activity. At weight five it is always 15. At weight six it can be 14 or 15. A total load alone cannot predict the result. [Full assignment formula](distances_proof.md)
- **Two rings.** With the attachments four or eight old steps apart, first-layer bond-distance changes add exactly on every one of the 325 old pairs in each arrangement. In both starts the outermost pair reads 43, 45, 45 and 47 with neither, first, second and both loaded. The same four preparations give 610, 356, 338 and 208 shortest routes at spacing four. Their joint route change differs from the sum of the individual changes by 124. At spacing eight the difference is 106. The first interaction in counts around all route midpoints occurs at layers two and four respectively. For later bond distances, 14 focused contrasts are exactly additive and the ten other certified intervals include zero. Later additivity for all pairs is open. [Four-arm bond results](bond_distances.md) · [Routes and midpoint counts](routes.md)

**Proved.** The age-one path formula on the named preparations, preservation of all ordinary step distances on the initially shared marks, monotonicity of each old bond distance within its own history, permanent adjacent-pair difference and an upper bound on how late a new shortest route can first appear. A shortest route between two old marks separated by s ordinary steps can only use knots born through layer floor((s−1)/2).

**Exhausted.** The full 210 old-pair comparison at layers one and two, all 325 at layer one on each double, all 120 background pairs on every measured stage for routes, and the 64 doubled-ring assignments in the stated dose test. There are 20,880 route profiles over 174 physical stages. The quiet/loaded single reaches layers 8/12. The four-step double reaches 6/7/7/10, and the eight-step double 7/8/8/12, in neither/first/second/both order. A certificate from the funded seventh-layer roster completes the only remaining ordinary route of the quiet four-step double without constructing all 33,512 distinctions. Every later shortest route and midpoint is thereby settled for these original single and double comparisons. Counts around those midpoints have only the physically reached bounds. Two separate calculations agree on the full 120 background-pair bond table in both preparations at both early layers. The proof of the permanent adjacent-pair reading also has 126 exact checks through layer six.

**Sample and weighting.** The 17-knot background and selected attachments are designed samples. Each old physical pair, shortest route from the designated end, distinct knot in a ball and allowed physical loading in its own fixed-source comparison gets one vote. The ordinary control panel covers 78 physical preparations across 31 initial activity arrangements. No population weighting over starts is inferred. Rounds index completed growth sizes. Independent referee review is pending.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — distances between old marks | **Status:** Successful | The same pair changes in both directions across histories |
| Local direction — range of feedback | Continue | A straddling pair responds across the background |
| Broader exploration — state-dependent growth | Known alternatives | Counts, routes and bond distance respond differently |
| Long-term goal — G1 Space from a law | Capability gained | An old separation depends on the stored state |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Detect the load with two nearby marks wholly on one side | 3/3 — Barrier | 2/3 — Testable | Use the first-layer equality and the two remote marks through layer four → a range bound or a remote local pair that changes | Selected · started |
| 2 | Decide later addition of two loads | 2/3 — Substantial | 2/3 — Testable | Tighten the four-step double's age-four bounds for e3 and e8 → a nonzero interaction or a proof covering this pair | Alternative · deferred |

The first direction asks whether a distant local observer can detect the ring with a short pair. Its fixed four-step pair already agrees through four layers, and the remaining question needs a proof across later sizes. The second targets a single four-history comparison whose interaction is already bounded between −1 and 2. A feasible lower bound that retains both connected sides is the outstanding step.

**Corrections:** None to the original feedback or eddy results. The 154 previously open comparisons are now settled.  
**Goals:** G1 Space from a law and G17's feedback lead B210 gained an old-to-old reading changed by the stored state.  
**Assumptions:** A97 remains scoped by the reading. A111, A113 and A114 specify the original law. A116 records the midpoint choice and fixed-midpoint control.  
**Basket:** B210 was taken on this line. B55 and B67 pose other ring-growth questions. The selected direction isolates range on the existing feedback law.

## Final report as sent

2026-11-19 20:41 PST

**Yes. Loading the loop changes the bond distance between existing marks.** Two marks that remain three ordinary steps apart can have a larger bond distance under loading at one layer and a smaller one at another. Bond distance measures how many distinctions are needed in the smallest bond containing both marks, minus one. [Proof and checked distances](https://github.com/jscul/knotlab/blob/main/research/OLD-MARK-GEOMETRY-20261119-001/distances_proof.md)

| Same two old marks | Ordinary steps at every layer | Before growth, quiet / loaded | Layers 1–3 | Layer 4 |
| --- | ---: | ---: | ---: | ---: |
| Across the attachment | 3 | 15 / 15 | 13 / 15 | **13 / 12** |
| Meeting at the attachment | 1 | 7 / 7 | 7 / 7 | **7 / 4** |
| Far away, on the same side | 4 | 9 / 9 | 9 / 9 | 9 / 9 |

The **7 versus 4** difference is proved permanent at every later size on these starts. Under loading, the attachment eventually meets the rest through four original distinctions and just one continuing distinction. Those five form the smallest bond containing the two marks. Within either history, growth preserves every old bond, so its minimum can only hold steady or fall. [Proof and independent certificates](https://github.com/jscul/knotlab/blob/main/research/OLD-MARK-GEOMETRY-20261119-001/certificates.md)

**How far the effect reaches.** After one layer, loading adds exactly two to the bond distance between marks straddling the ring whenever their nearer holders are at least one old knot step away on each side. That holds on **arbitrarily long backgrounds**. The absolute change stays two as both marks recede. Its fraction of their distance tends to zero. Every same-side pair agrees at that layer. This explains how the earlier radius-five counts at distant marks could stay fixed while the distance *between* two distant marks changes. [Arbitrary-length proof](https://github.com/jscul/knotlab/blob/main/research/OLD-MARK-GEOMETRY-20261119-001/padded_path.md)

**Routes and midpoint counts.** Every initially shared background pair keeps its shortest length in ordinary steps. Loading removes tied shortest routes for 44 of the 48 crossing pairs. For the marks 15 steps apart, the eventual count falls from **3,432 to 2,220**. No shortest route between old background marks passes through offspring of an originally loaded ring knot. Around the three-step pair’s two midpoints, layer two gives 14 quiet versus 16 loaded knots within two incidence hops. Around the original midpoint alone it gives nine in both. At six hops both readings give 58 versus 71. [Route counts, midpoint profiles and exact bounds](https://github.com/jscul/knotlab/blob/main/research/OLD-MARK-GEOMETRY-20261119-001/routes.md)

**Amount and second loop.** On a fixed ring with doubled meetings, the three-step pair’s first-layer bond distance across all 64 allowed loadings is 13 plus the number of the attachment’s two ring neighbors carrying activity. Five loaded distinctions always give 15, while six can give 14 or 15. With two rings four or eight steps apart, their bond-distance changes add exactly on all 325 old pairs at each spacing in layer one. Their route-count changes already interact. Whether later bond-distance changes always add remains open. [Dose and two-ring comparisons](https://github.com/jscul/knotlab/blob/main/research/OLD-MARK-GEOMETRY-20261119-001/bond_distances.md)

**Evidence and weighting.** We exhausted all 210 original pairs on the one-ring start at layers one and two. At both layers 75 had a larger loaded bond distance and 135 agreed, settling all 154 previously open comparisons. The route and midpoint study covered 20,880 pair readings on 174 reached stages. The weighting was one per physical pair, distinct shortest route, knot in a ball and allowed loading in its respective comparison. The starts were designed samples. Independent referee review is pending. [Full study](https://github.com/jscul/knotlab/blob/main/research/OLD-MARK-GEOMETRY-20261119-001/decision.md)

**The once-loaded transfer test also passed.** On the attached ring, starting with every loose distinction quiet, the least deterministic local rule in the tested fresh-only class writes two distinctions at each of two newborn knots. Keeping the entire first structure and the original ring fixed, those four writes change the second layer from **56 to 57 births**. Every admitted order of the funded births agrees up to renaming when each write happens with its birth. An independently delayed write can lose its destination. The rule copies the stored state forward. [Transfer proof and minimum](https://github.com/jscul/knotlab/blob/main/research/RING-TO-END-20261119-001/sharp_cost.md)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — separation of old marks | **Status:** Successful | A fixed pair changes in both directions across histories |
| Local direction — reach of feedback | Continue | A joint reading detects one load across arbitrarily many steps |
| Broader exploration — state-dependent growth | Known alternatives | Route counts, bond distances and local knot counts respond differently |
| Long-term goal — G1 Space from a law | Capability gained | A stored state changes an enduring separation |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Can two nearby marks wholly on one side detect a distant loop? | 3/3 | 2/3 | Use the far pair that agrees through four layers → prove a range bound or find a changed remote pair | Selected · started |
| 2 | Do two loads still add at later sizes? | 2/3 | 2/3 | Tighten the four-step example’s interaction bound of −1 to 2 → settle that pair | Alternative · deferred |

**Corrections:** Not a block. The transfer supplement called a newborn four-place. Its one spent and two fresh distinctions give three, as used in the calculation. [Corrected design](https://github.com/jscul/knotlab/blob/main/research/RING-TO-END-20261119-001/total_transfer_design.md)  
**Goals:** G1 gained a state-dependent distance between old marks. G5 and G17’s feedback lead B210 gained direct second-layer transfer.  
**Assumptions:** A111, A113 and A114 specify the feedback comparison. A115 records transfer at birth. A116 records the all-midpoint reading and its fixed-midpoint control.
