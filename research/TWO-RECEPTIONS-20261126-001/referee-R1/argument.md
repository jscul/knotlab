# What the shortage argument proves

**The argument holds for the not-all-equal law used in the census. The parity exception can make other newborns short.**

## All-birth condition and lifetime

Take any finite start and a completed round of the recorded growth with RELEASE. Suppose every birth, including an implied one, actually receives at least its demand. The demand roster contains all births and every old member that still holds a usable loose distinction. Steps for the recorded takes use only distinctions that were already shared before any birth. Fresh allocation gives each new distinction to one holder. It leaves all meetings unchanged.

Every birth with a positive fresh count is a member in the next round. If a birth receives zero, the hypothesis forces its demand to be zero. It has no joinable partner in the demand roster. Every joinable pair is either itself a group or belongs to a larger group. Removing a birth with demand zero from membership therefore leaves all other groups unchanged. Its holdings remain in the structure. Each newborn member owes its demand and holds at least that many usable loose distinctions.

A newborn that can pay gives one loose distinction to every kept group and the rest to one-parent births in that same round. This accounts for every usable loose distinction even when an old start member causes a cancellation. Its usable count becomes zero. Holders can only be added, barred distinctions stay barred, and ordinary growth fixes old knots' places. That newborn never becomes a member again. This completes the argument over its lifetime. Start knots may already be short and wait.

All births under the ordinary not-all-equal law receive at least one fresh distinction and at least their demand. The argument applies with each recorded take. [Growth rules, steps 1–7](../../RING-IN-BALANCE-20261123-001/definitions.md) · [Rules with taking, sections 1 and 2](../../PARTS-MEET-AGAIN-20261124-001/definitions.md)

## Parity counterexample

**Block on the extension to parity.** The note says “(Parity's implied births receive nothing and hold no usable distinction, so they are never members: outside the argument and harmless.)” In the engine, an implied birth enters the demand roster with a provisional holding of one. It receives zero fresh distinctions even when its own demand is positive. [Study note, lines 25–33](../README.md#L25) · [Round construction, lines 563–608](../../../experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot/eng.py#L563)

The explicit start in the check has eight knots. One distinction has three starting holders, permitted by the rules with taking. Each knot has at least three distinct places. Use ordinary count, parity, waiting, RELEASE, and the take of the oldest eligible distinction held by a knot the parent or parents meet. No start member is short. In round one two parents make a join on distinctions 10, 11 and 2. Its parity equation follows by adding the equations of the two parents and the knot they both meet. Four other births come from two parents holding two loose distinctions each.

All five births form one demand group. The join owes one provisionally, receives nothing and is absent from next-round membership. Each other birth received exactly one. An old knot meets all four remaining members. Their six pairs now form the groups, so **all four newborns owe three while holding one**. These shortages occur in unchanged growth. The same start, take and numbering under not-all-equal give all five births one fresh distinction. In round two they again form one group and all five pay.

Binary elimination followed by enumeration of every allowed assignment produced 256 joint states at the start and 256 after the five births. Each of the eight starting knots and each of the thirteen knots after the births projects to the full even-parity relation on its places. The distinct arities are three, four and five, with four, eight and sixteen allowed states respectively. Each projected relation passed K1, K2 and K3 in the canonical check. The first parity check took 0.002 seconds after imports in one process capped at 2 GiB. [Start and executable check](argument_witness.py) · [Growths and projection counts](argument_witnesses.jsonl) · [Canonical clauses and verdicts](argument_knot_checks.json)

The omitted birth has actual fresh count zero and demand one. This distinguishes the false extension to ordinary parity from the surviving conditional requiring **every actual birth** to receive its demand. This example checks the source of shortage. Whether that shortage carries a distant change was not run.

## Additions and hearing

**Narrowing to current members.** The note says “An added loose distinction raises what a knot holds and makes no sharing, so it makes no knot short either; a barred one can.” Adding a loose distinction to an existing member, as in the census, leaves its roster and all sharings unchanged. Its holding rises and every other member keeps the same owing and holdings. Subsequent unchanged rounds obey the same all-birth result. [Study note, lines 29–33](../README.md#L29)

Allow the addition to revive a spent knot and the conclusion changes. Start with the two knots holding `[0,1,2]` and `[0,3,4,5]`, under ordinary not-all-equal with no take. The second knot makes three one-parent births in the first round. Each holds two and owes two. After the round, give one loose distinction to the spent first start knot. It joins the next roster and meets the second start knot, which also meets all three births. Each birth now owes three while still holding two. Giving that same extra distinction to an already active birth leaves the three owing two apiece. [Paired calculation](argument_witnesses.jsonl)

**Block on the unrestricted hearing claim.** The decision says “Under the model's count a pattern's own knots cannot be reached after the start except by a removal”. Under ordinary not-all-equal with the local take of the oldest eligible distinction, adding a loose distinction to a sender member after round one changed the receiver's own round-two join. It received nine fresh distinctions without the addition and ten with it. No start knot or newborn was short in either run. An independent implementation and the engine agreed. This example uses a take and leaves the no-take case separate. [Decision, position table](../decision.md#L27) · [Hearing witness](check_hearing_witness.json)
