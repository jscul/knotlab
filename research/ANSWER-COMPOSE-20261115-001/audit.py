"""Independent scalar and communication-bound audit for ANSWER-COMPOSE.

The learned proposal, public certification and returned program are separate
objects. No producer fitter, grading routine or old sender is executed here.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from collections import Counter
import hashlib
from functools import lru_cache
from itertools import permutations, combinations
import json
from pathlib import Path
import random
import importlib.util
import math
import statistics


TICKET = "ANSWER-COMPOSE-20261115-001"
FAMILY = TICKET + "-E001_packet_nand"
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "artifacts" / TICKET / FAMILY
ARMS = ("raw", "certified", "lookup", "four", "one_call")


class AuditError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise AuditError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bit(value):
    require(type(value) is int and value in (0, 1), "Expected a literal binary bit")
    return value


def nand(expr, values, actions=None):
    require(isinstance(expr, (tuple, list)) and expr, "Malformed atomic program")
    if expr[0] in ("input", "const"):
        require(len(expr) == 2, "Malformed leaf")
        if expr[0] == "input":
            require(type(expr[1]) is int and 0 <= expr[1] < len(values), "Invalid input index")
            if actions is not None:
                actions["READ"] += 1
            return bit(values[expr[1]])
        if actions is not None:
            actions["CONST"] += 1
        return bit(expr[1])
    require(expr[0] == "NAND" and len(expr) == 3, "Only NAND, copy and constants are admitted")
    left = nand(expr[1], values, actions)
    if expr[1] == expr[2]:
        right = left
        if actions is not None:
            actions["COPY"] += 1
    else:
        right = nand(expr[2], values, actions)
    if actions is not None:
        actions["NAND"] += 1
    return 1 - left * right


def nand_cost(expr):
    if expr[0] in ("input", "const"):
        return 0
    return 1 + nand_cost(expr[1]) + (0 if expr[1] == expr[2] else nand_cost(expr[2]))


def validate_plan(plan):
    validate_ports(plan)
    ports = plan["ports"]
    require(plan.get("parameter_updates", 0) == 0, "Policy parameters changed at deployment")
    if len(ports) == 4:
        require(plan["dag"] is None, "A four-bit copy plan has an unexpected decoder")
        return
    dag = plan["dag"]
    require(isinstance(dag, dict) and set(dag) == {"gates", "output"}, "Invalid decoder DAG")
    for index, gate in enumerate(dag["gates"]):
        require(isinstance(gate, list) and len(gate) == 2 and
                all(type(address) is int and 0 <= address < index + 5 for address in gate),
                "A NAND gate reads an unavailable packet/constant/previous-gate address")
    require(type(dag["output"]) is int and 0 <= dag["output"] < len(dag["gates"]) + 5, "Invalid output tap")


def validate_ports(plan):
    ports = plan["ports"]
    require(isinstance(ports, list) and len(ports) in (3, 4) and ports == sorted(set(ports)) and
            all(type(port) is int and 0 <= port < 4 for port in ports), "Invalid physical computed-port addresses")
    omitted = sorted(set(range(4)) - set(ports))
    require(plan["omitted_port"] == (omitted[0] if omitted else None), "Omitted port differs from actual payload")


def decode(plan, packet, port, actions=None):
    """Receiver sees only the public program, its physical bits and late port."""
    validate_plan(plan)
    require(type(packet) is tuple and len(packet) == len(plan["ports"]), "Non-tuple or wrong-width physical channel")
    for value in packet:
        bit(value)
    require(type(port) is int and 0 <= port < 4, "Invalid delayed question")
    if port in plan["ports"]:
        if actions is not None:
            actions.update({"READ": 1, "COPY": 1, "WRITE": 1})
        return packet[plan["ports"].index(port)]
    values = list(packet) + [0, 1]
    for left, right in plan["dag"]["gates"]:
        values.append(1 - values[left] * values[right])
        if actions is not None:
            actions["NAND"] += 1
            actions["CONST" if left in (3, 4) else "READ"] += 1
            if right != left:
                actions["CONST" if right in (3, 4) else "READ"] += 1
            actions["COPY"] += left == right
            actions["WRITE"] += 1
    if actions is not None:
        actions["CONST" if plan["dag"]["output"] in (3, 4) else "READ"] += 1
        actions["WRITE"] += 1
    return values[plan["dag"]["output"]]


def tuple_tree(value):
    return tuple(tuple_tree(child) for child in value) if isinstance(value, list) else value


class SourceParser:
    """Independent execution of the shared frozen binary NAND parser."""

    def __init__(self, parser):
        self.parser = parser
        for role in ("literal", "clause", "question"):
            record = parser[role]
            require(record["inputs"] == 2 and record["nand_gates"] == nand_cost(record["expr"]), "Parser NAND metadata differs")
            require(record["truth_mask"] == sum(nand(record["expr"], (i & 1, i >> 1)) << i for i in range(4)),
                    "Parser truth metadata differs")

    def answer(self, question, raw):
        state = self.parser["question_initial"]
        for clause in question:
            row = self.parser["clause_initial"]
            for pin in clause:
                literal = nand(self.parser["literal"]["expr"], (raw >> (abs(pin) - 1) & 1, int(pin < 0)))
                row = nand(self.parser["clause"]["expr"], (row, literal))
            state = nand(self.parser["question"]["expr"], (state, row))
        return state

    @lru_cache(None)
    def table(self, question):
        return tuple(self.answer(question, raw) for raw in range(512))


def gate_cost(question):
    # The actual pinned parser has5+2 NANDs per literal and2 per clause.
    return 7 * sum(map(len, question)) + 2 * len(question)


def inline_calls(library, calls, output):
    gates, refs = [], list(range(5))
    def inline(expr, operands):
        if expr[0] == "input":
            return operands[expr[1]]
        if expr[0] == "const":
            return 3 + expr[1]
        left = inline(expr[1], operands)
        right = left if expr[1] == expr[2] else inline(expr[2], operands)
        gates.append((left, right))
        return len(gates) + 4
    for operator, left, right in calls:
        refs.append(inline(library[operator]["expr"], (refs[left], refs[right])))
    live = set()
    def visit(address):
        if address >= 5 and address not in live:
            live.add(address)
            for operand in gates[address - 5]:
                visit(operand)
    visit(refs[output])
    remap, retained = dict(enumerate(range(5))), []
    for address in sorted(live):
        remap[address] = len(retained) + 5
        retained.append([remap[operand] for operand in gates[address - 5]])
    return {"gates": retained, "output": remap[refs[output]]}, len(gates)


def dag_signature(dag):
    p = {"ports": [0,1,2], "omitted_port": 3, "dag": dag}
    return sum(decode(p, tuple(i >> bit & 1 for bit in range(3)), 3) << i for i in range(8))


def candidates(library, maximum_calls):
    require(maximum_calls in (1, 2), "Unexpected composition limit")
    best, offered, unpruned, packed = {}, 0, 0, 0
    def offer(calls, output):
        nonlocal offered, unpruned, packed
        dag, raw_cost = inline_calls(library, calls, output)
        sig = dag_signature(dag)
        key = (len(dag["gates"]), len(calls), calls, output)
        item = {"signature": sig, "calls": calls, "output": output, "dag": dag, "key": key}
        offered += 1
        unpruned += raw_cost
        packed += len(dag["gates"])
        if sig not in best or key < best[sig]["key"]:
            best[sig] = item
    for output in range(5):
        offer((), output)
    for op in range(len(library)):
        for left in range(5):
            for right in range(5):
                first = ((op, left, right),)
                offer(first, 5)
                if maximum_calls == 2:
                    for second in range(len(library)):
                        for a in range(6):
                            for b in range(6):
                                if a == 5 or b == 5:
                                    offer(first + ((second, a, b),), 6)
    ordered = sorted(best.values(), key=lambda item: item["key"] + (item["signature"],))
    return ordered, {"abstract_programs_generated": offered, "semantic_candidates": len(ordered),
                     "candidate_syntax_NAND_nodes": unpruned, "signature_packed_NANDs": packed,
                     "signature_scalar_NANDs": 8 * packed,
                     "required_fragment_groups": 1 + len(library) + (len(library) * (len(library) - 1) // 2 if maximum_calls == 2 else 0)}


def public_proposal(checkpoint, wiring, source, pool, catalogue, max_calls):
    probes = checkpoint["probe_masks"]
    rows = [tuple(source.table(question)[raw] for question in wiring) for raw in probes]
    chosen, tested, matched = None, 0, 0
    for omitted in range(4):
        ports = tuple(p for p in range(4) if p != omitted)
        groups = {}
        consistent = True
        for row in rows:
            code = sum(row[p] << i for i, p in enumerate(ports))
            if code in groups and groups[code] != row[omitted]:
                consistent = False
            groups[code] = row[omitted]
        if not consistent:
            continue
        known = sum(1 << code for code in groups)
        ones = sum(value << code for code, value in groups.items())
        for index, item in enumerate(pool):
            tested += 1
            if item["signature"] & known != ones:
                continue
            matched += 1
            rank = (len(item["dag"]["gates"]), len(item["calls"]), ports, item["calls"], item["output"], item["signature"])
            if chosen is None or rank < chosen[0]:
                chosen = rank, ports, omitted, index, item
            break
    public = {"public_rows": len(probes), "public_parser_calls": len(wiring) * len(probes),
              "public_scalar_nands": sum(map(gate_cost, wiring)) * len(probes),
              "public_packed_nands": sum(map(gate_cost, wiring)), "three_port_subsets": 4,
              "public_candidate_tests": tested, "public_constraint_code_rows": 32,
              "public_constraint_bitset_AND": 160, "public_constraint_bitset_XOR": 80,
              "probe_consistent_candidates": matched, "catalogue_semantic_candidates": len(pool),
              "catalogue_abstract_programs": catalogue["abstract_programs_generated"],
              "catalogue_fragment_groups_cold": catalogue["required_fragment_groups"],
              "catalogue_packed_NANDs_cold": catalogue["signature_packed_NANDs"],
              "catalogue_scalar_NANDs_cold": catalogue["signature_scalar_NANDs"], "composition_generator_learned": 0}
    if chosen is None:
        result = {"ports": [0,1,2,3], "omitted_port": None, "dag": None, "candidate_id": None, "candidate": None,
                  "proposal_reason": "no three-slot circuit matched the public probe rows"}
    else:
        _, ports, omitted, index, item = chosen
        result = {"ports": list(ports), "omitted_port": omitted, "dag": item["dag"],
                  "candidate_id": f"fn-{item['signature']:02x}/calls-{len(item['calls'])}/index-{index}",
                  "candidate": {"truth_signature": item["signature"], "library_calls": [list(call) for call in item["calls"]],
                                "abstract_output": item["output"], "library_applications": len(item["calls"]), "catalogue_index": index},
                  "proposal_reason": "minimum-work three-slot circuit matching the public probes"}
    result.update(public_actions=public, max_calls=max_calls, probe_count=len(probes), raw_proposal=True,
                  parameter_updates=0, external_certificate_used=False)
    result["proposal_sha256"] = digest(result)
    return result


def four_plan():
    return {"ports": [0,1,2,3], "omitted_port": None, "dag": None}


def public_rows(wiring, source):
    return [tuple(source.table(question)[raw] for question in wiring) for raw in range(512)]


def public_ledger(wiring):
    gates = sum(map(gate_cost, wiring))
    return {"public_rows": 512, "public_parser_calls": 2048,
            "public_scalar_nands": 512 * gates, "public_packed_nands": gates}


def certificate(wiring, proposed, source):
    validate_plan(proposed)
    if len(proposed["ports"]) == 4:
        return four_plan(), {"status": "four_by_construction", "public_rows": 0, "wrong_rows": 0}
    wrong = 0
    omitted = proposed["omitted_port"]
    for row in public_rows(wiring, source):
        packet = tuple(row[port] for port in proposed["ports"])
        wrong += decode(proposed, packet, omitted) != row[omitted]
    gates = len(proposed["dag"]["gates"])
    ledger = public_ledger(wiring) | {"status": "fallback_four" if wrong else "certified_three", "wrong_rows": wrong,
                                      "decoder_packed_nands": gates, "decoder_scalar_nands": 512 * gates}
    return (four_plan() if wrong else proposed), ledger


def lookup_compile(wiring, source):
    vectors = sorted({signature(row) for row in public_rows(wiring, source)})
    ledger = public_ledger(wiring) | {"patterns": len(vectors), "packed_intersections": 30,
                                      "omission_trials": 0, "table_entries_checked": 0}
    if len(vectors) <= 8:
        for omitted in range(4):
            ledger["omission_trials"] += 1
            ports = [port for port in range(4) if port != omitted]
            entries = {}
            for vector in vectors:
                packet = sum((vector >> port & 1) << i for i, port in enumerate(ports))
                output = vector >> omitted & 1
                ledger["table_entries_checked"] += 1
                if packet in entries and entries[packet] != output:
                    break
                entries[packet] = output
            else:
                return {"ports": ports, "omitted_port": omitted,
                        "lookup": sum(value << packet for packet, value in entries.items())}, ledger
    return four_plan(), ledger


def lookup_decode(plan, packet, port):
    validate_ports(plan)
    require(type(packet) is tuple and len(packet) == len(plan["ports"]) and type(port) is int and 0 <= port < 4,
            "Invalid lookup physical channel")
    for value in packet:
        bit(value)
    if port in plan["ports"]:
        return packet[plan["ports"].index(port)]
    key = sum(value << i for i, value in enumerate(packet))
    return plan["lookup"] >> key & 1


def raw_answers(wiring, raw):
    require(type(raw) is int and 0 <= raw < 512, "Expected nine raw input bits")
    result = []
    for question in wiring:
        answer = 1
        for clause in question:
            satisfied = False
            for pin in clause:
                require(type(pin) is int and 1 <= abs(pin) <= 9, "Invalid signed occurrence")
                if (raw >> (abs(pin) - 1) & 1) == int(pin > 0):
                    satisfied = True
            answer *= int(satisfied)
        result.append(answer)
    return tuple(result)


def signature(row):
    require(len(row) == 4, "Exactly four late question answers are required")
    return sum(bit(value) << port for port, value in enumerate(row))


def signed_port_orbit(rows):
    """Canonical allowed-answer relation under all 24*16 signed port maps."""
    patterns = {tuple(row) for row in rows}
    return min(sum(1 << (sum(row[port] << i for i, port in enumerate(order)) ^ sign_mask)
                   for row in patterns)
               for order in permutations(range(4)) for sign_mask in range(16))


def anf_degree(values):
    """Algebraic degree of a complete three-bit readout, by finite differences."""
    require(len(values) == 8 and all(value in (0, 1) for value in values), "A complete Boolean cube is required")
    coefficients = list(values)
    for source in range(3):
        for address in range(8):
            if address >> source & 1:
                coefficients[address] ^= coefficients[address ^ (1 << source)]
    return max((address.bit_count() for address, coefficient in enumerate(coefficients) if coefficient), default=0)


def communication_bounds(rows):
    patterns = {tuple(row) for row in rows}
    projections = []
    for omitted in range(4):
        groups = {}
        first_collision = None
        for raw, row in enumerate(rows):
            packet = tuple(value for port, value in enumerate(row) if port != omitted)
            previous = groups.setdefault(packet, (raw, tuple(row)))
            if previous[1] != tuple(row) and first_collision is None:
                first_collision = {"raw_masks": [previous[0], raw], "packet": packet,
                                   "answers": [previous[1], tuple(row)]}
        record = {"omitted": omitted, "retained": [port for port in range(4) if port != omitted],
                  "distinct_packets": len(groups), "identifies_all_answers": first_collision is None,
                  "first_collision": first_collision}
        if first_collision is None and len(groups) == 8:
            table = [None] * 8
            for packet, (_, row) in groups.items():
                address = sum(value << i for i, value in enumerate(packet))
                table[address] = row[omitted]
            record.update({"omitted_truth_mask": sum(value << i for i, value in enumerate(table)),
                           "omitted_readout_degree": anf_degree(table)})
        projections.append(record)
    offsets = {signature(row) for row in patterns}
    base = min(offsets)
    differences = {value ^ base for value in offsets}
    affine = all(a ^ b in differences for a in differences for b in differences)
    return {"answer_patterns": len(patterns), "minimum_bits": (len(patterns) - 1).bit_length(),
            "signed_port_orbit": signed_port_orbit(patterns), "affine_relation": affine,
            "three_computed_port_projections": projections,
            "any_three_computed_ports_identify": any(row["identifies_all_answers"] for row in projections)}


def rosters():
    """Independent reconstruction of the sealed literal input recipes."""
    A, B, C, D, E, F, G, H = range(1, 9)
    def cnf(*rows, pad):
        result = []
        for i, row in enumerate(rows):
            width = 3 if i == 0 else 2
            result.append(tuple(row) + (row[-1],) * (width - len(row)))
        return tuple(result + [(pad, -pad)] * (4 - len(result)))
    U = lambda v: cnf((v,), pad=v)
    AND = lambda *v: cnf(*((x,) for x in v), pad=v[0])
    OR = lambda *v: cnf(v, pad=v[-1])
    XOR = lambda x,y: cnf((x,y),(-x,-y),pad=y)
    OA = lambda x,y,z: cnf((x,y),(x,z),pad=z)
    MUX = lambda s,y,n: cnf((-s,y),(s,n),pad=n)
    lo, ro, la, ra, independent = OR(A,B), OR(C,D), AND(A,B), AND(C,D), XOR(E,F)
    triangle = (XOR(A,B), XOR(B,C), XOR(D,E))
    training = {"and_disjoint":(lo,ro,independent,cnf((A,B),(C,D),pad=C)),
                "and_overlap":(la,AND(B,C),OR(D,E),AND(A,B,C)),
                "or_disjoint":(la,ra,independent,cnf((A,C),(A,D),(B,C),(B,D),pad=C)),
                "or_overlap":(lo,OR(B,C),AND(D,E),OR(A,B,C)),
                "xor_triangle":triangle+(XOR(A,C),),
                "xor_separate":(U(-A),U(B),AND(C,E),XOR(-A,B)),
                "open_four_compounds":triangle+(XOR(A,F),),
                "open_correlated":(lo,ro,independent,cnf((A,B),(C,G),pad=C))}
    base, split = (OA(A,B,C),OA(A,B,-C),U(D)), (OA(A,B,C),OA(A,-B,H),U(D))
    mux_base, rare_base = (U(A),AND(B,D),AND(C,E)), (AND(A,B),AND(C,D),AND(E,F))
    mc = lambda selector: cnf((-selector,B),(-selector,D),(selector,C),(selector,E),pad=B)
    held = {"primary":(base+(XOR(A,D),),base+(XOR(E,D),)),
            "split_source":(split+(XOR(A,D),),split+(XOR(E,D),)),
            "and_or":(base+(OR(A,D),),base+(OR(E,D),)),
            "mux":(mux_base+(mc(A),),mux_base+(mc(F),)),
            "rare":(rare_base+(AND(A,B,C,D),),rare_base+(AND(A,B,C,H),))}
    orders = tuple(permutations(range(4)))
    def recode(template, family, split, layout, seed, order):
        rng = random.Random(seed)
        sources = rng.sample(range(1,10),9)
        phase = [rng.getrandbits(1) for _ in sources]
        physical = []
        for question in template:
            rows = []
            for row in question:
                pins = [(-sources[abs(v)-1] if (v < 0) ^ bool(phase[abs(v)-1]) else sources[abs(v)-1]) for v in row]
                rng.shuffle(pins)
                rows.append(tuple(pins))
            rng.shuffle(rows)
            physical.append(tuple(rows))
        wiring = tuple(physical[p] for p in order)
        identity = hashlib.sha256(json.dumps(wiring,separators=(",",":")).encode()).hexdigest()[:16]
        return identity,wiring,{"family":family,"split":split,"layout":layout,"port_order":list(order),
                               "cell_order":[s-1 for s in sources],"cell_phase":phase}
    train, test = [], []
    for i,(family,template) in enumerate(training.items()):
        order = orders[(5*i+1)%24]
        for layout in range(4):
            rotated = order[layout:]+order[:layout]
            train.append(recode(template,family,"train",f"{family}-{layout}",70127+241*i+19*layout,rotated))
    for i,(group,templates) in enumerate(held.items()):
        selected = orders if group=="primary" else tuple(orders[(2+i+5*j)%24] for j in range(4))
        for layout,order in enumerate(selected):
            pair = [recode(template,f"{group}_{side}","held",f"{group}-{layout}",91387+1493*i+23*layout,order)
                    for side,template in zip(("closed","open"),templates,strict=True)]
            pair[0][2]["partner"],pair[1][2]["partner"] = pair[1][0],pair[0][0]
            test.extend(pair)
    prior_path = ROOT / "research/GROUP-SENDER-20261115-001/audit.py"
    require(file_digest(prior_path)=="7e8d278a85bf4a9ef58dccb09853a01c5808285f1f2fffbcb67b4730b7f106f0",
            "Prior independent public-input reconstruction changed")
    spec = importlib.util.spec_from_file_location("prior_independent_inputs_only",prior_path)
    prior = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior)
    old = {key:(w,m) for key,w,m in prior.rosters()["held"] if m["family"] in ("xor_closed","xor_open")}
    pairs = (("e222e4c6f70ebd38","5becdc37b516b478"),("3a072e9eb4c9ff46","b511178208ab2c81"),
             ("148d2df296a6bc85","4b4bf998127df26c"),("d9a601d3e6ebdf8b","27388477186a5ba0"))
    for layout,pair in enumerate(pairs):
        for key,other in (pair,pair[::-1]):
            wiring,meta = old[key]
            require(meta["partner"]==other,"Archived XOR pairing changed")
            test.append((key,wiring,dict(meta,split="held",layout=f"archived-{layout}",original_id=key,
                                          cell_phase=[0]*9,source_ticket="GROUP-SENDER-20261115-001")))
    collision = (MUX(B,A,C),cnf((-A,C),(A,-C),(A,B),(-A,-B),pad=A),
                 cnf((B,),(A,C),(-A,-C),pad=B),cnf((A,),(-B,C),(B,-C),pad=A))
    test.append(recode(collision,"projection_collision","held","collision-0",129293,orders[17]))
    return train,test


def equality(actual, expected, label):
    require(canonical(actual)==canonical(expected),"Independent mismatch: "+label)


def measure(wiring, gold, arm, outbound, inbound, source):
    equality(outbound,inbound,"public plans at separate endpoints")
    validate_ports(outbound)
    per_port, correct, odd, full, first = [0]*4,0,0,0,None
    transcript = bytearray()
    for raw,wanted in enumerate(gold):
        packet = tuple(source.table(wiring[p])[raw] for p in outbound["ports"])
        require(len(packet)==len(outbound["ports"]),"Input-dependent physical width")
        transcript.extend((len(packet),*packet))
        read = lookup_decode if arm in ("lookup","four") else decode
        returned = tuple(read(inbound,packet,p) for p in range(4))
        matches = [a==b for a,b in zip(wanted,returned,strict=True)]
        correct += sum(matches)
        full += all(matches)
        odd += (raw.bit_count()%2)*sum(matches)
        per_port = [a+b for a,b in zip(per_port,matches,strict=True)]
        if first is None and not all(matches):
            first = {"raw":raw,"packet":packet,"wanted":wanted,"returned":returned}
    return {"width":len(outbound["ports"]),"ports":tuple(outbound["ports"]),"omitted_port":outbound["omitted_port"],
            "correct_questions":correct,"correct_vectors":full,"correct_odd":odd,"correct_by_port":per_port,
            "first_error":first,"physical_sha256":hashlib.sha256(transcript).hexdigest(),
            "decoder_nands":len((outbound.get("dag") or {}).get("gates",[]))}


def summarize(rows):
    result = {}
    for arm in ARMS:
        rec = [(row,row["arms"][arm]) for row in rows]
        result[arm] = {"correct_questions":sum(v["correct_questions"] for _,v in rec),"total_questions":2048*len(rec),
                       "correct_odd":sum(v["correct_odd"] for _,v in rec),
                       "all_exact_wirings":sum(v["correct_vectors"]==512 for _,v in rec),
                       "exact_minimum_wirings":sum(v["correct_vectors"]==512 and v["width"]==r["minimum_bits"] for r,v in rec),
                       "exact_projection_wirings":sum(v["correct_vectors"]==512 and v["width"]==r["projection_bits"] for r,v in rec),
                       "widths":dict(Counter(v["width"] for _,v in rec)),"sum_width":sum(v["width"] for _,v in rec)}
    return result


def generic_binary():
    best = {0:("const",0),15:("const",1),10:("input",0),12:("input",1)}
    levels, costs = [dict(best)], {mask:0 for mask in best}
    for size in range(1,6):
        current = {}
        def offer(mask,expr):
            if mask not in best and (mask not in current or expr<current[mask]):
                current[mask] = expr
        for i in range(size):
            for lm,left in levels[i].items():
                for rm,right in levels[size-i-1].items():
                    if left<=right:
                        offer(15^(lm&rm),("NAND",left,right))
        for mask,child in levels[size-1].items():
            offer(15^mask,("NAND",child,child))
        levels.append(current)
        best.update(current)
        costs.update({mask:size for mask in current})
    require(len(best)==16,"Incomplete independent binary NAND catalogue")
    return [{"inputs":2,"expr":expr,"nand_gates":costs[mask],"truth_mask":mask}
            for mask,expr in sorted(best.items(),key=lambda item:(costs[item[0]],item[1]))]


def bindings(out):
    load = lambda name: json.loads((out/name).read_bytes())
    binding, freeze = load("checkpoint_binding.json"),load("freeze.json")
    for name,key in (("checkpoint.json","checkpoint_sha256"),("freeze.json","sources_sha256"),
                     ("results.jsonl","training_output_sha256")):
        require(file_digest(out/name)==binding[key],"Broken source/checkpoint binding: "+name)
    require(freeze["before_fit"] is True,"Fit lacks a pre-fit source freeze")
    for relative,sha in freeze["files"].items():
        require(file_digest(ROOT/relative)==sha,"Frozen source/dependency changed: "+relative)
    raw = [json.loads(line) for line in (out/"results.jsonl").read_text().splitlines()]
    require(len(raw)==1 and raw[0]["case"]=="packet_nand" and raw[0]["status"]=="ok","Training record is incomplete")
    record,cp = raw[0]["result"],load("checkpoint.json")
    require((out/"checkpoint.json").read_bytes()==canonical(cp),"Checkpoint is not canonical frozen bytes")
    equality(cp,record["checkpoint"],"checkpoint vs original fitted parameters")
    require(digest(cp)==record["checkpoint_sha256"]==binding["checkpoint_sha256"],"Fitted digest differs")
    require(datetime.fromisoformat(raw[0]["finished_at"])>=datetime.fromisoformat(freeze["utc"]),"Fit predates source freeze")
    base = "experiments/"+TICKET+"/"+FAMILY+"/"
    require(raw[0]["job_sha"]==freeze["files"][base+"job.py"] and
            record["history"]["learner_sha256"]==freeze["files"][base+"learner.py"],"Fit used different code")
    for field,path in (("packet_io_sha256",base+"packet_io.py"),
                       ("codec_sha256","experiments/BIT-DECODER-20261114-001/BIT-DECODER-20261114-001-E001_atomic_codec/codec.py"),
                       ("parser_sha256","artifacts/BIT-DECODER-20261114-001/BIT-DECODER-20261114-001-E001_atomic_codec/varied_checkpoint.json")):
        require(cp[field]==freeze["files"][path],"Checkpoint component binding differs: "+field)
    catalogue = generic_binary()
    ids = cp["library_ids"]
    require(len(ids) in (1,2,3) and ids==sorted(set(ids)) and all(type(i) is int and 0<=i<16 for i in ids),"Invalid retained library")
    equality(cp["library"],[catalogue[i] for i in ids],"library syntax vs generic NAND catalogue")
    order = sorted(range(512),key=lambda raw:hashlib.sha256(f"answer-compose-probes-v1|{raw}".encode()).digest())
    require(cp["probe_count"] in (8,16,32,64,128) and cp["probe_masks"]==order[:cp["probe_count"]] and
            cp["max_library_applications"]==2,"Frozen public probe/composition grammar differs")
    return binding,freeze,cp,record,catalogue


def check_costs(out, rows, plans, fitted, wirings):
    value = json.loads((out/"costs.json").read_bytes())
    require(value["plans_sha256"]==file_digest(out/"plans.json"),"Timing benchmark used different plans")
    runs = value["runs"]
    require(len(runs)==18 and {(r["method"],r["side"],r["repeat"]) for r in runs}==
            {(m,s,i) for m in ("certified","lookup","four") for s in ("sender","receiver") for i in range(3)},
            "Missing endpoint timing cells")
    for run in runs:
        method, side = run["method"],run["side"]
        require(run["wirings"]==len(rows) and run["uses_per_wiring"]==128,"Different timing workload")
        width = sum(row["arms"][method]["width"] for row in rows)
        require(run["sum_packet_width"]==width,"Timing packet widths differ")
        source_nands,decoder_nands,lut = 0,0,0
        for row in rows:
            plan = plans[row["id"]][side][method]
            if side=="sender":
                source_nands += 128*71*len(plan["ports"])
            else:
                queries = 32 if plan["omitted_port"] is not None else 0
                decoder_nands += queries*len((plan.get("dag") or {}).get("gates",[]))
                lut += queries*int("lookup" in plan)
        equality((run["physical_parser_nands"],run["physical_decoder_nands"],run["physical_lut_reads"]),
                 (source_nands,decoder_nands,lut),"timed physical primitive counts")
        require(all(type(run[k]) is int and run[k]>=0 for k in
                    ("load_ns","plan_ns","explicit_certificate_ns","prepare_reader_ns","traffic_ns","scientific_qa_ns")),
                "Invalid CPU timing counter")
        if side=="sender":
            require(run["observed"]==128*width,"Sender benchmark didn't materialize all packet bits")
        else:
            observed=sum(raw_answers(wirings[row["id"]],(149*k+37*index)&511)[(k+index)%4]
                         for index,row in enumerate(rows) for k in range(128))
            require(run["observed"]==observed,"Receiver benchmark traffic checksum differs")
    def close(a,b,label):
        require(math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12),"Cost arithmetic differs: "+label)
    derived = {}
    for method in ("certified","lookup","four"):
        part = [r for r in runs if r["method"]==method]
        def sums(key,divisor=1):
            return [sum(r[key] for r in part if r["repeat"]==i)/(1e9*divisor) for i in range(3)]
        keys = ("load_ns","plan_ns","explicit_certificate_ns","prepare_reader_ns")
        setup = [sum(sum(r[k] for k in keys) for r in part if r["repeat"]==i)/1e9 for i in range(3)]
        target = value["profiles"][method]
        close(target["setup_s"]["median"],statistics.median(setup),"both-endpoint setup")
        equality(target["setup_s"]["range"],[min(setup),max(setup)],"setup spread")
        for key in keys:
            close(target["components_s"][key]["median"],statistics.median(sums(key)),key)
        traffic = statistics.median(sums("traffic_ns",128))
        close(target["traffic_s_per_use_of_each_wiring"]["median"],traffic,"both-endpoint traffic")
        acquisition = fitted["fit_cpu_seconds"] if method=="certified" else 0
        close(target["acquisition_s"],acquisition,"new training acquisition")
        model_bits = (out/"checkpoint.json").stat().st_size*8 if method=="certified" else 0
        require(target["checkpoint_bits_distributed_once"]==model_bits,"One-time parameter transfer omitted")
        require(target["packet_bits_per_use_of_each_wiring"]==part[0]["sum_packet_width"],"Marginal physical bits differ")
        derived[method]=(acquisition+statistics.median(setup),traffic,model_bits,part[0]["sum_packet_width"])
    for price,report in value["link_us_per_bit"].items():
        coefficients = {m:[a+int(price)*1e-6*size,b+int(price)*1e-6*width]
                        for m,(a,b,size,width) in derived.items()}
        for m,pair in coefficients.items():
            for x,y in zip(pair,report["coefficients_seconds"][m],strict=True):
                close(x,y,"cost line")
        for uses,totals in report["projected_seconds"].items():
            for method,(a,b) in coefficients.items():
                close(totals[method],a+int(uses)*b,"extrapolated operating point")
        low,high,impossible=1,None,False
        a,b=coefficients["certified"]
        for method in ("lookup","four"):
            c,d=coefficients[method]
            offset,slope=a-c,b-d
            if slope==0:
                impossible |= offset>=0
            elif slope<0:
                low=max(low,math.floor(offset/(-slope))+1)
            else:
                limit=math.ceil(-offset/slope)-1
                high=limit if high is None else min(high,limit)
        interval=None if impossible or (high is not None and high<low) else [low,high]
        equality(interval,report["uses_per_wiring_where_certified_beats_both"],"strict lower-envelope break-even interval")
    return {"status":"pass","endpoint_runs":18,"profiles":value["profiles"],"link_models":value["link_us_per_bit"],
            "scope":"In-process measured phases at both endpoints; process/common-parser startup and scientific QA excluded. Projections are extrapolations, link prices are assumptions.",
            "costs_sha256":file_digest(out/"costs.json")}


def audit(out):
    out=Path(out)
    binding,freeze,cp,fitted,binary=bindings(out)
    train,held=rosters()
    require(len(train)==freeze["train_count"]==32 and len(held)==freeze["held_count"]==89,"Panel sizes differ")
    require(digest(train)==freeze["training_panel_sha256"] and digest(held)==freeze["held_panel_sha256"],"Independent raw roster hash differs")
    require(len({w for _,w,_ in train+held})==121,"Raw wiring duplicated across split")
    prior=ROOT/"artifacts/BIT-DECODER-20261114-001/BIT-DECODER-20261114-001-E001_atomic_codec/varied_checkpoint.json"
    source=SourceParser(json.loads(prior.read_bytes())["parser"])
    pools={calls:candidates(cp["library"],calls) for calls in (1,2)}
    proposed=json.loads((out/"raw_proposals.json").read_bytes())
    require(proposed["checkpoint_sha256"]==binding["checkpoint_sha256"],"Raw plans bind another policy")
    planned=json.loads((out/"plans.json").read_bytes())
    require(planned["proposal_sha256"]==file_digest(out/"raw_proposals.json"),"Certificate changed raw proposals")
    official=json.loads((out/"result.json").read_bytes())
    require(official["plans_sha256"]==file_digest(out/"plans.json"),"Grade changed plans")
    results,bounds,train_orbits=[],{},set()
    for _,w,_ in train:
        train_orbits.add(signed_port_orbit([raw_answers(w,raw) for raw in range(512)]))
    matched=Counter()
    by_id={key:(w,m) for key,w,m in held}
    for index,(key,w,meta) in enumerate(held):
        gold=[raw_answers(w,raw) for raw in range(512)]
        for p,q in enumerate(w):
            equality(source.table(q),[r[p] for r in gold],"source NAND vs literal satisfaction")
        bound=communication_bounds(gold)
        bounds[key]={"metadata":meta,**bound}
        raw=public_proposal(cp,w,source,*pools[2],2)
        one=public_proposal(cp,w,source,*pools[1],1)
        equality({"raw":raw,"one_call":one},proposed["plans"][key],"raw public program search")
        certified,certificate_work=certificate(w,raw,source)
        lookup,lookup_work=lookup_compile(w,source)
        generated={"raw":raw,"one_call":one,"certified":certified,"lookup":lookup,"four":four_plan()}
        entry=planned["wirings"][key]
        equality(generated,entry["sender"],"sender compilation and fallback")
        equality(generated,entry["receiver"],"receiver recomputes public routing without sender state")
        equality(certificate_work,entry["certificate"],"all failed certificate rows charged")
        equality(lookup_work,entry["lookup_work"],"lookup projection/compiler work")
        possible=[r["omitted"] for r in bound["three_computed_port_projections"] if r["identifies_all_answers"]]
        record={"id":key,"metadata":meta,"distinct_answers":bound["answer_patterns"],"minimum_bits":bound["minimum_bits"],
                "possible_omissions":possible,"projection_bits":3 if possible else 4,
                "arms":{arm:measure(w,gold,arm,generated[arm],entry["receiver"][arm],source) for arm in ARMS},
                "even_answer_parity_rows":sum(sum(row)%2==0 for row in gold),
                "certificate_status":certificate_work["status"],"certificate_wrong_rows":certificate_work["wrong_rows"]}
        equality(record,official["rows"][index],"physical all-input/late-port grade "+key)
        results.append(record)
        if meta["family"].endswith("_closed") and "partner" in meta:
            partner,other=by_id[meta["partner"]]
            changed=[p for p in range(4) if w[p]!=partner[p]]
            require(changed==[meta["port_order"].index(3)] and other["partner"]==key,"Matched intervention changed another port")
            changes=sum(raw_answers(w,r)[changed[0]]!=raw_answers(partner,r)[changed[0]] for r in range(512))
            matched[meta["family"]]+=changes
    equality(summarize(results),official["summary"],"all arm totals")
    for family in {m["family"] for _,_,m in held}:
        equality(summarize([row for row in results if row["metadata"]["family"]==family]),official["families"][family],"family totals")
    named=("primary_closed","and_or_closed","mux_closed","xor_closed","projection_collision")
    orbit_by_family={name:{v["signed_port_orbit"] for v in bounds.values() if v["metadata"]["family"]==name} for name in named}
    require(all(len(v)==1 and not v&train_orbits for v in orbit_by_family.values()) and
            len(set.union(*orbit_by_family.values()))==len(named),"Held nonlinear/parity laws overlap training up to signed permutations")
    require({tuple(m["port_order"]) for _,_,m in held if m["family"]=="primary_closed"}==set(permutations(range(4))),"Missing primary port permutation")
    even=[r for r in range(512) if r.bit_count()%2==0]
    examples=[(w,[raw_answers(w,r) for r in even]) for _,w,_ in train]
    require(digest(examples)==fitted["training_data_sha256"],"Training examples differ")
    equality([key for key,_,_ in train],fitted["training_ids"],"training IDs")
    wrong=sent=work=decoder_cost=sender_cost=public_cost=tests=0
    for w,labels in examples:
        plan=public_proposal(cp,w,source,*pools[2],2)
        packet_gates=sum(gate_cost(w[p]) for p in plan["ports"])
        dg=len((plan["dag"] or {}).get("gates",[]))
        for raw,wanted in zip(even,labels,strict=True):
            packet=tuple(source.table(w[p])[raw] for p in plan["ports"])
            wrong+=sum(decode(plan,packet,p)!=wanted[p] for p in range(4))
        sent+=256*len(plan["ports"])
        sender_cost+=256*packet_gates
        decoder_cost+=256*dg
        public_cost+=plan["public_actions"]["public_scalar_nands"]
        tests+=plan["public_actions"]["public_candidate_tests"]
    work=sender_cost+decoder_cost+public_cost+tests
    history=fitted["history"]
    selected={"wrong_answer_bits":wrong,"transmitted_bits":sent,"work_units":work,"public_scalar_nands":public_cost,
              "public_candidate_tests":tests,"sender_scalar_nands":sender_cost,"decoder_scalar_nands":decoder_cost,
              "library_NAND_size":sum(p["nand_gates"] for p in cp["library"])}
    equality(selected,{k:history["final_loss"][k] for k in selected},"selected training objective")
    require(history["libraries"]==696 and history["model_candidates"]==len(history["model_scores"])==3480,"Training grammar coverage differs")
    expected_models=[(list(ids),budget) for size in (1,2,3) for ids in combinations(range(16),size)
                     for budget in (8,16,32,64,128)]
    equality([(row["library_ids"],row["probe_count"]) for row in history["model_scores"]],expected_models,"complete ordered library/budget coverage")
    for index,row in enumerate(history["model_scores"],1):
        require(row["model"]==index and row["library_NAND_size"]==sum(binary[i]["nand_gates"] for i in row["library_ids"]),
                "Model index/library cost differs")
        require(row["work_units"]==sum(row[k] for k in ("public_scalar_nands","public_candidate_tests","sender_scalar_nands","decoder_scalar_nands")),
                "Reported training work arithmetic differs")
    def rank(row):
        ids=row["library_ids"]
        return (row["wrong_answer_bits"],row["transmitted_bits"],row["work_units"],row["library_NAND_size"],len(ids),
                tuple(tuple_tree(binary[i]["expr"]) for i in ids),row["probe_count"])
    winner=min(history["model_scores"],key=rank)
    equality((winner["library_ids"],winner["probe_count"]),(cp["library_ids"],cp["probe_count"]),"recorded model rank/ties")
    two=min((row for row in history["model_scores"] if len(row["library_ids"])<=2),key=rank)
    diagnostic=history["best_cap_two_diagnostic"]
    equality((two["library_ids"],two["probe_count"]),(diagnostic["checkpoint"]["library_ids"],diagnostic["checkpoint"]["probe_count"]),
             "same-sweep cap-two diagnostic rank")
    require(diagnostic["separately_fitted"] is False and diagnostic["diagnostic_only"] is True,"Diagnostic changed the primary selection")
    actual=history["fit_actual_shared_compilation"]
    require(actual["fragment_groups_compiled"]==137 and actual["abstract_programs_generated"]==70805,"Actual shared catalogue acquisition count differs")
    require(history["fit_cold_catalogue_work"]["abstract_programs_generated"]==1574280,"Cold library totals confused with actual compilation")
    equality(history["fit_actual_parser_ledger"],{"public_rows":32*(128+256),"public_parser_calls":32*(128+256)*4,
             "public_scalar_nands":32*(128+256)*284,"public_packed_nands":32*2*284},"actual cached acquisition parser work")
    # Count both independent public endpoints, with a single cold catalogue
    # per endpoint. Per-wiring cold catalogue annotations are not summed89x.
    proposal_work=Counter()
    certification_work=Counter()
    lookup_work_total=Counter()
    for entry in planned["wirings"].values():
        proposal_work.update({k:v for k,v in entry["sender"]["raw"]["public_actions"].items() if k.startswith("public_")})
        certification_work.update({k:v for k,v in entry["certificate"].items() if type(v) is int})
        lookup_work_total.update({k:v for k,v in entry["lookup_work"].items() if type(v) is int})
    endpoint_work={"proposal_both_endpoints":{k:2*v for k,v in proposal_work.items()},
                   "certification_both_endpoints":{k:2*v for k,v in certification_work.items()},
                   "lookup_compile_both_endpoints":{k:2*v for k,v in lookup_work_total.items()},
                   "proposal_catalogue_per_endpoint_once":pools[2][1],
                   "per_use_of_all89_wirings":{arm:{"physical_bits":sum(r["arms"][arm]["width"] for r in results),
                     "encode_scalar_nands":71*sum(r["arms"][arm]["width"] for r in results),
                     "uniform_late_query_decoder_nands":sum(r["arms"][arm]["decoder_nands"] for r in results)/4}
                     for arm in ARMS}}
    sample=next(r for r in results if r["metadata"]["family"]=="primary_closed")
    chosen_plan=planned["wirings"][sample["id"]]["sender"]["raw"]
    mutated=json.loads(json.dumps(chosen_plan))
    mutated["dag"]["gates"][-1]=[3,3]
    wiring=by_id[sample["id"]][0]
    returned,wrong_gate=certificate(wiring,mutated,source)
    require(wrong_gate["status"]=="fallback_four" and wrong_gate["wrong_rows"]>0 and len(returned["ports"])==4,
            "Validly encoded wrong NAND gate survived public certification")
    rejections=[]
    for label,packet in (("truncated",(0,0)),("extra",(0,0,0,0)),("nonbit",(2,0,0)),("integer_payload",0)):
        try:
            decode(chosen_plan,packet,chosen_plan["omitted_port"])
        except AuditError:
            rejections.append(label)
        else:
            raise AuditError("Malformed physical channel accepted")
    equality(bindings(out)[0],binding,"freeze after replay")
    return {"ticket":TICKET,"status":"pass","schema_version":1,"audit_source_sha256":file_digest(__file__),"bindings":binding,
            "held_wirings":len(held),"physical_arm_replays":len(held)*5,"delayed_answers":len(held)*512*4*5,
            "summary":summarize(results),"families":official["families"],"bounds":bounds,
            "matched_changed_answers":dict(matched),"training_orbits":sorted(train_orbits),"novel_held_orbits":{k:list(v) for k,v in orbit_by_family.items()},
            "selected_training_objective":selected,"actual_shared_compilation":actual,
            "endpoint_logical_work":endpoint_work,"physical_mutations_rejected":rejections,
            "wrong_gate_certificate_wrong_rows":wrong_gate["wrong_rows"],
            "costs":check_costs(out,results,planned["wirings"],fitted,{key:w for key,(w,_) in by_id.items()}),
            "limits":["Learning selects the binary library and probe budget; online candidate generation/matching and external certification are supplied.",
                      "All-input public certification is per-wiring search/checking, separate from raw proposal generalization.",
                      "The matched lookup compiler and learner both transmit existing answer ports; arbitrary new code bits are outside this packet grammar.",
                      "Recorded3480-way selection ranks are checked and the selected loss is replayed; other model losses are not independently refitted.",
                      "Timing arithmetic is audited; host timings are observations, use/link-price projections are models."]}


def self_test():
    require(nand(["NAND", ["input", 0], ["input", 0]], (0,)) == 1, "Atomic NOT failed")
    affine = [(a, b, c, a ^ b ^ c) for a in range(2) for b in range(2) for c in range(2)]
    nonlinear = [(a, b, c, a ^ (b & c)) for a in range(2) for b in range(2) for c in range(2)]
    independent = [(a, b, c, d) for a in range(2) for b in range(2) for c in range(2) for d in range(2)]
    a, b, c = map(communication_bounds, (affine, nonlinear, independent))
    require(a["minimum_bits"] == b["minimum_bits"] == 3 and c["minimum_bits"] == 4, "Counting bound failed")
    require(a["affine_relation"] and not b["affine_relation"], "Nonlinear relation fixture failed")
    require(a["signed_port_orbit"] != b["signed_port_orbit"], "Affine/nonlinear laws collapsed under signed permutations")
    require(not c["any_three_computed_ports_identify"], "Independent four answers passed a three-bit channel")
    transformed = [tuple(row[i] ^ ((5 >> p) & 1) for p, i in enumerate((2, 0, 3, 1))) for row in nonlinear]
    require(signed_port_orbit(transformed) == b["signed_port_orbit"], "Signed-port canonicalization failed")
    collision = [(0,0,0,0),(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1),(1,1,0,0),(1,0,1,0),(1,0,0,1)]
    bound = communication_bounds(collision)
    require(bound["minimum_bits"] == 3 and not bound["any_three_computed_ports_identify"], "Projection limit was lost")
    p = {"ports": [0,1,2], "omitted_port": 3, "dag": {"gates": [[0,1]], "output": 5}}
    require(decode(p, (1,1,0), 3) == 0 and decode(p, (0,1,0), 3) == 1, "Flat NAND packet decoder failed")
    for bad in ({"ports": [0,1,2], "omitted_port": 3, "dag": {"gates": [[0,5]], "output": 5}},
                {"ports": [0,1,2], "omitted_port": None, "dag": p["dag"]}):
        try:
            validate_plan(bad)
        except AuditError:
            pass
        else:
            raise AuditError("Malformed physical DAG accepted")
    return {"status": "pass", "synthetic_NAND_and_bounds": True, "signed_port_orbits": True}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--self-test", action="store_true")
    cli.add_argument("--out",type=Path,default=DEFAULT_OUT)
    cli.add_argument("--write",action="store_true")
    args = cli.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), sort_keys=True))
    else:
        result=audit(args.out)
        if args.write:
            (args.out/"audit.json").write_bytes(canonical(result)+b"\n")
        print(json.dumps({"status":result["status"],"physical_arm_replays":result["physical_arm_replays"],
                          "summary":result["summary"],"novel_held_orbits":result["novel_held_orbits"]},indent=2))
