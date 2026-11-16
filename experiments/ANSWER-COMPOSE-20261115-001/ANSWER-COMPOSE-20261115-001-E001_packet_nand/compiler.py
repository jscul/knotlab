"""Exact public lookup compiler and a separate certificate for learned plans."""

from packet_io import ALL_PORTS, ALL_RAW, public_columns, validate_channel


def all_four():
    return {"ports":list(ALL_PORTS), "omitted_port":None, "dag":None}


def checked_ports(plan):
    ports = tuple(plan["ports"])
    if len(ports) not in (3, 4) or ports != tuple(sorted(set(ports))) or any(p not in ALL_PORTS for p in ports):
        raise ValueError("Expected three or four distinct public ports in order")
    missing = set(ALL_PORTS).difference(ports)
    if plan["omitted_port"] != next(iter(missing), None):
        raise ValueError("Inconsistent omitted-port routing")
    return ports


def eval_dag(dag, slots, lanes):
    data = [*slots, 0, lanes]
    if len(slots) != 3:
        raise ValueError("A circuit reconstructs one omitted port from three values")
    for pair in dag["gates"]:
        if len(pair) != 2 or any(type(k) is not int or not 0 <= k < len(data) for k in pair):
            raise ValueError("Invalid NAND operand")
        data.append(lanes ^ (data[pair[0]] & data[pair[1]]))
    output = dag["output"]
    if type(output) is not int or not 0 <= output < len(data):
        raise ValueError("Invalid circuit output")
    return data[output]


def certify(wiring, proposal):
    ports = checked_ports(proposal)
    if len(ports) == 4:
        if proposal["dag"] is not None:
            raise ValueError("Four-copy plan cannot depend on an omitted answer")
        return all_four(), {"status":"four_by_construction", "public_rows":0, "wrong_rows":0}
    columns, ledger = public_columns(wiring, ALL_RAW)
    predicted = eval_dag(proposal["dag"], [columns[p] for p in ports], (1 << 512) - 1)
    wrong = (predicted ^ columns[proposal["omitted_port"]]).bit_count()
    ledger.update(status="fallback_four" if wrong else "certified_three", wrong_rows=wrong,
                  decoder_packed_nands=len(proposal["dag"]["gates"]),
                  decoder_scalar_nands=512 * len(proposal["dag"]["gates"]))
    return (all_four() if wrong else proposal), ledger


def possible_vectors(columns, lanes):
    """Test which four-answer patterns occur. The full joint table stays public."""
    buckets = [lanes]
    for col in columns:
        buckets = [part & (lanes ^ col) for part in buckets] + [part & col for part in buckets]
    return [v for v, part in enumerate(buckets) if part]


def compile_lookup(wiring):
    columns, ledger = public_columns(wiring, ALL_RAW)
    vectors = possible_vectors(columns, (1 << 512) - 1)
    ledger.update(patterns=len(vectors), packed_intersections=30, omission_trials=0, table_entries_checked=0)
    if len(vectors) <= 8:
        for omitted in ALL_PORTS:
            ledger["omission_trials"] += 1
            ports = [p for p in ALL_PORTS if p != omitted]
            seen = {}
            for vector in vectors:
                key = sum(((vector >> p) & 1) << lane for lane, p in enumerate(ports))
                answer = (vector >> omitted) & 1
                ledger["table_entries_checked"] += 1
                if key in seen and seen[key] != answer:
                    break
                seen[key] = answer
            else:
                lookup = sum(value << key for key, value in seen.items())
                return {"ports":ports, "omitted_port":omitted, "lookup":lookup}, ledger
    return all_four(), ledger


def lookup_receive(plan, packet, port):
    validate_channel(packet, len(plan["ports"]), port)
    if plan["omitted_port"] != port:
        return packet[plan["ports"].index(port)]
    key = packet[0] + 2 * packet[1] + 4 * packet[2]
    return (plan["lookup"] >> key) & 1


def prepare_reader(plan):
    """Cache public routing and compile the recorded circuit for ordinary packet traffic."""
    ports = checked_ports(plan)
    routes = tuple(ports.index(p) if p in ports else None for p in ALL_PORTS)
    width = len(ports)
    if width == 4:
        reconstruct = None
    elif "lookup" in plan:
        table = plan["lookup"]
        def reconstruct(bits):
            return (table >> (bits[0] + 2*bits[1] + 4*bits[2])) & 1
    else:
        dag = plan["dag"]
        eval_dag(dag, (0,0,0), 1)  # Validate operand types and topological addresses once.
        values = ["bits[0]","bits[1]","bits[2]","0","1"]
        lines = ["def reconstruct(bits):"]
        for i,(left,right) in enumerate(dag["gates"]):
            name="g"+str(i)
            lines.append(f"    {name} = 1 ^ ({values[left]} & {values[right]})")
            values.append(name)
        lines.append("    return "+values[dag["output"]])
        namespace={"__builtins__":{}}
        exec("\n".join(lines),namespace)
        reconstruct=namespace["reconstruct"]
    def receive(bits,port):
        validate_channel(bits,width,port)
        slot=routes[port]
        return bits[slot] if slot is not None else reconstruct(bits)
    return receive
