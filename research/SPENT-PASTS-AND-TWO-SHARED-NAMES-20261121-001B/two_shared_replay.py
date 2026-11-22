"""Exact four-place source transitions and the two-reader signed instrument."""

import argparse
from collections import Counter, defaultdict
from dataclasses import astuple, dataclass, replace
from fractions import Fraction as F
import gzip
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIOR = HERE.parent / "UNREAD-COMPANION-AND-ORDER-FREE-WEIGHTING-20261121-001A"
sys.path[:0] = [str(PRIOR), str(ROOT / "tools")]
from companion_replay import (
    ALLOWED, BITS, ETA, IDENTITY, LAWS, ONE, SIGNED, TARGET_IDENTITY, Exact,
    Evidence, Mat, Matrix, classical_hardware, filter_columns, from_coefficients,
    local_hardware, null, record_address, sum_matrices,
)
from knotlab.knots import check_knot
from knotlab.relations import Relation


ORDER = "acbd"
SOURCES = tuple("".join(w) for w in product("01", repeat=4))
ACB = tuple("".join(w) for w in product("01", repeat=3))
ROWS = tuple("".join(w) for w in product("01", repeat=2))
COMPANIONS = {"together": "acd", "split": "abd"}
WEAK_RATE = Exact(F(1, 45))


def project(word, places):
    return "".join(word[ORDER.index(n)] for n in places)


def lawfulness(word, placement, laws):
    return tuple(project(word, places) in ALLOWED[law]
                 for places, law in zip(("acb", COMPANIONS[placement]), laws, strict=True))


def connected_sets(vertices, links):
    remaining = set(vertices)
    outcomes = []
    while remaining:
        marked = {min(remaining)}
        while True:
            additional = {b for a, b in links if a in marked} - marked
            if not additional:
                break
            marked |= additional
        outcomes.append(sorted(marked))
        remaining -= marked
    return outcomes


def source_table(placement, laws):
    checked = {w: lawfulness(w, placement, laws) for w in SOURCES}
    lawful = tuple(w for w, status in checked.items() if all(status))
    projection = {}
    for names, law in zip(("acb", COMPANIONS[placement]), laws, strict=True):
        counts = Counter(project(w, names) for w in lawful)
        assert tuple(sorted(counts)) == ALLOWED[law]
        relation = Relation(tuple(names), frozenset(tuple(bool(int(x)) for x in w) for w in counts))
        gates = check_knot(relation, names[:2], names[2])
        assert gates.is_knot
        projection[names] = {"extensions": {w: counts[w] for w in ACB}, "K1_K2_K3": gates.as_dict()}

    mathematics = {}
    for d in "01":
        options = [w for w in lawful if w[3] == d]
        steps = [(x, y) for x, y in product(options, repeat=2) if x != y and
                 (x[:2] == y[:2] or x[2] == y[2])]
        mathematics[d] = {"whole_words": options, "weight": str(F(len(options), len(lawful))),
                          "A_rows_00_01_10_11_B_columns_0_1": [[int(r+b+d in lawful) for b in "01"] for r in ROWS],
                          "one_site_moves_at_fixed_unread_word": steps,
                          "mutually_reachable_sets": connected_sets(options, steps)}
    reachable_ready = {}
    for side, positions, remainder in (("A", "ac", "bd"), ("B","b","acd")):
        fibres = {x: sorted({project(w,remainder) for w in lawful if project(w,positions) == x})
                  for x in (ROWS if side == "A" else "01")}
        allowed = {x: [y for y, right in fibres.items() if set(left) <= set(right)] for x, left in fibres.items()}
        reachable_ready[side] = {"prior_word_remote_fibres": fibres, "uniformly_lawful_local_substitutions": allowed,
                                 "meaning": "One reset of a current local value with blank work and no information from another reader."}

    def density(coherent):
        return Mat([[sum(w+d in lawful and v+d in lawful for d in "01") if coherent or w == v else 0
                     for v in ACB] for w in ACB], len(lawful)).dump()

    companion_swapped = COMPANIONS[placement][1] + COMPANIONS[placement][0] + "d"
    assert all((project(w,companion_swapped) in ALLOWED[laws[1]]) == checked[w][1] for w in SOURCES)
    swap_a_c = str.maketrans("ac","ca")
    recoded_companion = COMPANIONS[placement].translate(swap_a_c)
    recoded = {w: w[1]+w[0]+w[2:] for w in lawful}
    assert all(project(v,recoded_companion) == project(w,COMPANIONS[placement]) for w,v in recoded.items())
    return {"all_original_rows": checked, "allowed_acbd": lawful, "full_preparation_denominator": len(lawful),
            "named_projections": projection, "d_slices_only_mathematical": mathematics,
            "local_information_at_start": reachable_ready, "reduced_acb_order": ACB,
            "reduced_after_tracing_d": {"coherent": density(True), "diagonal": density(False)},
            "read_order_recodings": {"reverse_shared_order_in_companion": companion_swapped,
                                     "exchange_first_reader_name_labels": recoded,
                                     "companion_under_A_name_exchange": recoded_companion}}


