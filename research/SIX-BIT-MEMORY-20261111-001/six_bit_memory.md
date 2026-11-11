# Can the six-bit knots form a writable memory?

**The original four knots can hold a bit in their own six distinctions.** With two distinctions held at the same values after every write, a sample presented to a third is retained by a fourth. A fresh knot sharing that fourth distinction responds to the remembered value. The experiment supplied a rule of change, the input sequence and the connection to the fresh knot. The six distinctions remained the entire state of the memory.

This is a finite exploratory computation for G16. The [original proof](../../proofs/OVERLAP-READ-20261111-001B/OVERLAP-READ-20261111-001B-P001_what_nae_forces/proof.md) established the allowed states. The [preceding experiment](../SIX-BIT-REUSE-20261111-001/six_bit_reuse.md) added a controller and tables to learn their projections. Here every change in the six-bit base is an attempted flip of one original distinction. Choosing one distinction uniformly and rejecting disallowed flips gives the usual single-variable changes between solutions of Boolean constraints. [Gopalan, Kolaitis, Maneva and Papadimitriou](https://arxiv.org/abs/cs/0609072)

## Write a sample and read it elsewhere

Place the same not-all-equal rule on `abc`, `ayz`, `xbz` and `xyc`. It admits 18 joint states. Hold `a=0` and `x=1`. In the order `abcxyz` exactly two states remain, `001101` and `010110`. They differ on four distinctions. No single legal flip of a free distinction takes the base out of either state while the two holds persist.

To write, keep `a=0` and open the gate by bringing `x` to 0. Present the sample by bringing `b` to its value. Close the gate by bringing `x` back to 1 while still presenting the sample, then release `b`. A phase ends when its commanded values have actually been reached. A command can only change a bit through a legal flip. All the other free bits may change along the way. The read distinction `y` is free throughout.

| Sample presented to `b` | Only possible state after release | Later `y` | Fresh equal query allowed on `p,q` |
| --- | --- | --- | --- |
| 0 | `001101` | 0 | `11` |
| 1 | `010110` | 1 | `00` |

Both writes work from either starting state, including overwriting the other value. At every stage, from every reachable intermediate state a commanded state can be reached. On this finite system with independent uniform proposals that gives completion with probability one. An arbitrary scheduler could keep proposing a blocked flip. Once a write completes, every allowed continuation with the neutral holds preserves the reading.

For the later query, attach a fresh not-all-equal knot on `y,p,q`. It permits both mixed queries in either case. The two equal queries in the table distinguish the histories. Giving the fresh knot its own independent input admits all four queries for either history. This establishes how the stored bit can have a consequence elsewhere with a supplied connection.

## Where the memory comes from

The test tried all 360 ways to assign four distinct ports to reference, gate, sample and read. The original base works in 72 assignments, counting either a direct or inverted reading with its convention fixed across both samples. The complementary four knots with the same allowed states give the same answers. Removing any one of the four original knots leaves 26 states and zero working assignments under this protocol. The unconstrained six bits also give zero.

A pulse of the gate with the sample free allows either final reading from either start. Releasing the full neutral cue lets the six distinctions move among all 18 states. Holding just one distinction leaves nine connected states for either held value on any port. In this example both the presentation of a sample and the two subsequent holds have observable roles.

The exact census covered every way to place four distinct unsigned not-all-equal rules on six named distinctions. Of the 4,845 patterns, **4,170** can retain a bit for some assignment of ports. **175** work at the fixed ports `a,x,b,y`, of which 30 give `y=b` and 145 give its complement. The first count allows the experimenter to look for working ports after seeing the pattern. The second fixes the ports before inspecting it. Unused distinctions and failures are included. [Census and individual checks](../../artifacts/SIX-BIT-MEMORY-20261111-001/SIX-BIT-MEMORY-20261111-001-E001_writable_memory/result.json)

**A separate calculation after the census** asks what happens if the experimenter supplies a rule for forming knots and leaves the connections to chance. Start with six bits, hold the neutral cue `a=0,x=1`, and draw the other four values uniformly. Keep that assignment during formation. Four times, uniformly choose a previously unused triple that currently has mixed values and add its not-all-equal knot. Each placement consults only the values on the proposed triple. The sample values to be written later and the read port play no part in choosing placements. Release the four starting values for the writing test, keeping the neutral cue.

At these fixed ports, the probability of a working memory with either read convention is exactly **3047/139230**, about **2.19%**. Requiring `y=b` throughout gives **7771/2227680**, about **0.35%**. Conditional on each starting state, every four-element subset of its available triples has the same probability. Weighting those subsets over all 16 starting states gives the two fractions. This models a way a functioning part can arise without choosing its connections in advance. The rule for adding a knot and the timing of formation are supplied. [Calculation](assembly.py) · [Counts for each starting state](../../artifacts/SIX-BIT-MEMORY-20261111-001/SIX-BIT-MEMORY-20261111-001-E001_writable_memory/assembly.json)

## Does it learn that x, y and z are never all equal?

Compare exposure to the original base with exposure to one in which the knot on `abc` is removed. Only the latter permits `xyz=000` or `111`. There are legal histories of **50 moves** in each that start and end at the very same full state, `001001`. Each visits every allowed state of its own base. The second encounters both all-equal examples. With all six bits identical at the end, any later common test whose input is those six bits has the same response law for these two histories. Even seeing the complete evidence can leave no record distinguishing the rules. [Two explicit histories](../../artifacts/SIX-BIT-MEMORY-20261111-001/SIX-BIT-MEMORY-20261111-001-E001_writable_memory/experience.json)

There is a weaker effect of experience. Prepare each base uniformly on its allowed states, then compare just those with `xyz=001`. Under a common test with the knot on `abc` removed, the chance that the next proposal produces `xyz=000` is zero after original experience and 1/24 after experience of the base missing that knot. Only the latter sometimes has `abc=111`, where flipping `z` succeeds. Preparing exactly the same mixture of hidden values reproduces the effect. Under a common test that allows every flip, the next visible word stays put with probability 1/2 or changes any one of its three bits with probability 1/6 each, for every hidden state. [Experience calculation](experience.py)

What the knots supplied here is a place to **keep and use a presented value**. Learning the underlying rule would require their own experience to determine what gets written. The legal histories above give a concrete test for any proposed mechanism that does that. The evidence is finite and exploratory.

## Reproduce

The [frozen envelope](../../experiments/SIX-BIT-MEMORY-20261111-001/SIX-BIT-MEMORY-20261111-001-E001_writable_memory/contract.json) identifies the prior feasibility observations, supplied resources and primary tests. The growth calculation is a secondary reweighting of the census. A separately written [checker](verify.py) used a second method for finding closed sets of states under a command, enumerated all 4,845 patterns at fixed ports, and checked relabelings across all 21 classes. It matched the growth probabilities by summing the probabilities of successive placements and verified the two complete histories and the responses to common cues. Two executions of the primary experiment agreed on every scientific field. This is a separate same-task check (V1). [Verification record](../../artifacts/SIX-BIT-MEMORY-20261111-001/SIX-BIT-MEMORY-20261111-001-E001_writable_memory/verification.json)

From the repository root, run the following in Bash. The result is deterministic apart from elapsed times.

```bash
ticket=SIX-BIT-MEMORY-20261111-001
family=${ticket}-E001_writable_memory
trial_dir=$(mktemp -d)
python3 -B "experiments/$ticket/$family/run.py" --output "$trial_dir/result.json"
python3 -B "research/$ticket/experience.py" --output "$trial_dir/experience.json"
python3 -B "research/$ticket/assembly.py" "$trial_dir/result.json" --output "$trial_dir/assembly.json"
python3 -B "research/$ticket/verify.py" --producer "$trial_dir/result.json"
```
