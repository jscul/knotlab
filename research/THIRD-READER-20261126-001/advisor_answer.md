Both hivemind entries are in (one consultation, one standing fact); nothing else was touched. Everything below is by hand with no run, so it is `unverified` unless marked "read".

**Headline:** predictions 1 to 4 are all entailed, and prediction 2 is wrong as worded on the loose-chain family (g = 1 there, not 2). The three-reader game does not improve on the sorted square in fairness: a list in which one reader hears one other reader's setting wins it with certainty.

## What I read

- `tripartite.py`, `real_paradox.py`, `css.py`, `rings.py` in full; `repro.py` 29–80; `census.product`.
- `VALUE-CHANGE` README, decision, preregistration, referee reports R1 and R2, and `referee-R1/joined_results.json`, which holds the local dimensions I use below.

## 1. Separability for k readers

I found no counterexample; the argument closes as you wrote it. Each reader's parts X^(x_i) and Z^(z|R_i) commute, so the state is diagonal in a product of local bases, which is stronger than a mixture of products.

- **A shorter proof, wider scope.** Referee R1's proof (report line 35, read) extends word for word: fix the unread values, and each knot then constrains at most one reader, so the completions are a Cartesian product. It uses no linearity. It holds for any laws, not-all-equal included, and for any amplitude that is a product of one factor per knot.
- **Where your corollary is too wide.** "No table above any classical bound unless a reader in contact conditions it or takes part" needs a third exception: a state carrying a factor no knot holds. The recorded case is the swap study's supplied signed weighting, CHSH 4 with no knot holding a distinction of both readers (R1 fix 8, read).
- **The right form.** Join two readers when a knot holds a distinction of each. Across any split of the readers with no join, the state is a mixture of products. So a three-reader excess needs the middle joined to both ring readers.
- **Known?** In substance yes. From memory, not looked up: Fattal and others 2004 and Audenaert and Plenio 2005 for two parties; the k-party form is the conditional independence of a factor graph given a separating set (Hein, Eisert and Briegel 2004 for graph states).

## 2. Is the game a fair test, and what does a contact list score?

- **Value 1 with one bit.** The four scored triples have even parity, so a reader who hears one other reader's setting knows all three. Explicitly: A and B answer fair bits from the list, and the middle answers F(s)·a·b. Every single and pair marginal stays uniform and independent of the settings.
- **The whole table, not only the game.** A list in which only the middle hears both ring settings reproduces every table the three readers can show, whatever they read. This is because the A–B marginal is always local by section 1. The 3/4 bound holds only when no reader's answer depends on another's setting.
- **The sorted square has the same standing.** A middle that hears the row and column wins it too. Referee R2 already records it as a game won with certainty "when the score uses the middle record's signs" (2/3 pooled). So it was already a three-reader game with one middle setting; this epic adds only the second setting.
- **What it does test.** That the supplied state with a supplied quarter-turn read has no list of setting-independent values (Mermin 1990). Do not write "contextuality, not separated readers": the rule-R study's referee narrowed exactly that sentence, since the same table comes from three separate factors.
- **In the game, A and M read the two halves of one knot's law** (z1 is L's law, `tripartite.py` 68–69).
- **A native point you can assert:** the contact is through knots that hold no loose distinction, so no birth has parents in two regions (assert no mixed lineage through round 2).

## 3. g and the formula

The formula is right: with the pure state a product of triples, pairs and local pieces (Bravyi, Fattal and Gottesman), E(X) = g + e(X,Y) + e(X,Z).

- **g is not a new count.** g = E(A) + E(B) − E(M) − 2e(A,B). For separated ring readers this is their mutual information, which equals e(changes) + e(values) of `VALUE-CHANGE`, i.e. e(changes). Predictions 1 and 2 are that study's table.
- **Every triple is of the change kind:** one three-reader change, value laws pairwise. The other kind needs a cross change, which the split forbids.
- **The three routes are not independent.** They share `supported_dim` and `pair_e`. A fourth route: g = dim S − dim(S_AB + S_AM + S_BM), plus the same expression for the laws, which should be 0.
- **Hazard:** `counts` sums bit masks with no check that A and B are disjoint (`tripartite.py` 39). Assert `a & b == 0`.

Expected output, deduced from the referee's dimensions and the formula:

| Rows ('places', rounds 0–2) | E(A), E(B), E(M) | e(AB), e(AM), e(BM) | g |
|---|---|---|---|
| Pairs, three-ring families (the loose family's other two pairs included) | 2, 2, 3 | 0, 1, 1 | 1 |
| Pair, two rings | 1, 1, 1 | 0, 0, 0 | 1 |
| Loose-chain pair | 2, 2, 4 | 0, 2, 2 | 0 |
| Rings 0 and 2 together, ring 1 | 3, 2, 3 | 0, 1, 0 | 2 |
| The same on the loose family | 3, 2, 4 | 0, 2, 1 | **1** |

## 4. `real_paradox.py`

The phases and signs are right for what it searches (read: `product`, the Hermitian phase, the group phases all 0). It omits certainties of one or two readers, such as ZZI, but that does not matter, because the zero is forced.

- **Lemma.** On the positive counting state, let each reader make one real read i^|x∧z| X^x Z^z per round. Draw an allowed word w and a sum of laws p independently. The answer (−1)^(|x∧z|/2 + w·z + p·x) reproduces every product moment, hence the whole table, for any readers, any regions and any number of settings.
- **Consequence for the script.** Every right-hand side is c_a + c_b + c_m with c = |x∧z|/2, so v = c always solves. Three settings, or a reader holding pairs as well as triples, cannot help.
- **What an excess needs.** Either a quarter-turn read, or one reader reading together two reads P, Q with z_P·x_Q odd (X₁Z₂ with Z₁X₂). X₁Z₂ read with X₁ and Z₂ still has the list, so the README's "only through combined questions" is too weak.
- **Known?** The pure value and change case is Delfosse and others 2015. I have not seen the one-read-per-reader extension stated.
- **"Mermin's argument needs i" is false in general.** Take three free distinctions with amplitude sign the product of pairwise values: XZZ, ZXZ, ZZX read +1 and XXX reads −1, a game of certainty with plain reads. Word the claim "for positive amplitudes".
- **Cheapest checks:**
  1. Assert each right-hand side equals the c-sum.
  2. Run three settings at g = 2 (592,704 choices, expect 0).
  3. Run that signed state as a positive control (expect 1 of 1; the script has none with real reads).

## 5. Predictions

- **1:** entailed. Also state the loose family's other two pairs (g = 1).
- **2:** entailed on three families; fails as worded on the loose family (g = 1).
- **3:** entailed. I traced the four signs through `herm`, `product` and `certainty`: +1, −1, −1, −1. The chain laws close ζ_M + ζ_B and ζ_A + ζ_B. The table is the literature's by construction.
- **4:** a theorem (section 4).
- **Two rows that can fail, by hand:** the game on the direct-link family should win 1, and on the loose-chain family exactly 3/4 (two of the four products lose their law). The code skips both (line 155).
- **Smallest readers:** three distinctions each ({lL, a1, a2}, {d, c1, c2}, {lR, b1, b2}) should give the same table.

**What a referee presses first:**

1. Nothing in the frozen list is at risk.
2. The readers are in contact, a contact list wins, and the sorted square has the same standing.
3. The quarter-turn read is a fourth supplied piece, traded for the record-dependent score.
4. The game is at round 0 of built starts, so growth plays no part.
5. The three-reader value 4 is already in the rule-R study, part C.