@dataclass(frozen=True, order=True)
class Held:
    acbd: str
    u: int = 0
    v: int = 0
    saved_a: int = 0
    tag_a: str = ""
    tag_b: str = ""

    def remote_to(self, site):
        if site == "A":
            return self.acbd[2:], self.v, self.tag_b
        assert site == "B"
        return self.acbd[:2], self.acbd[3], self.u, self.saved_a, self.tag_a

    def leftover(self):
        return self.acbd, self.saved_a, self.tag_a, self.tag_b


def density_rows(rho):
    return [[astuple(x), astuple(y), q.pack()] for (x, y), q in sorted(rho.items()) if q]


class Trace:
    def __init__(self, placement, laws, coherent, words):
        self.placement, self.laws, self.coherent, self.words = placement, laws, coherent, words
        self.paths = {w: {Held(w): ONE} for w in words}
        self.den = ONE
        self.rho = {(Held(w), Held(v)): Exact(F(1, len(words))) for w, v in product(words, repeat=2)
                    if coherent or w == v}
        self.steps = [self.snapshot("supplied four-place preparation", "preparation")]

    def fork(self):
        out = object.__new__(Trace)
        out.__dict__ = self.__dict__.copy()
        out.steps = self.steps.copy()
        return out

    def lawful(self, x):
        return all(lawfulness(x.acbd, self.placement, self.laws))

    def weight(self):
        return sum((q for (x, y), q in self.rho.items() if x == y), Exact())

    def snapshot(self, label, side):
        assert all(self.lawful(x) and self.lawful(y) for x, y in self.rho)
        assert all(self.rho.get((y, x)) == q for (x, y), q in self.rho.items())
        words = defaultdict(Exact)
        for (x, y), q in self.rho.items():
            if x == y:
                assert q.nonnegative()
                words[x.acbd] += q
        total = sum(words.values(), Exact())
        assert total == self.weight()
        return {"primitive": label, "reader": side, "weight_per_launch": total.pack(),
                "source_word_weights": {w: q.pack() for w, q in sorted(words.items()) if q},
                "conditional_source_words": {w: (q/total).pack() for w,q in sorted(words.items()) if q} if total else None,
                "held_density": density_rows(self.rho)}

    def inadmissible_ready_moves(self, image):
        return [[orig, astuple(x), astuple(y), lawfulness(y.acbd, self.placement, self.laws)]
                for orig, paths in self.paths.items() for x in sorted(paths) if not self.lawful(y := image(x))]

    def prepared_inputs(self):
        return {x for x,y in self.rho if x == y}

    def update(self, label, side, op, denominator=ONE, *, weak=False):
        local = sorted(set().union(*(m.keys() for m in self.paths.values())))
        columns = {x: tuple((y, Exact.get(n)) for y, n in op(x) if n) for x in local}
        prohibited = []
        prepared = self.prepared_inputs()
        for x, outputs in columns.items():
            for y, _ in outputs:
                assert x.remote_to(side) == y.remote_to(side)
                if not self.lawful(y):
                    prohibited.append([astuple(x), astuple(y)])
                    assert weak and x not in prepared, (label, x, y)
        density = defaultdict(Exact)
        for (x, y), q in self.rho.items():
            for (a, r), (b, s) in product(columns[x], columns[y]):
                density[a,b] += q*r*s/denominator
        self.rho = {k: v for k,v in density.items() if v}
        paths = {}
        for origin, before in self.paths.items():
            after = defaultdict(Exact)
            for x, q in before.items():
                for y,n in columns[x]:
                    after[y] += q*n
            paths[origin] = {x:n for x,n in after.items() if n}
        self.paths = paths
        self.den *= denominator
        row = self.snapshot(label,side)
        row["column_squared_denominator"] = denominator.pack()
        row["nonzero_named_columns"] = [[astuple(x), [[astuple(y), n.pack()] for y,n in p]] for x,p in columns.items()]
        row["invalid_under_primary_basis_rule"] = prohibited
        self.steps.append(row)
        return self

    def move(self, label, side, image, *, weak=False):
        return self.update(label,side,lambda x: ((image(x),1),),weak=weak)

    def select(self, label, side, pred):
        return self.update(label,side,lambda x: ((x,1),) if pred(x) else ())

    def refuse(self, label, bad=()):
        self.steps.append(self.snapshot(label,"no offer"))
        self.steps[-1]["counterfactual_invalid_basis_transitions"] = bad
        return self

    def final(self):
        reconstructed = defaultdict(Exact)
        for (w,a),(v,b) in product(self.paths.items(),repeat=2):
            if self.coherent or w == v:
                for (x,q),(y,p) in product(a.items(),b.items()):
                    reconstructed[x,y] += q*p/self.den/len(self.words)
        assert self.rho == {k:q for k,q in reconstructed.items() if q}
        private = defaultdict(Exact)
        readable = defaultdict(Exact)
        for (x,y),q in self.rho.items():
            if x.acbd[3] == y.acbd[3]:
                readable[replace(x,acbd=x.acbd[:3]), replace(y,acbd=y.acbd[:3])] += q
            if x.leftover() == y.leftover():
                private[2*x.u+x.v,2*y.u+y.v] += q
        return {"weight": self.weight().pack(), "source_steps": self.steps,
                "final_four_word_paths": {w:[[astuple(x),q.pack()] for x,q in sorted(p.items())] for w,p in self.paths.items()},
                "final_common_squared_denominator": self.den.pack(),
                "readable_source_work_density_after_tracing_d": density_rows(readable),
                "meter_density_in_00_01_10_11_order": [[private[x,y].pack() for y in range(4)] for x in range(4)]}


