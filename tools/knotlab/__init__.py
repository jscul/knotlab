"""Knot laboratory: test the bound-loop formalization of the logical knot.

A knot of loops L1..Ln with contact c satisfies K1 binding, K2 loss on
erasure and K3 coexistence (INTUITIONS.md). Verdicts depend only on
the allowed states, never on how the constraints are written.
"""

from .competition import allowed_states, least_set_knot, separation, separation_levels, triangle, triangle_strip
from .depth import charge_depth, cutwidth, scope_hole_rank, toggle_width
from .executor import GuardedSystem, LeakReport, leak_report
from .holonomy import (
    allowed,
    allowed_fraction,
    basic_relaxation_accepts,
    knot_among_loops,
    nerve,
    orbit_sizes,
    selector_relation,
    sheets,
    star,
)
from .knots import KnotReport, check_knot, knot_relation, witness_chain
from .loops import LoopReport, implication_loop, loop_report, signature, signed_loop
from .patterns import (
    co_information,
    controls,
    emergent_information,
    entwines,
    hides_from_parts,
    least_violation,
    parity,
    parity_chain,
)
from .presence import TwoLoops, copy_ring, inverter_ring, running
from .relations import Relation, format_clause, parse_clause, parse_cnf
from .rings import bits, memory, network, predicted_excluded, ring, transfers
from .space import bonds, free_sets, homology, ties
from .worlds import (
    Rule,
    add_by_forced_world,
    atom,
    choices_reaching,
    dual_rail_adder,
    dual_rail_gate,
    essential,
    existence_profile,
    forced_world,
    from_atoms_and_distinctions,
    gate_relation,
    knot_tree,
    minimal_worlds,
    thread,
)

__all__ = [
    "GuardedSystem",
    "KnotReport",
    "LeakReport",
    "LoopReport",
    "Relation",
    "Rule",
    "TwoLoops",
    "add_by_forced_world",
    "allowed",
    "allowed_fraction",
    "allowed_states",
    "atom",
    "basic_relaxation_accepts",
    "bonds",
    "charge_depth",
    "check_knot",
    "choices_reaching",
    "co_information",
    "controls",
    "copy_ring",
    "cutwidth",
    "dual_rail_adder",
    "dual_rail_gate",
    "emergent_information",
    "entwines",
    "essential",
    "existence_profile",
    "forced_world",
    "format_clause",
    "free_sets",
    "from_atoms_and_distinctions",
    "gate_relation",
    "hides_from_parts",
    "homology",
    "implication_loop",
    "inverter_ring",
    "knot_among_loops",
    "knot_relation",
    "knot_tree",
    "leak_report",
    "least_set_knot",
    "least_violation",
    "loop_report",
    "minimal_worlds",
    "nerve",
    "orbit_sizes",
    "parity",
    "parity_chain",
    "parse_clause",
    "parse_cnf",
    "running",
    "scope_hole_rank",
    "selector_relation",
    "separation",
    "separation_levels",
    "sheets",
    "signature",
    "signed_loop",
    "star",
    "thread",
    "ties",
    "toggle_width",
    "triangle",
    "triangle_strip",
    "witness_chain",
]
