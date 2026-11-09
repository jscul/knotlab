# A one-dimensional return map and its digit recursion

Status: Partial (pre-registered 2026-11-09, before the proof attempt).

Ticket `RETURN-DIGITS-20261109-001A`.

## What is registered

At n = 2^m, h = n/2, for the walk of the n × n torus of rule-60 rings cut open both ways (over GF(2)), with the return map C_s of
`CONE-COLLAPSE-20261109-001A` (det(I − wA_cone) = det(I + C_s(w))):

1. **The one-dimensional model.** C_s = w^(n+1) T_h(w^(−2)), where T_h(c) is the matrix, in the ball basis W_k(t + 1/t) = Σ_{|j|≤k} t^j
   (k < h) of F[c][K]/(K^h), of the map f ↦ (K + c)·(ιf)(K + c) mod K^h, with ι(W_k) = W_(h−1−k). Equivalently, λ ≠ 0 is an
   eigenvalue of the walk exactly when det(λ^(n+1) I + T_h(λ²)) = 0.
2. **The digit recursion.** T_1 = [c] and T_2h = P [[A(R + c^h), c^h AR], [A + u(c^h u + v)ᵀ, AR + c^h uvᵀ]] P, with A = T_h, R the
   reversal, u = e_0, v = e_(h−1) and P = [[I, R], [0, I]] (the change from the ball basis of F[c][K]/(K^(2h)) to the basis W_i, K^h W_i).
3. **The un-reversed operator.** S_h = T_h R satisfies det(zI + S_h) = c^h (1 + Σ_{j<m} (z/c)^(2^j)): its eigenvalues are c·x for the
   h elements x of GF(n) of trace 1.

**Target.** Every nonzero root of det(λ^(n+1) I + T_h(λ²)) is a (2n − 1)-th root of unity, at every power of two. To be proved, or
left open with the gap stated.

**How 1 to 3 were found.** By exact computation before this registration: (1) against the torus at sides 4 to 32, (2) for h = 1 to
16, (3) for h = 1 to 32. Their proofs, and the target's, are the attempt registered here.

## Planned checks

- (1) at sides 4 to 32 against `CONE-COLLAPSE-20261109-001A`'s C_s; (2) for h = 1 to 32; (3) for h = 1 to 64; the target as
  det(λ^(n+1) I + T_h(λ²)) against the cone polynomials of `CONE-COLLAPSE-20261109-001A` at 4 to 64.
