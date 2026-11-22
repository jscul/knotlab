"""Audit equal-degree feeder pairs in the earlier immutable history archive."""

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, replace
from functools import cache
import gzip
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys


ARCHIVE = Path(__file__).resolve().parent.parent / "FEEDER-MEMORY-20261121-001"
sys.path.insert(0, str(ARCHIVE))
from history_reader import history_reason, history_verdict  # noqa: E402
from history_verify import layout  # noqa: E402


RUNS = "history_runs.json.gz"
PAIRS = "history_pairs.json.gz"
EXCHANGES = "intervention_rows.json.gz"
GROWTH_TURN = 5


@dataclass(frozen=True, slots=True)
class Cell:
    law: str
    seed: int
    source_key: str
    variant: str
    tape: int
    replicate: int


@dataclass(frozen=True, slots=True)
class Visit:
    cell: Cell
    route: tuple[int, ...]
    attempts: tuple[int, ...]
    meals: tuple[int, ...]
    public: tuple[tuple[bool, int, int, int, int], ...]

    @property
    def turn(self):
        return len(self.route)

    @property
    def holder(self):
        return self.route[-1]

    @property
    def current(self):
        return self.public[-1][:-1]

    @property
    def spent(self):
        return tuple(sorted(self.route[turn - 1] for turn in self.meals))

    @property
    def full(self):
        return self.holder not in self.spent

    @property
    def memory(self):
        paid_degree = self.public[self.meals[-1] - 1][3]
        assert paid_degree >= 1
        return "101" if paid_degree == 1 else "011"

    def packed(self):
        return {
            **asdict(self.cell),
            "turn": self.turn,
            "holder": self.holder,
            "stock_full": self.full,
            "spent_holders": self.spent,
            "attempt_turns": self.attempts,
            "meal_turns": self.meals,
            "last_meal_degree": self.public[self.meals[-1] - 1][3],
            "memory": self.memory,
            "route": self.route,
            "public": self.public,
            "verdict": _verdict(self.public),
            "reason": history_reason(self.public),
        }


@cache
def _verdict(public):
    return history_verdict(public)


