"""Terminal-reward search over guarded single-bit flips. No target crossing table is supplied."""

import argparse
import hashlib
import json
import random
from collections import Counter
from itertools import product


SEED = 27183
ISLANDS = 32
GENERATIONS = 256
BROOD = 12
MAX_LENGTH = 32
BIT_NAMES = ("x_high", "x_low", "y_high", "y_low")
MASKS = (8, 4, 2, 1)
COLORS = range(3)
POINTS = tuple(product(COLORS, repeat=2))
TRIPLES = tuple(product(COLORS, repeat=3))
TRAIN_TRIPLES = tuple(i for i, (x, y, z) in enumerate(TRIPLES) if z != (x + y + 1) % 3)
WORDS = tuple((x << 2) | y for x, y in POINTS)
START = bytes(range(len(POINTS)))


# Each guard fixes all three unmodified bits. Both possible values of the
# target must encode legal colors. This rule gives twelve elementary actions.
ACTIONS = tuple((target, guard) for target in MASKS for guard in WORDS
                if not guard & target and (guard | target) in WORDS)


def byte_table(values):
    return bytes(values).ljust(256, b"\0")


def compile_action(target, guard):
    return byte_table(WORDS.index(word ^ target) if (word & (15 ^ target)) == guard else i
                      for i, word in enumerate(WORDS))


COMPILED = tuple(compile_action(*action) for action in ACTIONS)
TRIPLE_BLOCKS = tuple(bytes(range(3 * value, 3 * value + 3)) for value in range(9))
PLUS_NINE = byte_table(range(9, 18))
PLUS_EIGHTEEN = byte_table(range(18, 27))


def program_image(program):
    image = START
    for action in program:
        image = image.translate(COMPILED[action])
    return image


def describe_action(action):
    target, guard = ACTIONS[action]
    return {
        "id": action,
        "toggle": BIT_NAMES[MASKS.index(target)],
        "guard": {name: int(bool(guard & mask)) for name, mask in zip(BIT_NAMES, MASKS) if mask != target},
    }


def elementary_execution(program, point):
    """Separate interpreter: literal NOTs, two ANDs and a target XOR per instruction."""
    x, y = point
    bits = [x >> 1, x & 1, y >> 1, y & 1]
    for action in program:
        target, guard = ACTIONS[action]
        literals = [bit if guard & mask else 1 ^ bit for mask, bit in zip(MASKS, bits) if mask != target]
        enabled = (literals[0] & literals[1]) & literals[2]
        bits[MASKS.index(target)] ^= enabled
    return 2 * bits[0] + bits[1], 2 * bits[2] + bits[3]


def primitive_counts(program):
    negations = sum(sum(not (guard & mask) for mask in MASKS if mask != target)
                    for target, guard in (ACTIONS[action] for action in program))
    return {"NOT": negations, "AND": 2 * len(program), "XOR": len(program)}


def program_digest(program):
    return hashlib.sha256(bytes(program)).hexdigest()


