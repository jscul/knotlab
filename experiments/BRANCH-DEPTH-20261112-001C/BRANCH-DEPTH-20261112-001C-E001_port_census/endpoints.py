"""Look for small bonds using any root ports and variables at the target copy."""
from collections import Counter
from itertools import combinations, product
import json

from census import OUT, SOURCE, allowed_local_words, bits
import gzip


def has_bond(mask, size):
    if not mask or mask == (1 << (1 << size)) - 1:
        return False
    for delete in range(size):
        # For each pair of words differing at just this bit, at least one is allowed.
        for word in range(1 << size):
            if not word & (1 << delete):
                if not ((1 << word | 1 << (word | 1 << delete)) & mask):
                    return False
    return True


def orbit(definition, allowed, words, relation, branches=((),), sizes=(3,), target_index=0):
    _, own, calls = definition
    first = next(args for k,args in calls if k == "SELF")
    power = frozenset((p,p) for p in allowed)
    seen, certs = {}, []
    # -1 marks a local name carried into a port. Ancestor locals are fresh
    # and distinct from all top ports, own distinctions, and other slots.
    names = (0,1,2)
    # A cut opens one chain of side calls below the target, then uses the
    # exact usual-limit relation at every call left unopened. Its other
    # branches introduce no observed variables, and meet only at the ports.
    children = [args for kind,args in calls if kind == "SELF"]
    by_port = {}
    for word,_ in words:
        by_port.setdefault(word & 7, []).append(word)
    cuts = []
    for path in branches:
        width = 3 + own
        cut = [(word,word) for word,_ in words]
        for child in path:
            expanded = []
            for data,parent in cut:
                target_port = bits(parent,children[child])
                for w in by_port[target_port]:
                    expanded.append((data | ((w >> 3) << width),w))
            cut = expanded
            width += own
        grouped = {}
        for data,_ in cut:
            grouped.setdefault(data & 7, []).append(data)
        cuts.append((path,width,grouped))

    while (power,names) not in seen:
        seen[power,names] = len(certs)
        # Pass actual root identities only once. The other cut variables are
        # either new own variables at the target or distinct prior locals.
        found = None
        for path,width,grouped in cuts:
            local_indices = [i for i in range(width) if i >= 3 or names[i] == -1]
            labels = ["abc"[i] for i in range(3)] + ["v"+str(i) for i in local_indices]
            target_vars = {f"v{i}" for i in range(3+target_index*own,3+(target_index+1)*own)}
            state = {top | (bits(data,local_indices)<<3)
                     for top,p in power for data in grouped[p]}
            for small in sizes:
                for selected in combinations(range(len(labels)),small):
                    selected_labels = [labels[i] for i in selected]
                    if selected[0] >= 3 or target_vars.isdisjoint(selected_labels):
                        continue
                    mask = 0
                    for w in state:
                        mask |= 1 << bits(w,selected)
                        if mask == (1 << (1 << small))-1:
                            break
                    if has_bond(mask,small):
                        found = dict(variables=selected_labels,mask=mask,size=small,
                                     path=list(path))
                        break
                if found:
                    break
            if found:
                break
        certs.append(found)
        power = frozenset((p,q) for p,mid in power for other,q in relation if other == mid)
        names = tuple(names[i] if i < 3 else -1 for i in first)
    start = seen[power,names]
    return dict(start=start,period=len(certs)-start,certificates=certs)


def classify(entry):
    checks = entry["certificates"]
    period = checks[entry["start"]:]
    if all(period):
        if all(checks[1:]):
            return "every_positive_depth"
        return "eventually_every_depth"
    if any(period):
        return "some_periodic_depths"
    return "no_eventual_certificate"


def main():
    tables = json.loads((OUT / "port_tables.json").read_text())
    results = []
    for filename in tables["source_files"]:
        included = {row["line"]:row for row in tables["rows"] if row["file"] == filename}
        with gzip.open(SOURCE / filename, "rt") as stream:
            for line, text in enumerate(stream,1):
                if line not in included:
                    continue
                row = included[line]
                if row["rectangular"] is not None:
                    continue
                definition = json.loads(text)["defs"][0]
                allowed, words, _, _ = allowed_local_words(definition)
                ties = orbit(definition, allowed, words, row["transition"], sizes=(2,))
                info = orbit(definition, allowed, words, row["transition"])
                if classify(info) != "every_positive_depth":
                    children = range(row["children"])
                    paths = [()] + list(product(children, repeat=1))
                    info = orbit(definition, allowed, words, row["transition"], paths)
                info["pair_ties"] = classify(ties)
                info.update(file=filename,line=line)
                info["classification"] = classify(info)
                results.append(info)
    totals = dict(Counter(e["classification"] for e in results))
    out = dict(totals=totals,rows=results)
    (OUT / "endpoint_tables.json").write_text(json.dumps(out,separators=(",",":")) + "\n")
    print(json.dumps(totals, indent=2))


if __name__ == "__main__":
    main()