def copy_coordinates(trace):
    trace.move("A copies its local parity to the ready meter", "A",
               lambda x: replace(x,u=x.u ^ int(x.acbd[0] != x.acbd[1])))
    trace.move("B copies old b and leaves it physical", "B", lambda x: replace(x,v=x.v ^ int(x.acbd[2])))


def transfer_c(x):
    a,c = map(int,x.acbd[:2])
    return replace(x,acbd=str(a)+str(x.u ^ (1-a))+x.acbd[2:],u=c)


def transfer_b(x):
    return replace(x,acbd=x.acbd[:2]+str(x.v)+x.acbd[3],v=int(x.acbd[2]))


def transfer_a_to_one(x):
    a,c = map(int,x.acbd[:2])
    change = 1 ^ x.saved_a
    return replace(x,acbd=str(change)+str(a ^ c ^ change)+x.acbd[2:],saved_a=a)


def balanced_filter(trace, s):
    f = filter_columns()[s]
    records = []
    for label, numerator, den, admit in (
        ("balance_success",f["inverse"],ONE/ETA,True),
        ("balance_refusal",f["refusal_matrix"],f["refusal_den"],False),
    ):
        branch = trace.fork().update(label,"A",lambda x: tuple((replace(x,u=i),r[x.u]) for i,r in enumerate(numerator)),den)
        records.append((label,branch,admit))
    return records


