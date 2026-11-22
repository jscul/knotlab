"""Reproduce the post-score reading of training ties without opening any test image."""

from collections import Counter
import json
from pathlib import Path
import sys

RECORD = Path(__file__).resolve().parent
ROOT = RECORD.parents[1]
PANEL = ROOT / "experiments" / RECORD.name / (RECORD.name + "-E001_groups") / "panel"
sys.path.insert(0, str(RECORD / "audit"))
from group_oracle import group_roster, mask_from_partition, priority, selected_groups
from pixel_counts import TURN_BIN, counts


def rows(name):
    return [json.loads(line) for line in (PANEL / name).read_text().splitlines()]


def inspect():
    labels = {row["id"]: int(row["label"] == "T") for row in rows("training_key.jsonl")}
    train = rows("train.jsonl")
    groups = list(group_roster([counts(row["pixels"]) for row in train],
                               [labels[row["id"]] for row in train]))
    separation = max(priority(group)[:2] for group in groups)
    best = [group for group in groups if priority(group)[:2] == separation]
    retained = selected_groups(groups)
    invariant = [group for group in best
                 if mask_from_partition(group.members) ==
                 mask_from_partition([TURN_BIN[i] for i in group.members])]
    clue = next(g for g in groups if g.members == (7, 11, 13, 14))
    record = json.loads((RECORD / "audit/postscore_rank_support.json").read_text())
    assert separation[0] and record["best_score"] == "infinite"
    for name, group_list in (("all_best", best), ("quarter_turn_closed_best", invariant)):
        actual = Counter(str(len(g.members)) for g in group_list)
        assert dict(actual) == record[name + "_partitions_by_smaller_side_size_before_tiebreak"]
    assert record["earlier_clue"] == {
        "bins": list(clue.members),
        "has_maximal_initial_rank": clue in best,
        "measured_means": [str(value) for value in clue.means],
        "score": "infinite" if clue.score[1] == 0 else str(clue.score),
        "selected": clue in retained,
    }
    return {"best_before_size_preference": len(best), "preserved_by_quarter_turn": len(invariant),
            "retained_groups": [g.members for g in retained], "earlier_clue": record["earlier_clue"]}


if __name__ == "__main__":
    print(json.dumps(inspect(), indent=2))
