# A growth step can write an ordinary sign that small reads cannot see

Two preparations on the same grown knots give opposite signs with certainty. Both begin with the same blank state, apply the same ordinary change request and grow once. Only their order differs. After the same mixing procedure, any four ordinary marks in the five-knot experiment have exactly the same joint distribution in both preparations. A particular set of five reveals the sign. At seven knots, the corresponding threshold is seven. A fixed measuring device can also collect the sign at one physical mark.

The sign records a difference between the complete ordinary states. A quantum relative phase can distinguish preparations that agree on the probability of **every** ordinary word. We tested that stronger comparison separately. [Registered design before evaluation](https://github.com/jscul/knotlab/blob/1ec570a40e26cb37e53ece47ffab771f8ea50bbb/research/GROWN-OPPOSITE-READS-20261125-001/preregistration.md) · [Prior phase calibration](../NATIVE-PHASE-READ-20261125-001/results.md)

## What writes the sign

In each start, every knot holds four binary distinctions and requires an even number of ones. It shares one distinction with its predecessor and one with its successor. Its remaining two are private. A pulse flips a smallest lawful set containing one designated shared mark. Growth preserves the old values, spends the available private distinctions and adds new knots using the program's existing fewest-funded rule. After this first growth the originally shared marks can be identified from the current holdings alone. Each belongs to two knots that both have exhausted their private distinctions.

The readout was fixed as plus for an even number of occupied originally shared marks and minus for an odd number. Before growth, every shortest response through the designated mark flips **one** originally shared mark. After growth, every such response flips **two**. Starting from zero, an early pulse therefore writes minus and a late pulse writes plus. The sign is certain before mixing. It survives every tied shortest response, every lawful choice of the newborn values and every later first-stage shortest change. No history is accepted or discarded by its measured sign. Any known starting parity gives the same relative reversal between the arms. The published motion study had already identified the conserved parity and the two classes of grown words. The new test uses the order of two ordinary operations to prepare them. [Original conservation result](../READS-HOLDERS-SOURCES-20261120-001A/motion.md)

| Starting knots | Grown knots / marks | Pulse then grow | Grow then pulse | Final words in each mixed preparation | Minimum marks in a distinguishing ordinary read |
| --- | --- | --- | --- | ---: | ---: |
| 5 | 10 / 25 | −1 on every trial | +1 on every trial | 16,384 | 5 |
| 7 | 14 / 35 | −1 on every trial | +1 on every trial | 1,048,576 | 7 |

For example, in the five-knot fixture the original shared marks are 0 through 4. An early pulse at 0 can flip 0, 5 and 7. One growth extension then also occupies 15 and 19, leaving only 0 occupied among the five read marks. With growth first, one possible late pulse flips 0, 1, 5 and 9, leaving two of the five occupied. All five choices of address and every tied move were checked. Seven was the prespecified size check. [Five-knot words and moves](../../artifacts/GROWN-OPPOSITE-READS-20261125-001/GROWN-OPPOSITE-READS-20261125-001-E001_grown_preparations/results.json) · [Seven-knot and later-growth checks](../../artifacts/GROWN-OPPOSITE-READS-20261125-001/GROWN-OPPOSITE-READS-20261125-001-E001_grown_preparations/larger.json)

## Why ordinary small reads agree

After growth, the shortest changes connect **all** words of a given old parity. There are exactly two reachable classes. Thus any binary function of the word conserved by every shortest change is either constant or this parity, up to exchanging the names of its outcomes. The common mixing procedure offers each distinct shortest change once, applying it with an independent fair choice. Every reachable word receives equal weight because the map from the choices to the resulting change is linear and has equally many histories for each image. Equal possibilities for small reads follow from reachability alone. Equal probabilities use the stated mixing law.

There is an explicit pairing of the two preparations for every choice of fewer than five marks. For each originally shared mark, choose one of its holder's private marks at either end, using distinct ones at each holder. In each new knot pair its two inherited marks with its two fresh marks. This produces five disjoint lawful changes, each reversing the designated parity. Any proposed four-mark observation misses one whole change. Flipping it pairs every word in one preparation with an equally weighted word in the other while keeping the observation fixed. This applies to a joint read and to an adaptive sequence of nondisturbing reads using at most four distinct marks. Reading the five designated marks attains the bound. The same certificate has seven disjoint changes in the seven-knot system. This hiding of a bit in the choice of a class of binary words is familiar from classical linear codes. Here both the classes and the operations that prepare them come from the actual grown knot holdings. [Pairing certificates](verify_larger.py) · [Ozarow and Wyner](https://doi.org/10.1002/j.1538-7305.1984.tb00072.x)

The five-knot check covered all 15,276 subsets of up to four marks, including the empty set. Sixteen five-mark parity reads attain the minimum. At seven knots, 57 seven-mark parity reads attain it. Any two whole holdings agree at five, and any three agree at seven. Three and four suitably chosen whole holdings, respectively, suffice. Each holder meets at most two disjoint changes in the certificate, and the indicated numbers of old holders can cover all the originally shared marks.

## Can one physical mark report it?

Before decoding, a single mark is fair in both mixed preparations. Two more ordinary growth rounds produced no individual mark or whole holding that distinguished them. At five we reached 20 knots and 45 marks, and at seven we reached 28 knots and 63 marks. In fact all marks outside the original shared set can be inspected **together** without revealing the sign in these growth-only continuations. Flipping the whole original shared set maps one mixed preparation onto the other while fixing every such observation. Each old holder sees two flips and subsequent births spend only previously private marks. The same fresh extensions can be paired in both preparations. [Growth results](../../artifacts/GROWN-OPPOSITE-READS-20261125-001/GROWN-OPPOSITE-READS-20261125-001-E001_grown_preparations/larger.json)

We then implemented the **same** parity readout at the originally addressed mark. The supplementary design was fixed before its replay. Every occupied nonpointer old mark may apply an existing lawful shortest change that toggles itself and a neighboring old mark one step closer to the pointer, together with the two other distinctions required by the affected knots. This clears the sending mark. If the receiving mark was already occupied, the two cancel. The sum of the remaining steps to the pointer over all occupied old marks falls at every firing. Every completed schedule therefore ends with the old marks clear except possibly the pointer. Since each firing preserves their collective parity, the pointer gives the sign. It needs no initialization of its own and never receives a preparation label.

| Starting knots | Pointer choices × old patterns | Completed firing schedules checked | Most firings | Pointer after early / late pulse |
| --- | ---: | ---: | ---: | --- |
| 5 | 5 × 32 | 910 | 6 | 1 / 0 |
| 7 | 7 × 128 | 275,394 | 12 | 1 / 0 |

Each tested transition lifts to a lawful change from **every** full word with that old pattern. Reversing the order of the holdings and renaming every mark transfers the pointer and reproduces all outcomes and firing counts. Applying a fixed sequence of the same moves without consulting occupancy leaves the pointer fair in both mixed preparations. The successful detector supplies a designated receiver and an irreversible rule for enabling moves toward it. The sign was already written before this device acted. [Fixed pointer design](https://github.com/jscul/knotlab/blob/6d5f7532845472a33b10e455de2037d984324de5/research/GROWN-OPPOSITE-READS-20261125-001/pointer_design.md) · [Pointer replay](verify_pointer.py)

## Which choices matter

- **Mixing.** Without it the sign is still exact. For the designated five-knot address, six individual marks and eight whole holdings distinguish the raw preparations. If instead each tick chooses one shortest move uniformly and tosses a fair coin to apply it, the difference in the probability of one at a particular neighboring old mark decays by a factor of 14/15 per tick at five and 20/21 at seven. It survives every finite number of those ticks. The fair offer of every move gives exact equality in finite time.
- **Address.** Any originally shared address works. If the pulse instead chooses uniformly over the entire shortest-move menu, its early sign is minus with probability 4/5 and its late sign is always plus.
- **Reference and erasure.** Starting uniformly over all allowed source words gives identical complete distributions in the two arms under common fair mixing. Offering the lawful change of the whole originally shared set with probability 1/2 after mixing also makes the complete distributions identical. A reader given identical complete input laws and the same dynamics must return identical output laws.
- **Quantum benchmark.** Denote the normalized, uniform quantum vectors over the even and odd classes by E and O. The hypothetical vectors (E + iO)/√2 and (E − iO)/√2 give every ordinary word exactly the same probability. Our physical parity reader returns plus with probability 1/2 on both. In the quantum comparison, the observable that assigns the old-parity sign, exchanges the two classes and multiplies amplitudes by i has certain opposite eigenvalues. The ordinary growth, motion and pointer do not supply that amplitude operation. This is the distinction between recovering a bit distributed among ordinary states and recovering a relative phase between those states. [Benchmark calculation](verify_larger.py) · [Phase groups in classical and quantum models](https://arxiv.org/abs/1003.5005)

## Reproduce

Use the repository's existing Python environment. All counts are exact. The five-knot check expands the full word distribution. The independent checker uses the actual growth routine, binary ranks and disjoint moves at both sizes. The pointer checker verifies all firing orders by grouping transitions with the same remaining old pattern.

```sh
study=GROWN-OPPOSITE-READS-20261125-001
family="artifacts/$study/${study}-E001_grown_preparations"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
.venv/bin/python -B "$family/check.py" --check
.venv/bin/python -B "research/$study/verify_larger.py" | cmp - "$family/larger.json"
.venv/bin/python -B "research/$study/verify_pointer.py" | cmp - "$family/pointer.json"
```

## Research position

| Scope | Verdict | Why |
| --- | --- | --- |
| Opposite signs with matched small reads | Successful | Exact at both registered sizes |
| A pointer for the stored sign | Successful with supplied detector | Every enabled firing order agrees |
| Quantum relative phase | Unresolved | The two ordinary preparations have disjoint full-word supports |
| G5, dynamics | Capability gained | The order of two ordinary operations writes one conserved bit |

**Next step:** Research directions — No next action selected.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Find a native complementary phase read | 3/3 — Barrier | 1/3 — Stated | Specify its preparations and dynamics → test full-word equality and opposite signs | Alternative · deferred |

**STOP.** The local hiding and ordinary pointer questions have exact answers on the two tested systems. A mechanism with identical complete ordinary-value statistics and a complementary readout would reopen the quantum question. Additional ordinary parity encodings leave this distinction intact.

**Corrections:** None. The two grown classes and their conservation were known inputs.

**Goals:** G5, dynamics, gains an operational preparation and readout.

**Assumptions:** A269 and A270 added as assumed. A267 gains a history entry.

**Scaffolds:** Common known starting parity, the pulse address and order, fair mixing, and the pointer's conditional enabling rule. Changing the address among shared marks preserves the result. Changing the source, weighting or detector has the effects reported above.
