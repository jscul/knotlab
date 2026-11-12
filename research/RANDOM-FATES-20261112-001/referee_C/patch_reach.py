p="reach.py"; s=open(p).read()
s=s.replace("""    for q, b in [(0.0, 3), (0.0, 0), (0.1, 3), (0.3, 1), (0.5, 2), (0.5, 7), (0.7, 0), (0.9, 6)]:
        for s in range(40, 760, 30):""", """    for q, b in [(0.0, 3), (0.1, 3), (0.3, 1), (0.5, 2), (0.7, 0), (0.9, 6)]:
        for s in range(40, 400, 30):""")
s=s.replace("""    with Pool(int(sys.argv[1])) as pool:
        for q, b, out in pool.imap_unordered(task, args):
            res.setdefault(f"{q}:{b}", []).extend(out)
            print(q, b, out[0], flush=True)
    json.dump(res, open("reach.json", "w"))""", """    with Pool(int(sys.argv[1])) as pool, open("reach.jsonl", "w") as f:
        for q, b, out in pool.imap_unordered(task, args):
            f.write(json.dumps({"q": q, "base": b, "rows": out}) + "\\n"); f.flush()
            print(q, b, out[0], flush=True)""")
open(p,"w").write(s)