def isolated_equal(trace, keep):
    entries = []
    for value in ("equal","unequal"):
        b = trace.fork().select("A reports the " + value + " row predicate","A",
                                lambda x: (x.acbd[0] == x.acbd[1]) == (value == "equal"))
        admit = False
        if value == "equal":
            b.move("copy a without recording which equal row","A",lambda x: replace(x,u=int(x.acbd[0])))
            if keep:
                b.move("B retains b and copies its complemented value","B",lambda x: replace(x,v=x.v ^ (1-int(x.acbd[2]))))
                admit = True
            else:
                for label,side,action in (("clear the original A row to 01","A",lambda x: replace(x,acbd="01"+x.acbd[2:])),
                                          ("clear b into its private bit","B",transfer_b)):
                    if bad := b.inadmissible_ready_moves(action):
                        b.refuse("old isolated equality offer stops before " + label,bad)
                        break
                    b.move(label,side,action)
                else:
                    b.move("B complements its private copy","B",lambda x: replace(x,v=1-x.v))
                    admit = True
        entries.append((value,b,admit))
    return entries


def shared_read(trace, joint):
    for a in BITS:
        ta = trace.fork().select(f"A reports actual a={a}","A",lambda x: x.acbd[0] == str(a))
        if not joint:
            yield f"a={a}",ta,a
            continue
        side = "A" if trace.placement == "together" else "B"
        name = "c" if side == "A" else "b"
        i = ORDER.index(name)
        for v in BITS:
            tb = ta.fork().select(f"{side} reports actual {name}={v}",side,lambda x: x.acbd[i] == str(v))
            yield f"a={a},{name}={v}",tb,a


def prior_shared_route(trace):
    out = []
    for key,t,s in shared_read(trace,False):
        for label,side,action in (("retain old c privately and set c=1-a","A",transfer_c),
                                  ("retain old b privately and set b=0","B",transfer_b)):
            if bad := t.inadmissible_ready_moves(action):
                out.append((key+"/refusal",t.refuse("old one-shared route stops before " + label,bad),False))
                break
            t.move(label,side,action)
        else:
            out.extend((key+"/"+label,branch,admit) for label,branch,admit in balanced_filter(t,s))
    return out


FIRST_FAILURES = (("plus_refusal",(1,1),F(2)),("minus_refusal",(1,-1),F(4)))
LAST_FAILURES = (("refusal_1",(5,0,-2),F(45)),("refusal_2",(0,8,1),F(72)),("refusal_3",(0,0,1),F(40,27)))


def weak_split(trace, enabled, tag, phase):
    assert trace.placement == "split" and trace.laws == ("nae","nae")
    if tag:
        trace.move("retain an actual tag of the original A row","A",lambda x: replace(x,tag_a=x.acbd[:2]))
        trace.move("retain an actual tag of original b","B",lambda x: replace(x,tag_b=x.acbd[2]))
    trace.move("transfer c privately while leaving c=1-a","A",transfer_c)

    def first_pass(x):
        if x.acbd[0] == "0":
            return ((replace(x,u=0),(-1)**x.u),)
        return ((x,2),)

    data = []
    for name,row,den in FIRST_FAILURES:
        failure = trace.fork().update("first filter "+name,"A",
                    lambda x: ((replace(x,u=0),row[x.u]),) if x.acbd[0] == "0" else (),Exact(den))
        data.append((name,failure,False))
    passed = trace.fork().update("first filter passes, compress only the A sector a=0","A",first_pass,Exact(F(4)))
    bad = passed.inadmissible_ready_moves(transfer_b)
    assert bad and not passed.inadmissible_ready_moves(lambda x: x)
    ready_on_current_state = all(passed.lawful(transfer_b(x)) for x in passed.prepared_inputs())
    if not enabled or not ready_on_current_state:
        passed.refuse("withhold B transfer before any illegal source or target change",bad)
        return [*data,("pass_but_B_refuses",passed,False)]
    assert trace.coherent and not tag
    assert {i[0] for i in bad} == {"0010","0110"}
    passed.move("prepared-state-only B transfer to private v, leaving b=0","B",transfer_b,weak=True)
    passed.move("save old a privately and set physical A to 10","A",transfer_a_to_one,weak=True)

    def filter_arm(x, rows):
        k = ((0,0),(1,0),(1,1)).index((x.saved_a,x.u))
        return tuple((replace(x,saved_a=0,u=i),r[k]) for i,r in enumerate(rows))

    fine = (("success",((2,0,1),(0,1,-1)),F(9),True),
            *((key,(row,),den,False) for key,row,den in LAST_FAILURES))
    for key,rows,den,admit in fine:
        branch = passed.fork().update("final private "+key,"A",lambda x: filter_arm(x,rows),Exact(den),weak=True)
        if admit and phase:
            branch.update("act with a supplied private real phase reversal at B","B",
                          lambda x: ((x,(-1)**x.v),),weak=True)
        data.append(("first_pass/"+key,branch,admit))
    return data


