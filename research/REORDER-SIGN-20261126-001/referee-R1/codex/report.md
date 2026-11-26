confirmed with fixes

1. **Listing orders — confirmed.** The full contradiction occurs for exactly the prefix/suffix reversals, giving 3/6, 4/24, 5/120 and 6/720 at three through six distinctions. Oddness alone selects the right orders only at three. At each requested size three through eight, full reversal gives the phase $(-i)^k$ on every even word of weight $k$ and passes the full contradiction test. [Exact census](listings.json)
2. **Grown ternary — confirmed.** Against production order `abc`, exactly `acb`, `bac` and `cba` give $P=-1$. Reversal matches 64/64 fixed-label probabilities. The other two match 48/64, or 64/64 after one reader reverses its flip outcomes. Reading the old distinction alone wins 5/8 in every order (40 matching cells). With $s=+1$, the block readers also win 5/8 (44 matching cells). [Exact tables](block.json)
3. **Unknown and coherently summed orders — confirmed with a scope fix.** With the specified readings, the best Mermin scores are 4/3 over the three odd orders and 7/6 over all six. Under the equal-amplitude coherent sum, a word survives exactly when at most one child has odd fresh parity. The surviving ternary **parent** word is `000`, with **eight** nine-mode completions. [Mixtures and surviving words](block.json)
4. **Sequential fermionic model — confirmed for the stated preparation and readers.** For both specified parent orders, and independently for all six, F1 gives the full contradiction exactly at the three relatively even commit orders. Committing in parent order gives 64/64 with fixed labels. F2 on the same first fresh distinctions gives no full contradiction. This finding was exploratory after P7 failed. [Exact occupation-space tables](fock.json)
5. **Earlier-first convention — confirmed with a qualification.** With the input vector fixed, appending a child equals left creation with an earlier-mode parity string on the odd term. Ordinary left births then differ by reversal of the **child blocks**. If the parents are also created by chronological left multiplication, a second reversal cancels the first on this fixture. [Derivation and two intermediate inputs](conventions.md)

## Prior work to add

