Confirmed with fixes

Fresh code was written from the frozen specification and the mathematics; neither forbidden implementation was opened or imported. This is AI-authored independent recomputation, with activity and wording reviews by subagents in this task. All fate and joining-frequency conclusions concern the registered records and levels 1–12; activity classes are computed exactly from their finite automata. No human or external replication is claimed.

Validation independence is V2 for the fresh reconstruction against the study implementation. Comparisons between this task's Python and compiled checkers are same-task checks; no V3 claim is made.

## 1. Certified returns

All **48/48 returns** are independently certified: each has an independently proved dead level followed by a directly checked alive level. All 48 first deaths and F2 labels agree. The **seven parity-alternating descriptions have all 84 levels certified: 53 alive and 31 dead**, with no missing dead-level certificate.

Across all 48 descriptions, **346 alive levels** have assignments checked directly against every reconstructed knot, **218 dead levels** have checked unsatisfiability certificates, and **12 levels remain uncertified**. 43 descriptions have all twelve levels certified. There are no conflicting certified verdicts. The unresolved levels include 4 originally decided verdicts and 8 original nulls; solver budget exhaustion or an incomplete certificate check neither confirms nor contradicts that original level. Exact levels, attempts, assignments and certificate paths are in [referee_summary.json](referee_summary.json) and each linked case below.

The fresh NAE encoding has exactly two clauses per distinct triple. All accepted certificates prove the original CNF without a symmetry unit. The completed refinement certificate expands a proof of one complement-symmetry half into unconditional DRUP before checking. Unfinished candidate proofs, including a reduced proof, are retained without crediting a verdict. Both checkers use only unit propagation and never call a solver; ignored deletion lines are sound because every retained addition has already been proved RUP. The Python checker passed 4,000 comparisons with separate plain propagation, an exhaustively checked Fano example, and invalid/truncated-proof controls. The compiled checker passed 300 further plain-propagation comparisons and agrees with the Python checker on 20 saved certificates. Certificate replay files state which checker was used. No completed check of a retained solver certificate failed; interrupted checks remain uncredited.

**Narrowing:** F2 records an observed alive-then-dead pair, not permanent extinction. The supplied Glucose recheck confirms a return for every key but leaves 26 individual levels null; its `agree: true` does not certify all twelve levels.

`1` = directly verified alive; `0` = independently certified dead; `?` = uncertified in this audit. † identifies the seven alternating descriptions. Full keys and level evidence are linked.

