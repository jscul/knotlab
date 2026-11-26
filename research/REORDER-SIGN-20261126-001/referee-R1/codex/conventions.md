# Which reversal relates the two birth conventions?

**Claim 5 is confirmed with fixes.** Positive appending in an earlier-first list can be implemented by a particular parity string on the odd part of each birth. With the initial Fock vector held fixed, ordinary left births differ from these append births by reversing the sequence of child blocks. If positive chronological left creation is also used for the old distinctions, the two reversals cancel on the ternary start. The resulting nine-mode vectors agree coefficient for coefficient. Distinguishing the two operations then requires examining an intermediate birth.

## The sign at a birth

Let \(O\) be the occupied creator word for the earlier modes, \(N\) its length, and \(F\) the occupied creator word in one new pair, always written with \(y\) before \(z\). The parity \(p\) of \(F\) equals the old distinction \(x\) that funds this child. Every new mode is distinct from every old one. The canonical anticommutation relations give

\[
OF=(-1)^{Np}FO .
\]

Thus appending \(F\) to \(O\) on the right has the same action as the ordinary left birth multiplied by \(P_E^p\), where \(P_E=(-1)^{\sum_{u\in E}n_u}\) and \(E\) contains all previously present modes. The string acts before creation. Writing \(K_j=K_{j,\mathrm{even}}+K_{j,\mathrm{odd}}\) for the two terms of the stated birth gives the append map \(K_{j,\mathrm{even}}+K_{j,\mathrm{odd}}P_E\) on inputs with the fresh modes empty. This realizes the earlier-first positive listing in the same fixed Fock representation. The frozen text gives a rule for relative weights and a prescription for the readers. It does not single out an operator implementation from all maps agreeing on the prepared inputs. [Frozen listing rule and readings](../../preregistration.md)

The sign is already detectable at the second child in order \(a,b,c\). In both cases its parent \(b=1\), and the birth creates \(y_b\).

| Occupied before the birth | Parity of all old distinctions | Compensation for the left birth |
| --- | --- | --- |
| \(b,c\) | even | \(+1\) |
| \(a,y_a,b\) | even | \(-1\) |

Each input occurs in this growth round. The two cases rule out a correction depending only on \(b\). Because the three original distinctions always have even total parity, a string over the earlier fresh blocks alone has the same action on these inputs. The full prefix is a valid extension. Its action outside the occupied input space requires an additional choice.

## The sign over a round

Write \(P_\rho\) for the occupied old distinctions in earlier-first order \(\rho\). Let \(\pi\) be the child commit order. Positive earlier-first appending gives the creator word

\[
W_{\mathrm{append}}=P_\rho F_{\pi_1}F_{\pi_2}F_{\pi_3}.
\]

Starting from the same \(P_\rho\), ordinary left births give \(F_{\pi_3}F_{\pi_2}F_{\pi_1}P_\rho\). Passing all children over the old word costs \((-1)^{|x|\sum p_j}=+1\) on the even start. Reversing the child blocks costs

\[
D(x)=(-1)^{\sum_{i<j}p_i p_j}=(-1)^{\binom{|x|}{2}} .
\]

Consequently the fixed-start left vector equals the append vector with the sequence of child blocks reversed. Reversing only the old listing also gives \(D(x)\), because there is one child for each occupied old distinction. If positive left creation was used for the old distinctions in chronological order \(\rho\), the input monomial is already \(P_{\mathrm{rev}(\rho)}=D(x)P_\rho\). The two signs then multiply to \(+1\). A literal reversal of every individual mode also reverses the creators inside every fresh pair. Swapping \(c_y^\dagger c_z^\dagger\) for \(c_z^\dagger c_y^\dagger\) contributes \((-1)^{\sum_j y_jz_j}\). Even with all \(x_j=0\), a single fresh \(11\) changes that sign.

The exact check compared all 32 occupied words and all 36 pairs of parent and child orders. With the input vector held fixed, 864 of 1,152 coefficients changed sign. With chronological left creation throughout, all 1,152 agreed with earlier-first append. Reversing each fresh pair as well changed 576. The prefix identity held for all 576 stage inputs counted across the six child orders and 32 final words, including repeat visits to intermediate inputs. [Calculation](conventions.py) · [Exact output](conventions.json)

## What the start and the readings fix

Use the grouped basis \((x_j,y_j,z_j)\) for each reader. Its occupied groups have even parity, so permuting whole groups contributes \(+1\). Interleaving parents and fresh blocks costs \(D(x)\) when their orders agree. For arbitrary \(\rho,\pi\), the named-word sign in that basis is

\[
D(x)(-1)^{\sum_{\{i,j\}} I_{\rho,\pi}(i,j)x_i x_j},
\]

where \(I_{\rho,\pi}\) is one exactly on pairs whose relative order changes. This formula assumes positive coefficients in the chronological parent preparation. Multiplying those coefficients by a fixed sign function \(h(x)\) multiplies the displayed answer by \(h(x)\). For example, taking \(h=D\) with the readers fixed moves exact agreement from first-created-first-served to the reverse order, and the carrying class from even to odd relative orders. More generally, any \(\rho'\) describes the identical family of states for every \(\pi\) if its initial coefficients are \(h'(x)=h(x)(-1)^{\sum_{\{i,j\}}I_{\rho,\rho'}(i,j)x_ix_j}\). Thus the sign calibration matters even when all six child orders are tested. A passive change of representation transports both the start and each reading, which preserves every probability.

The ordinary start is one ternary holding that funds three children through three distinct old distinctions. It specifies their even joint words. Permuting their names preserves that relation. Chronology is meaningful when a history supplies it, and the positive amplitudes in that chronology must also be specified. The unsigned start alone supplies neither. In the frozen rule, old indices give a listing on which an ordering convention can be based. [Earlier birth definition](../../../GROWTH-SIGN-LAW-20261125-001/results.md) · [Earlier source and reader gauge control](../../../WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001/preregistration.md)

The label “physical sequential” also needs qualification. Both specified pair readings are even operators in their three-mode algebra, and readings on disjoint groups commute. Each \(K_j\) has an even and an odd component. Conjugating it by total fermion parity changes the sign of just its odd component. It is supported on its own modes as an element of the anticommutation algebra, but implementing it as a parity-preserving physical operation would require further apparatus or a different model. An ordering string in a qubit representation alone does not determine this physical question. [Study’s operator definitions](../../results.md)