The frozen design already credits Jordan–Wigner, Mermin and the stabilizer literature. Bravyi and Kitaev's equations (5)–(8) give the occupied-swap sign and its controlled-Z correction explicitly. In the study’s notation their equation (14) also gives the gate $\exp(-i\pi F1/4)$, with F1 itself as the generator. Verstraete, Cirac and Latorre's equation (12) gives the same gate in matrix form. The study-specific result is the classification of commit orders for the stated birth and reader operators. [Bravyi and Kitaev](https://arxiv.org/pdf/quant-ph/0003137) · [Verstraete, Cirac and Latorre](https://arxiv.org/pdf/0804.1888)

Campbell, Hoban and Eisert examine the three-party GHZ contradiction with local even Majorana readings and prove an obstruction for their topologically protected preparations. The conditional births here lie outside that operation set. Szalay and colleagues give the subsystem embeddings and parity rules needed to distinguish a change of listing from a change of preparation. [Campbell, Hoban and Eisert, §6](https://arxiv.org/pdf/1305.1953) · [Szalay et al.](https://arxiv.org/abs/2006.03087)

Procopio and colleagues explicitly retain an order control and measure it in a superposition basis. This distinction matters here. Discarding an orthogonal order record gives the mixture. Projecting the control onto the equal superposition gives the specified coherent sum, with success probability 1/4 for this ternary. [Procopio et al., Fig. 1](https://arxiv.org/pdf/1412.4006)

## Wording and convention changes

**What selects F1 or F2.** In the table, $yz$ means the written product $c_y^\dagger c_z^\dagger$, whose right factor acts first. Each row uses the same choice at all three readers. The listed flip gives three carrying orders and one fixed-label 64/64 match, in parent order. The other flip gives zero carrying orders. Both Majorana factors in each flip are odd under fermion parity. The prime distinguishes them, so “the odd factor sits on the old distinction” should read “the primed Majorana is on the old distinction” for F1.

| Written creator product | Fresh distinction read | Successful flip |
| --- | --- | --- |
| $yz$ | $y$ | F1 |
| $zy$ | $y$ | F2 |
| $yz$ | $z$ | F2 |
| $zy$ | $z$ | F1 |

The rule holds **reader by reader**. A reader must use F1 on the left written creator or F2 on the right. A mismatch makes every scored correlation that flips that reader vanish. When all three match, the relatively even orders carry. With the original $yz,y$ at all three readers, each of the six genuinely mixed F1/F2 assignments therefore fails. Mixed flips can work when the record or pair convention also varies. For example, with parent order `abc`, products $yz$ throughout, records $(z,y,y)$ and flips (F2,F1,F1), the unique fixed-label match is `bca`. In general it requires inverting precisely the pairs whose matched flip types differ. Exchanging both fresh labels everywhere preserved every table. The full sweep covered 18,432 choices, with 1,152 full contradictions and 288 fixed-label matches. [Indexed probability tables](fock.json)

**What “parents' creation order” provides.** A specified history orders the parents. The unsigned parity constraint specifies four allowed words. A further preparation rule sets their relative phases. In the common ascending creator basis, positive chronological creation in order `abc` gives signs `+---` on `000,011,101,110`. Order `cba` gives `++++`. Keeping the actual state and transporting its operators through a change of coordinates preserves every probability. Resetting the coefficients to positive in another ordering changes the state. With `++++` held fixed in the common basis, `cba` remains the exact commit regardless of how the history is labelled. Of all eight real, equal-magnitude starts up to overall sign, two give no fixed-label exact order at all. Thus the data support a reference supplied by a **chronologically calibrated preparation**. The parity rule alone leaves that calibration open. [Eight start signs](phase_reference.json) · [Coordinate controls](fock.json)

In the original F1 reading, let $h_{ab},h_{ac},h_{bc}$ be the initial coefficients on the three occupied pairs in that common basis, scaled to signs with the vacuum positive. Each inverted pair in the commit order reverses its own sign. The ternary contradiction occurs exactly when $h_{ab}h_{ac}h_{bc}\,\mathrm{sgn}(\pi)=-1$. Exact fixed-label agreement requires all three resulting pair signs to be negative. This explains why a change in start phases can preserve the carrying class while removing its exact match. [Start-phase derivation and check](phase_reference.py)

**Which reversal.** Moving a fresh monomial of parity $p$ past $N$ earlier occupied modes costs $(-1)^{pN}$. Over the round, reversing the child blocks costs $D(x)=(-1)^{\binom{|x|}{2}}$. Reversing the old occupied creator word costs the same $D(x)$. The two chronological constructions agree on all 1,152 final coefficients when both reversals apply. Holding the old input vector fixed instead changes 864 coefficients. Reversing the creators *inside* each child introduces the further sign $(-1)^{\sum_j y_jz_j}$. The prefix string is a valid implementation on fresh-vacuum inputs. P7's final tables do not identify a unique birth operator away from those inputs. Also, $K_j$ coherently combines an even term and an odd term. Calling it a physical local operation under fermion-parity superselection would require an implementation that accounts for that parity. [Exact coefficient comparisons](conventions.json) · [Parity and local operations](https://arxiv.org/abs/2006.03087)

**How far the score and the order rule extend.** “Best Mermin score” here optimizes real outcome labels for the fixed readings. The same optima hold if their two setting names may also be swapped. With different real readings, the odd-order and all-order mixtures already attain $168/(25\sqrt{10})$ and $308/(25\sqrt{37})$, respectively, both above 2. These are witnesses, with two distinct settings per reader. The coherent cancellation has a separate cause. For a fixed word, exchanging two odd child labels pairs each order with one of the opposite sign. With old word `000`, each fresh pair can still be `00` or `11`. [Directions and exact squared scores](block.json)

I also checked the proposed four-reader extrapolation on the direct one-round extension with four one-parent births. With parent order `abcd` and the original F1 readers, the carrying orders are `abcd`, `bcda`, `cdab` and `dabc`. These **4 of 24** include two odd permutations. This gives an exact counterexample to extending the three-reader evenness rule. For the separate single-knot listing census, an extra size gave 7/5,040, and reversal passed through nine distinctions. Its exact criterion is that the polar form of the inversion exponent on even words equals the dot product. Mere nonvanishing is weaker. At four distinctions every *adjacent* single swap fails, but two nonadjacent transpositions carry. [Four-reader calculation](phase_reference.py) · [Listing proof and enumeration](listings.py)

## Independent reproduction

The frozen preregistration matches commit `5a5a285351`. I used the stated one-round ternary and the independently specified 64-cell target. The scores use equal weight over the four promised settings. All five referee calculations replayed from integer signs and exact rational probabilities. The study modules were neither imported nor executed. The final comparison matched the archived listing and ternary summaries, all six P7 order summaries and all 24 archived Fock rows. The archived Fock calculation used floating point and saved four correlations and a scored win per order. The independent calculation directly checked all 64 probabilities, including the four unscored settings. The study's other growth fixtures are outside this five-claim referee brief. [Target definition](../../../WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001/preregistration.md) · [Receipt comparison](compare_receipts.py)

Run from this directory with Python 3.11 or later. Only the last command reads the study receipts.

```sh
python3 -B listings.py --output listings.json
python3 -B block.py > block.json
python3 -B fock.py --output fock.json
python3 -B conventions.py > conventions.json
python3 -B phase_reference.py
python3 -B compare_receipts.py
```

| Scope | Verdict | Why |
| --- | --- | --- |
| Five-claim referee check | Successful | The reported numerical cases reproduce exactly |
| Parent order as reference | Conditional | The preparation fixes relative signs |
| Physical fermionic growth | Unresolved | The conditional birth mixes fermion parities |
| G5 Dynamics and G9 Witnesses | Conditional witness | One calibrated round realizes the full table |

**Next step:** Research directions — No next action selected. **STOP** at the referee brief's requested boundary.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Source of the parent phases | 2/3 — Substantial | 2/3 — Testable | Specify a growth operation fixing the relative phases → test it on the four parent words | Alternative · deferred |

**Corrections:** Narrowing. Qualify the parent reference, the reversal, the fixed readings and the surviving old word. The specified ternary counts stand.

**Goals:** G5 Dynamics and G9 Witnesses receive an independently checked conditional example.

**Assumptions:** A144 supplies squared weights, A275 the swap sign and A276 the reader. The chronological phase calibration is an additional premise of the interpretation.

**Scaffolds:** Varied the listing, start phases, within-pair product, fresh record, local flip choices and treatment of commit order. All referee files are confined to this directory. Nothing was committed.
