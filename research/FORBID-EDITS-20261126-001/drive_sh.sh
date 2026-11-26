#!/bin/bash
# drive_sh.sh: the contact addendum (README.md, "With a contact"): the census of starts up to five knots, E1 and M1,
# placements with a birth of two readers read too; six processes
cd "$(dirname "$0")"
for K in E1 M1; do for P in 0 2500 5000; do
  /home/jscul/p-vs-np-contact-first/.venv/bin/python -B forbid.py run "$K" "$P" "$((P + 2500))" --shared > "shared_${K}_${P}.jsonl" &
done; done
wait
