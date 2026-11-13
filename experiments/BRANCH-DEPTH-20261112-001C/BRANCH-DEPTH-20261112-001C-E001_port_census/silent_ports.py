"""Remove ports unused anywhere below their copy, then replay both growth tests."""
from collections import Counter
import gzip
import json

from census import OUT, SOURCE, allowed_local_words, bits
from chains import cycle, find_links


def used_slots(definition):
    _,_,calls=definition
    active={i for kind,args in calls if kind=="K" for i in args if i<3}
    children=[args for kind,args in calls if kind=="SELF"]
    if any(sorted(args)==[0,1,2] for args in children):
        active.update(range(3))
    while True:
        added={args[p] for args in children for p in active if args[p]<3}
        if added.issubset(active):
            return sorted(active)
        active.update(added)


def rectangle(rel):
    step=frozenset(rel)
    power=step
    seen=set()
    while power not in seen:
        if len(power)==len({a for a,_ in power})*len({b for _,b in power}):
            return len(seen)+1
        seen.add(power)
        power=frozenset((a,b) for a,mid in power for c,b in step if mid==c)
    return None


def main():
    tables=json.loads((OUT/"port_tables.json").read_text())
    rows=[]
    for filename in tables["source_files"]:
        unchecked={r["line"]:r for r in tables["rows"] if r["file"]==filename and r["rectangular"] is None}
        for line,raw in enumerate(gzip.open(SOURCE/filename,"rt"),1):
            if line not in unchecked:
                continue
            rule=json.loads(raw)["defs"][0]
            slots=used_slots(rule)
            if len(slots)==3:
                continue
            rect=rectangle({(bits(a,slots),bits(b,slots)) for a,b in unchecked[line]["transition"]})
            if rect is None:
                continue
            g,local,_,_=allowed_local_words(rule)
            first=next(args for op,args in rule[2] if op=="SELF")
            moves=[dict(top=i,out=j,kind="carry") for j,i in enumerate(first) if i in slots and j in slots]
            links=find_links(rule,g,local,True)
            moves += [e for e in links if e["top"] in slots and e["out"] in slots]
            rows.append(dict(file=filename,line=line,active_slots=slots,rectangular=rect,cycle=cycle(moves)))
    totals=dict(Counter((r["rectangular"],bool(r["cycle"])) for r in rows))
    (OUT/"silent_ports.json").write_text(json.dumps(rows,separators=(",",":"))+"\n")
    print(totals)


if __name__=="__main__":
    main()
