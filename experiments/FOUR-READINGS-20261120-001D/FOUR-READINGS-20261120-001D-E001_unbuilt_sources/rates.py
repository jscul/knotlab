"""Derive named denominator counts, censoring, and marginal/simultaneous intervals."""
from collections import Counter
import json
from pathlib import Path

from scipy.stats import beta
from panel import OUT, LAWS

EVENTS = {"funded":"Funded", "one_or_more":"At least one release", "exactly_one":"Exactly one release",
          "two_or_more":"Two or more releases", "direct":"Direct meeting", "indirect":"Indirect meeting",
          "recurrent":"Unbounded emission"}
KEYS = {"funded":"funded","one_or_more":"at_least_one_recognized_release",
        "exactly_one":"one_recognized_release","two_or_more":"two_or_more_recognized_releases",
        "direct":"both_persist_direct","indirect":"both_persist_indirect","recurrent":"recurrent_source"}
ARMS = {"tree":"Uniform labelled tree","tree_plus_meeting":"Tree plus one meeting",
        "partnered":"Partnered runaway at age 5","archive_00":"Jump-selected six-knot start at age 12",
        "eddy":"Fixed-rate five-knot eddy at age 32"}
READERS = ("full_current","growing_end")
OBS = "inherited_readers"
POST = "additional_lawful_comparison"
BROAD = "any_reading_bounds"
# Covers all all-draw study cells, even when law, reader and two contrasts coincide.
CELLS = len(ARMS) * len(LAWS) * len(READERS) * len(EVENTS) * 3


def interval(y, u, n, alpha):
    return [float(beta.ppf(alpha / 2,y,n-y+1)) if y else 0.,
            float(beta.ppf(1-alpha/2,y+u+1,n-y-u)) if y+u < n else 1.]


def stats(counts):
    y,u,n = counts["yes"],counts["unknown"],sum(counts.values())
    return {"n":n,"yes":y,"no":counts["no"],"unknown":u,"identified":[y/n,(y+u)/n],
            "binomial95":interval(y,u,n,.05),"certification_only_binomial95":interval(y,0,n,.05),"all_draw_simultaneous95":interval(y,u,n,.05/CELLS),
            "if_no_detections_one_sided95_upper":1-.05**(1/n) if y==0 else None}


def broader(x,k,detected_later):
    base = x["with_return_uncertainty"][k]
    if k=="funded" or k=="recurrent":
        return base
    if k=="indirect" and detected_later:
        return "yes"
    # A source which is never funded or goes completely spent cannot have lasting releases.
    if not x["funded"] or all(p["closed"] for p in x["parts"]):
        return "no"
    if k=="exactly_one":
        return "no" if x["certified_releases"]>=2 else "unknown"
    return "yes" if base=="yes" else "unknown"


