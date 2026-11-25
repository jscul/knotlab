"""Classify exact relations ordered by the bit index 4a + 2b + c."""

from functools import cache
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys


def bit_rows(mask, width):
    return (word for word in range(1 << width) if mask >> word & 1)


def marginal(mask, width, keep):
    result = 0
    for row in bit_rows(mask, width):
        word = 0
        for place in keep:
            word = 2 * word + (row >> (width - place - 1) & 1)
        result |= 1 << word
    return result


def informative_pair(mask):
    first, second = (tuple(bit_rows(marginal(mask, 2, (i,)), 1)) for i in range(2))
    independent = sum(1 << (2 * a + b) for a, b in product(first, second))
    return mask != independent


@cache
def classify(mask):
    if type(mask) is not int or not 0 <= mask <= 255:
        raise ValueError(f"invalid truth mask {mask!r}")
    ab = marginal(mask, 3, (0, 1))
    ac = marginal(mask, 3, (0, 2))
    bc = marginal(mask, 3, (1, 2))
    product_arms = sum(
        1 << (4 * a + 2 * b + c)
        for a, b, c in product(range(2), repeat=3)
        if ac >> (2 * a + c) & 1 and bc >> (2 * b + c) & 1
    )
    joint_ac = informative_pair(ac)
    joint_bc = informative_pair(bc)
    binding = mask != 255
    loss = ab == ac == bc == 15
    coexistence = mask != 0
    is_knot = binding and loss and coexistence
    factorizes = mask == product_arms
    if not coexistence:
        category = "empty"
    elif not binding:
        category = "full"
    elif is_knot:
        category = "knot"
    elif factorizes and joint_ac and joint_bc:
        category = "proper_hub"
    elif factorizes and joint_ac != joint_bc:
        category = "one_sided"
    else:
        category = "other"
    return {
        "mask": mask,
        "category": category,
        "ab": ab,
        "ac": ac,
        "bc": bc,
        "informative_ac": joint_ac,
        "informative_bc": joint_bc,
        "factorizes": factorizes,
        "arm_product_mask": product_arms,
        "constant_roles": [
            role for i, role in enumerate("abc") if marginal(mask, 3, (i,)) in (1, 2)
        ],
        "nonopen_roles": [
            role for i, role in enumerate("abc") if marginal(mask, 3, (i,)) != 3
        ],
        "binding": binding,
        "loss_on_erasure": loss,
        "coexistence": coexistence,
        "is_knot": is_knot,
    }


def canonical_receipt(mask):
    """Ask the unmodified knotlab CLI about this exact truth table."""
    root = Path(__file__).resolve().parents[4]
    cnf = "\n".join(
        " ".join(f"~{name}" if word >> (2 - i) & 1 else name for i, name in enumerate("abc"))
        for word in bit_rows(255 ^ mask, 3)
    )
    args = [
        sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf,
        "--loops", "a", "b", "--contact", "c", "--json",
    ]
    invocation = subprocess.run(
        args, cwd=root, env=dict(os.environ, PYTHONPATH=str(root / "tools")),
        capture_output=True, text=True, check=True,
    )
    result = json.loads(invocation.stdout)
    observed = sum(1 << int(word, 2) for word in result["allowed"])
    want = classify(mask)
    if (
        observed != mask or result["variables"] != ["a", "b", "c"]
        or result["erasure"] != "forgetting"
        or any(result[key] != want[key] for key in (
            "binding", "loss_on_erasure", "coexistence", "is_knot",
        ))
    ):
        raise ValueError(f"canonical checker disagreed on mask {mask}")
    return {"classification": want, "canonical": result}
