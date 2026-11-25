# What the record holds on handing a value on: survey for MADE-COPIER-20261125-001

Written 2026-11-24 by a helper for the study, before its runs: the owner's step 2 ("Check the record
first"). Read-only survey of the repository as it stood that day; nothing in it was edited. "Line n" cites a file as it
stands. Every result cited is **computed or argued, scientific referee pending**, unless marked otherwise. Words are the
glossary's and those of [the fold study's definitions](../PARTS-MEET-AGAIN-20261124-001/definitions.md) ("FD") and of
[this study's definitions](definitions.md) ("D"); "shared" means held by two or more knots, and the number of holders is
given wherever it matters. "Tied" is the glossary's (equal in every allowed state, or unequal in every allowed state).
**Loose** keeps the shared definitions' meaning (one holder); the glossary's "open" (free on its own) is not used for it.
The checks marked "this survey" were run in the drafter's scratch folder (`sB_record_checks.py`, `t_ties.py`,
`v3_checks.py`), unreviewed; the structures they used are registered in
[record_structures.json](../MADE-COPIER-20261125-001A/record_structures.json). Versions 1 and 2 of this survey are filed
in the advisor folder as sent.

## The answer to step 2, in two sentences

**Parity**: with at most two holders, two loose distinctions tied to each other are the only loose distinctions of their
connected structure, so two usable loose places for one value, in a connected structure that has any other loose
distinction (usable or barred), need a distinction with a third holder. (With no other, four knots suffice:
`{f1, a, b}`, `{a, b, v}`, `{v, c, d}`, `{c, d, f2}` tie f1, v and f2, f1 and f2 the only loose distinctions, every knot
passing under parity; checked by this survey.) **Not-all-equal**:
with at most two holders nothing is tied at all, and when every birth receives a fresh distinction, growth from a start
with no tie never ties a made distinction to anything, third holders or not (section 2.1).

In every values case the prototype found (the one under a stated rule, its run with the second pattern barred, and the
33 registered take lists: 35 in all), the place v had one holder (21 cases) or two (14) after round s and from 2 to 11
holders at the round read (three or more in 24), and the structure read had at least six distinctions with three or more
holders.

## 1. The note's two claims, checked

