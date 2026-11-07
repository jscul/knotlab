#!/usr/bin/env python3
"""Build the generated parts of this repository from the records and data/.

Usage: python3 scripts/build.py            write RESULTS.md, RANKING.md, data/results.json,
                                          data/ranking.json, data/epics.json and README.md's counts
       python3 scripts/build.py --check    exit 1 if any of them is out of date

Inputs: research/*/discoveries/*.json (the records), tickets/*.json (epic titles and programs),
data/lines.json, data/notes.json, data/qualifications.json and data/tiers.json. Standard library only.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

K = Path(__file__).resolve().parent.parent
BLOB = "https://github.com/jscul/knotlab/blob/main/"
COUNTS = re.compile(r"<!-- counts -->.*?<!-- /counts -->", re.S)


def load(path):
    return json.loads((K / path).read_text())


def clean(text):
    return re.sub(r"\s+", " ", text or "").strip()


def ticket(ticket_id):
    path = K / "tickets" / f"{ticket_id}.json"
    return json.loads(path.read_text()) if path.exists() else {}


def epic_prefix(epic_id):
    return re.sub(r"-20\d{6}-\d{3}$", "", epic_id)


def place(epic_id, lines, notices):
    """The line of work for an epic: by name, then by research program, then the fallback."""
    prefix = epic_prefix(epic_id)
    for line in lines["lines"]:
        if prefix in line["epics"]:
            return line["key"]
    program = ticket(epic_id).get("fields", {}).get("program")
    key = lines["program_defaults"].get(program)
    if key:
        notices.append(f"{epic_id}: placed in '{key}' by its program '{program}'")
        return key
    notices.append(f"{epic_id}: no line or program default; placed in '{lines['fallback']['key']}'")
    return lines["fallback"]["key"]


def read_records(lines, quals, notices):
    records = []
    for path in sorted(K.glob("research/*/discoveries/*.json")):
        d = json.loads(path.read_text())
        evidence = [e for e in d.get("evidence", []) if e.get("explanation_path")]
        records.append({
            "id": d["id"], "scope": d["scope_id"], "line": place(d["scope_id"], lines, notices),
            "date": d.get("curated_at", ""), "title": clean(d.get("title")), "conclusion": clean(d.get("conclusion")),
            "status": d.get("status"), "superseded_by": d.get("superseded_by"),
            "evidence": [(e["artifact_id"], e["explanation_path"], e.get("kind", "")) for e in evidence],
            "closure": (d.get("epic_closure") or {}).get("report_path"),
            "tickets": {re.sub(r"-[PE]\d{3}$", "", e["artifact_id"]) for e in d.get("evidence", [])},
            "issue": quals.get(d["id"]),
        })
    for r in records:
        for _, p, _ in r["evidence"]:
            if not (K / p).exists():
                raise SystemExit(f"missing evidence file {p}")
    return records


def build_results(lines, notes, quals, notices):
    records = read_records(lines, quals, notices)
    all_lines = [(l["key"], l["name"], l["description"]) for l in lines["lines"]]
    if any(r["line"] == lines["fallback"]["key"] for r in records):
        f = lines["fallback"]
        all_lines.append((f["key"], f["name"], f["description"]))
    epics = sorted({r["scope"] for r in records}
                   | {p.name for p in (K / "research").iterdir() if re.search(r"-20\d{6}-001$", p.name)})
    by_line = defaultdict(list)
    for r in records:
        by_line[r["line"]].append(r)
    active = [r for r in records if r["status"] == "active"]

    out = []
    w = out.append
    w("# Results")
    w("")
    w("Every result the program has recorded since the knot test K1–K3 became canonical on 19 October 2026, in the program's")
    w("own language. Each entry gives the date it was recorded, its statement, and links to the proofs and experiments that")
    w("support it. The documents that define the working perspective are in [docs/](docs/), starting with")
    w("[docs/KNOT_INTUITION.md](docs/KNOT_INTUITION.md); [INTUITIONS.md](INTUITIONS.md) is a shorter introduction.")
    w("")
    w(f"**{len(active)} current results** and {len(records) - len(active)} superseded ones, from {len(epics)} research epics, plus "
      f"{len(notes)} notes. The records are published exactly as they stand in our research workspace, so the hashes in their")
    w("manifests still verify. None has been reviewed by a human expert; AI agents produced most of this work under the")
    w("direction of the repository owner. Where a statement awaits a qualification, the entry says so. New epics appear here")
    w("automatically when they close.")
    w("")
    w("How to read an entry:")
    w("")
    w("- the **date** is when the result was recorded at the close of its epic;")
    w("- **proof** links go to a `proof.md` with a `check.py` beside it, and **experiment** links go to a frozen contract and its")
    w("  result;")
    w("- record names such as `KNOT-LOOPS-20261019-001-D001` are the labels used throughout the records.")
    w("")
    w("## Lines of work")
    w("")
    for key, name, _ in all_lines:
        n_active = sum(r["status"] == "active" for r in by_line[key])
        anchor = re.sub(r"[^a-z0-9 -]", "", name.lower()).replace(" ", "-")
        w(f"- [{name}](#{anchor}): {n_active} results")
    w(f"- [Notes](#notes): {len(notes)} self-contained notes")
    w(f"- [Epics](#epics): all {len(epics)} epics with their closures")
    w("")

    site_items = []
    for key, name, desc in all_lines:
        w(f"## {name}")
        w("")
        w(desc)
        w("")
        for r in sorted(by_line[key], key=lambda r: (r["date"], r["id"])):
            links = ", ".join(f"[{kind or 'evidence'} {aid.split('-')[-1]}]({p})" for aid, p, kind in r["evidence"])
            if r["closure"]:
                links += f", [epic closure]({r['closure']})"
            status = f" **Superseded** by `{r['superseded_by']}`." if r["status"] == "superseded" else ""
            w(f"- **{r['date']} · {r['title']}** (`{r['id']}`).{status}")
            w(f"  {r['conclusion']}")
            if r["issue"]:
                w(f"  *{r['issue']}*")
            w(f"  {links}")
            primary = r["evidence"][0][1] if r["evidence"] else (r["closure"] or "")
            site_items.append({
                "id": r["id"], "line": key, "date": r["date"], "title": r["title"], "statement": r["conclusion"],
                "status": r["status"], "superseded_by": r["superseded_by"], "issue": r["issue"],
                "href": BLOB + primary if primary else "",
            })
        w("")

    w("## Notes")
    w("")
    w("Self-contained write-ups. The first three are also in [notes/](notes/) with standalone checks.")
    w("")
    for note in notes:
        d = next((p for p in sorted((K / "proofs" / note["id"]).glob("*")) if p.is_dir()), None)
        if d is None:
            raise SystemExit(f"missing note folder {note['id']}")
        w(f"- **{note['date']} · {note['title']}** (`{note['id']}`). [Note folder]({d.relative_to(K)}/)")
        if quals.get(note["id"]):
            w(f"  *{quals[note['id']]}*")
    w("")

    w("## Epics")
    w("")
    w("Each epic's closure proof lists its tickets, their outcomes and its recommendation for what came next.")
    w("")
    w("| Opened | Epic | Closure | Notes |")
    w("| --- | --- | --- | --- |")
    epic_rows = []
    for e in sorted(epics, key=lambda x: (re.search(r"-(20\d{6})-", x).group(1), x)):
        m = re.search(r"-(20\d\d)(\d\d)(\d\d)-", e)
        opened = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        closure = next(iter(sorted((K / "proofs").glob(f"{e}Z/*/proof.md"))), None)
        research = K / "research" / e
        node = ticket(e)
        title = node.get("title") or e
        w(f"| {opened} | {title} (`{e}`) | " + (f"[closure]({closure.relative_to(K)})" if closure else "—") + " | "
          + (f"[folder](research/{e}/)" if research.exists() else "—") + " |")
        epic_rows.append({"id": e, "title": title, "opened": opened, "program": node.get("fields", {}).get("program"),
                          "status": node.get("status_class"),
                          "closure": closure.relative_to(K).as_posix() if closure else None,
                          "research": f"research/{e}/" if research.exists() else None})
    w("")
    results_json = {"lines": [{"key": k, "name": n, "description": d} for k, n, d in all_lines], "results": site_items}
    return "\n".join(out) + "\n", results_json, epic_rows, records, len(active), len(records) - len(active), len(epics)


def build_ranking(tiers, records):
    def short(t):
        m = re.match(r"(.+)-(20\d{6})-001([A-Z]?)$", t)
        return f"{m.group(1)} {m.group(3)}".strip() if m else t

    def proof_md(t):
        dirs = sorted(p for p in (K / "proofs" / t).glob("*") if (p / "proof.md").exists())
        if not dirs:
            raise SystemExit(f"no proof for {t}")
        return (dirs[0] / "proof.md").relative_to(K).as_posix()

    def closure_md(e):
        hits = sorted((K / "proofs").glob(f"{e}Z/*/proof.md"))
        if not hits:
            raise SystemExit(f"no closure for {e}")
        return hits[0].relative_to(K).as_posix()

    by_id = {r["id"]: r for r in records}
    tier_of, site_tiers = {}, []
    md = ["# Ranking", "", tiers["intro"], "",
          "The full dated list of results is in [RESULTS.md](RESULTS.md); results without a tier there are not in the ranking.", ""]
    for tier in tiers["tiers"]:
        number, name, desc = tier["number"], tier["name"], tier["description"]
        md += [f"## Tier {number}: {name}", ""]
        if desc:
            md += [desc, ""]
        site_items = []
        for item in tier["items"]:
            title, text = item["title"], item["text"]
            matched, links = set(), []
            for t in item.get("tickets", []):
                links.append({"label": short(t), "href": BLOB + proof_md(t)})
                matched |= {rid for rid, r in by_id.items() if t in r["tickets"]}
            for e in item.get("epics", []):
                links.append({"label": short(e), "href": BLOB + closure_md(e)})
                matched |= {rid for rid, r in by_id.items() if r["scope"] == e}
            for rid in item.get("records", []):
                if rid not in by_id:
                    raise SystemExit(f"unknown record {rid}")
                matched.add(rid)
                for t in sorted(by_id[rid]["tickets"]):
                    href = BLOB + proof_md(t)
                    if href not in {l["href"] for l in links}:
                        links.append({"label": short(t), "href": href})
            for note in item.get("notes", []):
                links.append({"label": note["label"], "href": note["href"]})
            matched -= set(item.get("exclude", []))
            matched = {rid for rid in matched if by_id[rid]["status"] == "active"}
            if not matched:
                raise SystemExit(f"no records for {title}")
            for rid in matched:
                tier_of[rid] = min(tier_of.get(rid, 9), number)
            dates = sorted(by_id[rid]["date"] for rid in matched)
            date = dates[0] if dates[0] == dates[-1] else f"{dates[0]} to {dates[-1]}"
            statements = sorted({by_id[rid]["title"] for rid in matched}) if not text else []
            site_items.append({"title": title, "text": text, "date": date, "lean": bool(item.get("lean")),
                               "statements": statements, "links": links, "records": sorted(matched)})
            md.append(f"- **{title}** ({date}). " + (text if text else "; ".join(statements) + "."))
            md.append("  " + ", ".join(
                f"[{l['label']}]({l['href'].replace(BLOB, '') if l['href'].startswith(BLOB) else 'https://jscul.dev' + l['href']})"
                for l in links))
        md.append("")
        site_tiers.append({"number": number, "name": name, "description": desc, "items": site_items})
    return "\n".join(md) + "\n", {"intro": tiers["intro"], "tiers": site_tiers}, tier_of


def dump(obj):
    return json.dumps(obj, indent=1, ensure_ascii=False) + "\n"


def outputs():
    lines, notes, tiers = load("data/lines.json"), load("data/notes.json")["notes"], load("data/tiers.json")
    quals = {q["id"]: q["text"] for q in load("data/qualifications.json")["items"]}
    notices = []
    results_md, results_json, epic_rows, records, n_active, n_superseded, n_epics = build_results(lines, notes, quals, notices)
    known = {r["id"] for r in records} | {n["id"] for n in notes}
    unknown = sorted(set(quals) - known)
    if unknown:
        raise SystemExit(f"qualifications name unknown records or notes: {unknown}")
    ranking_md, ranking_json, tier_of = build_ranking(tiers, records)
    for r in results_json["results"]:
        r["tier"] = tier_of.get(r["id"])
    readme = (K / "README.md").read_text()
    if not COUNTS.search(readme):
        raise SystemExit("README.md has no <!-- counts --> block")
    readme = COUNTS.sub(f"<!-- counts -->{n_active} current results and {n_superseded} superseded ones<!-- /counts -->", readme)
    files = {
        "RESULTS.md": results_md, "RANKING.md": ranking_md, "README.md": readme,
        "data/results.json": dump(results_json), "data/ranking.json": dump(ranking_json), "data/epics.json": dump(epic_rows),
    }
    return files, notices, (n_active, n_superseded, n_epics, len(tier_of))


def main():
    check = "--check" in sys.argv[1:]
    files, notices, (n_active, n_superseded, n_epics, n_tiered) = outputs()
    stale = [name for name, text in files.items() if not (K / name).exists() or (K / name).read_text() != text]
    if check:
        if stale:
            print("out of date: " + ", ".join(stale) + " (run python3 scripts/build.py)")
            return 1
        print("generated files are up to date")
        return 0
    for name in stale:
        (K / name).write_text(files[name])
    for notice in notices:
        print("placement:", notice)
    print(f"{n_active} current and {n_superseded} superseded results from {n_epics} epics; {n_tiered} ranked; "
          f"updated: {', '.join(stale) if stale else 'nothing'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