| Key (first 12 SHA-256 digits) | Levels 1–12 | First death | Return certified |
| --- | --- | ---: | --- |
| [03702b84f550](returns/03702b84f55054331b98cb32190567a2113edcf52164075660b140a47ea28d50.json) † | `111010101010` | 4 | yes |
| [06473cf24911](returns/06473cf24911c977ce8654fef740078c9ddc478b13665fae30c39691056af7ff.json) † | `111101010101` | 5 | yes |
| [333f0477eb69](returns/333f0477eb69a4496692d5bf6673b3a1768e8e72b9dd32fdc2718dba56dab381.json) † | `111010101010` | 4 | yes |
| [40f24dbdb074](returns/40f24dbdb074a3f21b5859d4003773672e266abdb590cf18498acbc54672ef4d.json) † | `111101010101` | 5 | yes |
| [91c75673c09d](returns/91c75673c09d90467aefb05915109cabd5a02fc0103944cb525be8f56ca212c2.json) † | `111110101010` | 6 | yes |
| [cf32542e22ac](returns/cf32542e22ac0223655caaefc6e02bbdac9b16eb1115cc60631ec2f90294b2b3.json) † | `111101010101` | 5 | yes |
| [f4fd01e9afa5](returns/f4fd01e9afa5631440f1607276c889547b4767423ee44873e86cf9c85b7d2c4d.json) † | `110101010101` | 3 | yes |
| [09f2cd8cab27](returns/09f2cd8cab276fc26a8c15cbf47a27a92e26299378c302170d67bb9430dbeee4.json) | `111010000000` | 4 | yes |
| [1192a383481e](returns/1192a383481ebee3a8b1e81fbdb6eddd9b0fecb79e5ddd12957e8ed7190a79f1.json) | `111100011111` | 5 | yes |
| [198b8f08a663](returns/198b8f08a66334d6f6ae8b45d312ad48d13ef8a369b3e8c3e7a447f6ec16a4ed.json) | `11110100????` | 5 | yes |
| [2130707ad030](returns/2130707ad030c9de035e437325b1c3bdf4dfaec7ab9d51f8af24cecf7c455f26.json) | `111110100000` | 6 | yes |
| [258af17e538b](returns/258af17e538b57d16e0a1a2cbd6795ad319e7ad166e4d6d8fc0d9fff18237ac3.json) | `110100000000` | 3 | yes |
| [275976cb867b](returns/275976cb867b2b1ae5bf7f15a4e8f6b94f244b8c259a0dc5c6988c544426664a.json) | `111010000000` | 4 | yes |
| [28315fc68361](returns/28315fc6836196dda30d976a451882084082ee7012e1906e688cea168a947e03.json) | `11110101000?` | 5 | yes |
| [335b9c2432ae](returns/335b9c2432aea4fd927cb1ac5f874c1cd47c5be4cf8bf4c1487802d7f0ada4b2.json) | `111111010011` | 7 | yes |
| [4ae63f2fb377](returns/4ae63f2fb37778148cf47eeae1ce99e43e43238bb50b2353d77de0a0e25d4d42.json) | `111111011111` | 7 | yes |
| [4cb28c7d879a](returns/4cb28c7d879ab5da04da1d224f4126b05a0becd5ae716a1766158f4ec3984e1e.json) | `110100000000` | 3 | yes |
| [545d4c874195](returns/545d4c874195cf46ff1178e61e16f3177d49ebdc2b3705d4d1d68932f0383fc4.json) | `111101111111` | 5 | yes |
| [55359fe336ad](returns/55359fe336ad7a9e774325d3fb5d820bdd69bb5043c902d95df7cbc44fe5bfd0.json) | `110000011111` | 3 | yes |
| [56bc6262a4bc](returns/56bc6262a4bc0af1902721a1550b50e12932ea78a533c90188cc0e774f4a4c36.json) | `111000011111` | 4 | yes |
| [583f27564c9e](returns/583f27564c9edb420d71f109849664df5f8c86c24f20e7f5c88831142e6a731e.json) | `110011111111` | 3 | yes |
| [5a3a4d678ee1](returns/5a3a4d678ee1ff8ed137e2eb388e70007e841f8f1588749219050fd79b8b6a96.json) | `111011111111` | 4 | yes |
| [5afccf1f3c40](returns/5afccf1f3c40af11ca9b44ebc58b555636fadef2766a5bed9d4a7558916b3946.json) | `110100000000` | 3 | yes |
| [5c060d06e1d7](returns/5c060d06e1d746516c052d1462d9b6b72c16965c2fa120f92beb3bbad8ef6e56.json) | `111010000000` | 4 | yes |
| [614f5db4b5eb](returns/614f5db4b5eb56705fe620aa44e6b94260907f4542a32be3657d13f057c351cc.json) | `11110111111?` | 5 | yes |
| [675f17e8ba2e](returns/675f17e8ba2e0ac82f3ea86f4117221fb0f28c66597634f1d0c7537d4012e57e.json) | `111101000000` | 5 | yes |
| [69b038af2a52](returns/69b038af2a526c44729b29259c5872b0611f595b48e491217bcc92071075ca8b.json) | `110111111111` | 3 | yes |
| [6b6c5c44f0ee](returns/6b6c5c44f0ee1d43f9e1578cd91fdbb4c7ae30cbd482d6b8ae33ab21ade89d94.json) | `111010000000` | 4 | yes |
| [6e4fa365b97d](returns/6e4fa365b97d41da67ef5e2b259abff4e4278129b1b6a00b0c8b6f7dd6b2dbb0.json) | `111101011111` | 5 | yes |
| [7a5516c46580](returns/7a5516c46580ddf8fdea6e2c83b6ba8cec72429b324953ea3e3a75b5a99eb41b.json) | `111110111111` | 6 | yes |
| [8007fbad2a9d](returns/8007fbad2a9d53d7bca159821fd321c38eaa3fea36601667a6512178aac247eb.json) | `111010000000` | 4 | yes |
| [82b7a95c9108](returns/82b7a95c9108bf92dcefdc4f5065a264a56ca5080e9e6b615a04b2b3a975f181.json) | `110100001111` | 3 | yes |
| [992406d45fdf](returns/992406d45fdf062bff0e8cc33560aea027dac7ee7fee8c3a335ed9db690dd265.json) | `111011111111` | 4 | yes |
| [a536dd5ebd6a](returns/a536dd5ebd6ace77e069e277f5486a2842827aef4bfc5967689208ab3d22a4e1.json) | `111000001011` | 4 | yes |
| [b2e473c198e7](returns/b2e473c198e73911e004ee854c1e0ce3906b4f730d6828e0564da15964d944a5.json) | `111110111111` | 6 | yes |
| [b3084d65c377](returns/b3084d65c3776282c5e369c82208161b8efd90e8994732c4c85b6aba0956fd6b.json) | `111100011111` | 5 | yes |
| [be21be3d5445](returns/be21be3d54454a32bc6cbbc7417f68bea9b75e7a48381774baf1d17e10eb53f0.json) | `1111001100??` | 5 | yes |
| [cf817ba4fe56](returns/cf817ba4fe567cac5a1c7c8d38b888bc51d3ea948d35e2044723cbbf05587056.json) | `111011000000` | 4 | yes |
| [d1162371e754](returns/d1162371e754a38c8f2dd54733426989e4b4268173334ec3e5a2a6c4b1a73658.json) | `111111011111` | 7 | yes |
| [d3ce4bc693ff](returns/d3ce4bc693ff90efb0b165f6138deb0e804d86d67f409f648ac202a6c3187cfd.json) | `111011010000` | 4 | yes |
| [da9865d3275d](returns/da9865d3275d2aea1bc2920bb3e1bd0aa724e137d71074c26f69869212860207.json) | `11101100????` | 4 | yes |
| [db143aa56b6c](returns/db143aa56b6c082a072b2e6397d3cd745fcd62385b994e36faff4b43f2048b9f.json) | `110111111111` | 3 | yes |
| [e01e93bce96b](returns/e01e93bce96bb402ded512354f9344bdad4556d6cefa5f86ec5a6f639571a42e.json) | `110011111111` | 3 | yes |
| [e9d3586b195e](returns/e9d3586b195e125126cfb0ce0b1845aac4faf9ab04182c7c11fd522fcbb78849.json) | `110100000000` | 3 | yes |
| [ef2fdb361a23](returns/ef2fdb361a2396d74013a2791082c2b84de4a1749292458301f022fc12f1582b.json) | `111000011111` | 4 | yes |
| [f3d44a866f6c](returns/f3d44a866f6ca8068910062948264fc89845891d659a1e785a0c64b84ad82d4d.json) | `110111000001` | 3 | yes |
| [fac273f1ba4c](returns/fac273f1ba4cb9392a534736e4e23094801cd18774093d620a2e48b3433f8415.json) | `111101000000` | 5 | yes |
| [fed569be3c24](returns/fed569be3c2454e6b8b8ba4007a4679cc5bb4d04f6cdba0423a144a348c954a5.json) | `111010000000` | 4 | yes |