def forward_reward(image):
    left = b"".join(TRIPLE_BLOCKS[value] for value in image)
    right = image + image.translate(PLUS_NINE) + image.translate(PLUS_EIGHTEEN)
    left_table, right_table = byte_table(left), byte_table(right)
    lhs = left.translate(right_table).translate(left_table)
    rhs = right.translate(left_table).translate(right_table)
    agree = sum(lhs[i] == rhs[i] for i in TRAIN_TRIPLES)

    first = tuple(value // 3 for value in image)
    second = tuple(value % 3 for value in image)
    first_rows = [len(set(first[3*i:3*i+3])) for i in COLORS]
    second_cols = [len(set(second[i::3])) for i in COLORS]
    first_joint = max(first_rows) > 1 and any(len(set(first[i::3])) > 1 for i in COLORS)
    second_joint = max(second_cols) > 1 and any(len(set(second[3*i:3*i+3])) > 1 for i in COLORS)
    diagonal = sum(image[4*i] == 4*i for i in COLORS)
    noninvolution = any(image[image[i]] != i for i in START)
    return agree + sum(first_rows) + sum(second_cols) + 2*diagonal + 4*(first_joint or second_joint) + 2*noninvolution


def round_trip_reward(frozen_image):
    """The scoring environment holds the forward effect. The undo agent receives one scalar."""
    def score(candidate):
        return sum(candidate[frozen_image[i]] == i for i in START) + sum(frozen_image[candidate[i]] == i for i in START)
    return score


def random_program(rng):
    return tuple(rng.randrange(len(ACTIONS)) for _ in range(rng.randint(6, 24)))


def mutate(parent, rng):
    # Draw the same variation instructions even if corresponding guided and
    # neutral parents have different lengths. Positions are uniform conditional on length.
    kind = rng.randrange(100)
    a, b = rng.random(), rng.random()
    action = rng.randrange(len(ACTIONS))
    n = len(parent)
    if not n:
        return (action,)
    if kind < 30 and n < MAX_LENGTH:
        i = int(a * (n + 1))
        return parent[:i] + (action,) + parent[i:]
    i = int(a * n)
    if 30 <= kind < 55:
        return parent[:i] + parent[i+1:]
    if kind < 85:
        return parent[:i] + (action,) + parent[i+1:]
    without = parent[:i] + parent[i+1:]
    j = int(b * n)
    return without[:j] + (parent[i],) + without[j:]


def policy_search(score_function, maximum, guided, stage_seed, *, islands, generations, brood):
    variation = random.Random(stage_seed)
    selection = random.Random(stage_seed + 1)
    cache = {}
    evaluations = 0
    first_maximum = None
    checkpoint = None
    trajectory = []

    def evaluate(program):
        nonlocal evaluations, first_maximum, checkpoint
        image = program_image(program)
        if image not in cache:
            cache[image] = score_function(image)
        score = cache[image]
        evaluations += 1
        if score == maximum and first_maximum is None:
            first_maximum = evaluations
        if checkpoint is None or (score, -len(program)) > (checkpoint[1], -len(checkpoint[0])):
            checkpoint = (program, score)
        return program, score

    parents = [evaluate(random_program(variation)) for _ in range(islands)]

    def record(generation):
        trajectory.append([generation, evaluations, checkpoint[1], len(checkpoint[0]),
                           sum(score for _, score in parents)])

    record(0)
    for generation in range(1, generations + 1):
        for island, (parent, parent_score) in enumerate(parents):
            candidates = [(parent, parent_score)]
            candidates.extend(evaluate(mutate(parent, variation)) for _ in range(brood - 1))
            candidates.append(evaluate(random_program(variation)))
            if generation % 32 == 0:
                parents[island] = candidates[-1]
            else:
                if guided:
                    top = max(score for _, score in candidates)
                    candidates = [candidate for candidate in candidates if candidate[1] == top]
                parents[island] = candidates[int(selection.random() * len(candidates))]
        record(generation)
    program, score = checkpoint
    return {
        "actions": list(program), "sha256_action_bytes": program_digest(program), "primitive_counts": primitive_counts(program),
        "score": score, "maximum_train_score": maximum, "first_maximum_evaluation": first_maximum,
        "proposals_scored_including_initializations": evaluations, "distinct_images_scored": len(cache),
        "parent_choices_including_restarts": generations * islands,
        "trajectory_columns": ["generation", "proposals", "best_score", "best_length", "sum_parent_scores"],
        "trajectory": trajectory,
    }


def fit():
    """Run the single frozen comparison. The forward action sequence never enters undo search."""
    stages = {}
    sizes = {"islands": ISLANDS, "generations": GENERATIONS, "brood": BROOD}
    for name, guided in (("guided", True), ("neutral", False)):
        stages[name + "_forward"] = policy_search(forward_reward, 48, guided, SEED, **sizes)
    frozen_effect = program_image(stages["guided_forward"]["actions"])
    undo_score = round_trip_reward(frozen_effect)
    for name, guided in (("guided", True), ("neutral", False)):
        stages[name + "_undo"] = policy_search(undo_score, 18, guided, SEED + 1000, **sizes)
    return {
        "seed": SEED, "undo_variation_seed_offset": 1000, "selection_seed_offset": 1,
        "sizes": sizes, "initial_length": [6, 24], "maximum_length": MAX_LENGTH, "restart_period": 32,
        "operator_repertoire": [describe_action(i) for i in range(len(ACTIONS))],
        "forward_training_triples": [TRIPLES[i] for i in TRAIN_TRIPLES],
        "undo_scorer_forward_sha256": stages["guided_forward"]["sha256_action_bytes"],
        "stages": stages,
    }


def three_moves(move, state, positions):
    state = list(state)
    for i in positions:
        state[i:i+2] = move(state[i], state[i+1])
    return tuple(state)


def check_forward(move):
    """Exhaust raw tuples and audit every property without the compiled reward or masks."""
    table = {p: move(*p) for p in POINTS}
    held_out = []
    train = []
    for p in TRIPLES:
        x, y, z = p
        left = three_moves(move, p, (0, 1, 0))
        right = three_moves(move, p, (1, 0, 1))
        panel = held_out if z == (x + y + 1) % 3 else train
        panel.append({"input": p, "left": left, "right": right, "equal": left == right})
    row_sizes = [len({move(x, y)[0] for y in COLORS}) for x in COLORS]
    col_sizes = [len({move(x, y)[1] for x in COLORS}) for y in COLORS]
    dependencies = []
    for i in (0, 1):
        varies_x = any(move(0, y)[i] != move(x, y)[i] for x, y in POINTS)
        varies_y = any(move(x, 0)[i] != move(x, y)[i] for x, y in POINTS)
        dependencies.append([name for name, varies in (("x", varies_x), ("y", varies_y)) if varies])
    diagonal = sum(move(x, x) == (x, x) for x in COLORS)
    twice_changed = sum(move(*move(*p)) != p for p in POINTS)
    train_pass = sum(row["equal"] for row in train)
    hold_pass = sum(row["equal"] for row in held_out)
    mixed = any(len(support) == 2 for support in dependencies)
    score = train_pass + sum(row_sizes) + sum(col_sizes) + 2*diagonal + 4*mixed + 2*bool(twice_changed)
    return {
        "point_order": POINTS, "image": [table[p] for p in POINTS], "distinct_outputs": len(set(table.values())),
        "first_row_distinct_counts": row_sizes, "second_column_distinct_counts": col_sizes,
        "fixed_diagonal": diagonal, "output_dependencies": dependencies, "two_forward_changed": twice_changed,
        "train_braid_agreements": train_pass, "held_out_braid_agreements": hold_pass,
        "train_triples": train, "held_out_triples": held_out, "recomputed_train_score": score,
        "full_gate": (len(set(table.values())) == len(POINTS) and row_sizes + col_sizes == [3]*6 and
                      diagonal == 3 and mixed and twice_changed > 0 and train_pass + hold_pass == len(TRIPLES)),
    }


def check_undo(forward, undo):
    rows = []
    for p in POINTS:
        first = elementary_execution(undo, elementary_execution(forward, p))
        second = elementary_execution(forward, elementary_execution(undo, p))
        rows.append({"input": p, "forward_then_undo": first, "undo_then_forward": second})
    score = sum(row["input"] == row[key] for row in rows for key in ("forward_then_undo", "undo_then_forward"))
    return {"rows": rows, "exact_round_trips": score, "round_trips": 2 * len(rows), "full_inverse": score == 2*len(rows)}


def assess(checkpoint):
    """Replay frozen programs one Boolean instruction at a time on the full panels."""
    stages = checkpoint["stages"]
    for record in stages.values():
        if program_digest(record["actions"]) != record["sha256_action_bytes"]:
            raise ValueError("The saved action sequence does not match its digest")
    forward = stages["guided_forward"]["actions"]
    if stages["guided_forward"]["sha256_action_bytes"] != checkpoint["undo_scorer_forward_sha256"]:
        raise ValueError("The forward checkpoint differs from the forward effect used to score undo")
    results = {}
    for method in ("guided", "neutral"):
        stage = method + "_forward"
        program = stages[stage]["actions"]
        result = check_forward(lambda x, y: elementary_execution(program, (x, y)))
        if result["recomputed_train_score"] != stages[stage]["score"]:
            raise AssertionError(f"Independent forward reward differs for {method}")
        results[stage] = result
        stage = method + "_undo"
        result = check_undo(forward, stages[stage]["actions"])
        if result["exact_round_trips"] != stages[stage]["score"]:
            raise AssertionError(f"Independent undo reward differs for {method}")
        results[stage] = result

    def other_permutation(x, y):
        # For x=0,1, swap the other two colors. For x=2 use identity.
        return ((-x-y) % 3 if x != 2 else y), x

    results["analytic_counterexample_post_fit"] = check_forward(other_permutation)
    results["constructive_reverse_post_fit_control"] = check_undo(forward, list(reversed(forward)))
    return results


def smoke():
    """Check executors and parent-selection bookkeeping against a synthetic reward."""
    if len(ACTIONS) != 12:
        raise AssertionError("Unexpected action count")
    for i in range(len(ACTIONS)):
        raw = [elementary_execution((i,), p) for p in POINTS]
        if bytes(3*x + y for x, y in raw) != program_image((i,)) or program_image((i, i)) != START:
            raise AssertionError(f"Guarded bit flip {i} failed replay")
    counts = Counter()
    for guided in (False, True):
        mock = policy_search(lambda img: int(img[0] == 0), 1, guided, 0, islands=2, generations=2, brood=3)
        counts["toy_proposals"] += mock["proposals_scored_including_initializations"]
    return {"guarded_actions": len(ACTIONS), "point_executions": len(ACTIONS)*len(POINTS), **counts}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fit", action="store_true")
    mode.add_argument("--assess", metavar="CHECKPOINT_JSON")
    mode.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.smoke:
        output = smoke()
    elif args.assess:
        with open(args.assess, encoding="utf-8") as handle:
            saved = json.load(handle)
        output = assess(saved.get("fit", saved))
    else:
        trained = fit()
        output = {"fit": trained, "assessment": assess(trained)}
    print(json.dumps(output, sort_keys=True))
