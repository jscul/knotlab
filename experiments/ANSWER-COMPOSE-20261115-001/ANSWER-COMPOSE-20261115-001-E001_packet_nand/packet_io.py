"""Shared physical sender and public probe evaluator for all comparison arms.

Only the three previously learned NAND expressions interpret signed clauses.
The received-answer decoder is a separate program. This module has no grader.
"""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PRIOR = "BIT-DECODER-20261114-001"
PARSER_PATH = ROOT / "artifacts" / PRIOR / (PRIOR + "-E001_atomic_codec") / "varied_checkpoint.json"
PARSER_SHA = "b328cd2bcd4aa95976fad2513252ad1c23e0e21fa337323b84919a8ea93db0cd"
parser_bytes = PARSER_PATH.read_bytes()
if hashlib.sha256(parser_bytes).hexdigest() != PARSER_SHA:
    raise ValueError("Shared predecessor parser failed its content binding")
PARSER = json.loads(parser_bytes)["parser"]
ALL_RAW = tuple(range(512))
ALL_PORTS = tuple(range(4))
FULL_COLUMNS = tuple(sum(((raw >> i) & 1) << raw for raw in ALL_RAW) for i in range(9))


def _compile(program):
    """Compile the validated binary NAND AST to a short straight-line Python function."""
    instructions = []
    def visit(expr):
        if expr[0] == "const" and len(expr) == 2 and type(expr[1]) is int and expr[1] in (0, 1):
            return "lanes" if expr[1] else "0"
        if expr[0] == "input" and len(expr) == 2 and type(expr[1]) is int and expr[1] in (0, 1):
            return ("first", "second")[expr[1]]
        if expr[0] != "NAND" or len(expr) != 3:
            raise ValueError("Unexpected expression in the pinned binary parser")
        left = visit(expr[1])
        right = left if expr[1] == expr[2] else visit(expr[2])
        name = "v" + str(len(instructions))
        instructions.append(f"    {name} = lanes ^ ({left} & {right})")
        return name
    result = visit(program["expr"])
    if len(instructions) != program["nand_gates"]:
        raise ValueError("Pinned binary parser gate count disagrees with its syntax")
    source = "\n".join(["def run(first, second, lanes):", *instructions, "    return " + result])
    namespace = {"__builtins__": {}}
    exec(source, namespace)
    implementation = namespace["run"]
    mask = sum(implementation(i & 1, i >> 1, 1) << i for i in range(4))
    if mask != program["truth_mask"]:
        raise ValueError("Compiled NAND program changed its binary function")
    return implementation


LITERAL, CLAUSE, QUESTION = (_compile(PARSER[name]) for name in ("literal","clause","question"))


def parser_gate_cost(question):
    pins = sum(map(len, question))
    return pins * (PARSER["literal"]["nand_gates"] + PARSER["clause"]["nand_gates"]) + len(question) * PARSER["question"]["nand_gates"]


def _scan(question, columns, lanes):
    value = lanes if PARSER["question_initial"] else 0
    for row in question:
        met = lanes if PARSER["clause_initial"] else 0
        for pin in row:
            literal = LITERAL(columns[abs(pin) - 1], lanes if pin < 0 else 0, lanes)
            met = CLAUSE(met, literal, lanes)
        value = QUESTION(value, met, lanes)
    return value


def public_columns(wiring, raw_masks):
    masks = tuple(raw_masks)
    if not masks:
        raise ValueError("At least one hypothetical input is required")
    if masks == ALL_RAW:
        columns = FULL_COLUMNS
    else:
        if any(type(raw) is not int or not 0 <= raw < 512 for raw in masks):
            raise ValueError("Probes must be nine-bit hypothetical inputs")
        columns = tuple(sum(((raw >> i) & 1) << lane for lane, raw in enumerate(masks)) for i in range(9))
    lanes = (1 << len(masks)) - 1
    gates = sum(map(parser_gate_cost, wiring))
    return tuple(_scan(q, columns, lanes) for q in wiring), {
        "public_rows":len(masks), "public_parser_calls":len(wiring) * len(masks),
        "public_scalar_nands":gates * len(masks), "public_packed_nands":gates,
    }


def query_values(wiring, raw, ports):
    if type(raw) is not int or not 0 <= raw < 512:
        raise ValueError("Expected a nine-bit source")
    columns = tuple((raw >> i) & 1 for i in range(9))
    return tuple(_scan(wiring[p], columns, 1) for p in ports)


def validate_channel(packet, width, port):
    if type(port) is not int or not 0 <= port < 4 or len(packet) != width:
        raise ValueError("Delayed port or physical packet length is invalid")
    if any(type(b) not in (bool, int) or b not in (0, 1) for b in packet):
        raise ValueError("A physical slot must carry a bit")
