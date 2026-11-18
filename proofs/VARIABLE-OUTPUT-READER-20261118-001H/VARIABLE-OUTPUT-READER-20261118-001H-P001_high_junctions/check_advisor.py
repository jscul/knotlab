"""Check the advisor's proposed false six-place junction on two seven-site rings of meetings."""

from importlib import util
from itertools import combinations, permutations
import json
from pathlib import Path

PROOFS = Path(__file__).resolve().parents[2]
module_path = next((PROOFS / "VARIABLE-OUTPUT-READER-20261118-001G").glob("*/six_check.py"))
spec = util.spec_from_file_location("preceding_six_check", module_path)
engine = util.module_from_spec(spec)
spec.loader.exec_module(engine)


def trial(unary_outputs):
    seed = (0, 1, 2)
    next_name = 3
    history = [("seed", seed)]
    unary = []
    for i, bit in enumerate(seed):
        fresh = tuple(range(next_name, next_name + unary_outputs))
        next_name += unary_outputs
        unary.append(fresh)
        history.append((f"w{i}", (bit, *fresh)))
    ring_triad = []
    ordinary_marks = []
    cap_inputs = []
    for i in range(3):
        left, right = unary[i][0], unary[(i-1) % 3][1]
        ring_triad.append(left)
        ordinary_marks.append(next_name)
        cap_inputs.append(next_name + 1)
        history.append((f"a{i}", (left, right, next_name, next_name + 1)))
        next_name += 2
    added = tuple(range(next_name, next_name + 3))
    capped = history + [("cap", (*cap_inputs, *added))]
    # These histories have different widths. Only their local proposed signatures can match.
    engine.replay(capped)
    bare_h, bare_adj = engine.incidence(history)
    tight_h, tight_adj = engine.incidence(capped)
    bare_menu = engine.direct_triples(bare_h, bare_adj)
    tight_menu = engine.direct_triples(tight_h, tight_adj)
    assert tuple(ordinary_marks) in bare_menu and tuple(ordinary_marks) not in tight_menu

    def measure(rows, owners, mark):
        bonds = engine.wired_bonds(rows, owners)
        def K(names):
            group = engine.mask(names)
            return min((s.bit_count() for s in bonds if s & group == group), default=None)
        names = (*ordinary_marks, *mark)
        matrix = [[0 if i == j else K((a, b)) for j,b in enumerate(names)] for i,a in enumerate(names)]
        near = [x for x in sorted(owners) if x not in mark and all(K((x, b)) <= 6 for b in mark)]
        return matrix, K(mark), near

    bare, bare_k3, near = measure(history, bare_h, ring_triad)
    tight, cap_k3, _ = measure(capped, tight_h, cap_inputs)
    preserving = []
    for top in permutations(range(3)):
        for bottom in permutations(range(3,6)):
            image = (*top, *bottom)
            if all(bare[a][b] == tight[image[a]][image[b]] for a,b in combinations(range(6),2)):
                preserving.append(image)
    return {"unary_outputs": unary_outputs, "bare_history": history, "cap": capped[-1],
            "ordinal_marks_legal_before_forbidden_after": ordinary_marks, "bare_ring_triad": ring_triad,
            "cap_triad": cap_inputs, "bare_marked_six_matrix_K": bare, "capped_marked_six_matrix_K": tight,
            "minimum_joint_bond_cardinalities": [bare_k3,cap_k3],
            "other_distinctions_within_K6_of_bare_triad": near,
            "six_mark_signature_matching_bijections_preserving_the_two_groups": len(preserving)}


if __name__ == "__main__":
    print(json.dumps([trial(2), trial(3)], indent=2))
