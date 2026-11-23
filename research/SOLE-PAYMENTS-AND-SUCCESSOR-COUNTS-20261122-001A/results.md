# What two sole payments can force at a returning receiver

**Two parents can be forced to send equal values on an actual return. They can face this structural restriction together at most once along one continuing receiver.** After that receipt, any continuing descendants have two fresh distinctions apiece following an initial unary handoff. One writable paying parent then suffices for any requested future arrival. On every indefinitely returning material course the limiting fraction can be any number from 0 to 1 under either law. [Proof](../../proofs/SOLE-PAYMENTS-AND-SUCCESSOR-COUNTS-20261122-001A/SOLE-PAYMENTS-AND-SUCCESSOR-COUNTS-20261122-001A-P001_sole_payments/proof.md)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt · repeated sole payments | **Status: Successful, scientific referee pending** | A reached pair forces silence, then isolates its child from every sibling |
| Local direction · one growing receiver | Sharp structural obstruction | All other returns whose payers were born during growth admit simultaneous prescription of their readings |
| Broader exploration · signal frequencies | Depends on receiver access and enrollment | A mark supplied at a symmetric choice permits continued material tracking |
| G5 Dynamics | Capability and limit established | Ordinary growth fixes a particular receipt while leaving all asymptotic fractions possible |

**Next step:** Research directions — **STOP** on the assigned one-receiver question. The argument covers every funded complete-cut course in the stated class.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | More examples of this one-receiver case | 1/3 · no new limiting behavior in the proved class | 3/3 · existing fixtures recur | Compare another source → the same theorem applies | Closed at STOP |
| 2 | Simultaneous receipts in several receivers | 2/3 · joint values can constrain one another | 3/3 · the five-phase preparation supplies a parity check | Change the object to a specified family → a sharp joint-support statement | Outside this study |

**Corrections:** None.  
**Goals:** G5 Dynamics. A sole-bank restriction at one real return cannot bound the long-run fraction for this single-receiver reading.  
**Assumptions:** A150 and A153 record the choices of a return test and continuing family. The theorem fixes a material course while varying the lawful fills. [Assumptions register](../../docs/ASSUMPTIONS.md)  
**Scaffolds:** The common Boolean convention, value-independent enrollment, complete funded cuts, one exactly two-payer score per cohort and, in one continued example, a fresh name designated at an otherwise symmetric split. Removing the designation ends unique enrollment at that split. [Reviewed freeze](preregistration.md)

## The two controls

In the reached example, three live founders A, M and B fund the pairs A,M and M,B. Their two children share M as an older payer and receive exactly one fresh distinction each. On the common initial word both children ingest 00. At the following true binary birth, the only possible incoming pair is 00 under parity and 11 under not-all-equal. Both are silent returns. Another lawful founding word makes one payer’s inherited values mixed. That payer’s one fresh name remains free under not-all-equal.

| What is changed | What follows |
| --- | --- |
| Remove the remote continuing part | Parity adds its implied final equality on the two arriving names and closes. Not-all-equal still gives its child one fresh name. |
| Retain the remote part | The returned child has one fresh name, then a unary successor with two. The ensuing two unary children can be exchanged by a physical renaming that preserves all founder marks. |
| Supply a choice at that split | The same enrollment continues. Its first two cuts score binary receipts, the next two are unary, and each cut from five onward can score a binary receipt. The remaining limiting fraction is unconstrained. |
| Keep a completely identified five-founder receiver | Its positive turns recur even on the wholly quiet alternating word. This case needs no designation of a newly interchangeable child. |

The consequence for later receipts follows from true parents. Sole payers cannot pay any other child in the same cohort, so their joint child shares no earlier payer with any sibling. Once isolated, its component never reconnects through future parent groups. After its unary continuation, each path grows by an actual pair on each adjacent pair and a unary at each end. Every new member receives two fresh names. A two-parent return never again faces two sole-name payers on this one succession. [Named physical replay](physical_replay.json) · [Independent replay program](check_payments.py)

At a postfounding return with one payer holding at least two fresh names, either value can occupy its actual payment to the receiver. The other name can satisfy parity, or take the opposite value under not-all-equal. All sibling writes remain jointly lawful on the fixed older word. Returns need not be evenly spaced. A founding pair’s values are already set, while closures and lost enrollments contribute no further trials. A value-responsive routing policy can change the chosen physical payments when a word changes. The construction holds each material course fixed across its compared fills. [Five-founder control](../QUIET-RETURNS-AND-SIGNAL-FRACTIONS-20261122-001/decision.md) · [Independent scientific referee handoff](referee_handoff.md)

## Physical verification

With one extra loose distinction at the remote founder, holder 8 paid name 27 and holder 9 paid name 28 to their common child, holder 11. Its fresh name was 31 under both laws. The two actual values were 00 under parity and 11 under not-all-equal on the common quiet founder. Holder 11 paid 31 to a unary. Designating the unary’s fresh name 38 selected child 20 at the otherwise symmetric split. The next four true payer pairs were (20,21), (27,28), (36,38) and (48,50). All these payers received two fresh distinctions. The retained example yielded readings 0000 under parity and 0010 under not-all-equal over these four later receipts. These are individual lawful histories. [Complete physical receipts](physical_replay.json)

The independent implementation checked 283 births in 42 funded cuts over the two laws and three supplies at the remote founder (absent, one or two loose). It checked the original and reached star projections, reversed payments at the same parents, transported words and names, rejected a wrong grant, and verified the displayed sibling exchange. The native relation checker passed at arities 3, 4, 5, 6, 7, 8 and 11 under both laws. The two-place implied equality was checked separately. A separate application of the ordinary end operator reproduced 126 path transitions, both laws at each width 2 through 64. A check of 432 possible sibling rosters over five former payers also left the sole pair’s child isolated. These finite checks supplement the inductive proof.

The physical receipt has SHA-256 `86458e6a8626e3bff74d63f8e75600fd5b4fcb537cd3332c84a6bc88086b811f`. Three hash-seed replays, using seeds 2, 11 and 19, reproduced it. One ran in 59.36 seconds and used 43,396 KiB peak memory. The work is in-task V1, with independent scientific referee pending.

```sh
t=SOLE-PAYMENTS-AND-SUCCESSOR-COUNTS-20261122-001A
set -o pipefail
PYTHONHASHSEED=11 .venv/bin/python -B "research/$t/check_payments.py" |
  cmp - "research/$t/physical_replay.json"
```