def _load(name):
    with gzip.open(ARCHIVE / name, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def _reached(block, degrees):
    cell = Cell(**{name: block[name] for name in Cell.__annotations__})
    reached = {}
    for episode in block["terminal_prefixes"]:
        public = tuple(map(tuple, episode["public"]))
        route = tuple(episode["route"])
        attempts = episode["attempt_turns"]
        meals = episode["meal_turns"]
        for turn, (row, holder) in enumerate(zip(public, route, strict=True), 1):
            key = cell.law, cell.seed, turn >= GROWTH_TURN, holder
            assert degrees.setdefault(key, row[3]) == row[3]
            paid = tuple(meal for meal in meals if meal < turn)
            if not row[0] or not paid:
                continue
            previous_attempts = tuple(attempt for attempt in attempts if attempt < turn)
            visit = Visit(
                cell, route[:turn], previous_attempts, paid,
                (*public[:turn - 1], (*row[:-1], -1)),
            )
            assert reached.setdefault((turn, previous_attempts), visit) == visit
    return cell, tuple(reached.values())


def _rank_pair(pair):
    empty, full = pair
    return empty.turn, empty.cell.seed, empty.cell.tape, empty.attempts, full.attempts


def _twins_of(pair, visits):
    twins = []
    for visit in pair:
        renamed = replace(visit.cell, variant="renamed")
        twins.append(visits.get((renamed, visit.holder, not visit.full, visit.public)))
    return tuple(twins)


def _holding_check(visit, degrees):
    cell = visit.cell
    _, formations = layout(cell.seed, cell.law, cell.variant)
    after_growth = visit.turn >= GROWTH_TURN
    links, feeder_holders = formations[after_growth]
    shared = links[visit.holder]
    assert visit.holder in feeder_holders
    assert len(shared) == visit.current[3]
    assert len(shared) == degrees[cell.law, cell.seed, after_growth, visit.holder]
    return {
        "holder": visit.holder,
        "degree_at_query": len(shared),
        "ordinary_shared_distinctions_and_other_holders": sorted(shared),
    }


def _distinct_target(cells, degrees):
    counts_by_law = defaultdict(Counter)
    splits = defaultdict(lambda: Counter({"empty/full": 0}))
    live_splits = defaultdict(lambda: Counter({"empty/full": 0}))
    public_index = {
        (cell, visit.holder, visit.full, visit.public): visit
        for cell, reached in cells
        for visit in reached
    }
    examples = {}
    for cell, reached in cells:
        count = counts_by_law[cell.law]
        count["archive_cells"] += 1
        count["distinct_feeder_visits_after_meal"] += len(reached)
        groups = defaultdict(lambda: ([], []))
        for visit in reached:
            groups[visit.turn, visit.current, visit.memory, len(visit.meals)][visit.full].append(visit)
        for empties, fulls in groups.values():
            for empty, full in product(empties, fulls):
                if empty.holder == full.holder:
                    continue
                count["distinct_targets_opposite_stock"] += 1
                count["identical_complete_histories"] += empty.public == full.public
                if empty.holder not in full.spent:
                    continue
                count["full_branch_consumed_empty_target"] += 1
                if empty.spent != full.spent:
                    continue
                count["same_spent_set"] += 1
                if len(empty.meals) != 1:
                    continue
                count["same_single_paid_holder"] += 1
                verdicts = f"{_verdict(empty.public)}/{_verdict(full.public)}"
                splits[cell.law][verdicts] += 1
                if empty.current[2] != 2 or empty.current[1] < 2:
                    continue
                count["same_single_paid_holder_previous_move_energy_at_least_two"] += 1
                live_splits[cell.law][verdicts] += 1
                if cell.variant != "original":
                    continue
                pair = empty, full
                twins = _twins_of(pair, public_index)
                if None in twins:
                    continue
                count["original_live_single_paid_pairs_with_two_exact_renamed_twins"] += 1
                earlier = examples.get(cell.law)
                if earlier is None or _rank_pair(pair) < _rank_pair(earlier[0]):
                    examples[cell.law] = pair, twins

    results = {}
    for law, count in counts_by_law.items():
        pair, twins = examples[law]
        results[law] = {
            "counts": dict(count),
            "single_paid_pair_verdicts_empty_then_full": dict(splits[law]),
            "live_single_paid_arrival_verdicts_empty_then_full": dict(live_splits[law]),
            "earliest_two_twin_example": {
                "current_public": pair[0].current,
                "holdings_degree_check": [_holding_check(visit, degrees) for visit in pair],
                "empty": pair[0].packed(),
                "full": pair[1].packed(),
                "renamed_full_twin_of_empty": twins[0].packed(),
                "renamed_empty_twin_of_full": twins[1].packed(),
            },
        }
    return results


def _same_source_transcript_twins(cells, degrees):
    classes = defaultdict(lambda: ([], []))
    counts = {cell.law: Counter({"both_paid_a_neither_paid_b": 0}) for cell, _ in cells}
    for cell, reached in cells:
        for visit in reached:
            key = cell.law, cell.seed, cell.source_key, visit.public
            classes[key][visit.full].append(visit)

    examples = {}
    for (law, _, _, _), (empties, fulls) in classes.items():
        if not empties or not fulls:
            continue
        count = counts[law]
        count["opposite_stock_transcript_classes"] += 1
        for empty, full in product(empties, fulls):
            count["all_opposite_stock_pairs_in_class"] += 1
            if empty.holder == full.holder:
                continue
            count["distinct_targets"] += 1
            if empty.holder not in full.spent or full.holder in empty.spent:
                continue
            count["both_paid_a_neither_paid_b"] += 1
            same_spent = empty.spent == full.spent
            same_tape = empty.cell.tape == full.cell.tape
            same_route_before_query = empty.route[:-1] == full.route[:-1]
            count["also_same_spent_set"] += same_spent
            count["also_same_tape"] += same_tape
            count["also_same_route_before_query"] += same_route_before_query
            rank = (
                not same_tape,
                not same_spent,
                not same_route_before_query,
                len(empty.meals),
                *_rank_pair((empty, full)),
                empty.cell.variant,
                full.cell.variant,
                full.cell.tape,
            )
            if law not in examples or rank < examples[law][0]:
                examples[law] = rank, empty, full

    results = {}
    for law, count in counts.items():
        example = None
        if law in examples:
            _, empty, full = examples[law]
            example = {
                "current_public": empty.current,
                "holdings_degree_check": [_holding_check(visit, degrees) for visit in (empty, full)],
                "empty": empty.packed(),
                "full": full.packed(),
            }
        results[law] = {"counts": dict(count), "example": example}
    return results


def _previous_same_target(degrees):
    counts_by_law = defaultdict(Counter)
    for pair, exchange in zip(_load(PAIRS), _load(EXCHANGES), strict=True):
        fields = ("law", "seed", "variant", "tape", "turn")
        assert all(pair[field] == exchange[field] for field in fields)
        empty, full = pair["empty"], pair["full"]
        assert [empty["attempt_turns"], full["attempt_turns"]] == exchange["prefix_eats"]
        target = pair["target_holder"]
        assert target == exchange["holder"]
        count = counts_by_law[pair["law"]]
        count["all_original_study_same_target_pairs"] += 1
        if pair["last_paid_types"][0] != pair["last_paid_types"][1]:
            continue
        memory = exchange["memory"]
        bits = exchange["bits"]
        assert memory[0] == memory[1]
        assert bits["original"] == bits["sham"] == bits["swapped"]
        count["same_first_memory_nonflips"] += 1
        count[f"both_memory_{memory[0]}"] += 1
        other = pair["other_paid_holder"]
        if other is None or target == other:
            continue
        prefix = pair["law"], pair["seed"], pair["turn"] >= GROWTH_TURN
        if degrees[*prefix, target] != degrees[*prefix, other]:
            continue
        count["same_query_epoch_degree_target_and_other_paid"] += 1
        count["same_query_epoch_degree_both_publicly_certified"] += exchange["certified_both"]
        if len(empty["meal_turns"]) == len(full["meal_turns"]) == 1:
            assert full["paid_in_order"] == [other]
            relevant = {target, other}
            visited = all(relevant.issubset(branch["route"]) for branch in (empty, full))
            visited_before = all(relevant.issubset(branch["route"][:-1]) for branch in (empty, full))
            assert visited == pair["both_feeders_visited"]
            assert visited_before == pair["both_feeders_visited_before_probe"]
            count["same_query_epoch_degree_one_paid_each"] += 1
            count["same_query_epoch_degree_one_paid_each_both_feeders_visited_by_query"] += visited
            count["same_query_epoch_degree_one_paid_each_both_feeders_visited_before_query"] += visited_before
    return {law: dict(count) for law, count in counts_by_law.items()}


def audit():
    degrees = {}
    cells = tuple(_reached(block, degrees) for block in _load(RUNS))
    files = (RUNS, PAIRS, EXCHANGES, "history_reader.py", "history_verify.py")
    return {
        "schema_version": 1,
        "archive": ARCHIVE.name,
        "archive_sha256": {name: sha256((ARCHIVE / name).read_bytes()).hexdigest() for name in files},
        "distinct_target_gate": (
            "Same archived law, founder, presentation, tape, decision turn, current public observation, "
            "earlier positive meal count and first-memory word. Different queried holders and opposite stock. "
            "Count each pair of distinct reached action prefixes once, with the empty branch first."
        ),
        "previous_same_target_gate": (
            "Same first-memory word and no physical flip in the predecessor's accepted same-target pair ledger. "
            "The exact degree comparison uses both distinct actual holders in the query's growth period."
        ),
        "holding_check": (
            "Counts shared distinctions directly from the predecessor's independent ordinary-growth owner audit "
            "on the already archived candidate seed at the query. No new movement or policy is run."
        ),
        "distinct_target": _distinct_target(cells, degrees),
        "same_source_transcript_twins_gate": (
            "Equal complete public transcripts on the same archived law and founder across any tapes "
            "or presentations. Query distinct feeders A empty and B full. "
            "Both histories previously paid A and neither previously paid B."
        ),
        "same_source_transcript_twins": _same_source_transcript_twins(cells, degrees),
        "previous_same_target": _previous_same_target(degrees),
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
