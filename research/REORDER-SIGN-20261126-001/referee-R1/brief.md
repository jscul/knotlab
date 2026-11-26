# Referee brief: REORDER-SIGN-20261126-001

You are an independent referee for a Prespatial Labs study in /home/jscul/p-vs-np-contact-first. Read AGENTS.md first. Check
the claims below with your own code, written from the definitions; do not import or run the study's modules except to compare
outputs at the end. Write everything to research/REORDER-SIGN-20261126-001/referee-R1/codex/ and commit nothing. Finish with
research/REORDER-SIGN-20261126-001/referee-R1/codex/report.md, verdict first: confirmed / confirmed with fixes / refuted, then
one line per claim, then any missed prior work and any wording that outruns the evidence.

Records: research/REORDER-SIGN-20261126-001/preregistration.md (frozen at commit 5a5a285351) and results.md. Code:
artifacts/REORDER-SIGN-20261126-001/REORDER-SIGN-20261126-001-E001_reorder_signs/check.py (results.json beside it) and
research/REORDER-SIGN-20261126-001/verify_fock.py (verify_fock.json beside it).

Definitions. Swap rule: list distinctions in order of creation; a listing's weight relative to another is (-1)^(number of pairs
of distinctions that both hold 1 whose relative order differs). Readings: ordinary Z and real flip X, held fixed. Full
contradiction: every even-size correlation <X_T Z_rest> is +-1 and T -> c(T)/c(empty) is not a character
(three readers: <ZZZ><XXZ><XZX><ZXX> = -1).

Claims to check, each proved or computed exactly:
1. (computed) On one parity knot of n distinctions with all n! listing orders, the full contradiction appears for exactly the n
   orders that reverse a prefix and its complementary suffix separately: 3/6, 4/24, 5/120, 6/720. Odd orders predict it only at
   n = 3. The reversal sign equals (-i)^k on even words for n = 3..8.
2. (computed) Grown ternary (one parity ternary and its three one-parent children from the fewest-funded parity round), readers
   holding their old distinction and their child's first fresh distinction, flip X_x X_y, state signed relative to the
   production listing: odd commit orders give P = -1; the reversal matches the 64-cell target exactly; reading the old
   distinction alone gives scored win 5/8; s = +1 gives 5/8 in every order.
3. (computed) Orders unknown to the readers (equal mixture): best Mermin score 4/3 over odd orders, 7/6 over all six. Orders not
   recorded (equal-weight coherent sum over commit orders): only words with at most one odd child survive; on the ternary only
   000.
4. (computed, the main finding, found after the frozen prediction P7 failed) Fermionic model: nine modes, the start a positive
   parity knot with its parents created in a stated order, births K_j = (1-n_j)(1 + c+_y c+_z)/sqrt2 + n_j(c+_y + c+_z)/sqrt2
   applied in commit order, readers with (-1)^n_x and F1 = -i g'_x g_y (g = c + c+, g' = i(c+ - c)). The full contradiction
   appears exactly for commit orders even relative to the parents' creation order, under both parent orders; committing in the
   parents' order gives 64/64 with fixed labels; with F2 = i g_x g'_y no order carries it.
5. (argued) The frozen P7 check used a convention equivalent to births carrying a string over all earlier distinctions; the
   physical sequential model differs from it by a reversal.

Also check: whether claim 4 survives a different within-pair order of the child's fresh creators (c+_z c+_y), a different
assignment of the reader's record (the second fresh distinction), and mixing F1 and F2 across readers; and whether the
"parents' creation order" is well defined when the start's sign convention changes. Report what changes.

Budget: exact small computations; keep it under an hour.
