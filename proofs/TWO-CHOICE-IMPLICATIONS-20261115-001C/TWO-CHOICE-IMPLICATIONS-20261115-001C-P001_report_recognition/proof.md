# The cost of recognizing a two-choice report

Status: Proved

## Standard statement

A block of a fixed guarded serial Boolean formula exposes two local endpoints and two middle variables \(h,k\) shared across a cut. Fix its local endpoints to \(1,0\). Each of the following recognition problems is NP-hard under a polynomial-time many-one reduction even when only guard bits change on one wiring per source-variable count. The first asks whether the allowed ordered pairs are *exactly* the implication \(h\to k\). The second asks whether any conjunction of unary restrictions and positive implications on \(h,k\) describes those pairs. Four independent SAT queries determine the entire local relation for a fixed endpoint pair.

## Nearest known result

The previous fixed-wiring prefix realizes strict 3-SAT on a guard-selected catalogue. It was used to show that recognizing whether to drop agreement on one choice is NP-hard. The present tests ask different questions about the information to report on two choices. Each reduction uses only switches before a fixed observation gadget. [Earlier prefix and boundary relation](../../GUARD-CHOICE-SEPARATION-20261115-001C/GUARD-CHOICE-SEPARATION-20261115-001C-P001_recognition_cost/proof.md)

## Construction

Use the prefix \(P_F(x,u)=(x\le u)\lor\operatorname{SAT}(F)\) of that earlier proof. The outer units are disabled and the query pins \(x=1\). Consequently \(u=1\) is always possible and \(u=0\) is possible exactly when the input strict 3-CNF \(F\) has a satisfying assignment. Both gadgets below leave the last local boundary \(b\) free, and the query takes \(b=0\). They use a single occurrence of each of \(h,k\). A right block can have one whole stage, with \(b\to h,b\to k\) its only constraints. At \(b=0\) this side permits every pair, and its far endpoint may also be fixed to zero. Thus the actual two-sided query observes exactly the left report while both middle names occur on both sides. Each middle or pad has at most two uses.

**Recognizing one given implication.** In two stages let the enabled implications be \(u\to h\to c\to k\) for a fresh internal boundary \(c\). All other implications in those stages are off; both padded halves of each required arrow are active. When \(F\) is satisfiable we can pick \(u=0\), and exactly \(00,01,11\) remain. When \(F\) is unsatisfiable we must pick \(u=1\), so only \(11\) remains. In the latter case the implication still *holds*, but reporting it alone would admit two nonexistent pairs. This proves the reduction for exact reporting.

**Recognizing the whole positive-implication language.** In one stage put \(h,k\) on the two incoming branches and share a fresh padding bit \(p\) with opposite active signs. Depending on \(p\), just one of \(u\to h\) and \(u\to k\) is enforced. The outgoing halves are off. Eliminating \(p\) produces \(\neg u\lor h\lor k\). A satisfiable \(F\) allows \(u=0\) and hence all four pairs, described by the empty conjunction. An unsatisfiable \(F\) produces \(h\lor k\), whose pairs are \(01,10,11\). Both coordinates take both values and both directions of implication fail. Equivalently, the relation omits the coordinatewise minimum \(00\) of two of its states. No unary restrictions and positive implications can express it. This proves the second reduction.

For fixed \(n\), the strict-clause prefix uses \(8\binom n3\) catalogue slots and its full guard list. Each gadget uses a constant number of extra stages and fixed switches. All source-dependent information is in the prefix switches. The length of either encoding is polynomial in the source size after reindexing. For an upper bound ask SAT once on the raw block with its guard settings and the two ports fixed to each of \(00,01,10,11\). Compare the resulting four-bit table with the desired language. This upper bound is for one specified endpoint pair. The proof supplies NP-hardness and makes no completeness assertion. ∎

The checker enumerates all 256 width-three selector menus, then checks width-four and width-five fixed catalogues. It tests the pinned raw CNF for every port pair in both gadgets and compares with source enumeration, verifying the suffix guards and the two names that actually cross. [Checker](check.py) · [Raw query counts](checks.json)
