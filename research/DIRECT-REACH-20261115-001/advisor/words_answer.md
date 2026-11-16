Yes, I'd count "window" as spatial: it is an opening you look through, and the guide already uses it in exactly that sense ("every small window of the pattern looks consistent", lines 1629 and 1666). Using it for a fixed set of addresses would also give it a second meaning.

1. **Window → "block"** (a "level-n block": one orbit's addresses with their children). The glossary's Periodic entry already uses block for the unit of distinctions and knots that repeats, which is the role this set plays. For "a tree of windows", avoid "tree": say "blocks meet only at shared addresses, and no ring of blocks closes", or define a "parent block" relation and state that every block has exactly one. Check that "block" in the brace-tree records ("atoms are blocks") is not in the guide in a clashing sense; if it is, fall back to "orbit block".

2. **Automatic state → "finite-reader state"**, defined once as a state whose value at each address is output by a finite machine reading the address letter by letter, with "the literature's automatic sequence" given once. "Automatic" alone reads as "happens by itself" and sits too close to "automaton maps". If you would rather stay close to the literature, keep "automatic state"; it is not spatial, only slightly ambiguous.

3. **Chain of windows along a letter sequence → "descent of a block along a letter sequence"** (short: "a block's descent"), with "eventually periodic descent" when the letters are. Do not use "chain" here: the glossary's chain is rules in a row, each sharing one distinction with the next, and this is one block followed down the levels. "Eventually periodic" is safe, since it qualifies letters, not a base, but say "eventually periodic letters" in full. Give "orbital Schreier graph along a rational point" once as the literature's.

Keep: "level", "address", "orbit" (already marked as the literature's at line 2410) and "eventually periodic". Replace: "window", "tree of windows" and "chain of windows".

I checked only `INTUITIONS.md`: "descent" and "finite-reader" do not appear there, so both are free.
