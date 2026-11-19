**(1) Yes.** It holds by construction: t is a function of the allowed states, so same-states rivals get identical tables (up to the same relabelling). The 72 rivals and 4,474 groups stay under this or any k-way circuit reading.

**(2) I'd bet on the 11, not on all 152.** A circuit reading sees only the supports of parity consequences, so it is blind to three things:
- **Non-parity content:** two state sets with the same parity closure read the same.
- **Signs:** x=y and x≠y have the same support. This is my main worry for the 152, since two-distinction consequences are exactly where a sign can differ with nothing else changing.
- **Differences first visible at four or more:** triple minima need not determine the circuit set.

The 11 look safe if the junctions are three-place parities. A trade or swap then changes which triples are 3-circuits, and a triple reads 2 exactly when it is one.

A cheap check before running: compare the circuit-support sets within each group. If they are identical, no k-way reading separates the group.

Also fix a "none" value before freezing. Three distinctions need not share any circuit, and if x,y are in a 2-circuit then every (x,y,z) reads none.

**(3) Sound, with conditions.** A circuit of size d+1 through the triple does put every inner pair and triple at ≤ d, so the filter is a valid necessary condition and a unique survivor is forced. This needs:
- candidates enumerated over all (d+1)-sets containing the triple, not only sets already known;
- exact readings.

It forces the support only, not the sign. One further sound filter is available: a candidate may not properly contain, or sit inside, an already forced circuit.