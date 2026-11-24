# Parts that copy themselves: what stands

Epic `COPYING-PARTS-20261123-001` (direction 1 of `RING-IN-BALANCE-20261123-001`; goals G18 with G17), closed 2026-11-23.
One frozen study, computed, scientific referee pending. [Ticket A: result](../COPYING-PARTS-20261123-001A/results.md) ·
[pre-registration](../COPYING-PARTS-20261123-001A/preregistration.md) · [referee hand-off](referee_handoff.md) ·
[advisor review before the freeze](advisor/README.md) · [the thread's side checks](checks/)

## The answer

The owner asked whether the growth has structures that make other structures, like cells that reproduce. Under rules added by
hand it does, in the simplest form found so far.

1. **The copier.** Two knots that hold two usable loose distinctions each and can join through one knot. Under three rations
   that give a new knot just enough for three places, they join; the join receives one distinction where two will be asked of
   it, so it is short and its joins are cancelled; and each of the two offshoots releases two offshoots of its own. One part
   has become two of the same.
2. **How fast.** By what the short join then does. It retires: the copies double every two rounds. It makes an offshoot: one
   more copy a round later, and the count grows by the golden ratio a round (on the ring of five, five times the Fibonacci
   numbers). It waits: one more copy two rounds later, and the counts from one copier are the Pell numbers.
3. **Every knot is a knot on the small starts**, under parity (by argument and 57,171 verdicts) and under not-all-equal
   (19,113 verdicts). Under the ration that always gives a fresh distinction no knot fails in any of 3,344 starts of up to five
   knots; under the two rations that can give a join of three parents nothing, knots do fail, exactly in the rounds where that
   happens.
4. **It is common under these laws.** A part copies itself in 85 to 97 of every hundred starts of up to five knots, each start
   counted once, depending on the treatment.
5. **What it needs.** A join that receives less than it is asked, offshoots that receive more than they are asked, and a
   treatment that cancels the short join's groups. It needs neither waiting nor the release rule. With the ordinary count, a
   cap of two or three, or a fixed ration of two, nothing copies in this way; a fixed ration of three has a larger copier of
   five knots that copies itself every round, and a fixed ration of four has parts of seven and nine that turn into one another.
6. **What stops it.** The fillers rule stops everything within three rounds. Removing offshoots stops it at once.

Ten predictions and a gate were frozen. Nine predictions and the gate hold. One hand prediction holds for two treatments and
fails for the third: with knots holding instead of releasing, and the short join waiting, nothing copies and the growth jams.

## Scaffolds, and what survived their swaps

| Scaffold | Swapped for | Survived? |
| --- | --- | --- |
| The ration (A224) | FLOOR0, FLOOR1, ONE-FEWER give the same copier; the ordinary count, caps and a fixed two give none; a fixed three and four give other copiers | The two-knot copier is specific to a ration that gives a join one. |
| The treatment (A224) | retiring, offshoots, waiting | Yes: all three copy, at three different rates. |
| The release rule (A224) | holding | Yes with retiring and offshoots; no with waiting. |
| Offshoots | none | No. |
| The fillers | added | No: everything stops. |
| Parity | not-all-equal | Yes on the small starts. |
| The start | two small starts, the ring of five, 3,344 starts of up to five knots | Yes: common under that census's weighting. |
| The complete round (A104) | not swapped | By the earlier study's argument the copies act alone, so rounds part by part would give the same; not run here. |

This is a result about rations and treatments added by hand, not about ordinary growth, under which a join receives what it is
asked and no part comes apart.

## What it does not show

The copies never meet again, so they cannot combine or read one another: the laws rule it out. Nothing reads the count of
copies; the one who runs the growth counts them. No claim is made about living things.

## Limits

Finite and computed: three named starts to 20,000 knots, 3,344 starts for ten rounds. The recurrences for every round are an
argument, written out for the referee. The census counts are lower bounds. One engine; the thread's side checks use the
pilot's program, which has no distinctions in it, and agree on every count compared.
