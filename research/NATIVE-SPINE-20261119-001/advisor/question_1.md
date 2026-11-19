# Question for the advisor (NATIVE-SPINE-20261119-001, before the freeze)

You have no tools. Answer only from this text, and say where you are unsure. Keep it short.

**Setting.** A parity growth in complete rounds; each junction born in round t has parents in round t − 1. In ten "eddy" starts the
round counts satisfy c(t) = c(t − 2) + c(t − 3) from round 4–6 on. The spine relation joins each junction j of round t to its
ancestors at exact depths 2 and 3, each with a number m(a, j) of parent chains. At every recurrent round it has a perfect matching
(Hopcroft–Karp), so every junction gets one partner two rounds on and one three rounds on: the Padovan substitution a → b → c → ab
made of parent chains. No set of up to 3 of the 10 most frequent "interval types" (unfolded chain shapes) makes it biregular.

**The bounded test (coordinator's bound: three rules).** For each j keep:
- N, "newest": its depth-2 ancestors;
- M, "most chains": its ancestors (either depth) of largest m(a, j);
- F, "fewest chains": those of smallest m(a, j).
A rule picks the spine at a round if what it keeps is a perfect matching of round t with rounds t − 2 and t − 3. Readout: is the
full relation's perfect matching unique (no alternating cycle)?

**Pilot on one start (rounds 4–13):** N keeps no single partner anywhere (it can't reach round t − 3, so it fails by count); M gives
11/26 … 82/323 junctions a single partner; F 3/26 … 17/323; the matching is never unique.

**Questions.**
1. Is this a fair test of the three rules, and is "fails by count" the right verdict for N? Is there a reading of "newest" that is
   native and not trivially refuted?
2. Predict the frozen outcome on all ten, and name one risky prediction.
3. A stronger, rule-free impossibility test I am considering only as a direction: an ancestry-invariant rule must commute with
   automorphisms of the ancestry, so if every perfect matching is moved by some automorphism (e.g. two junctions with the same
   parents and isomorphic futures), no native rule can pick one. Is that sound, and how would you make it checkable on a finite
   window without the window's edge creating fake symmetries?