## 2. Fresh patterns and fates

The separate deterministic sample contains **31 records**, spanning state counts [1, 2, 3, 4, 5] and distinct placement counts [1, 2, 3, 4, 5, 6, 7, 8, 9]. All twelve knot counts, joining counts and full pattern hashes agree for every sampled record; every sampled level is directly verified alive, and its 18 F0 and 13 F3 fates agree. The empty cases are weak pattern controls; the 48 nonempty returning F2 descriptions supply an additional 576 reconstructed levels, and section 4 checks another 20 nonempty patterns. SHA-1 serialization is signed little-endian int64 level, row count, then lexicographically sorted distinct triples in row order.

Two separate builders—induction on suffix length and scalar letter-by-letter composition—agree on 200 further small pattern cases; reversing the specified product order is detected in 63 controls. Words `(q,r)` apply r first and then q. **Not a block:** no sampled reconstruction, hash or fate discrepancy was found. This is a stratified check, not an accuracy estimate for the entire census.

## 3. Relative activity classes

**80 nonempty distinct (pattern hash, relative class) units, 20 per class**, agree on relative class and polynomial degree. The independently built signed product automata include every ordered pair in each placement: 1,528 distinct products, 1,644 ordered pairs, and 780,808 finite action/address comparisons, all matching. Identity sections are detected behaviorally; the complete reachable component calculation, preserving parallel transitions, supplies the exact class. Analytic finitary, bounded, polynomial-degree-one/two and exponential controls, inverse identities, and deliberate wrong-action controls pass. Details: [relative_activity_notes.md](relative_activity_notes.md), [relative_activity.json](relative_activity.json).

