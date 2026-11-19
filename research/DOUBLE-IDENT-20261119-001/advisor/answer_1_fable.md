**Verdict:** Lemma M is sound for the growth counts as you state them, with one addition and one hypothesis to tighten. I could not reconstruct the definitions of "group", "offshoot" and where pendant points sit in X⁺ from this text, so the points that depend on them are flagged as checks.

## 1. Lemma M

**The GF(2) argument holds**, given that every distinction lies in at most two knots; state that hypothesis. The sum over S has support loose(S) ∪ boundary(S) whatever the multiplicities, so the row space meets the loose bits only in unions of components. Three consequences, all independent of multiplicity:

- **Rank:** rank = knots − [zero loose].
- **Frozen loose bit:** this happens exactly when the start holds one loose distinction. That matches your 32.
- **Tied loose pair:** this happens exactly when the start holds two loose distinctions.

**The junction neighbour relation is safe.** Swapping two bits shared by the same two knots is a symmetry of the presentation, as is swapping two loose bits of one knot. A doubled bit never becomes loose, so no junction touches a parent through two bits.

**Addition: the round-0 floor reads multiplicity.** The number of distinctions is Σ open + e, with e counted with multiplicity. Any absolute count at round 0 (distinctions, or solution dimension = Σ open + e − rank) therefore needs e or the places, which (i) and (ii) do not give. Add this as (iii), or state the Lemma for increments from round 1 only. If "dimension" means the growth degree, it is unaffected.

**Tighten (S6′).** "At least two loose" is not enough. With exactly two loose distinctions on two live knots that share a block, the pair junction takes every loose distinction and is implied. Example: dead w = {x,y,z,t}, u = {x,y,a}, v = {z,t,b}, so a + b is forced. Use "at least three loose", or "no round-1 candidate takes every loose distinction".

**Wording of the implied test.** A junction with fresh bits is never GF(2)-implied. What is implied is its old part, which freezes the fresh part. Say that.

## 2. Other uses of "simple"

Lemma M reduces everything to the underlying simple graph K̄ plus an open function that no longer equals places − degree. The girth, even-walk and piece arguments run on K̄, where a double touch adds no cycle and no new walk parity. What can break is any step that used open = places − deg:

- **Leaves:** a leaf can now have open 1 or 0. Any step using "a leaf has two rays" or "a leaf is live" fails.
- **Even walks and pieces:** these must be taken in K̄ with dead knots as intermediates. The live-induced graph can be disconnected while a dead knot joins its parts, and a dead knot can close the only odd cycle. If the relay rule counts pieces on live knots only, it will miscount.
- **(S3):** test it on the blocks of all w, dead ones included. A dead 4-place knot touching three live knots is a block of three.
- **Dead common neighbour in a cycle:** nothing more is needed, provided its block is kept and it gets no point, pendant or ray. A dead leaf's singleton block is inert.

I could not see why "a non-live knot is isolated" held for simple K, since a dead simple knot has as many neighbours as places. Check what that sentence was used for.

## 3. Three shared distinctions

What matters is |A △ B| = places_A + places_B − 2m:

- **0:** a duplicate or a contradiction. Then K = {A, B} with zero loose and no growth, and K3 can fail.
- **1:** that bit is frozen. If it is loose, this is your one-loose case with K = {A, B}. If it is shared with C, then C holds a fixed value and acts as a knot with one place fewer.
- **2:** the two bits are tied, so the pair acts as a wire.

None of this changes the counts, by Lemma M. It does mean the start has distinctions that are not open, which is worth a source label. Beyond that, a triple share makes dead leaves, which only lower a neighbour's open count, and dead knots with two neighbours, which are pure blocks of two.

## 4. Predictions

**Share:** I cannot give a number, because the census total is not in the text. Directionally, multiplicity lowers K̄-degrees, so (S3) and (S4) pass more often and the class share should be higher among double-touch arrangements than among simple ones.

**Risky outcome:** mismatches beyond the 32, concentrated in three places:

1. **Two-loose starts sharing a block.** The predicted pair junction is absent. If pendant points sit in that block, round 2 is wrong too.
2. **Starts whose live knots are joined only through dead knots.** The relay or piece count is off.
3. **A later round where one junction takes every loose distinction.** This is possible if junction sizes let the loose count shrink.

If all mismatches fall in (1), the fix is the tightened (S6′) alone.