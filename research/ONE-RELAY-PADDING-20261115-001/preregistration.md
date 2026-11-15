# A linear cut scan with shared hidden padding

2026-11-15 (Pacific). Goals G3 and G16.

## The question

G3 and G16: after arbitrary reuse of the Boolean padding that used to make implication clauses strict, determine whether reorganizing the choices still makes decision easy with zero or one shared middle identity.

## Prior work in the program

`scripts/track.py objects "hidden shared padding" --until 2026-11-15 --exclude ONE-RELAY-PADDING-20261115-001 --limit 3`

`scripts/track.py objects "minimal route guard" --until 2026-11-15 --exclude ONE-RELAY-PADDING-20261115-001 --limit 3`

`scripts/track.py objects "implication path cuts" --until 2026-11-15 --exclude ONE-RELAY-PADDING-20261115-001 --limit 3`

- `UNSIGNED-ROUTE-JOINS-20261115-001` studied Minimal switch supports and old-scan errors after one positive middle identification. Keep every visible switch and every local witness independent by name. Reuse only padding bits on binary implication edges, with both signs available, and permit zero or one positive middle class of unbounded multiplicity. Endpoint padding remains private.
- `HIDDEN-COPY-20261112-001` studied Self-maps of harmony stitches and their hidden-copy gadget-definable relations. Keep every visible switch and every local witness independent by name. Reuse only padding bits on binary implication edges, with both signs available, and permit zero or one positive middle class of unbounded multiplicity. Endpoint padding remains private.
- `NEST-COUNT-20261112-001` studied Relations defined by NAE knots on distinct distinctions with hidden helpers. Keep every visible switch and every local witness independent by name. Reuse only padding bits on binary implication edges, with both signs available, and permit zero or one positive middle class of unbounded multiplicity. Endpoint padding remains private.
- `SIGNED-KNOT-OVERLAP-20261114-001` studied Ternary supports and private four-bit sign observations of fixed guarded clause templates. Keep every visible switch and every local witness independent by name. Reuse only padding bits on binary implication edges, with both signs available, and permit zero or one positive middle class of unbounded multiplicity. Endpoint padding remains private.
- `OVERLAP-READ-20261111-001` studied Finite NAE relations read through pair counts, with books and the Pasch as examples. Keep every visible switch and every local witness independent by name. Reuse only padding bits on binary implication edges, with both signs available, and permit zero or one positive middle class of unbounded multiplicity. Endpoint padding remains private.

Keep every visible switch and every local witness independent by name. Reuse only padding bits on binary implication edges, with both signs available, and permit zero or one positive middle class of unbounded multiplicity. Endpoint padding remains private.

## Prior work outside the program

Switching networks with repeated literal labels are classical (https://www.numdam.org/item/ITA_1995__29_1_75_0.pdf); series/parallel circuits go back to Shannon (https://dspace.mit.edu/entities/publication/2dffdeb7-2862-4575-8a8e-b29fb59319e5). Here existential padding is taken out of the literal strict CNF, and the particular joined schedule and permitted normal forms matter.

## Evidence and stopping rule

Expose the single pad literal required to disable an edge with one active strict clause. Without a numeric runtime guess, enumerate every local equality pattern for four edge pads and all eight half-slot states, prove why interstage reuse does or does not survive. Then fix a single highly repeated middle bit and seek a complete decision procedure by moving the change between true and false boundary values. Test endpoint erasures, signed conflicts on separated stages and a raw SAT oracle. Stop at a proof or counterexample.