**Narrowing:** as specified, V-rel checks relative **actions**, while V-act-class checks the original **letter maps**. Neither directly validates the primary inverse-product class calculation. This audit fills that gap on its 80-unit sample; a finite count discriminator alone would not prove an asymptotic class for every product automaton.

## 4. Joining counts and tail classes

For **20 globally distinct nonempty patterns, five per class**, all **240** level checks match `join_n`, knot counts and pattern hashes. Joining was counted independently using explicit suffix partitions. The registered `join_n` uses **k=1**, namely mixed last letters; the separately retained k=2 counts have no registered comparator. See [joining_check.json](joining_check.json).

**Block:** the assertion that every tail class has the same inner knots is false. In the proof note around line 110 and `addr_knots.md` around line 23, prefix action is mistaken for equality of the actual internal knot subsets. A two-state counterexample has `sw=[1,0]`, `d0=[1,0]`, `d1=[1,1]` and a single placement with word indices `(2,3,5)`, i.e. words `(1,)`, `(0,0)`, `(1,0)`. At level 4, after dropping the last two letters, suffix classes **00 and 01 have no internal triples**, while **10 and 11 each have {(0,1,2),(0,1,3)}**. The raw key's two additional placements add no level-4 triples. The total is 14 knots and agrees with the record. This was reconstructed separately by both the wording reviewer and the lead; full fixture: [pattern_controls.json](pattern_controls.json).

Fix: “A map's prefix action is independent of the suffix; its section determines the output suffix. Both internal knot subsets and joining knots may therefore depend on the tail.” This blocks the stated identical-copy interpretation, **not** the checked census or the separately stated B0 induction. Relative activity still bounds joining from above.

## 5. Wording and denominators

The note has correct explicit level-12 and weighting qualifications in its scope paragraph. Several headlines and the Answer nevertheless exceed those qualifications. Exact quotations, calculations and proposed replacements are in [wording_notes.md](wording_notes.md) and [wording_audit.json](wording_audit.json).

