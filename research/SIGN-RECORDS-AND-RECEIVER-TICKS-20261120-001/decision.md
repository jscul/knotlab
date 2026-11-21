# Recording a relative sign and measuring delay in receiver ticks

## Final report as sent

2026-11-20 22:05 PST

The four-knot reader recorded which operations happened first, but reversing the relative sign between the same two allowed words at fixed preparation history never changed its answer.

The receiver counted **four ticks from send to receipt** with the third structure connected at both ends and **five without it**, and an equally short passage through a finite structure gave the same four.

| Test | Status | What established the answer |
| --- | --- | --- |
| B243 · Sign detection | Scoped obstruction proved under both knot laws | The supplied swaps changed a memory mark that the reader could read. Even when every single-time distribution agreed, saving the earlier memory value let the reader distinguish the histories. Reversing the sign independently of that history left the pointer unchanged. The proof covers ordinary operations that use retained records, including feedback. [Physical histories](https://github.com/jscul/knotlab/blob/main/research/SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001A/physical_records.md) · [Proof](https://github.com/jscul/knotlab/blob/main/proofs/SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001A/SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001A-P001_record_obstruction/proof.md) |
| B243 · Probability calibration | **64/64** one-read calibration checks reproduced | A data singleton gave a fair answer when the original uncertainty had moved into memory. Fixing the entire apparatus made the answer deterministic. A separately supplied sum-and-difference operation detected both signs. Any perfect normalized detector for them must give a fair answer on either singleton. [Calibration and controls](https://github.com/jscul/knotlab/blob/main/research/SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001A/results.md) |
| B259 · Internally measured delay | Matched witness proved under both knot laws | From its own recognizable origin, the receiving member counted **five versus six** ticks. It recovered its ancestor at the send and counted **four versus five** strictly after that ancestor, up to and including receipt. One actual parent carried the specific emission and the continuing receiver parent lacked it. The first common descendant occurred at the same parent step in all five primary starts. [Receipt proof](https://github.com/jscul/knotlab/blob/main/proofs/SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001B/SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001B-P001_receiver_ticks/proof.md) |
| B259 · Sustained activity | Equal counts proved at fixed usable passage in this class | A lasting third connected at only one end gave five ticks. Rewiring two spent knots preserved all 130 live holdings and their supplies while ending the designated third family. After both finite families had ended, a later send still took **six** ticks on each short passage and **seven** on the long one. The receiver kept one tick per 24 parent steps. All 38 prepared comparisons registered without a stall. The pure clock never took the foreign send, and all 44 neutral controls failed the same receipt test. [Matched starts and controls](https://github.com/jscul/knotlab/blob/main/research/SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001B/results.md) |

**Next step:** Research directions — selected: #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Change which three parents can contribute together while keeping passage and funding fixed (B277) | 3/3 · isolates an effect beyond passage length | 2/3 · a known edit changes the parents, and both clocks must survive | Compare common and separate witnesses. Stop at a traced tick difference against an inactive control or a proof of equality. | Selected · deferred |
| 2 | Test a physical erasure for relative-sign detection (B268) | 3/3 · could supply the missing measurement | 2/3 · the test is exact, and a physical erasure is still needed | Keep both erasure outcomes and cross the two signs at fixed history. Stop at an ordinary sign-sensitive pointer or a scoped obstruction. | Alternative · deferred |

**Corrections:** None to a published claim.  
**Goals:** G18 gains a test that separates sign detection from ordinary memory. G5 gains a delay measured by the receiver itself. Both studies closed after independent Astra Max review of their original and revised designs. Scientific refereeing is pending. [B243 handoff](https://github.com/jscul/knotlab/blob/main/research/SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001A/referee_handoff.md) · [B259 handoff](https://github.com/jscul/knotlab/blob/main/research/SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001B/referee_handoff.md)  
**Validation:** The scoped proofs, replays and evidence links passed. The workspace-wide checkpoint still flags a pre-existing wording change in an unrelated research skill.  
**Assumptions:** A161 records which preparation history the reader can access. A162 records how the receiver identifies a send and counts a tick.  
**Scaffolds:** The two-word preparation, swap controls, memory access and quantum comparison were supplied. The clock frames, sending phase, receiving family, ports and tick reading were also supplied. Ordinary growth determined the actual parents and payments.  
**Basket:** B243 and B259 closed. B277 is selected because it changes an ordinary parent decision while keeping the passage fixed.

For G1, the model now exhibits an internally measured change in signal delay caused by the available passage. Whether a third structure’s sustained activity can change that delay at fixed passage, or change the receiver’s pace in a way that supports a law of gravity, remains open.