def extract(trace, method, tag=False, phase=False):
    if method == "isolated_equal":
        return isolated_equal(trace,False)
    if method == "retain_equal_words":
        return isolated_equal(trace,True)
    if method == "coordinate_copies":
        copy_coordinates(trace)
        return [("offered",trace,True)]
    if method in ("public_shared_value", "public_shared_pair"):
        out = []
        for label,branch,_ in shared_read(trace,method == "public_shared_pair"):
            copy_coordinates(branch)
            out.append((label,branch,True))
        return out
    if method == "prior_one_shared":
        return prior_shared_route(trace)
    assert method in ("primary_attempt_of_weak", "prepared_state_only")
    return weak_split(trace, method == "prepared_state_only", tag, phase)


def target_matrix(trace, addresses, drives):
    total = defaultdict(Exact)
    words = defaultdict(lambda: defaultdict(Exact))
    writers = set()
    denominator = 2**sum(a is not None for a in addresses)
    for (x,y),q in trace.rho.items():
        if x.leftover() != y.leftover():
            continue
        a,b = (x.u,x.v), (y.u,y.v)
        if any(port is None and i != j for port,i,j in zip(addresses,a,b,strict=True)):
            continue
        exponent = sum(port*(i+j) for port,i,j in zip(addresses,a,b,strict=True) if port is not None)
        weight = q*F((-1)**exponent,denominator)
        words[x.acbd][a,b] += weight
        total[a,b] += weight
        writers.add(tuple("ab"[port] if port is not None else "idle_"+"ab"[i]
                          for port,i in zip(addresses,a,strict=True)))
    return from_coefficients(total,drives), {w:from_coefficients(p,drives) for w,p in sorted(words.items())}, sorted(writers)


def check_input_trace(population, mode, source):
    prior = defaultdict(F)
    for x,y,q in source.steps[0]["held_density"]:
        if x[0][3] == y[0][3]:
            assert q[1] == "0"
            prior[x[0][:3],y[0][:3]] += F(q[0])
    det = population["reduced_after_tracing_d"][mode]
    assert [[prior[x,y] for y in ACB] for x in ACB] == [[F(q,det["den"]) for q in row] for row in det["rows"]]


