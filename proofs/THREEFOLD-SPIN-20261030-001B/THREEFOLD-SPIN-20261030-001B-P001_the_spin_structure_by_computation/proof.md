# The spin structure by computation

Status: Proved

Ticket `THREEFOLD-SPIN-20261030-001B`, 2026-10-30. This ticket confirms ticket A by exact computation and extends it to non-planar glue and
non-minimal maps. A computation does not discharge a theorem; each range below is stated.

**What it uses:**
- **`THREEFOLD-SPIN-20261030-001A`:** `spin_lib.py`: faces and the Kasteleyn condition, homology classes by pairing with cocycles, perfect
  matchings, the Cimasoni–Reshetikhin form, and the Arf invariant by Gauss sum.
- **`THREEFOLD-SURFACES-20261030-001A`:** `surface_lib.py` (rotation systems, SAT enumeration of minimal maps).
- **`THREEFOLD-GRAMMAR-20261030-001B`:** the census, which gives the four 19-point classes.
- **`THREEFOLD-AMPLITUDE-20261030-001B`:** trisums of prisms (`computation_lib.py`).
- **This ticket:** a fast Arf computation. It evaluates q on a basis of H₁ and on pairwise sums, which give the intersection form, then
  reduces to a symplectic basis. It agrees with the Gauss sum on all 919 maps of genus at most 3 where both were computed.

## Standard statement

1. **Spaces up to 22 points.** The Fano space (16 maps), the 13-point space (128 maps), the four 19-point classes (128 maps each) and the
   21- and 22-point spaces (64 maps each) were tested. On every map tested:
   - every face has length 2 mod 4;
   - every vertex lies on three distinct faces;
   - the knot's spin structure has Arf invariant 0;
   - the form vanishes on every difference of perfect matchings (all of them: 24 to 6,144);
   - the differences realize exactly 3^h of the 2^(h−1)(2^h + 1) even classes, for h Fano atoms. That is 3 of 3, 9 of 10, and 27 of 36.
2. **Larger spaces.** The 35-point space with non-planar (trisum) glue (genus 5) and the 43-point twisted cube (genus 6), 3 minimal maps
   each:
   - faces of length 2 mod 4 and three distinct faces at every vertex;
   - Arf invariant 0 (528 and 2,080 zeros of q, the even counts);
   - the form vanishes on 2,000 sampled matching differences.
3. **Non-planar glue braces.** The trisums of three prisms (2,2,2), (2,2,3), (2,3,3) with a flip, and (3,3,3):
   - each has genus 1 and is rigid at every vertex;
   - on all of its minimal maps (36, 56, 76, 96) its Pfaffian signing is Kasteleyn with three distinct faces at every vertex and Arf 0;
   - the matching differences fill exactly the three even classes.

   So these pieces behave like Fano atoms.
4. **The Heawood torus.** On each of its 16 maps, the four Kasteleyn classes have determinants of absolute value 24 (the knot's class) and
   8, 8, 8. Only the knot's class counts the 24 perfect matchings. The Cimasoni–Reshetikhin sum Σ (−1)^{Arf} ε(D₀) det gives 48 = 2¹ · 24.
5. **Non-minimal maps** (1,500 seeded random rotation systems each). The same signs can be Kasteleyn with an odd spin structure:

   | System | Kasteleyn maps | odd |
   |---|---|---|
   | 13-point space | 1,002 | 22 (genus 6 and 7) |
   | trisum (2,2,3) | 1,149 | 8 (genus 5) |
   | Heawood graph | 1,240 (genus 1–4) | none |

   - No odd case was found below genus 3.
   - On every Kasteleyn map the form vanishes on the matching differences, as Cimasoni–Reshetikhin and the Pfaffian property require.

## Reading

- **Ticket A is confirmed on every small space, and extends to non-planar glue.** The trisums of prisms are genus-one pieces that the knot's
  signs make Kasteleyn and even, exactly like Fano atoms.
- **The handle-even spin structures are exactly what the matchings induce.** For h atoms that is 3^h of the even spin structures, not all
  of them. The ones missed are even overall but odd on some pairs of handles.
- **Evenness is a property of the minimal surface.** On larger surfaces carrying the same signs, odd spin structures appear, rarely (about
  1–2% of Kasteleyn maps) and only from genus 3 on.

## Nonclaims

- Sampled ranges are only sampled: the larger spaces' maps and matchings, and the non-minimal maps.
- No theorem is claimed for non-planar glue beyond the stated trisums.
- The observation that odd spin structures need genus 3 or more is not proved.
