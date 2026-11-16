"""Link a stage result to the public raw-input NAND prefix and materialize the return."""


def attach_physical(case, result):
    frontier = list(case["frontier"])
    m, n = len(frontier), case["n"]
    prefix = case["upstream_count"]
    stage = result["circuit"]
    if result["n"] != m or stage.get("n", m) != m:
        raise ValueError("stage arity disagrees with supplied frontier")
    wires = frontier + [n, n + 1]
    gates = list(case["gates"][:prefix])
    for a, b in stage["gates"]:
        if not (0 <= a < len(wires) and 0 <= b < len(wires)):
            raise ValueError("stage NAND has an invalid predecessor")
        gates.append([wires[a], wires[b]])
        wires.append(n + 1 + len(gates))
    answer = {key: result[key] for key in
              ("status", "n", "triple", "width", "class_count", "summary_wires", "circuit")}
    answer["physical"] = dict(n=n, gates=gates, outputs=[wires[w] for w in stage["outputs"]],
                              summary_wires=[wires[w] for w in result["summary_wires"]],
                              frontier=frontier)
    return answer