def evaluate(evidence, placement, laws, population, coherent, method, *, tag=False, phase=False, fault="intact"):
    trace = Trace(placement,laws,coherent,population["allowed_acbd"])
    mode = "coherent" if coherent else "diagonal"
    check_input_trace(population,mode,trace)
    branches = extract(trace,method,tag,phase)
    words = trace.words
    for w,v in product(words,repeat=2):
        gram = sum((n*s.paths[v].get(out,Exact())/s.den
                    for _,s,_ in branches for out,n in s.paths[w].items()), Exact())
        assert gram == Exact.get(w == v)

    source, fine, complete = {}, {}, {}
    accepted = Exact()
    refusal = null(16)
    for label,branch,proceed in branches:
        p = branch.weight()
        source[label] = branch.final()
        source[label]["proceed"] = proceed
        if proceed:
            accepted += p
        analyzes = (proceed and fault != "A_reader_idle", proceed)
        drives = (analyzes[0], proceed and fault != "B_gate_disconnected")
        branch_effects = []
        for address in product(*(BITS if x else (None,) for x in analyzes)):
            channel, named, writer = target_matrix(branch,address,drives)
            row = label+":"+record_address(address)
            sign = (-1)**sum(address) if None not in address else None
            if not proceed:
                assert channel == IDENTITY.scale(p)
                assert address == (None,None)
                refusal += channel
            raw = evidence.probe(channel,named,p)
            for point in raw.values():
                point["four_place_word_weights"] = point.pop("named_five_place_word_weights")
                point["four_place_conditional_word_weights"] = point.pop("named_five_place_conditional_word_weights")
            fine[row] = {
                "source_record": label, "physical_analyzer_flags": address, "offered_target_controls": drives,
                "sign_if_both_actual_flags_arrive": sign, "target_channel": evidence.channel(channel),
                "target_channels_by_four_place_diagonal_word": {w:evidence.channel(ch) for w,ch in named.items()},
                "eligible_actual_writer_pairs": writer if proceed else [("blank","blank")],
                "probes": raw,
            }
            complete[row] = channel
            branch_effects.append(channel.effect())
        assert sum_matrices(branch_effects,4) == TARGET_IDENTITY.scale(p)
    assert sum_matrices((ch.effect() for ch in complete.values()),4) == TARGET_IDENTITY
    assert refusal == IDENTITY.scale(ONE-accepted)

    sign_maps = {t: sum_matrices((complete[k] for k,v in fine.items()
                                 if v["sign_if_both_actual_flags_arrive"] == t),16) for t in (1,-1)}
    succeeds = bool(accepted) and all(sign_maps[t] == SIGNED[t].scale(accepted) for t in (1,-1))
    sign_probs = bool(accepted) and all(sign_maps[t].effect() == SIGNED[t].effect().scale(accepted) for t in (1,-1))
    is_comparison = method == "prepared_state_only"
    receives_weak_meter = is_comparison and coherent and not tag
    if receives_weak_meter:
        assert accepted == WEAK_RATE
        assert source["first_pass/success"]["source_steps"][-1]["source_word_weights"] == {"1000":WEAK_RATE.pack()}
        assert source["plus_refusal"]["weight"] == Exact(F(9,20)).pack()
        assert source["minus_refusal"]["weight"] == Exact(F(1,40)).pack()
        if fault == "intact":
            frame = -1 if phase else 1
            for t in (1,-1):
                assert sign_maps[t] == SIGNED[frame*t].scale(WEAK_RATE)
            for k,r in fine.items():
                t = r["sign_if_both_actual_flags_arrive"]
                if t is not None:
                    assert complete[k] == SIGNED[frame*t].scale(WEAK_RATE/2)
    else:
        assert not succeeds
        assert not any(step.get("invalid_under_primary_basis_rule")
                       for x in source.values() for step in x["source_steps"])
    if method == "primary_attempt_of_weak":
        assert accepted == Exact()
    for s in source.values():
        for step in s["source_steps"]:
            assert all(all(lawfulness(w,placement,laws)) for w in step["source_word_weights"])
    return {
        "placement": placement, "ordered_laws": laws, "preparation": mode, "protocol": method, "tag": tag,
        "phase_reversal_control": phase, "fault_setting": fault,
        "reading": "prepared-state-only comparison" if is_comparison else "primary basis-safe",
        "all_elements_of_source_Kraus_gram_equal_identity": True,
        "all_probes_all_flags": fine, "source_records": source,
        "offered_per_full_launch": accepted.pack(), "no_source_target_operations_map": evidence.channel(refusal),
        "joined_sign_maps_per_launch": {str(t): evidence.channel(ch) for t,ch in sign_maps.items()},
        "joined_sign_maps_given_offer": {str(t): evidence.channel(ch.scale(ONE/accepted)) if accepted else None
                                         for t,ch in sign_maps.items()},
        "exact_signed_maps_with_current_labels": succeeds,
        "exact_sign_frequencies_with_current_labels": sign_probs,
    }, complete


