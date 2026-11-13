"""Find uniformly liftable chains of ternary relations along a fixed branch."""
from collections import Counter
import gzip
import json

from census import OUT, SOURCE, allowed_local_words, bits
from endpoints import has_bond


def exact_link(pairs, top, allowed):
    result = {}
    for p in allowed:
        bit = (p >> top) & 1
        if bit in result and result[bit] != pairs[p]:
            return None
        result[bit] = pairs[p]
    if len(result) != 2:
        return None
    mask = sum(1 << (x | (q << 1) | (v << 2))
               for x, pairs_at_x in result.items() for q,v in pairs_at_x)
    if mask != sum(1 << (7-i) for i in range(8) if mask & (1 << i)):
        return None
    return mask if has_bond(mask,3) else None


def find_links(definition, allowed, local, children_as_helpers):
    _, own, calls = definition
    children = [args for kind,args in calls if kind=="SELF"]
    first = children[0]
    candidates = [(None,var) for var in range(3,3+own)]
    if children_as_helpers:
        candidates += [(child,var) for child in range(1,len(children))
                       for var in range(3,3+own)]
    child_values = {(p,v): {(w>>v)&1 for w,_ in local if w&7 == p}
                    for p in allowed for v in range(3,3+own)}
    links = []
    for out, carrier in enumerate(first):
        if carrier < 3:
            continue
        for child,var in candidates:
            if child is None and var == carrier:
                continue
            pairs = {p:set() for p in allowed}
            for w,_ in local:
                values = {(w>>var)&1} if child is None else child_values[bits(w,children[child]),var]
                pairs[w&7].update(((w>>carrier)&1,v) for v in values)
            for top in range(3):
                mask = exact_link(pairs,top,allowed)
                if mask is not None:
                    links.append(dict(top=top,out=out,carrier=carrier,child=child,var=var,mask=mask))
    return links


def cycle(links):
    for start in range(3):
        todo = [(start,[],{start})]
        while todo:
            slot,path,seen = todo.pop()
            for link in links:
                if link["top"] != slot:
                    continue
                new = link["out"]
                if new == start and link.get("kind") != "carry":
                    return path+[link]
                if new not in seen:
                    todo.append((new,path+[link],seen|{new}))
    return []


def main():
    tables = json.loads((OUT/"port_tables.json").read_text())
    rows = []
    for filename in tables["source_files"]:
        included={r["line"]:r for r in tables["rows"] if r["file"]==filename and r["rectangular"] is not None}
        for number, raw in enumerate(gzip.open(SOURCE/filename,"rt"),1):
            if number not in included:
                continue
            definition = json.loads(raw)["defs"][0]
            allowed, words, _, _ = allowed_local_words(definition)
            first=next(args for kind,args in definition[2] if kind == "SELF")
            carries=[dict(top=i,out=j,kind="carry") for j,i in enumerate(first) if i<3]
            links = find_links(definition,allowed,words,False)
            certificate = cycle(carries+links)
            if not certificate:
                certificate = cycle(carries+find_links(definition,allowed,words,True))
            rows.append(dict(file=filename,line=number,cycle=certificate))
    totals = dict(Counter(len(r["cycle"]) for r in rows))
    (OUT/"chains.json").write_text(json.dumps(dict(cycle_lengths=totals,rows=rows),separators=(",",":"))+"\n")
    print(totals)


if __name__ == "__main__":
    main()
