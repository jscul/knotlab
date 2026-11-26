"""Read every first-round allocation and the full unchanged cap growth of the 28 linked pairs."""
import argparse
from collections import Counter
import json
from time import process_time

from archive import panel
from growth import Growth
from replay import alternative_counts
from starts import build_pair, census_pairs, linked_pairs


def audit(name, limit):
    begin = process_time()
    frame = list(linked_pairs() if name == "linked" else census_pairs())
    saved = panel(name)
    assert set(frame) == set(saved)
    rows = []
    first_inputs = Counter()
    offshoots = Counter()
    high = Counter()
    for pair in frame[:limit]:
        g = Growth(*build_pair(*pair), law="CAP-3").run(24 if name == "linked" else 1,
                                                         6000 if name == "linked" else 1500)
        for b in g.rounds[0].births:
            counts = alternative_counts(b)
            first_inputs[b.kind,b.p,b.D] += 1
            if b.p == 1 and counts["PLACES"] != b.f:
                offshoots[b.D] += 1
            if b.D >= 5:
                high[b.D, counts["HALF"]] += 1
        all_births = [b for row in g.rounds for b in row.births]
        rows.append({"pair":pair,"rounds":len(g.rounds),"births":len(all_births),
                     "cap_vs_places":sum(b.f != alternative_counts(b)["PLACES"] for b in all_births),
                     "cap_vs_half":sum(b.f != alternative_counts(b)["HALF"] for b in all_births),
                     "cap_vs_ordinary":sum(b.f != alternative_counts(b)["ORD"] for b in all_births)})
    return {"panel":name, "rows":rows,
            "first_inputs":[[*key,n] for key,n in sorted(first_inputs.items())],
            "first_offshoot_disagreements":offshoots,
            "first_high_demand":[[*key,n] for key,n in sorted(high.items())],
            "cpu_seconds":round(process_time()-begin,3)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("panel", choices=["linked","census"])
    parser.add_argument("limit", type=int)
    args = parser.parse_args()
    print(json.dumps(audit(args.panel, args.limit)))