def complete_replay(evidence):
    populations = {}
    settings, exact, failed = {}, {}, {}
    for placement,law0,law1 in product(COMPANIONS,LAWS,LAWS):
        laws = law0,law1
        group = f"{placement}/{law0}-{law1}"
        population = source_table(placement,laws)
        populations[group] = population
        for coherent in (True,False):
            mode = "coherent" if coherent else "diagonal"
            config = group + "/" + mode
            for method in ("isolated_equal","retain_equal_words","coordinate_copies",
                           "public_shared_value","public_shared_pair","prior_one_shared"):
                key = config + "/" + method
                settings[key],exact[key] = evaluate(evidence,placement,laws,population,coherent,method)
            selected = "coordinate_copies" if law0 == "parity" else "retain_equal_words"
            reference = config+"/"+selected
            channels = settings[reference]["all_probes_all_flags"]
            chosen = next((name,x) for name,x in channels.items() if x["physical_analyzer_flags"] == (0,0))
            name,row = chosen
            probe = row["probes"]["00"]
            assert probe["overlap_with_pure_ideal_conditionals"]["1"] == ["1/2","0"]
            failed[config] = {"case": reference, "actual_source_and_flag_record": name, "product_00": probe}
            if group == "split/nae-nae":
                primary = config+"/primary_attempt_of_weak"
                settings[primary],exact[primary] = evaluate(evidence,placement,laws,population,coherent,"primary_attempt_of_weak")
                variants = [("baseline",False,False,"intact")]
                if coherent:
                    variants.extend((("tag",True,False,"intact"),("phase",False,True,"intact"),
                                     ("A_reader_idle",False,False,"A_reader_idle"),
                                     ("B_gate_disconnected",False,False,"B_gate_disconnected")))
                for label,tag,phase,fault in variants:
                    key = config+"/prepared_state_only/"+label
                    settings[key],exact[key] = evaluate(evidence,placement,laws,population,coherent,
                                                        "prepared_state_only",tag=tag,phase=phase,fault=fault)
    assert sum(r["exact_signed_maps_with_current_labels"] for r in settings.values()) == 1
    return populations,settings,exact,failed


def repeat(evidence, record, exact):
    table = {}
    by_sign = defaultdict(lambda: null(16))
    completeness = null(4)
    fine = record["all_probes_all_flags"]
    for (ka,a),(kb,b) in product(exact.items(), repeat=2):
        output = b.after(a)
        completeness += output.effect()
        sa = fine[ka]["sign_if_both_actual_flags_arrive"]
        sb = fine[kb]["sign_if_both_actual_flags_arrive"]
        if sa is not None and sb is not None:
            by_sign[sa,sb] += output
        table[ka+" | "+kb] = {"target_channel": evidence.channel(output),
                              "probe_weights": {k: output.apply(evidence.inputs[k]).trace().pack()
                                                for k in ("00","1/u+v","1/u-v","-1/u+v","-1/u-v")}}
    assert completeness == TARGET_IDENTITY
    for s,t in product((1,-1),repeat=2):
        expected = SIGNED[s].scale(WEAK_RATE*WEAK_RATE) if s == t else null(16)
        assert by_sign[s,t] == expected
    return {"distinct_source_and_writers_on_second_launch": True, "all_two_launch_records": table,
            "joined_two_successful_signs": {f"{s}/{t}":evidence.channel(ch) for (s,t),ch in by_sign.items()}}