def main():
    draws=[json.loads(l) for l in (OUT/'draws.jsonl').read_text().splitlines()]
    more=json.loads((OUT/'checks.json').read_text())
    positive={(q['weighting'],q['draw'],q['law']) for q in more["physical_interventions"]}
    morehosts=json.loads((OUT/'explosive.json').read_text())["hosts"]
    eddy=json.loads((OUT/'deep.json').read_text())["summary_by_reader"]
    ans=[]
    for w in ARMS:
        for q in LAWS:
            for reader in READERS:
                for denom in ("all","lawful","funded"):
                    for scope in (OBS,POST,BROAD):
                        for k in EVENTS:
                            if w in ("tree","tree_plus_meeting"):
                                tally=Counter()
                                for dr in draws:
                                    x=dr['laws'][q]
                                    if dr['weighting']!=w or (denom=="lawful" and not x["legal"]) or (denom=="funded" and not x["funded"]):
                                        continue
                                    extra=(w,dr["pair_index"],q) in positive
                                    status=x["with_return_uncertainty"][k]
                                    if scope==POST and k=="indirect" and extra:
                                        status="yes"
                                    if scope==BROAD:
                                        status=broader(x,k,extra)
                                    tally[status]+=1
                            else:
                                rec=eddy[reader] if w=="eddy" else morehosts[w]["summary_by_law"][q][reader]
                                what="broader_existence" if scope==BROAD else "frozen_reader"
                                tally=Counter(rec[what][KEYS[k]]["counts"])
                            ans.append({"weighting":w,"law":q,"reader":reader,"denominator":denom,
                                        "scope":scope,"event":k,**stats(tally)})
    (OUT/'rates.json').write_text(json.dumps({"all_draw_bonferroni_cells":CELLS,"rows":ans},separators=(',',':'))+'\n')
    directory=OUT.parents[2]/"research"/OUT.parent.name
    def display(row):
        a=row["yes"]; b=a+row['unknown']; n=row["n"]; l,h=row['binomial95']
        positive=str(a) if a==b else f'{a}–{b}'
        return f'{positive}/{n} ({100*l:.1f}–{100*h:.1f}%)'
    lines=["# Rates under the two physical readings", "",
        "Each entry gives certified to possible successes over its stated denominator, followed by the marginal 95% exact binomial limits. "
        "The complete-current and witnessed-growing-end rows agree for these anonymous outputs. "
        "A focal holder's earlier origin can remain hidden on the growing end. "
        "Counts from one host apply to a uniform knot within that host. Counts on trees apply to independent draws of starts. The original physical withdrawal alone certified 21/256 trees (95% interval 5.1–12.3%) and 5/256 augmented draws (0.6–4.5%) under each law. The ranges in the indirect column allow for the same causal event in draws where that withdrawal was inadmissible. "
        "[Full machine table](../../artifacts/"+OUT.parent.name+"/"+OUT.name+"/rates.json)", ""]
    idx={(z["weighting"],z["law"],z["reader"],z["denominator"],z["scope"],z["event"]):z for z in ans}
    for scope, label in ((OBS,"Frozen readers and donor withdrawal"),(POST,"With the additional lawful comparator"),(BROAD,"Existence under other readings")):
        lines.extend(['## '+label,''])
        if scope==POST:
            lines.extend(["Only the indirect column changes. Disjoint continuing parties, their actual common descendant and the required changed output have the original meaning. The new physical comparison adds three knots to the donor-off specimen. The raw count is 30/256 in the tree arm and 8/256 in the augmented arm under each law.",''])
        if scope==BROAD:
            lines.extend(["The broad bounds use proven positives and impossibilities only. A different reader may identify additional lasting families. Exactly one under all possible readings asks for absence of a second family. A sample with one observed family alone leaves that question open.",''])
        for denom in ('all','funded'):
            if scope != OBS and denom=='funded':
                continue
            lines.extend(["### "+("All draws, also all lawful draws" if denom=='all' else "Conditional on first-step funding"),'',
                          '| Weighting and law | '+' | '.join(EVENTS.values())+' |','| --- | '+' | '.join(['---:']*len(EVENTS))+' |'])
            for w,label in ARMS.items():
                for q in LAWS:
                    fields=[]
                    for k in EVENTS:
                        a=idx[w,q,READERS[0],denom,scope,k]; b=idx[w,q,READERS[1],denom,scope,k]
                        assert (a["yes"],a["unknown"],a["n"])==(b["yes"],b["unknown"],b["n"])
                        fields.append(display(a))
                    lines.append('| '+label+' · '+('parity' if q=='parity' else 'not-all-equal')+' | '+' | '.join(fields)+' |')
            lines.append('')
    lines.extend(["## Interval coverage",'',
      "The lower endpoint uses the exact one-sample binomial lower limit on certified successes. The upper uses its upper limit on successes plus unresolved draws. Each tail has error probability at most 2.5%. The all-draw simultaneous limits divide that error across all "+str(CELLS)+" weighting, law, reader, event and interpretation cells. Independence between different table cells is unnecessary. Within each cell the preregistered draw units are independent with replacement. For 0/256 detections the one-sided 95% upper bound on detection is 1.16%. For 0/96 it is 3.07%. A bound for a detector does not control an unresolved existence claim. A separate deterministic proof can fix a whole-host fraction at zero or one even when the displayed design-based interval is wider.", ''])
    (directory/'rates.md').write_text('\n'.join(lines))


if __name__=='__main__':
    main()
