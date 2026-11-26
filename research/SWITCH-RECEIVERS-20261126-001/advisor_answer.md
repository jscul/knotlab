# The advisor's answer (26 November 2026)

To [the question](advisor_question.md), asked before the census of receivers was run.

**1. Two rounds per step, three under CAP-4.** Your formula is what I would derive from a counting picture, but I have not checked it against a trace. Suppose each pass along the line raises the link knots' owed count by one, and each turnaround at an end costs one round. Link knots start owed 2 and go short at k + 1, so that takes k − 1 passes and k − 2 turnarounds: (k − 1)d + (k − 2). This is consistent with the influence cone, at one step per round. Two cautions:
- Two caps fit any two-parameter form, so run CAP-5 at d = 2, 3 (predicted rounds 11 and 15, inside 16).
- Under CAP-4 the three passes must *start* at the far end and turn around at the receiver's own site. That would make the sender a source rather than a mirror, and may be why fewer senders work.

To test it, print the owed count of each link knot by round and look for a front that advances one knot per round and steps up by one at each turnaround.

**2. Why two loose and not three.** My guess is that the far site only turns the front around if it is itself tight. With three loose under CAP-3 it is owed 3 and holds 3, so it is never short and absorbs the front. With two loose it goes short once, its join with the line's last knot is cancelled, that knot makes an offshoot, and its demand rises by one. A stub has nothing to cancel. The one-loose path senders then fit as a tight knot one step deeper: 2(d + 1) + 1 = 2d + 3. If so, the same senders under CAP-4 should give 3(d + 1) + 2 = 3d + 5.

**3. The threshold.** "After 2d" is an echo time, not the cone bound. I would use three bands for the first-difference round r:
- **r < d:** impossible by the cone, so any hit is a bug check on the code.
- **d ≤ r ≤ 2d:** a one-way reading. Your definition drops these silently, so report them.
- **r > 2d:** an echo.

Define "switch" by behaviour (no own knot short before, short every other round after) and report r separately as a histogram of r − 2d_eff.

Controls that separate the far end from the line's own growth:
- **Longer line, no sender:** d + m link knots ending in nothing. The switch should not occur, or should move with line length.
- **Mid-run swap:** change the far site's loose count at round t₀. The receiver's births should change no earlier than t₀ + d. This measures the reading directly.
- **Common baseline:** compare every sender against the stub, not all ten pairs.

**4. Expected failures and gaps.**
- **Prediction (3) is the likeliest to fail.** With 3- and 4-knot receivers the tight knot can sit behind the site, so the site need not hold one loose.
- **Prediction (2) fails next, for the same reason.** Expect 2d + 5 and beyond, though always odd if the echo picture is right. An even round would refute the picture.
- **Prediction (1)** spans a factor of ten and can hardly fail, so narrow it.
- **Prediction (5), ORD:** "none reads" within 16 rounds is "not seen", not a negative.

Design gaps:
- **Round limit.** CAP-4 at d = 5 predicts round 17, past the 16-round limit, and deeper reflectors (2d + 5 = 15 at d = 5, 3d + 5) crowd it too. Extend to about 22 rounds for d ≥ 4, or mark those cells "not run".
- **Knot limit.** The 3,000-knot stop arrives at different rounds for different senders. Compare births only up to the last round both runs completed, and count censored pairs separately.
- **3d + 2 coverage.** It has been checked only where it fits inside 16 rounds (d ≤ 4), so say so.
- **Sender attachment.** Record which knot of each sender is joined, and its depth to the nearest tight knot, so d_eff can be computed before the run rather than fitted after.
- **Receiver as sender.** In this symmetric case, check that both ends switch in the same round.
