**Verdict: the route looks clear to me, but not by compressing k.** The unbounded k comes from cutting the gadget horizontally at the window; cut it vertically, subtree by subtree, and k never appears. This is reasoning from your statement only, not checked against the repo or the census.

**(b) Yes, and this is the route I would take.**
- **Interface.** Because the skeleton is a tree, every subtree meets the rest through one orbit, with at most 16 states.
- **Summary.** For a subtree with member set M and interface state x, let R_x be the allowed member assignments after projecting out witnesses. For each assignment m, put X_m = {x : m ∈ R_x}. The summary is the *set* of realized X_m, a family of subsets of the interface states, so it is finite whatever |M| is.
- **Freeness.** Two parts glue to a free set iff every realized X above meets every realized X′ below (after the block's transfer).
- **Composition.** At a block step or branch point, the new family comes from the children's families alone.
- **The three conditions.** Track realized triples (X_m, X_m with level-k members forgotten, X_m with far members forgotten). Forgetting is a union over the forgotten coordinates, so the triples still compose.
- **Member-free side subtrees** contribute a single set, which is your saturation condition.

This gives a bottom-up tree automaton with a finite state set that handles all k at once.

**What remains is boundedness in s**, which is a limitedness question for that automaton with weight = number of members.
- **One far spine** (all level-(3+s) members below one long unbranched path): the spine is a word over (step composite, side-subtree state), and side subtrees get least weights by an ordinary fixpoint. Least weight at gap s is an entry of a min-plus matrix power, which is ultimately periodic-linear per residue. Bounded iff a zero-weight cycle of the right length lies on an accepting path. This reproves Theorem D's dichotomy and is total.
- **Several far members on synchronized spines:** iterate by height, w_{h+1} = F(w_h), with F a monotone min-plus polynomial of degree at most the block arity. Capping weights at c is a semiring homomorphism, which gives your semi-decision. Totality needs a bound on c, and there are two ways to get one:
  - Cite decidability of boundedness for alternating cost automata on finite words (Colcombet–Löding's regular cost functions). With bounded arity, total weight is bounded iff weight plus branchings is bounded along every path, so the sum form reduces to their max form. I am recalling this theorem from memory; check its exact statement before relying on it, and it would enter through evidence admission.
  - Prove it directly. That is essentially a Hashiguchi-style argument and not short.

**(a) Not locally, I think.** Two crossings of the same composite type and lower condition cannot simply be merged or dropped, because the upper profile can need both (an X_m covered only by their joint states). Any compression that works is the automaton pumping above, so I would not look for a separate Ramsey argument.

**(c) Yes, and it falls out for free.** The natural restricted theorem is the single-far-spine case, or far members with a common ancestor within bounded distance. A cheap first check is whether the least bonds in your 1,391 census patterns ever have far members on two long synchronized spines. If they never do, the restricted theorem covers everything observed.

**(d) Estimate.**
- Summary lemma, automaton and single-spine decision: a few days. The main risk is the bookkeeping for the triples at branch points.
- Full totality by citation: a few more days, mostly verifying that the cited theorem applies.
- Full totality self-contained: open-ended.

I would do the few-day version, state the synchronized case as conditional on the citation, and then move to growing orbits rather than grind on a direct limitedness proof.
