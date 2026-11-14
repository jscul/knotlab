"""Assemble the final referee deliverables from frozen local result JSON."""
import ast,collections,datetime,hashlib,json,platform,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]


def load(name):return json.loads((HERE/name).read_text())
def fmt(n):return f'{n:,}'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    search=load('final_search.json');wide=load('wide_search.json');recount=load('heldout_recount.json');guard=load('guarded_recount_and_starts.json')
    witness=load('counterexample.json');boundary=load('structural_and_boundary_controls.json');prefix=load('prefix_invariant.json');controls=load('controls.json')
    assert recount['complete'] and not recount['mismatches_vs_census_results'] and not guard['mismatches_vs_heldout_json']
    assert controls['passed'] and prefix['passed']
    for r in (search,wide):
        assert not r['counts'].get('time_gate_reached') and not r['N_violation_count'] and not r['repaired_A_counterexample_count'] and not r['repaired_A_bound_failure_count']
        assert not r['exact_verdicts'].get('capped',0)
    assert search['counts']['outside_census']==load('extended_search.json')['counts']['outside_census']
    assert search['counterexample_count']==load('extended_search.json')['counterexample_count']
    a=guard['guarded_rule_A_aggregate'];held=a['heldout'];train=a['train']
    coverage_rows=[]
    for s in ('chain/1def','chain/multi','nonchain/1def','nonchain/multi'):
        t=train['coverage'][s];h=held['coverage'][s]
        coverage_rows.append(f"| {s} | {fmt(t['by_A'])}/{fmt(t['certified'])} ({100*t['by_A']/t['certified']:.2f}%) | {fmt(h['by_A'])}/{fmt(h['certified'])} ({100*h['by_A']/h['certified']:.2f}%) |")
    comparison_rows=[]
    for title,r in [('Exhaustive grids plus random one/two definitions',search),('Additional two-definition helpers, 3–6 ports',wide)]:
        c=r['counts'];comparison_rows.append(f"| {title} | {fmt(c['outside_census'])} | {fmt(c['alive'])} | {fmt(r['counterexample_count'])} | {fmt(c['repaired_A_certified'])} | {r['repaired_A_counterexample_count']} / {r['repaired_A_bound_failure_count']} |")
    exhaustive={k:v for k,v in search['by_generator'].items() if k.startswith('exhaustive')}
    exhaustive_text='; '.join(f"{k.split('_')[1]}: {fmt(v['outside_census'])} outside-census descriptions, {fmt(v['alive'])} living" for k,v in exhaustive.items())
    text=f'''**Verdict: Refuted — Rule A as written.** The version that excludes **every selected-call argument from peeling, including ports in F**, survives this audit and exactly reproduces the reported census results. The forbidden implementation was neither opened nor imported; this is a defect in the written rule/proof, not a finding about that unread code.

Scope: `epic FORGET-RULE-20261114-001`, independent referee recomputation. All writes are in this directory. No network, publication, Git mutation, or shared-record edit. Rule A/N are fresh implementations from stage 2; per-call SAT projection and the exact nonrectangular-product automaton reuse the expressly permitted CENSUS-FORGET referee engine. A separate pure-set implementation verifies the decisive witness without that engine.

## 1. Rule A: counterexample search

**Block — retained outputs cannot be existentially peeled.** The written alternative “an own distinction not among call i's arguments, or a port in F” protects outputs only in its first arm. The literal second arm is false. Required repair:

```text
eligible(v) = v not in arguments(i)
              and (v is an own distinction or v is a port in F).
```

If the intended meaning of “remaining constraint” already counts the selected continuation's argument occurrences, state that explicitly; it supplies this same guard. The numerical results below support the guarded reading, but do not identify the unread implementation.

A small complete witness, with own distinctions u,v, is:

```text
S(p0,p1,p2):
  NAE(p0,p1,p2)
  NAE(p0,p2,v)
  SELF(p1,u,v)
```

Its raw A79 description is `[[3,2,[["K",[0,1,2]],["K",[0,2,4]],["SELF",[1,3,4]]]]]`. Its usual greatest support is NAE, so it is living. No pass-through correction is added. N has only the arc `1 → 0` and is acyclic.

The literal generic-start automaton reaches M empty after **3** calls. At its second step it peels through current port 1 in F even though that port is the next argument 0. The exact removed-continuation relation, with no final child-support constraint, is

```text
R((a,b,c),(d,e,f)) ⇔ NAE(a,b,c) ∧ d=b ∧ NAE(a,c,f).
```

It has 20 pairs, mask `0x00aa0555aaa05500`. For every n≥1,

```text
R^n[010] = {{101,111}} at odd n, {{000,010}} at even n;
R^n[101] = the opposite row.
```

Only 101 in the first row and 010 in the second can continue, since constant intermediate triples violate the next block's first NAE. This proves the displayed rows for all n. Crossed pairs are absent, so no power is rectangular. Independently, `R²=0x00ffa0ffff05ff00`, `R³=0x00ff05ffffa0ff00`, and `R⁴=R²` give an exact period-two certificate. The guarded automaton rejects the family. See [counterexample.json](counterexample.json).

This minimal key is absent from the full 124,572-record census, but nine isomorphic presentations occur there, all classified bounded and outside the 12,772-family first-ray-grower study. I therefore also verified a stronger holdout with **no isomorphic presentation** under any port/own renaming, NAE argument reorder, or call reorder:

```text
S(p0,p1,p2), own u,v,w,x:
  NAE(u,w,x)
  NAE(p0,p2,v)
  NAE(p0,p1,u)
  NAE(p0,p1,p2)
  SELF(v,w,p1)
```

All four own distinctions are used. Its raw description and complete lasso are in [structural_and_boundary_controls.json](structural_and_boundary_controls.json). Literal A again certifies r≤3; its exact products are nonrectangular and periodic; guarded A rejects it.

Both search pools stayed within raw language caps, used only living greatest-limit families for the theorem tests, and exactly decided every tested family; **no search case was capped**.

| Search pool | Distinct keys outside full census | Living/exactly tested | Literal A false certificates | Guarded A certificates | Guarded false certificates / bound failures |
| --- | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(comparison_rows)}

The first pool includes two completed exhaustive grids, {exhaustive_text}. Grid 1 covers own counts 0–2, every ordered distinct SELF triple, and every set of 0–3 unordered NAE triples. Grid 2 covers the same own counts and continuations, every placement of a ternary NAE helper, and 0–1 additional NAE triples. Random searches add own counts through 6, multiple continuation/side calls, recursive side definitions, and two-definition helpers with 3–6 ports. Literal A also gave **{fmt(search['bound_failure_count'])}** incorrect finite bounds in the first pool and **{fmt(wide['bound_failure_count'])}** in the second. Counts are distinct description keys within each pool; the pools are reported separately, without asserting structural uniqueness or adding potentially overlapping pools. No guarded-rule failure was found; finite search alone does not prove its theorem.

## 2. Rule N

**Confirmed on living families.** No identity-cyclic family forgot in either search pool or among all 12,772 recomputed census families. The proof needs nonemptiness: on the nonempty powers of a cycle word, identity forces equality of an endpoint coordinate; complement closure supplies both diagonal values, and a rectangle would contain the missing crossed values. Rectangularity persists under further composition, so arbitrarily long nonrectangular cycle-word powers exclude every uniform r.

**Narrowing — state the living/nonempty-word hypothesis.** Complement closure alone does not imply either value occurs. An A79 negative-domain control uses all ten NAE triples on five distinctions plus `SELF(p0,p1,p2)`: it is unsatisfiable, identity-cyclic, and has empty (hence rectangular) R. For a living greatest-limit S, every word has a nonempty realization with endpoints in its support, which supplies the missing premise. See [structural_and_boundary_controls.json](structural_and_boundary_controls.json).

## 3. Proof of Rule A

**(a) Block — the F output guard above is necessary.** After that repair, preserve two invariants: F contains no identity of an original top port and no variable touched by a retained upper constraint; every eliminated variable is absent from the next frontier. An eligible own distinction is fresh above and absent below. An eligible F port is absent above and absent below. Degree one is then degree one in the whole composite, and its full two-coordinate projection justifies exact existential elimination. Not revisiting older layers can miss additional eliminations, which only makes the guarded test conservative.

**(b) Not a block — frontier partitions retain climb-back paths.** Joining the old frontier partition with the new block and restricting to its arguments computes connectivity in the entire retained prefix. Every excursion into an older prefix enters and leaves through its frontier, whose connectivity is already recorded. A prefix component missing that frontier cannot reconnect later. Complete-prefix checks matched **{fmt(prefix['prefix_steps'])}** guarded transitions on **{fmt(prefix['words'])}** six-layer words, including the advisor's inequality gadget; **{fmt(prefix['steps_with_nontrivial_upper_partition'])}** transitions had a nontrivial upper partition. See [prefix_invariant.json](prefix_invariant.json). The advisor's 22-state count excludes F; use the actual augmented automaton's longest-live-path bound.

**(c) Not a block — the generic start is necessary and fixes the reconstructed eight training errors.** A main-conditioned entry can already be a product even though generic S products are not. I reconstructed main-entry states without reading the first implementation: it produces **8** nonforgetting false certificates in training, and **9** in held out. All 17 are rejected by the generic guarded start. This reproduces the reported training count, not the unavailable historical identities. See [guarded_recount_and_starts.json](guarded_recount_and_starts.json).

**(d) Narrowing — rectangularity and bond growth have different premises.** Rules N and guarded A, H1–H3, and the forgetting fractions in H4 are relational statements; they do not need the gap argument. Interpreting forgetting as a growing free-bond lower bound does: it covers copies of S whose ancestry after main consists of S calls. Other recursive own targets and delayed routes to S are not automatically covered. For wrappers use `2 + floor((s−1)/r)`, as specified by the [earlier referee](../../../CENSUS-FORGET-20261114-001/referee-R1/report.md). Saying only “copies of S” misses delayed S. The identity/forced-equality-only explanation remains a hypothesis; N plus a sufficient rule do not prove a characterization. See [proof_critique.md](proof_critique.md) for the full invariant argument.

## 4. Held-out read

I freshly rebuilt all **12,772** greatest-limit blocks, all **{fmt(recount['R_i_fresh'])}** per-call relations, and every exact forgetting decision. Every R_i and all previously completed verdicts/least r values match the permitted CENSUS-FORGET data. The graph method also resolves all **66** previously capped cases as nonforgetting. The guarded implementation reproduces **every field** of both train and held-out tables in `heldout.json`.

- **H1:** 0 held-out N violations.
- **H2, guarded A:** 1,051 certificates; 0 false certificates; all exact r are within the guarded bounds.
- **H3, guarded A:** 1,051/2,861 = **36.7354%**, within the frozen band; training is 1,107/2,980 = 37.1477%. Each stratum is within eight percentage points.
- **H4:** all **2,096/2,096** N-acyclic chains forget; **765/817 = 93.6353%** N-acyclic non-chains forget.

| Stratum | Training guarded A / forgetting | Held-out guarded A / forgetting |
| --- | ---: | ---: |
{chr(10).join(coverage_rows)}

**Block — these numerical confirmations require the guarded reading.** Literal A instead certifies **1,372** held-out families (47.96% of forgetting families), with **273 incorrect r bounds**; training gives 1,421 certificates and 277 incorrect bounds. It has no nonforgetting false certificate *in this selected study population*, but the outside-population witnesses above refute general sufficiency. Therefore literal H2 fails its frozen bound clause and literal H3 fails its 30–42% band. See [heldout_recount.json](heldout_recount.json), [heldout_fresh.jsonl](heldout_fresh.jsonl), and [guarded_recount_and_starts.json](guarded_recount_and_starts.json).

## Files written and reproduction

- Fresh rules/engine adapter: [independent_rules.py](independent_rules.py); controls: [controls.json](controls.json).
- Search: [search_counterexamples.py](search_counterexamples.py), [wide_search.py](wide_search.py); `first_search.*`, `extended_search.*`, `final_search.*`, `wide_search.*` JSON/JSONL. First/extended runs preserve discovery history; final search adds explicit guarded-bound checks over the same deterministic pool, not additional independent families.
- Decisive verification: [validate_counterexample.py](validate_counterexample.py), [counterexample.json](counterexample.json), [structural_and_boundary_controls.py](structural_and_boundary_controls.py), its JSON.
- Census/start audit: [recount_heldout.py](recount_heldout.py), [audit_starts_and_counts.py](audit_starts_and_counts.py), and the three result files linked above.
- Whole-prefix audit: [check_prefix_invariant.py](check_prefix_invariant.py), [prefix_invariant.json](prefix_invariant.json).
- Delegated proof audit: [proof_critique.md](proof_critique.md), [proof_critique.json](proof_critique.json).
- Assembly/provenance: [write_report.py](write_report.py), [summary.json](summary.json), [run_manifest.json](run_manifest.json), [validation.json](validation.json), this report.

All Python runs use `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`. Reproduction commands and content hashes are in `run_manifest.json`. At most three research jobs ran concurrently; each used a 2 GiB address-space ceiling once the referee adapter loaded. The largest measured job RSS was {max(search['max_rss_kib'],wide['max_rss_kib'],recount['max_rss_kib'])/1024:.1f} MiB. Every substantive command completed below 15 minutes. No theorem is inferred from the number of tests, and no shared correction/publication/lifecycle file was edited under this task's write restriction.
'''
    (HERE/'codex_report.md').write_text(text)
    summary={'verdict':'Refuted','qualification':'Literal stage-2 Rule A refuted; all reported results reproduce with selected-call-output protection.',
        'Rule_A_required_guard':'Every eliminated variable is absent from the selected continuation arguments; this includes ports in F.',
        'counterexample':witness['defs'],'counterexample_R':witness['R'],'counterexample_A_bound':witness['A_literal']['bound'],
        'structural_holdout_counterexample':boundary['structurally_new_counterexample']['defs'],
        'search_pools':[{k:r[k] for k in ('mode','seed','counts','exact_verdicts','counterexample_count','bound_failure_count','N_violation_count','repaired_A_counterexample_count','repaired_A_bound_failure_count','seconds')} for r in (search,wide)],
        'census_families':recount['families'],'census_fresh_R_i':recount['R_i_fresh'],'guarded_heldout':held,
        'main_start_false_training':guard['main_relative_nonforgetting_by_half']['train'],'main_start_false_heldout':guard['main_relative_nonforgetting_by_half']['heldout'],
        'prefix_invariant':prefix,'exact_engine_inherited':True,'producer_Python_opened_or_imported':False}
    (HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    paths=[
        'research/FORGET-RULE-20261114-001/forget_rule.md','research/FORGET-RULE-20261114-001/preregistration.md','research/FORGET-RULE-20261114-001/advisor_review_answer.md',
        'research/FREE-TARGET-20261114-001/referee-R1/codex/relations_audit.py','research/CENSUS-FORGET-20261114-001/referee-R1/codex/sample_audit.py',
        'research/CENSUS-FORGET-20261114-001/referee-R1/report.md',
        'experiments/SHORT-DESC-20261112-001A/SHORT-DESC-20261112-001A-E001_description_census/dlang.py',
        'experiments/LIMIT-STATE-20261112-001A/LIMIT-STATE-20261112-001A-E001_limit_states/census.py',
        'artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz',
        'experiments/CENSUS-FORGET-20261114-001A/CENSUS-FORGET-20261114-001A-E001_forget_census/full/results.jsonl',
        'experiments/FORGET-RULE-20261114-001A/FORGET-RULE-20261114-001A-E001_rule/heldout.json',
        'experiments/FORGET-RULE-20261114-001A/FORGET-RULE-20261114-001A-E001_rule/gadget_control.json']
    commands=['independent_rules.py','validate_counterexample.py','structural_and_boundary_controls.py',
        'recount_heldout.py','audit_starts_and_counts.py','check_prefix_invariant.py',
        'search_counterexamples.py --mode all --seconds 600 --count 100000 --name final_search','wide_search.py','write_report.py']
    manifest={'scope_kind':'epic','scope_id':'FORGET-RULE-20261114-001','role':'independent referee assistant','created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'python':sys.executable,'python_version':platform.python_version(),'commands':['/home/jscul/p-vs-np-contact-first/.venv/bin/python -B '+str(HERE/command) for command in commands],
        'forbidden_python_prefix':'experiments/FORGET-RULE-20261114-001A/','forbidden_source_opened_or_imported':False,
        'network_used':False,'Git_mutations':False,'publication':False,'write_root':str(HERE),
        'input_sha256':{s:digest(ROOT/s) for s in paths},
        'source_sha256':{p.name:digest(p) for p in sorted(HERE.glob('*.py'))},
        'evidence_sha256':{p.name:digest(p) for p in sorted(HERE.iterdir()) if p.suffix in ('.json','.jsonl','.md') and p.name not in ('run_manifest.json','validation.json','brief_codex.md','codex_last_message.md')},
        'resource_scope':'No more than three scientific subprocess jobs; adapter caps each at2GiB address space. Tool orchestration and filesystem edits are not computational workers.',
        'subagent':{'role':'bounded independent proof critique','native_thread_id':'01a1d7aa-a9b1-7040-a90f-1dfd6963d356','owned_files':['proof_critique.md','proof_critique.json']},
        'epistemic_classes':['counterexample with uniform mathematical proof','exact finite recomputation','bounded exploratory search','advisory proof critique'],
        'prior_files_preserved':['brief_codex.md','codex_last_message.md']}
    (HERE/'run_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (HERE/'validation.json').write_text(json.dumps({'phase':'validating'})+'\n')
    validation={'Python_AST_files':0,'JSON_files':0,'JSONL_files':0,'JSONL_records':0,'local_links_checked':0,'errors':[]}
    for p in sorted(HERE.iterdir()):
        if p.suffix=='.py':ast.parse(p.read_text(),filename=p.name);validation['Python_AST_files']+=1
        if p.suffix=='.json':json.loads(p.read_text());validation['JSON_files']+=1
        if p.suffix=='.jsonl':
            validation['JSONL_files']+=1
            for line in p.open():json.loads(line);validation['JSONL_records']+=1
    for name in ('codex_report.md','proof_critique.md'):
        for target in re.findall(r'\]\(([^)]+)\)',(HERE/name).read_text()):
            if '://' in target:continue
            validation['local_links_checked']+=1
            if not (HERE/target.split('#')[0]).exists():validation['errors'].append({'file':name,'missing_link':target})
    validation['semantic_assertions_passed']=True;validation['all_valid']=not validation['errors']
    (HERE/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    assert validation['all_valid'],validation
    print(json.dumps({'verdict':summary['verdict'],'validation':validation,'report':str(HERE/'codex_report.md'),'fresh_R_i':recount['R_i_fresh']}))

if __name__=='__main__':main()
