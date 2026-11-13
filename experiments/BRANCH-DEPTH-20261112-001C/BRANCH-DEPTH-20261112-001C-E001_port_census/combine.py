"""Partition the inventory by the conclusions its certificates actually establish."""
from collections import Counter
import json

from census import OUT


def combine():
    def read(name):
        return json.loads((OUT/(name+".json")).read_text())
    def index(rows):
        return {(r["file"],r["line"]):r for r in rows}
    ports=index(read("port_tables")["rows"])
    endpoints=index(read("endpoint_tables")["rows"])
    small=index(read("fixed_three")["rows"])
    four=index(read("four_members")["rows"])
    cycles=index(read("chains")["rows"])
    silent=index(read("silent_ports"))
    initial_residual={k for k,r in endpoints.items() if r["classification"]!="every_positive_depth"}
    assert set(small)==set(four)==initial_residual
    assert set(ports)==set(endpoints)|set(cycles) and not set(endpoints)&set(cycles)
    classes={}
    rows=[]
    for key, row in ports.items():
        forced=row["rectangular"]
        if key in silent:
            forced=silent[key]["rectangular"]
            assert forced and silent[key]["cycle"]
        elif forced:
            assert key in cycles
        exact_three=key in endpoints and endpoints[key]["classification"]=="every_positive_depth"
        last_three=None
        if key in small:
            orbit=small[key]["orbit"]
            repeat=orbit["answers"][orbit["preperiod"]:]
            if all(repeat) and all(orbit["answers"][1:]):
                exact_three=True
            else:
                assert not any(repeat)  # Checked fact about this particular inventory.
                last_three=max((i for i,q in enumerate(orbit["answers"]) if q),default=-1)
        upper_four=key in four and four[key]["classification"]=="every_positive_depth"
        if forced:
            assert not exact_three and not upper_four
            has_cycle=key in silent or bool(cycles[key]["cycle"])
            name="linear" if has_cycle else "linear_lower_bound_only"
        elif exact_three:
            name="exactly_three"
        elif upper_four:
            assert last_three is not None
            name="eventually_exactly_four"
        else:
            assert last_three is not None
            name="larger_sizes_unresolved"
        rows.append(dict(file=key[0],line=key[1],outcome=name,
                         forgetting_length=forced,last_depth_with_three=last_three))
        classes[key]=name
    return dict(totals=dict(Counter(classes.values())),rows=rows)


if __name__=="__main__":
    data=combine()
    (OUT/"outcomes.json").write_text(json.dumps(data,separators=(",",":"))+"\n")
    print(json.dumps(data["totals"],indent=2))
