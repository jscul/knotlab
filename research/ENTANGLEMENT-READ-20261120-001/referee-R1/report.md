# Referee report ENTANGLEMENT-READ-001-R1 (lean)

**Verdict: stands as stated. The score of 4 comes from settings that are part of the state, not from anything like entanglement.
No Block, no correction; one wording point.**

## The ten-knot witness, rebuilt

The referee rebuilt it from the text with its own code:
- **The start.** Alice's knot {X, A0, A1, P}, Bob's {Y, B0, B1}, and two copies of four three-place knots tying A0 to B1 and A1 to
  B0. That is 10 knots and 17 distinctions, with **128 allowed states**, 32 for each setting pair.
- **The correlations.** Reading the bit indexed by each side's own setting gives (1, 1, 1, −1), so CHSH = 4. Every reported bit
  is fair.
- **The giveaway.** In every state A0 ⊕ A1 = Y, so Alice reads Bob's setting off her own two distinctions.
- **Independent settings on the same 128 states** give (0, 1, 1, 0), so CHSH = 2.

## The coordinator's reading is right

- **Why the score is 4.** The tie makes A0 = B1 = r and A1 = B0 = q, and Bob's knot forces Y = q ⊕ r. So the outcomes' parity is
  XY, which yields the four correlations above.
- **This is setting dependence**, the study's mechanism (a). The settings are functions of the same state that produces the
  outcomes. A Bell or Tsirelson comparison assumes the settings are free, so it does not apply.
- **The independent-settings bound is Bell–CHSH and Fine's theorem.** One common weighting gives a single joint distribution of
  all four outcomes, hence CHSH ≤ 2. It is classical, and here it is correctly applied at every finite stage.
- **GHZ and Mermin–Peres** have no common assignment. That is also classical. So neither can be a projection of one ordinary state
  set.
- **The 8/3 table** comes from an added non-uniform weighting, a scaffold, as the study says. Nothing native to the growth exceeds 2
  with free settings.

## Wording point (for the owner, not a correction)

"The score of 4 exceeds the quantum maximum of 2√2" is arithmetically true but invites a wrong reading. The quantum bound concerns
free settings, and here the settings are not free. A reader-facing summary should put the setting dependence first.

## How the work was split

- **The referee:** rebuilt the witness and the four tables by direct enumeration of its 2^17 assignments (seconds, run directly),
  and read the decision note and `embodied_control.md`.
- **No study code was run.**
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
