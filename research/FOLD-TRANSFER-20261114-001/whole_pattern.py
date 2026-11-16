"""Independent signed-NAE verification and a literal truth-table baseline.

The solver reads only raw knot incidences and held signs.  It never reads a
source's packaged table or an expected target.  All variables of every source
remain in one SAT instance, including the two variables at each declared join.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from itertools import product
from typing import Any

from pysat.solvers import Solver


def raw_table(
    sources: Sequence[Mapping[str, Any]],
    reads: Sequence[int],
    sever_after: int | None = None,
) -> str:
    """Read a chain directly from its full signed-NAE formula.

    Each source has eight local variables and eight three-place knots.  Local
    inputs are 0, 1, 4; the selected read is 5 or 6.  A join equates one
    source's selected read with the next source's variable 0.  ``sever_after``
    omits exactly one such equality, keeping the two variables independent.

    External input order is the first source's 0, 1, 4 followed by each later
    source's 1, 4.  Rows are lexicographic in their Boolean values.  A row is
    ``x`` when neither output value is possible, ``u`` when both are possible,
    and otherwise the unique value ``0`` or ``1``.
    """
    count = len(sources)
    if count == 0 or len(reads) != count:
        raise ValueError("give one selected read for each of at least one source")
    if any(type(read) is not int or read not in (5, 6) for read in reads):
        raise ValueError("each selected read must be local variable 5 or 6")
    if sever_after is not None and (
        type(sever_after) is not int or not 0 <= sever_after < count - 1
    ):
        raise ValueError("sever_after must identify an existing join")

    clauses: list[list[int]] = []
    for module, source in enumerate(sources):
        try:
            knots = source["points_by_knot"]
            signs = source["held_signs"]
        except (KeyError, TypeError) as exc:
            raise ValueError("each source needs points_by_knot and held_signs") from exc
        if not isinstance(knots, (list, tuple)) or len(knots) != 8:
            raise ValueError("each source must contain eight knot triples")
        if not isinstance(signs, (list, tuple)) or len(signs) != 24:
            raise ValueError("each source must contain 24 sign bits")
        if any(not isinstance(bit, (int, bool)) or bit not in (0, 1) for bit in signs):
            raise ValueError("held_signs must contain only Boolean bits")

        for knot, points in enumerate(knots):
            if (
                not isinstance(points, (list, tuple))
                or len(points) != 3
                or any(type(point) is not int or not 0 <= point < 8 for point in points)
                or len(set(points)) != 3
            ):
                raise ValueError("each knot needs three distinct local variables in 0..7")
            literals = [
                (8 * module + point + 1) * (-1 if signs[3 * knot + role] else 1)
                for role, point in enumerate(points)
            ]
            clauses.append(literals)
            clauses.append([-literal for literal in literals])

    for module in range(count - 1):
        if module == sever_after:
            continue
        left = 8 * module + reads[module] + 1
        right = 8 * (module + 1) + 1
        clauses.extend(([-left, right], [left, -right]))

    inputs = [1, 2, 5]
    for module in range(1, count):
        inputs.extend((8 * module + 2, 8 * module + 5))
    output = 8 * (count - 1) + reads[-1] + 1
    table: list[str] = []
    with Solver(name="cadical153", bootstrap_with=clauses) as solver:
        for values in product((0, 1), repeat=len(inputs)):
            assumptions = [variable if value else -variable for variable, value in zip(inputs, values)]
            zero = solver.solve(assumptions=assumptions + [-output])
            one = solver.solve(assumptions=assumptions + [output])
            table.append("u" if zero and one else "0" if zero else "1" if one else "x")
    return "".join(table)


def plain_table_tree(tables: Iterable[str]) -> dict[str, list[tuple[int, int]]]:
    """Identify distinct literal tables by balanced Boolean row queries.

    At each node, select the row dividing the remaining full-string candidates
    most evenly, breaking ties by the lowest zero-based row index.  Return each
    distinct candidate's complete transcript.  No target family, quotient, or
    source representation is supplied to this baseline.
    """
    supplied = list(tables)
    if not supplied:
        return {}
    if any(not isinstance(table, str) for table in supplied):
        raise ValueError("candidate tables must be strings")
    width = len(supplied[0])
    if width == 0 or width & (width - 1):
        raise ValueError("a complete Boolean table must have a positive power-of-two row count")
    if any(len(table) != width or set(table) - {"0", "1"} for table in supplied):
        raise ValueError("candidate tables must have equal lengths and only Boolean labels")

    candidates = sorted(set(supplied))
    transcripts: dict[str, list[tuple[int, int]]] = {table: [] for table in candidates}

    def divide(remaining: list[str], prefix: list[tuple[int, int]]) -> None:
        if len(remaining) == 1:
            transcripts[remaining[0]] = prefix
            return
        row = min(
            range(width),
            key=lambda index: (
                abs(len(remaining) - 2 * sum(table[index] == "1" for table in remaining)),
                index,
            ),
        )
        for label in (0, 1):
            branch = [table for table in remaining if table[row] == str(label)]
            if branch:
                divide(branch, prefix + [(row, label)])

    divide(candidates, [])
    return transcripts
