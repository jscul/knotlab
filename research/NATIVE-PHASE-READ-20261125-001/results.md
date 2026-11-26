# Can a parity knot supply a phase-sensitive measurement?

One parity knot can store a distinction that behaves like a phase label in repeated one-reader measurements. Its four ordinary states also impose a sharp limit. No update on those states can perform the calibrated quantum quarter turn on the six preparations tested here. For three readers, the program's first growth step supplies usable memory. The full quantum correlation table appears when we give the readers a particular rule for sharing and changing that memory. Growth supplies three equivalent storage choices. The passing device gives all three readers access to one writable bit. It therefore breaks the November 23 Bell study’s restriction against handing the same value to two users.

The ordinary devices in this study use bits, allowed changes and explicit sampling weights. The quantum predictions specify what a device would have to reproduce. Some control rules were chosen or searched for with those predictions in view. Their agreement measures what can be encoded. [Frozen design](preregistration.md) · [Subsequent sensitivity tests](sensitivity.md)

## What the three readers have to reproduce

The allowed words of one knot are 000, 011, 101 and 110. Each has even parity, meaning an even number of ones. Every two bits are unconstrained when the third is forgotten. The relation passes the program's K1–K3 test. Give each word probability 1/4 and choose each reader's setting independently. In the earlier Greenberger–Horne–Zeilinger (GHZ) comparison, each of the three readers chooses an ordinary value read, Z, or a phase-sensitive read, Y. With zero Y choices the three answers have even parity. With two they have odd parity. Each of the four words of the required parity has probability 1/4. With one or three Y choices all eight words have probability 1/8. We test the same eight settings in each of the six orders of the readers. [Earlier comparison](../FOUR-SETTINGS-PARITY-20261125-001/results.md) · [Mermin's three-reader experiment](https://physics.umd.edu/courses/Phys622/bedaque/mermin.pdf)

| Ordinary device | Three-reader result | What the result depends on |
| --- | --- | --- |
| Four words, Z leaves the state unchanged, Y can change the whole word | Perfect scored parities impossible in all orders | The word is the only writable state shared between readers |
| Different readout with a fixed order | Four of four scored tables in ABC, one in CAB | The outcome depends on which reader acts first |
| First growth round, each reader uses its own new bit | One of four scored tables in every order | The three new bits are independent given the root word |
| First growth round, every reader uses one common new bit | All 384 probabilities agree | An immediate second Y read always reverses the answer |
| Four words, Z can write, plus one independent common random bit | All 384 probabilities agree | Three of the six individual instruments reverse on repetition |
| Four words, Z can write, plus a stored copy of the initial word and a common random bit | All 384 probabilities and both specified repeat tests agree | Reader rules can consult a preparation-specific reference |

## What one undisturbing read implies

Let reader K use Z while I and J use Y. Begin from a particular word $w$. Reader I can report any bit $u$ and change the word to any allowed word $w'$, even irreversibly or at random. Reader J then reports $v$ from $w'$. Compare orders KIJ and IKJ. Since K reads without leaving a trace, exactly the same I and J branches are possible in both. Perfect odd parity requires

```text
w[K]  XOR u XOR v = 1
w'[K] XOR u XOR v = 1
```

Consequently I must leave K's bit unchanged. Either of the other two readers could have been K, so I must preserve both of their bits. Even parity then fixes I's bit as well. This applies to each reachable positive-probability transition, including conditional on static shared randomness. With all writes idle, the original word and setting-independent random choices can be fixed in advance. Each reader then has one answer for each of its two settings. Across the four scored parity conditions each preassigned answer occurs twice, while the target contains three odd parities. At least one condition fails. The conclusion rules out perfection for the declared model. The familiar 3/4 winning bound applies to preassigned answers. The order argument does not assign that numerical bound to every imperfect state-changing device. [Argument checks](verify_phase.py)

A narrower exact census lets each Y reader report its own current bit or its complement and apply any permutation of the four words. Among 110,592 triples of such rules, the best worst-order score was three complete scored tables, attained by 102 triples. A broader readout can pass all four in one order. For A/B/C, one such device passes 4, 2, 2, 3, 1 and 1 tables in ABC, ACB, BAC, BCA, CAB and CBA order. The census counts whole probability tables, with their zero entries. [Census and explicit devices](../../artifacts/NATIVE-PHASE-READ-20261125-001/NATIVE-PHASE-READ-20261125-001-E001_sequential_readings/results.json)

## What growth actually supplies

One round of the program's ordinary fewest-funded growth preserves the root ABC and adds three knots with holdings $(A,f_A,g_A)$, $(B,f_B,g_B)$ and $(C,f_C,g_C)$. Both the archived implementation and an independent reconstruction give these holdings. Each added relation has even parity. Of the 32 possible full states, eight extend each original word. On those eight, the triple of fresh bits $(f_A,f_B,f_C)$ takes each value once. Thus under uniform extension each new bit is fair and the three are independent even after the root word is known. Every permutation of A, B and C extends to a permutation of the three new holdings. [Growth replay](verify_growth.py)

At setting Z return the root bit. At Y return that bit XOR the chosen fresh bit, then flip both fresh bits in its holding. The pair flip preserves every knot. If each reader uses its own holding, all three scored settings with two Y choices fail. If every reader uses the same holding, all 384 probabilities agree. With two Y choices the two reads of the common bit have opposite values, so they reverse the original even parity exactly once. With an odd number of Y choices its fair initial value makes the final parity fair. Uniform sampling of the root word provides uniformity within each parity class.

Preparing the common bit at zero preserves the four scored tables and loses the other four. Leaving a fair common bit untouched loses all three nonzero scored tables. Calling the toggling Y reader twice in succession gives opposite answers on every trial. An ideal projective Y measurement repeated on its own output gives the same answer. The common-bit device also lets the readers communicate through writable state during a trial. The ability to store a bit comes from growth. Choosing one holding, granting all three readers access and implementing the read-and-toggle remain supplied rules. [Local and common memory tests](verify_growth.py)

The November 23 Bell test makes the difference in access precise. Its two sides used local records, with every present allowed word equally weighted and each complete local record hiding the other side’s setting. With one shared binary distinction the study proved the CHSH ceiling of 2. With two shared distinctions, the ceiling of 2 held throughout the tested two-holder classes. Its 20/9 comparison required one value to serve two users while its distinction was still needed for a birth. A value shared before the settings can enter the one-distinction proof as common randomness. Here successive readers can read and change the same bit during one trial. An earlier choice can therefore change what a later reader receives. The three-reader agreement is a result about shared writable memory. [November 23 Bell study, lead C](../REVIEW-LEADS-20261123-001C/result.md)

## When even the ordinary read is allowed to write

Dropping that single condition gives a second passing device. Let $r$ be a common fair bit independent of the uniformly prepared word $ABC$. Return each answer before applying the indicated XOR change to the word. Each change preserves ordinary even parity.

| Reader | Z answer | Z change | Y answer | Y change |
| --- | --- | --- | --- | --- |
| A | A | 110 | 1 XOR r | 000 |
| B | B | 101 | 1 XOR r XOR C | 011 |
| C | C | 011 | r XOR B | 101 |

This device reproduces all 384 probabilities. Without the shared random sign it still wins every scored parity test, but matches only 12 of 24 full scored tables and none of the 24 unscored tables. An immediate repeat reverses the answers of A on Z, B on Y and C on Z. [Exact replay](verify_disturbing_reads.py)

We then allowed **every** deterministic four-word state update, including irreversible ones, and any Y answer depending on the current word. Z still reports its own current bit. Requiring the four promised parities with certainty in all orders and perfect immediate repetition of both settings is infeasible when all four starting words occur for a fixed random seed. The finite encoding uses 96 transition variables, 12 answer variables and 2,652 distinct clauses. Two solvers independently returned infeasible. Requiring those parities on any three starting words already suffices. Every two-word subset admits a rule if repetition is imposed on all four words. For stochastic rules with no hidden evolving state, choosing one positive-probability branch per input preserves requirements that must hold with certainty. This gives the same exclusion under the stated support condition. [Encoding and checks](verify_disturbing_reads.py)

The support condition matters. Grant a reader a read-only copy of the initial word and an independent common fair sign. It can now interpret the four mutable states relative to that copy, so each fixed preparation reference needs only one starting word. One such device passes all the tables and immediate repeats, then fails when another reader acts between two reads. A second explicit device passes even that holdout. We verified all 384 table cells, 48 immediate-repeat trials and 192 trials with one other reader interposed from the specified initial preparation. The checker includes a fixed device and verifies it directly in addition to solving for a device. Both incorporate readouts tailored to the target and a preparation record available to all readers. Longer histories and other preparations are outside that finite comparison. [Devices and sequence checks](verify_disturbing_reads.py) · [Classical memory in sequential quantum tests](https://arxiv.org/abs/1007.3650)

## Can one reader detect a phase?

Give the three bits the roles Z, X and Y for a **single** reader. These are three questions about one system. Prepare any one bit at either value, weighting its two allowed words equally. A reader reports the requested bit, then either flips the other two together or leaves them alone with equal probabilities. Each update is lawful. Repeating the read gives the same answer. Either of the other questions gives a fair answer and leaves the instrument in the corresponding new two-word preparation. Checking each of the 30 possible one-step conditional distributions proves closure and hence the statistics of every finite adaptive sequence of these three readings on the six preparations. Two preparations with opposite Y labels give the same separate Z and X statistics and can be distinguished perfectly by Y. Their full distributions on ordinary words differ. This realizes the familiar restricted toy-bit example. [One-reader checks](verify_phase.py) · [Spekkens's toy theory](https://arxiv.org/abs/quant-ph/0401052)

A quantum quarter turn about a fixed Z reference is a sharper calibration. Write the three values as signs $z,x,y$. Every allowed word has $zxy=+1$. The required action $(z,x,y)\mapsto(z,-y,x)$ has product −1 on every input. Each word occurs in three of the six equally weighted preparations. On any proposed output, at most two of the three required signs can be right. Randomizing the output cannot improve that bound. Swapping X and Y attains **2/3** average success, against **1** for the calibrated quantum pulse. All 256 deterministic maps on the four words agree with that bound. A fourth distinction $h$ with $zxyh=+1$ allows the pulse by also reversing $h$. This changes which ordinary states and readings are available.

Lawful changes can already give a weaker directional signal. In bit notation $F(a,b,c)=(b,1-a,1-c)$ uses a two-bit change on every word and has order four. On the preparation with $a=0$ and fair $b$, reading $b$ after $F$ gives one with certainty and after its inverse gives zero with certainty. Choosing fairly between the two directions gives probability 1/2. The read depends on the prepared reference and the choice of which permitted pair to flip. The phase groups of a toy bit and a stabilizer qubit differ in exactly the ability to perform an order-four change while keeping the specified reference fixed. [Quarter-turn checks](verify_phase.py) · [Coecke, Edwards and Spekkens](https://arxiv.org/abs/1003.5005)

Finally, a direct test of a relative phase needs two preparations. The quantum reference states $(|000\rangle+i|011\rangle)/\sqrt{2}$ and $(|000\rangle-i|011\rangle)/\sqrt{2}$ give exactly the same probabilities in **all 64 cells** of the original Z/Y panel. Read X at B and Y at C with a fixed calibration, and their sign product is certainly +1 for the first preparation and −1 for the second. We verified this using exact Gaussian-integer numerators. A common ordinary process acting on identical complete ordinary preparations must give identical output distributions. A logical account could still generate two different retained histories or references with the same plain-read statistics. The open step is to produce those preparations and the reading by the system's own rules and predict which sign will be reported. [Two-preparation comparison](verify_phase.py)

For the one-reader control, both fair choices matter. Starting with Z fixed, a 3:1 weighting of its two possible words changes the probability of one on a subsequent X read to 1/4. With Z initially zero, read X and then Z. Turning off the pair flip gives zero probability of one at the last read. The fair flip gives 1/2 and an unconditional flip gives one. [Weighting and disturbance checks](verify_phase.py)

Carroll begins with a quantum state and its unitary dynamics. The question here is whether a specified logical system can supply even one of the measurements used in that description. A decisive new result would give two preparations, a common reference and a rule for reading the sign before consulting the quantum answer. [Carroll, *Reality as a Vector in Hilbert Space*](https://arxiv.org/abs/2103.09780)

## Reproduce

From the repository root, run the frozen census and the three targeted checks.

```sh
study=NATIVE-PHASE-READ-20261125-001
python3 -B "artifacts/$study/${study}-E001_sequential_readings/check.py" --check
python3 -B "research/$study/verify_phase.py"
.venv/bin/python -B "research/$study/verify_disturbing_reads.py"
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -B "research/$study/verify_growth.py"
PYTHONPATH=tools python3 -B -m knotlab check --loops A B --contact C --cnf 'A B ~C; A ~B C; ~A B C; ~A ~B ~C'
```

The full reversible census took 0.29 seconds and 15.2 MiB on the study host. Its receipt reproduced byte for byte. All probabilities and failures above are exact for the specified rules. A267 records the alternative choices of accessible state. A268 records the one-reader calibration. This study sharpens the program's question about dynamics, G5. It leaves the source of a quantum phase reference open. [Assumptions register](../../docs/ASSUMPTIONS.md)

## Research position

| Scope | Verdict | Why |
| --- | --- | --- |
| Phase-sensitive reading on one knot | Partially successful | Repeatable one-reader statistics, sharp pulse limit |
| Bare four-word dynamics | Retire for this calibration | Best pulse succeeds on 2/3 |
| Grown preparations | Known alternatives | Growth produces memory, common access is supplied |
| G5, dynamics | Obstruction learned | A native phase reference is still missing |

**Next step:** Research directions — No next action selected.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Generate two phase preparations with a common reference | 3/3 — Barrier | 2/3 — Testable | Fix the preparation and readout → test the opposite signs | Alternative · deferred |

**STOP.** The four-state calibration is settled. The opposite-sign test is sharp, and a larger native preparation that commits to its readout would reopen the investigation. Another fitted table would leave that question open.

**Corrections:** The shared-bit comparison now identifies which access restriction in the November 23 Bell study the successful sequential device crosses.

**Goals:** G5, dynamics, gains a bounded obstruction. Its wording is unchanged.

**Assumptions:** A267 and A268 added as assumed. A152 gains a history entry and remains under challenge.

**Scaffolds:** We varied the fixed readout, preparation weights, disturbance, order, and access to memory. Common access or a copied preparation changes which tests an ordinary device passes.
