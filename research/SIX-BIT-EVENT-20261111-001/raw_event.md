# Can seeing 000 or 111 make the six-bit knots remember?

**Yes, in a model with three permanent input connections and a fixed local rule of change.** An all-equal observation can leave a mark on the original distinction `y`. Mixed observations alone never mark a clear witness. A separate knot joined only to `y` can use the mark after the source returns to exactly its earlier state. No step of the system checks whether it is time to write.

The [preceding six-bit test](../SIX-BIT-MEMORY-20261111-001/six_bit_memory.md) used an external sequence to open the memory, present a value and close it. Here the changing values come from the source and the memory runs continuously. This is an exact, exploratory finite experiment for G16.

## Where the observation comes from

The six-bit witness always obeys not-all-equal on `abc`, `ayz`, `xbz` and `xyc`. Its own `xyz` can never be all equal. Give it three input values `u,v,w` from another source. Connect each to the same two original distinctions through an ordinary not-all-equal rule on `(u,a,x)`, `(v,a,x)` or `(w,a,x)`.

If the three inputs are mixed, the connections require `a` and `x` to differ in any state satisfying all three. With that pair opposite, the witness has four resting states. In each, changing any single bit either violates an original knot or breaks a satisfied input connection. On `000`, the pair can also become `11`. On `111`, it can also become `00`. Either event opens a way for the rest of the witness to change.

On each attempt, choose a witness bit uniformly. Accept its flip if all four original knots still hold and none of the three input connections becomes newly violated. A source change can temporarily disagree with a connection. The same local rule then permits repairs. The source can move again at any time. For the first memory test, give `y` a constant one-way preference so that once it becomes 1 it stays 1. The preference applies under every input. The four original rules, the choice of connections, the clear preparation, the update rule and the upper connection are all supplied. All retained information in the witness lives in its six bits.

With no inputs held, the canonical `knotlab check` finds the six mixed states on each of the three input connections, on internal `xyz`, and on the upper knot. It finds all eight assignments on the three external inputs taken together. These static checks are distinct from the dynamical tests below.

## A source that supplies its own examples

Run a second six-bit system as the source. Let its `xyz` be the raw input. Attach a fresh knot on `y,p,q`, leaving its two new distinctions free to change. Each of the fourteen distinctions in the source, witness and reader is equally likely to try a flip at each step. The source follows its own constraints and receives no feedback. The reader stays attached and its constraint applies to flips at either end. Initialize the witness in either of its clear resting states and allow every compatible initial reader pair.

| Source | Reachable joint states | Can `y` record an event? | Can the upper pair reach `00`? |
| --- | ---: | --- | --- |
| Original four knots, 18 source states | 108 | Never | Never |
| Remove the source knot on `abc`, 26 source states | 1,404 | Eventually, with probability one | Eventually, with probability one |

These are reachability and probability results over all the permitted initial states. In the relaxed source, every reachable joint state has a path to a written state and to an upper `00`. In this finite system every such path has positive probability. There is no closed set of reachable states that can avoid either target forever. In the original source, every reachable witness remains clear.

There are two short histories from the same start that isolate the cause. In one, the source visits `000` and never `111`. In the other, it visits `111` and never `000`. In both it returns to the same full source state, `001001`, with the same upper pair `01`. In each history `y` finishes switching on after the source has returned. Now propose the identical upper change from `01` to `00`. It succeeds with the mark and fails at the original clear state. The upper knot sees only `y`. Replacing that shared distinction with an independent one removes the dependence on the memory. [Autonomous system and both histories](../../artifacts/SIX-BIT-EVENT-20261111-001/SIX-BIT-EVENT-20261111-001-E001_raw_event/source.json)

## A single observation can be missed

For a timing test, present the same raw word for a fixed number of witness proposals. Then supply the same mixed word `001` and let the witness settle. This gives the limiting read probability under a fixed background, with no feedback about capture. Both clear starting states give the same numbers.