- **Narrowing:** “bounded joining is rare” should give frequencies and name **bounded relative activity**. It accounts for **453/5,759 = 7.87%** of nonempty W draws, versus **146/3,993 = 3.66%** of nonempty W pattern/class units, and **292/8,948 = 3.26%** in E. “About 8% of weight and patterns” conflates denominators. “A minority” is better calibrated; no threshold for “rare” was registered.
- **Narrowing:** class counts use `(hash, class)`, not distinct hashes: W has **3,997 memberships but 3,990 hashes**; E has **8,952 memberships but 8,937 hashes**. A pattern can be counted in multiple classes.
- **Narrowing:** exponential activity is an upper bound, not a lower bound on actual joining. Exponential-class key `cb20b8fe2c4262bab1f0cf6a4b0124c0f082e6e72267baf75842775b08776d97` has recorded joining counts `[0,4,4,…,4]`. Replace “almost every pattern doubles with each level” by the measured class averages at levels 10–12 under the registered weighting; “late ends need growing joining” becomes the observed association with exponential activity through level 12.
- **Narrowing:** the eligible comparison is where **few**, not zero, deaths occur: bounded has 0 deaths/36 units; exponential has 8 F2 and 16 FU among 1,108 units (1,092 decided). Its frozen equivalence verdict is within a ten-percentage-point margin, not equality. The density bins show association, rather than establishing that density determines fate.
- **Narrowing:** settlement is **74.8%** under each draw's own description flags (314/1,452 = 21.6% F2 among the rest), versus **79.9%** under the addendum's inherited pattern settlement (314/1,155 = 27.2%). Label which definition is used. The stated 61.8% one-state plus 18.2% other-empty raw composition is correct.
- **Narrowing:** qualify Lemma A's interpretation to its three uniform list forms, and qualify the gate-pass statement to the frozen summary's core checks with skipped ambiguous assertions. The unchecked finite-types remark is not promoted by this audit.
- **Not a block:** B0 and first-letter settlement have separately stated mathematical all-level scope; the finite census does not establish all-level survival, alternation, or per-pattern joining growth.

## Files and execution

Reconstruction and checks: `fresh_patterns.py`, `recompute.py`, `pattern_controls.py`, `check_rup.py`, `check_rup_fast.cpp`, compiled `check_rup_fast`, `fast_certificates.py`, `refine_unknowns.py`, `replay_certificates.py`, `relative_activity.py`, `joining_check.py`, `linear_assignments.py`, `cadical_families.py`, and `summarize_referee.py`. The bounded linear-colouring probe found no candidates for the initially unresolved levels and supplies no unsatisfiability conclusion. CaDiCaL family trajectories retain separately checked models and do not promote unlogged refutations.

Evidence: `returns/` (48 per-key JSON records), `sample/` (31 records), `certificates/` (accepted proofs plus explicitly unaccepted candidates), `certified_verdicts.md`, `referee_summary.json`, the activity/joining/wording files and notes, the control and selection JSON files, `audit_manifest.json`, `execution_notes.json`, replay JSON files, and execution logs. Source and code hashes are in the JSON records. Existing brief and last-message files were preserved.

**Not a block to the mathematics; procedural deviation:** initial PySAT calls used anonymous system-temporary proof files before its default was noticed. Their descriptors were closed; subsequent solver and verifier scratch and compiler temporary files are explicitly confined to this directory. This write-scope deviation is disclosed in [execution_notes.json](execution_notes.json); it is not a claim of perfect procedural compliance. No forbidden implementation, network, Git mutation or publishing was used.

Replay, without a SAT solver:

```sh
TMPDIR="$PWD/research/ADDR-KNOTS-20261113-001/referee-R1/codex" g++ -O2 -std=c++17 research/ADDR-KNOTS-20261113-001/referee-R1/codex/check_rup_fast.cpp -o research/ADDR-KNOTS-20261113-001/referee-R1/codex/check_rup_fast -lz
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/ADDR-KNOTS-20261113-001/referee-R1/codex/replay_certificates.py all --fast
```

Report generated 2026-11-13T23:20:02+00:00. The retained files, rather than unaccepted solver refutations, determine the verdict counts.