The note is `research/THIRD-HOLDER-20261123-001/third_holder_moves.md` ("One argument, one small check and a reading of
the record. Scientific referee pending", lines 3–4).

### 1.1 Parity, every distinction with at most two holders: a value is handed on once — confirmed, with one precision

**The note** (lines 13–25): take a connected part of parity knots, every distinction with one or two holders; an end is
a distinction with one holder inside the part. By the bond-closure criterion
(`research/BOND-CLOSURE-20261120-001/criterion.md` line 11, "A cut containing only loose distinctions must include
every loose distinction, since H is connected"; that study is "Proof and bounded experiment. Independent program
referee pending", its decision line 3), the ends satisfy exactly one rule, their total parity. So a part with exactly
two ends ties them; a part with three or more ends ties no two of them; "it cannot take a loose value and hand it to
two users".

**Confirmed, by the same argument, in the form the study needs.** With at most two holders the allowed states are the
cycle space of the graph (the literature's word) whose vertices are the knots and one outside vertex, and whose edges
are the distinctions (a loose one joined to the outside). So:
- two distinctions are tied exactly when they form a cut of two (neither alone a cut); every parity tie is an equality,
  since the all-zero state is allowed;
- two **loose** distinctions of a connected structure are tied only when they are its only two loose distinctions (a
  cut made only of loose edges is the whole set of loose edges, the criterion's line 11);
- hence, in a connected structure with three or more loose distinctions, **no value is at two loose places**.

**The precision.** "Ties no two of its ends" holds for the part taken alone (outside holders read as loose). In the whole
structure the outside can tie two ends of a part, and a value can sit at three or more places, but at most two of them
loose: pieces joined one to the next carry one value through every shared distinction between them. Example found by
this survey: knots `[[4,5,9],[3,6,8],[0,4,5],[1,2,10],[1,7,9,10],[3,6,7,8]]` tie `{0, 2, 9}`: 0 and 2 loose (the
structure's only two loose distinctions), 9 shared. This does not change the note's conclusion; it says where a value
can sit.

**Direct check (this survey; computed).** 3,659 drawn connected structures of 2 to 9 knots of 3 to 5 places, two
holders at most (seed 2026112501): no tie class with three loose members; no two loose distinctions tied while a third
loose distinction exists; on 14,459 connected parts taken alone (of 14,636 drawn; the rest had a frozen distinction or
fewer than two ends), every part with exactly two ends ties them (292) and none with three or more ends ties two
(14,167). Tie classes with three or more members: 2 (each with two loose members, as above). The tie test agrees with
brute force on 800 drawn structures under both knot laws (`t_ties.py`).

Evidence class: proved by hand (a cut argument resting on the bond-closure criterion, referee pending), checked by
computation.

### 1.2 Not-all-equal can hand one value to three places, with a third holder — confirmed, and the statement for two holders is stronger

**The note** (lines 27–35): the Fano pattern less one knot ties that knot's three distinctions; those three have two
holders each and the other four have three. Checked by this survey: for each of the seven knots left out, the left-out
knot's three distinctions are tied, with holders as stated; every one of the six knots passes the knot test in that
structure; and **none of the seven distinctions is loose**: the three places that carry the value are all shared. So the
Fano piece puts one value at three places, but at no loose place; a value handed on from it would need a further holder
on one of the three.

**Stronger for two holders, and already in the record.** The note says that with two holders a not-all-equal structure
always allows a word (B265) and "no copy made of them has been found". The record has more:
`research/READS-HOLDERS-SOURCES-20261120-001A/details.md` line 89, "All-size obstruction under the precise tie
definition": with not-all-equal on any finite holding, every knot of three or more places and at most two holders per
distinction, **every single distinction can change while every other value stays fixed** (an Euler-tour colouring
argument, after `research/NAE-GROWTH-20261119-001/nae_growth.md`; that study's results line 9: referee pending). So no
two distinctions are ever tied, and not-all-equal needs a third holder to tie anything at all. Checked by this survey
(computed): no tie in all 80,811 labelled structures of one to three knots of three or four places, nor in 3,690 drawn
connected structures of 2 to 9 knots (each tie claim confirmed or refuted by a solver).

Evidence class: the Fano tie is proved (the nesting study, `research/SUBST-NEST-20261112-001/subst_nest.md` lines 50–52
and 61, proved by hand, refereed by R1 with fixes, lines 92–101) and checked by the note's script; the two-holder
statement is proved in the record (argument, referee pending) and checked here.

## 2. What this implies for "pasting a value" (the owner's words)

Write **a made distinction tied to v** for a distinction made after round s and tied to an older distinction v, v
still free. "Two of v" in values: two such distinctions, both usable and **loose** at the same round read. A birth
**hands v on** (the note's phrase) when one of its fresh distinctions is tied to v; the owner's "paste" is kept in his
words.

### 2.1 A lemma that covers every law in which every birth receives a fresh distinction

**Ties are decided at birth.** The fold definitions (section 7, lines 271–274) record that under not-all-equal with a
ration that gives every birth a fresh distinction (ORD, CAP-k, FLOOR1, RATION-k) every round extends, and a knot's
relation on its places never changes after its birth. The same holds under parity with the IMPLIED closing (a birth
with a fresh distinction adds a row with a column of its own; a birth with none adds a row already in the span), and in
both cases whether or not any knot passes; several births taking one shared distinction change nothing, since each
closes on its own fresh distinction. It excludes LITERAL, FLOOR0 and ONE-FEWER. Since adding knots never adds states,
**the allowed states restricted to the distinctions that exist after round t never change after round t**. So whether
two distinctions are tied is settled at the round the younger is made, and no later meeting can tie or untie them.
(Argued here; it uses nothing about holders, so it holds for every taking rule of the fold study's ladder.)

**Not-all-equal: when a made distinction is tied (argued; checked).** Under a law in which every birth receives a fresh
distinction, a fresh distinction f of a birth u is tied to another distinction **exactly when u has one fresh
distinction and its inputs are all tied equal before its round**; f is then tied unequal to each input. (If u has two
or more fresh distinctions, or its inputs are not constant in every allowed state, there are two allowed states
differing only in f: flip f in a state where u's other places are not constant; at u's round only u holds f.) A knot
whose inputs are constrained together without being all forced equal fails the knot test and still ties nothing. By
induction with the lemma: **from a start with no tie, no made distinction is ever tied to another, under any taking rule
and any choice, whether or not knots pass.** "Any start" is wrong: the Fano pattern less the knot {2, 4, 5} ties 2, 4 and
5; add start knots {7, 2, 4} and {8, 4, 5}; then 7 and 8 are equal in every allowed state, and a join that takes 7 and 8
receives one fresh distinction tied to 7 (checked; the two added start knots fail the knot test). The registered designs
have at most two holders per distinction, so by the record's two-holder fact (section 1.2) they have no tie; the starts
with a third pattern, in which e has three holders, have none at round 0 either (this survey, computed for all 60, both
knot laws). Checked by this survey's prototype: no tie class containing a made distinction in 480 not-all-equal runs
(2,860 structures: Q, MET, STEPS-1, STEPS-2, five base laws, four choices, six starts) and 240 histories with every take
drawn; and none in the first test's 792 not-all-equal runs or in version 1's 213 pairs. The only way out on a tie-free start is a birth with no fresh
distinction (FLOOR0, ONE-FEWER).

**Parity: a birth hands on the parity of what it takes (argued here; checked).** Under parity with IMPLIED a birth with
two or more fresh distinctions hands nothing on (without IMPLIED two of its fresh distinctions could be tied to each
other). A birth u with exactly one fresh distinction f has x_f = the sum of its inputs in every allowed state, so **f is
tied to v exactly when the sum, over the field of two elements, of u's inputs and v lies in the span of the rules before
its round, zero included**. If v is itself an input, the other inputs sum to a rule and u fails the knot test, so a
passing maker of a distinction tied to v never holds v. (For v made in the same round the clause holds only when v's
maker also has one fresh distinction; the values reading never needs it, since v exists after round s.) Under FLOOR1
with the fresh count by distinct inputs (A235), a join receives one fresh distinction, and so does every offshoot that
takes a shared distinction. Under MET (and STEPS-1) every offshoot of a knot that is not a start knot takes one (its
parent q holds exactly one place of its own parent g; g's other places are shared, hence eligible and not held by q), so
**every birth other than an offshoot of a start knot hands a value on**: the parity of its inputs. Which value is set by
what it takes, that is by the choice.

### 2.2 What changes under the fold study's laws, which give three or more holders

- **Under parity, a third holder is now made where a value would need it.** The note's own diagnosis was that "sending
  one value to two places" needs a birth that takes a distinction already held twice (lines 48–50: "No recorded growth
  move gives a third holder to a value that is not already tied"). Under MET every taking offshoot is such a birth, and
  a value can be tied at two loose places. Smallest structure by hand: knots `{v, p, q}`, `{p, q, c1}`, `{p, q, c2}`.
  Then c1 = p + q = v and c2 = v: one value at three loose places (v, c1, c2), with p and q held three times; every knot
  passes under parity (checked). Under not-all-equal the same three knots tie nothing (checked).
- **In growth, under MET, seen (prototype):** on the two-knot start under COPY-LAW(CANCEL-OFFSHOOT) (the fold study's name
  for (FLOOR1, CANCEL-OFFSHOOT, RELEASE), not a law of copying) with MET(NEWEST), parity, after round 3 the start's
  shared distinction 0 (four holders) is tied to the fresh distinctions 22 and 24 of two round-3 offshoots, one descended
  from each start knot: one value at two loose places, made by births. The births before each of the two took the other
  places of their ancestors again (22 = 16 + 7 = (8 + 1) + 7 = 2 + 1 = 0, by the rows of knots 3 and 0). Without a taking
  rule the same prototype found only ties of the kind 1.1 allows (one value handed on, birth by birth, to one loose
  place).
- **Under not-all-equal nothing changes on a tie-free start:** the statement of 2.1 holds with any number of holders. The
  third holders that the taking laws make never tie a made distinction there. A tie in the start can be handed on (the
  Fano counterexample).

So: **under parity a value can be handed on to two loose places, by births with one fresh distinction whose inputs close
a rule; under not-all-equal, from a tie-free start, no made distinction is ever tied to another.** The owner's question,
in values, is therefore unsettled only under parity, and there it is a question about the choice.

## 3. Is anything in the record already a made pattern that leaves two of what it met?

No, in none of the three readings (form, built structure, values; see [the claim](claim.md)).

| Record | What it has | Two of what it met? |
| --- | --- | --- |
| `COPYING-PARTS-20261123-001` (decision lines 13–15, 53) | a two-knot part becomes two of the same every two rounds under added rations; the copies never meet again | No: it takes no input; what it makes two of is itself (form). |
| `COPIES-AND-MEETINGS-20261120-001` (decision lines 15, 19) | proved: a finite start cannot keep releasing independent copies of one fixed finite product (in the reconstructible class); one product changes another's child's fresh count (33 against 34) | No: the effect is on a count; nothing of the other product is copied. |
| `GENERATORS-20261120-001` (decision lines 5–13) | ordinary growth releases packets; two packets make a shared child (18 against 15 fresh distinctions); a packet can be a source | No: a source copies nothing it meets; the shared child is joint, not a copy. |
| `STORED-BIT-AND-NEXT-ACTION-20261122-001` (decision lines 13–25) | under parity a single stored value cannot change alone (0 of 64); with two marks the receiver's fresh pair must switch parity; under not-all-equal the stored value changes the receiver's allowed fresh words | Handing a value on once, under parity (the receiver's pair carries it); no value at two loose places, and no birth acts on it. |
| `PARTS-MEET-AGAIN-20261124-001` (results lines 92–102) | 72 confirmed cases with a joint birth; "in none does the course depend on what the other part is" | No: what the course follows is one value, whether the other part is there. |
| `SUBST-NEST-20261112-001` (lines 35–52) | a block substituted for every distinction ties a part across the whole pattern; the Fano gadget ties its terminals | A value at every copy of a block, but in a pattern built by substitution, not grown, and with no second pattern. |
| `THIRD-HOLDER-20261123-001` (note lines 27–46) | the Fano piece ties three places; built patterns with three or six holders | Built, not grown; the tied places are all shared. |

## 4. What the record does not have

- A taking law has never been run with the question "does anything of the other part appear twice". The fold study's
  fourth mark (the course differs with what the other is) was asked on 16 pairs and never held (results line 38).
- No study has asked whether the two-knot part still copies itself under a taking law. This survey's prototype finds it
  does not (the claim, section 5, and the pre-registration's disclosure).