| Initial word | One proposal, then common background | 128 proposals, then common background |
| --- | ---: | ---: |
| Any mixed word | 0 | 0 |
| `000` | 1/26 (3.85%) | 94.40% |
| `111` | 1/14 (7.14%) | 99.95% |

At one proposal the bit is still clear immediately after the pulse. What the observation can do in that first step is open the pair. Later internal changes can finish the write. For any finite exposure, repeatedly proposing a blocked bit has positive probability, so there is always a chance to miss. A sustained event writes with probability one. So do infinitely many equal observations in any fixed stream independent of the proposals. From every unwritten core state at an equal observation there is a sequence of at most four proposed flips that captures, whatever the later inputs. One such opportunity succeeds with probability at least 1/1,296. For disjoint opportunities the conditional failure bound therefore tends to zero. This bound concerns the witness proposal clock. The autonomous fourteen-distinction case was checked separately. [Pulse results and controls](../../artifacts/SIX-BIT-EVENT-20261111-001/SIX-BIT-EVENT-20261111-001-E001_raw_event/result.json) · [Short capture paths](../../artifacts/SIX-BIT-EVENT-20261111-001/SIX-BIT-EVENT-20261111-001-E001_raw_event/polarity.json)

With reversible changes to `y`, a pulse can still leave a readable bit in the subsequent mixed background. During continued equal input the bit can change back. Removing any one input connection opens a path for a mixed word to produce a false mark. Reversing one input's sign changes which two words free the pair. These controls locate the event selectivity in the supplied connections and the persistence in the one-way dynamics.

## Can it remember which word?

A [separately specified test](secondary_plan.md) replaced the constant preference with a local rule allowing `y` to change only toward the value opposite the current `a`. Its input is one internal distinction. Now sustained `000` leaves `y=0` and sustained `111` leaves `y=1` with probability one. Each reading survives every subsequent sequence of mixed inputs after settling. A later sustained all-equal word overwrites it in either order. Starting with the opposite reading, after 64 proposals the chance of a stable correct reading is 97.32% for either word. The fresh knot reads either value through the same two equal queries. This alternative can distinguish the two polarities. One bit by itself cannot also distinguish “nothing seen yet” from an event matching the initial value.

Holding the last unanimous value is familiar in asynchronous logic as the behavior of a Muller C-element. This model has a stochastic response time. The result here concerns how the six distinctions and the declared local connections realize the behavior. [Oxford technical report, section on the Muller C-element](https://www.cs.ox.ac.uk/files/3308/PRG39.pdf)

The witness can thus carry evidence of an observation to another knot. A clear bit after a finite run gives no proof that the source forbids either word. How a base would acquire the three connections or the directional rule from experience remains open.

## Reproduce the test

The [frozen contract](../../experiments/SIX-BIT-EVENT-20261111-001/SIX-BIT-EVENT-20261111-001-E001_raw_event/contract.json) gives the primary inputs, update rule, controls and timing assumptions. The exact probability enumeration covers 512 pulse cases at nine durations. The polarity calculation and the autonomous input calculation are additional finite tests. The [verification record](../../artifacts/SIX-BIT-EVENT-20261111-001/SIX-BIT-EVENT-20261111-001-E001_raw_event/verification.json) gives the scope of the separate same-task checks.

```bash
ticket=SIX-BIT-EVENT-20261111-001
family=${ticket}-E001_raw_event
run_dir=$(mktemp -d)
python3 -B "experiments/$ticket/$family/run.py" --output "$run_dir/result.json"
python3 -B "research/$ticket/polarity.py" --output "$run_dir/polarity.json"
python3 -B "research/$ticket/source.py" --output "$run_dir/source.json"
python3 -B "research/$ticket/verify.py" --producer "$run_dir/result.json"
python3 -B "research/$ticket/verify_polarity.py" --record "$run_dir/polarity.json"
python3 -B "research/$ticket/verify_source.py" --source "$run_dir/source.json"
```