def build():
    evidence = Evidence()
    populations,settings,known,failed = complete_replay(evidence)
    weak = "split/nae-nae/coherent/prepared_state_only/baseline"
    twice = repeat(evidence,settings[weak],known[weak])
    gates,analyzers,writers,fresh,denied = local_hardware()
    joins = classical_hardware(writers)
    lookup = joins["combined_keeper_branches"]
    assert lookup["a/00/b/11/11/0"]["local_keepers"] == ("110","011")
    assert lookup["a/00/b/11/11/0"]["joined_keeper"] == "011"
    assert lookup["a/11/b/11/01/0"]["joined_keeper"] == "110"
    earlier = HERE.parent/"SPLIT-KNOT-METER-AND-CLOSING-TRIPLE-20261121-001A"
    older = HERE.parent/"TWO-READERS-ONE-SURVIVING-SIGN-20261121-001A"
    sources = (Path(__file__).resolve(),HERE/"preregistration.md",PRIOR/"companion_replay.py",earlier/"meter_replay.py",
               older/"instrument_math.py",older/"instrument_hardware.py",ROOT/"tools"/"knotlab"/"knots.py")
    return {
        "four_place_order": ORDER, "ordinary_holder_rules": ["acb",COMPANIONS],
        "source_qualification_scope": "The projected holders qualify as a supplied initial holding. The ordinary birth rule supplies only one input per parent; qualification alone gives no native birth.",
        "field": "An exact value [r,s] is r+s sqrt(5). A pair of matrix identifiers denotes the rational and root parts.",
        "retained_basis_slots": ["acbd","private_A_meter","private_B_meter","saved_a","old_A_tag","old_B_tag"],
        "populations": populations, "instrument_settings": settings, "explicit_primary_lawful_00_failures": failed,
        "prepared_state_only_positive_comparison": weak,
        "fresh_prepared_state_only_repeat": twice,
        "physical_hardware": {"actual_target_calibration": gates, "local_binary_analyzers": analyzers,
                              "local_writers": writers, "fresh_meter_transfers": fresh,
                              "refused_before_coupling_identity_word_traces": denied, "classical_collector": joins},
        "complete_channel_recipe": "Each target record sums signed data permutations selected by the private bits and weights from the final held density. Each fired X analyzer of address k contributes (-1)^(ik)/sqrt(2) at private input i, and replaces only that private register by the addressed port. Trace identical leftover words and tags. The ordinary writer and message controls follow the measured address without acting on the four source places or the target.",
        "weak_filter_details": {"first_A_sector_a0_success_numerator": [1,-1], "first_a0_success_squared_denominator": "4",
                                "first_A_sector_a1_success_identity": True,
                                "first_refusal_numerators_squared_denominators": [(k,r,str(q)) for k,r,q in FIRST_FAILURES],
                                "final_success_numerator": [[2,0,1],[0,1,-1]], "final_squared_denominator": "9",
                                "final_refusal_numerators_squared_denominators": [(k,r,str(q)) for k,r,q in LAST_FAILURES],
                                "weak_success_probability_per_full_launch": WEAK_RATE.pack()},
        "inputs": {k:evidence.cat.put(m) for k,m in evidence.inputs.items()},
        "maps": evidence.maps, "matrix_catalogue": evidence.cat.matrices,
        "summary": {"populations":len(populations), "candidate_words":len(populations)*len(SOURCES),
                    "named_valid_population_members":sum(r["full_preparation_denominator"] for r in populations.values()),
                    "instrument_settings":len(settings), "fine_source_records":sum(len(r["source_records"]) for r in settings.values()),
                    "full_single_launch_records":sum(len(r["all_probes_all_flags"]) for r in settings.values()),
                    "fresh_double_launch_records":len(twice["all_two_launch_records"]),"ordinary_writer_cases":len(lookup)},
        "source_sha256": {str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sources},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify",action="store_true",help="recompute the exact archive and require byte identity")
    args = parser.parse_args()
    result = build()
    raw = (json.dumps(result,sort_keys=True,separators=(",",":"))+"\n").encode()
    compressed = gzip.compress(raw,mtime=0)
    destination = HERE/"two_shared_evidence.json.gz"
    if args.verify:
        assert destination.read_bytes() == compressed
    else:
        destination.write_bytes(compressed)
    assert gzip.decompress(destination.read_bytes()) == raw
    print(json.dumps(result["summary"],sort_keys=True))
    print("sha256",sha256(compressed).hexdigest(),"bytes",len(compressed))


if __name__ == "__main__":
    main()
