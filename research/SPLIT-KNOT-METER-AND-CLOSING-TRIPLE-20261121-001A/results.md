# A split parity knot cannot power the two-reader sign meter

The two readers cannot use the positive-amplitude preparation of a single split parity knot to measure the joint sign while each individual operation keeps the physical knot lawful. The probability of an exact, announced return is **zero**. With the same access and the positive not-all-equal preparation, they can do it on **exactly one third of launches**, the optimum even with unrestricted separate quantum operations. A stronger atomic offer at both readers makes the coherent parity source work on **every launch**. [Proof](../../proofs/SPLIT-KNOT-METER-AND-CLOSING-TRIPLE-20261121-001A/SPLIT-KNOT-METER-AND-CLOSING-TRIPLE-20261121-001A-P001_split_meter/proof.md)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — one split knot and an independent two-register target | **Successful** | Every finite serial parity protocol leaves a mixture of products on target input 00. Both required signs would return entangled states. |
| Local direction — keeping every named word lawful | Resolved for the two registered preparations | One shared classical success flag and single-place changes suffice for not-all-equal. Parity keeps a physical record of which of two alternatives occurred. |
| Broader exploration — coherent readings of larger holdings | Open | The present proof covers the split with one binary place at the second reader. A companion knot inaccessible to either reader can change the source they receive. |
| Long-term goals — G18 Comparing growth laws and G5 Dynamics | Operational distinction established | The two laws admit different uses of supplied weights. Neither ordinary law produces the initial coherent preparation or the measuring gates. |

**What blocks parity.** The first reader's local parity always equals the last physical bit, held by the other reader. Whenever one reader acts, the other still holds a record distinguishing their two alternatives. Forbidden outputs from one cannot cancel outputs from the other. At each fine outcome, including a postselected outcome with arbitrary private memory, each alternative remains product on the independent 00 target. Forgetting the physical source therefore leaves a mixture of products. Either ideal sign would return $(|00\rangle-t|11\rangle)/\sqrt2$. Even a real reader asked only to distinguish the equiprobable opposite-sign mixtures gets no information. This obstruction already holds when safety is tested only on the actual prepared state. A separate local read can still see coherence *within* each parity alternative. [Access audit](access_audit.md) · [All complete-word checks](access_checks.json)

**What works for not-all-equal.** Write the named places in order $a,c,b$, with $a,c$ at the first reader. One local herald accepts the two equal first-reader rows together. The words 001 and 110 pass. The first reader stores $a$ privately and makes its physical row 01. The other reader can now store and clear its bit. Both word paths leave the same physical source 010 and the same herald. After calibration their private bits are the positive coherent pair 00 and 11. On the four other words the herald refuses, the target remains untouched and all three ordinary keepers stay blank. A kept record distinguishing 001 from 110 spoils the read. Coherently returning that additional record restores it. Dephasing the six words gives the same one-third admission with only a classical private pair. [All source and target outcomes](meter_evidence.json.gz)

| Source and access | Complete signed return per full launch | Error-free sign alone on equal priors | Best compulsory guess of that sign |
| --- | ---: | ---: | ---: |
| Coherent parity, one reader at a time | 0 | 0 | 50% |
| Fully dephased parity or not-all-equal, one reader at a time | 0 | 0 | 50% |
| Coherent not-all-equal, each reached named word must stay lawful | 1/3 | 1/3 | $1/2+\sqrt5/6$, about 87.27% |
| Coherent not-all-equal, every offer must handle all originally compatible remote words even after a herald | 0 | 0 | 50% |
| Coherent parity, two controlled clears allowed as one atomic offer | 1 | 1 | 100% |

An obligatory guess may disturb the target. An error-free sign reader may refuse. For the complete return, each sign must leave all within-sign states and untouched spectators intact. The three numbers for not-all-equal follow from the two original reduced weights $5/6$ and $1/6$. Each successful exact return on 00 uses at least half its branch probability from the smaller weight. Both optimal sign-only comparisons have separate proofs. [Conditional maps and both sign bounds](../../proofs/SPLIT-KNOT-METER-AND-CLOSING-TRIPLE-20261121-001A/SPLIT-KNOT-METER-AND-CLOSING-TRIPLE-20261121-001A-P001_split_meter/proof.md)

**What the readers can retain.** With the coherent pair, the two complete flags $u,v$ announce $t=(-1)^{u+v}$. On a successful launch each fine pair gives $P_t\rho P_t/2$, where $P_t=(I+tM)/2$ and $M=-J\otimes J$, $J=XZ$. On 00 the four fine-record probabilities are each $1/12$ per original not-all-equal launch and $1/4$ conditional on admission. The two signs together account for $1/3$ of launches. Refusal accounts for $2/3$. A fresh successful repeat preserves every returned within-sign superposition. The local keepers write 101 or 011. A third keeper writes 101 for equal measured bits and 011 for different bits only after both arrive. Without both, it remains 110 even when a physical measurement has already occurred. Across 59 settings the replay retains 283 one-launch records, 270 fresh-repeat records and 968 keeper and message settings. The checks use the existing ordinary keeper under both growth laws. [Independent-source replay and physical writer](meter_replay.py)

A second not-all-equal protocol transfers the entire source to private registers. Its private filter gives the same optimal one-third rate on the positive preparation. When applied to the fully diagonal state, that filter accepts on $17/75$ of launches and its three refusals have weights $6/25$, $1/3$ and $1/5$. No sign is recovered from the accepted diagonal state. The proofs and receipt distinguish the unconditional source transfer from waiting to transfer the last place until after the filter. [Filter, named source and refusal records](meter_evidence.json.gz)

**What synchronization costs.** In the four parity words, the two readers can first copy the same effective bit into separate blanks. Then they clear the two corresponding physical places together. Both halves succeed as a joined reversible offer on the reached equal private controls. Either half by itself violates parity on 011 and 101. The discrete joined offer cannot be implemented by a continuous product of local unitary drives preserving the physical relation throughout. Its application to the not-all-equal source produces forbidden 000 on three of six words. The specified ready apparatus, failed offer, retained tags, reversed phases and disconnected readers are in the [exact records](meter_evidence.json.gz).

**Next step:** Full pivot — No next action selected.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | An unread companion knot sharing one distinction | 3/3 | 3/3 | Trace its unread names in a fixed positive preparation → determine the best lawful signed return | Alternative · deferred to the joint decision |
| 2 | Two overlapping not-all-equal knots with two bits per reader | 2/3 | 2/3 | Use the two rules on $a,c,b$ and $a,b,d$, splitting $a,c$ from $b,d$ → find an optimal serial read or an obstruction | Alternative · deferred |

Direction 1 tests whether the meter survives when supplied inside a larger holding. Direction 2 changes the access question on four named bits: neither reader has a single physical word compatible with every alternative at the other. The one-place transfer argument leaves that case open. These are comparisons for the [joint decision](../SPLIT-KNOT-METER-AND-CLOSING-TRIPLE-20261121-001/decision.md).

**STOP** on the isolated split source. The frozen success-or-obstruction question has a proof, exact controls and retained failures. Independent scientific referee pending.

**Corrections:** None to earlier public claims. The earlier split reading explicitly allowed a local change to leave the original relation.

**Goals:** B294 tests G18 Comparing growth laws and G5 Dynamics. The declared access separates the two preparations.

**Assumptions:** A182 fixes single-reader word safety and gives an atomic joint offer separate standing. A181 supplies the full surviving-state requirement.

**Scaffolds:** Real positive amplitudes, fully dephased controls, squared weights, private ready storage, coherent target operations, classical communication and the optional atomic offer are specified. No native source of coherence is inferred.
