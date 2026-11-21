"""Physical word histories and exact signed-gate calibrations for B292."""

import argparse
from collections import defaultdict
from fractions import Fraction as F
from functools import cache
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
import json
from math import isqrt
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = "TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001"
OLD = ROOT / "research" / (PREVIOUS+"B")
HARDWARE = OLD / "pointer_hardware.py"
ASSIGNMENT = ROOT / "research" / PREVIOUS / "founders.py"
CLOSURE = ROOT / "artifacts" / (PREVIOUS+"A") / (PREVIOUS+"A-E001_meetings") / "matched_and_signed.json.gz"
ERASURE = ROOT / "research/ERASURE-AND-CLOSING-SIGNS-20261121-001A/ordinary_routes.py"
OLD_CYCLE = ROOT / "research/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001A/physical_composition.py"
WORDS = "abcd"
TRITS = "abc"
LAWS = ("parity", "nae")
ZERO = (F(0), F(0))
ONE = (F(1), F(0))
H = (F(0), F(1,2))


@cache
def _prior():
    spec = spec_from_file_location("b292_ancestor_hardware",HARDWARE)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _identity(n):
    return tuple(tuple(int(i==j) for j in range(n)) for i in range(n))


def _multiply(a,b):
    return tuple(tuple(sum(x*y for x,y in zip(row,col,strict=True)) for col in zip(*b,strict=True)) for row in a)


def _tensor(a,b):
    return tuple(tuple(x*y for x in u for y in v) for u in a for v in b)


def _negative(a):
    return tuple(tuple(-x for x in row) for row in a)


def _pauli(a,b):
    p,x,z = a
    q,y,w = b
    return (p+q+2*(z&y).bit_count())%4,x^y,z^w


def _target():
    with gzip.open(CLOSURE,"rt") as src:
        archive = json.load(src)
    index = archive["four_cut_rank"]["odd_admitting"]
    physical = archive["physical_last_words"][index]
    laws = archive["ranked_sources"][index]["founder"]["laws"]
    terminal = laws["parity"]["terminal"]
    rows = physical["preceding_rows"]+[physical["closing"]["support"]]
    assert len(rows) == 18
    owners = {name: tuple(i for i,r in enumerate(rows) if name in r) for name in range(31)}
    assert len(set(owners.values())) == 31 and all(len(h)==2 for h in owners.values())
    names_by_holders = {h:name for name,h in owners.items()}
    assert names_by_holders[16,17] == 30
    routes = (((14,13,9,5,3,4,6,10),(14,12),(14,17)),
              ((15,10),(15,11,7,12),(15,17)),((16,10),(16,12),(16,17)))
    direct,archived = {},{}
    identity = _identity(2)
    x,z = ((0,1),(1,0)),((1,0),(0,-1))
    j = _multiply(x,z)
    wanted = _negative(_tensor(j,j))
    word_matrices = ((_tensor(x,identity),_tensor(identity,x),_tensor(x,x)),
                     (_tensor(identity,z),_tensor(z,identity),_tensor(z,z)),
                     (_tensor(x,z),_tensor(z,x),wanted))
    archived_routes = {frozenset(path["named_meetings"]) for path in terminal["certificate"]["paths"]}
    assigned_routes = []
    for i in range(3):
        for k in range(3):
            route, operator = routes[i][k], word_matrices[i][k]
            names = [names_by_holders[tuple(sorted((a,b)))] for a,b in zip(route,route[1:])]
            assert frozenset(names) in archived_routes
            assert tuple(zip(*operator,strict=True))==operator and _multiply(operator,operator)==_identity(4)
            assigned_routes.append({"row_holder":route[0],"column_holder":route[-1],"ordered_holders":route,
                                    "physical_names":names,"two_word_slots_matrix":operator})
            for name in names:
                assert name not in direct
                direct[name] = operator
    assert direct[30] == wanted
    archived = {name:tuple(op) for name,op in terminal["binary_pauli"]["actual_named_operators"]}
    assert set(archived)==set(owners) and all(_pauli(p,p)==(0,0,0) for p in archived.values())
    reports = []
    for h, row in enumerate(rows):
        result, phase = _identity(4),(0,0,0)
        ops = [direct.get(name,_identity(4)) for name in row]
        for a,b in combinations(ops,2):
            assert _multiply(a,b)==_multiply(b,a)
        for a,b in combinations([archived[name] for name in row],2):
            assert _pauli(a,b)==_pauli(b,a)
        for name,op in zip(row,ops,strict=True):
            result = _multiply(result,op)
            phase = _pauli(phase,archived[name])
        assert result == (_negative(_identity(4)) if h==17 else _identity(4))
        assert phase == (2 if h==17 else 0,0,0)
        reports.append({"holder":h,"names":row,"real_matrix_product":result,"archived_binary_pauli_product":phase})
    assert laws["nae"]["terminal"] is None
    even_last = laws["parity"]["cuts"][-1]["births"][0]
    nae_last = laws["nae"]["cuts"][-1]["births"][0]
    assert even_last["inputs"]==nae_last["inputs"]==[28,29,30] and even_last["new_names"]==[] and nae_last["new_names"]==[31]
    assert physical["supplied_odd"]["words"]==0
    return {"physical_name":30,"owners":owners[30],"word_order":["00","01","10","11"],"observable":wanted,
            "all_eighteen_signed_products":reports,"all_local_commutations_checked":True,
            "independent_four_by_four_routes":assigned_routes,"all_named_binary_pauli_operators":archived,
            "comparison_of_namings":"The archived routes are grouped from columns to rows. Each physical name set matches the independent row-to-column route. The archived binary Pauli representation and the independent four-by-four assignment are different representations of the same physical roster.",
            "ordinary_parity_and_nae_fourth_birth":{"parity":even_last,"nae":nae_last},
            "old_even_words":physical["old_even"]["words"],"original_forbidden_odd_words":physical["supplied_odd"]["words"],
            "operator_question_is_supplied":True}


def _add(a,b):
    return a[0]+b[0],a[1]+b[1]


def _mul(a,b):
    return a[0]*b[0]+2*a[1]*b[1],a[0]*b[1]+a[1]*b[0]


def _scaled(a,n):
    return a[0]*n,a[1]*n


def _rationalized(a):
    return [str(x) for x in a]


def _addresses_guard(bank, code):
    return _prior()._selector_guards(bank,code)


def _h_options(words, bank, encoding, *, offered=True):
    reader = _prior()
    current = words[bank]
    if not offered:
        return [(words,ONE,{"offer":"real H disconnected", "target":bank,"initial":current,"final":current,"offered":False})]
    support = reader._basis_offer(current,"real_ab",inverse=False,reverse=encoding[bank])
    options = []
    for out in support["all_four_basis_rows"]:
        n,den = out["amplitude"]
        if n:
            next_words = dict(words)
            next_words[bank] = out["ordinary_word"]
            assert den in (1,2)
            options.append((next_words,_scaled(ONE if den==1 else H,n),
                            {"offer":"calibrated real H", "target":bank,"initial":current,"final":next_words[bank],"offered":True,
                             "ordinary_support_witnesses":out["ordinary_support_witness"],"compared_addresses":out["address"]}))
    return options


def _x_option(words, data, meter, encodings, *, controlled=True, offered=True, tag=False):
    old = _prior()
    sim = old.Trace(words,permitted_shared_guards=False,encodings=encodings)
    guard = ((data,old.Q,1),)
    if controlled:
        guard += _addresses_guard(meter,"b")
    if tag:
        sim.exchange("store the actual control-dependent firing",meter,old.L,guard,offered=offered)
    sim.exchange("guarded real X support",data,old.S,guard,offered=offered)
    return sim.words,ONE,sim.output()


def _exact_gate(words, encodings, steps, *, drive=True, tag="clean", hx_only=False):
    """Resolve actual basis supports and add amplitudes before any measurement."""
    prior = _prior()
    data,meter = "A_data","A_meter"
    state = [(dict(words),ONE,[])]
    if tag in ("control_kept","control_hidden","control_returned","fully_read"):
        sim = prior.Trace(words,permitted_shared_guards=False,encodings=encodings)
        if tag=="fully_read":
            for bank in (data,meter):
                for dest,control in zip(prior.PRE_READ_COPY,(prior.Q,prior.S),strict=True):
                    sim.exchange("record complete ordinary input",bank,dest,((bank,control,1),))
        else:
            sim.exchange("copy actual meter arm",meter,prior.L,_addresses_guard(meter,"b"))
        state = [(sim.words,ONE,[sim.output()])]
    for slot, gate in enumerate(steps):
        next_state = []
        for w, amp, log in state:
            if gate=="H":
                options = _h_options(w,data,encodings,offered=drive or hx_only)
            else:
                options = [_x_option(w,data,meter,encodings,offered=drive,tag=tag=="firing_kept" and slot==steps.index("X"))]
            for new,factor,leg in options:
                next_state.append((new,_mul(amp,factor),[*log,leg]))
        state = next_state
    if tag=="control_returned":
        returned = []
        for w,amp,log in state:
            sim = prior.Trace(w,permitted_shared_guards=False,encodings=encodings)
            sim.exchange("clean return using unchanged meter",meter,prior.L,_addresses_guard(meter,"b"))
            returned.append((sim.words,amp,[*log,sim.output()]))
        state = returned
    sums = defaultdict(lambda:ZERO)
    for w,amp,_ in state:
        key = w[data],w[meter]
        sums[key] = _add(sums[key],amp)
    sums = {w:a for w,a in sums.items() if a!=ZERO}
    assert sum((_mul(a,a)[0] for a in sums.values()),F(0))==1 and sum((_mul(a,a)[1] for a in sums.values()),F(0))==0
    return sums,[{"terminal_words":w,"amplitude_in_1_sqrt2":_rationalized(amp),"steps":log} for w,amp,log in state]


GATES = {"H":("H",), "CX":("X",), "CZ":("H","X","H"),
         "CJ":("H","X","H","X"), "C_minus_J":("X","H","X","H")}


def _guarded_gate_calibrations():
    prior = _prior()
    trace_table, support, adjoints, record_controls = {}, {}, {}, {}
    reverses = {"H":"H","CX":"CX","CZ":"CZ","CJ":"C_minus_J","C_minus_J":"CJ"}
    for data_rev,meter_rev in product((False,True),repeat=2):
        enc = {"A_data":data_rev,"A_meter":meter_rev}
        key = f"{int(data_rev)}{int(meter_rev)}"
        tables = {}
        for gate,word,control in product(GATES,WORDS,WORDS):
            form = f"{key}/{gate}/{word}{control}"
            words = {"A_data":prior._basis(word,data_rev),"A_meter":prior._basis(control,meter_rev)}
            maps,branches = _exact_gate(words,enc,GATES[gate])
            active = word in "ab" and control=="b"
            if gate=="H":
                expected = {a["ordinary_word"]:_scaled(ONE if a["amplitude"][1]==1 else H,a["amplitude"][0]) for a in
                            prior._basis_offer(words["A_data"],"real_ab",inverse=True,reverse=data_rev)["all_four_basis_rows"] if a["amplitude"][0]}
            else:
                changed = active and gate in ("CX","CJ","C_minus_J")
                sign = -1 if active and ((gate in ("CZ","CJ") and word=="b") or (gate=="C_minus_J" and word=="a")) else 1
                ending = ("b" if word=="a" else "a") if changed else word
                expected = {prior._basis(ending,data_rev):_scaled(ONE,sign)}
                support[form] = {"data_out":ending,"phase":sign,"applied_on_binary_code":active,
                                 "complete_words_after":(next(iter(expected)),words["A_meter"])}
            assert maps=={(w,words["A_meter"]):a for w,a in expected.items()}
            tables[(gate,word,control)] = {prior._address(w,data_rev):a for w,a in expected.items()}
            trace_table[form] = {"inputs":words,"encodings":enc,"chronological_schedule":GATES[gate],
                                 "complete_coherent_basis_terms":[[list(w),_rationalized(a)] for w,a in sorted(maps.items())],
                                 "actual_word_support_branches_before_addition":branches,
                                 "ordinary_word_support_does_not_supply_relative_phases":True}
        verified = []
        for gate,word,control in product(GATES,WORDS,WORDS):
            accum = defaultdict(lambda:ZERO)
            for intermediate,p in tables[gate,word,control].items():
                for output,q in tables[reverses[gate],intermediate,control].items():
                    accum[output] = _add(accum[output],_mul(q,p))
            assert {x:a for x,a in accum.items() if a!=ZERO}=={word:ONE}
            verified.append((gate,word,control))
        adjoints[key] = verified
    for reverse,gate,word,ctrl,mode in product((False,True),("CJ","C_minus_J"),"abc","abc",
                                               ("audit","control_kept","control_hidden","control_returned","fully_read","firing_kept","disconnected","cx_links_disconnected")):
        initial = {"A_data":prior._basis(word,reverse),"A_meter":prior._basis(ctrl,reverse)}
        encs = {bank:reverse for bank in initial}
        maps,legs = _exact_gate(initial,encs,GATES[gate],drive=mode not in ("disconnected","cx_links_disconnected"),
                                hx_only=mode=="cx_links_disconnected",tag=mode)
        if mode in ("disconnected","cx_links_disconnected"):
            assert maps=={tuple(initial.values()):ONE}
        if mode in ("audit","control_returned"):
            expected = support[f"{int(reverse)}{int(reverse)}/{gate}/{word}{ctrl}"]
            assert maps=={tuple(expected["complete_words_after"]):_scaled(ONE,expected["phase"])}
        k = f"{int(reverse)}/{gate}/{word}{ctrl}/{mode}"
        record_controls[k] = {"initial":initial,"gate":gate,"ordinary_mode":mode,
                              "complete_coherent_basis_terms":[[list(w),_rationalized(a)] for w,a in sorted(maps.items())],
                              "trace":legs,"physically_retained_control_or_component_mark":mode in ("control_kept","control_hidden","fully_read","firing_kept"),
                              "mark_is_part_of_clean_reader_output":False}
    return {"signed_gate_expansion":GATES,"all_complete_gate_columns":trace_table,"monomial_output_columns":support,
            "true_adjoint_gate_names":reverses,"true_adjoint_column_checks":adjoints,
            "records_and_independent_disconnections":record_controls,
            "inactive_rule":"Basis a,b uses XZ or ZX with control b. Each c,d input coordinate is an identity component of the supplied full gate. The registered pre-read membership filter refuses c,d separately.",
            "signed_convention":"Chronological H-CX-H-CX gives XZ; CX-H-CX-H gives ZX, the opposite active sign. Signed amplitudes require the supplied calibration."}


def _power(trace,target,selector,sign,*,guards=(),offered=True):
    for address in ("b","c","c"):
        trace.cycle(target,sign,(*_addresses_guard(selector,address),*guards),offered=offered)


def _encoding_calibration():
    prior = _prior()
    ints, roots = prior.ANALYZERS["three_way"]
    assert _multiply(tuple(zip(*ints,strict=True)),ints)==tuple(tuple(roots[i] if i==j else 0 for j in range(4)) for i in range(4))
    c = tuple(tuple(int(prior._cycle_address(WORDS[j],1)==WORDS[i]) for j in range(4)) for i in range(4))
    assert _multiply(tuple(zip(*c,strict=True)),c)==_identity(4)
    skew = tuple(tuple(a-b for a,b in zip(row,col,strict=True)) for row,col in zip(c,zip(*c,strict=True),strict=True))
    # U C encodes ordered a,b by the r and s columns of U.
    numerators = tuple(tuple(row[k] for k in (1,2)) for row in ints)
    wdw = _multiply(tuple(zip(*numerators,strict=True)),_multiply(skew,numerators))
    assert (wdw[0][0],wdw[1][1])==(0,0)
    denom = isqrt(roots[1]*roots[2]*3)
    assert denom**2==roots[1]*roots[2]*3
    active = ((0,F(wdw[0][1],denom)),(F(wdw[1][0],denom),0))
    assert active==((0,-1),(1,0))
    reports = {}
    for reverse,address in product((False,True),WORDS):
        trace = prior.Trace({"A_data":prior._basis(address,reverse)},reverse,permitted_shared_guards=False)
        trace.cycle("A_data",1)
        output = prior._basis_offer(trace.words["A_data"],"three_way",inverse=False,reverse=reverse)
        inverse = prior._basis_offer(prior._basis(address,reverse),"three_way",inverse=True,reverse=reverse)
        terms = []
        for leg in inverse["all_four_basis_rows"]:
            if leg["ordinary_word"] is not None:
                back = prior.Trace({"A_data":leg["ordinary_word"],"A_fresh_meter":prior._basis("c",reverse)},reverse,permitted_shared_guards=False)
                back.cycle("A_data",-1)
                before_move = back.address("A_data")
                back.move_pointer("A_data","A_fresh_meter")
                assert back.address("A_data")=="c" and back.address("A_fresh_meter")==before_move
                terms.append({"amplitude":leg["amplitude"],"decoded_meter_address":before_move,**back.output()})
        reports[f"{int(reverse)}/{address}"] = {"ordinary_C_before_U":trace.output(),"U_column_after_C":output,
                                                "U_transpose_before_inverse_C":inverse,"inverse_C_and_fresh_binary_meter_transfer":terms}
    return {"W_axes":["r","s"],"physical_order":"first C then U. The true adjoint first applies U transpose then C inverse.",
            "all_four_W_and_adjoint_word_columns":reports,"transpose_times_forward_is_identity_on_all_four":True,
            "W_transpose_C_minus_C_transpose_W_over_root_three":[[str(a) for a in row] for row in active],
            "physically_reversing_C_at_fixed_W_negates_J":True}


def _admission_columns():
    prior = _prior()
    rows = {}
    for dr,mr,data,meter in product((False,True),(False,True),WORDS,WORDS):
        words = {"A_data":prior._basis(data,dr),"A_meter":prior._basis(meter,mr),"A_membership":prior._basis("c",dr)}
        trial = prior.Trace(words,encodings={"A_data":dr,"A_meter":mr,"A_membership":dr},permitted_shared_guards=False)
        trial.exchange("copy joint local binary-code membership to one flag","A_membership",prior.T,
                       (("A_data",prior.Q,1),("A_meter",prior.Q,1)))
        valid = data in "ab" and meter in "ab"
        assert trial.value("A_membership",prior.T)==valid
        assert all(trial.words[k]==words[k] for k in ("A_data","A_meter"))
        assert trial.words["A_membership"]==prior._basis("c",dr,t=int(valid))
        rows[f"{int(dr)}{int(mr)}/{data}{meter}"] = {"admitted":valid,**trial.output()}
    return rows


def _local_route_record_columns():
    prior = _prior()
    rows = []
    for reverse,path,mode in product((False,True),WORDS,("audit","kept","hidden","returned","disconnected")):
        data,ref,route = "A_data","A_reference","A_path"
        ready = {data:prior._basis("a",reverse),ref:prior._basis("b",reverse),route:prior._basis(path,reverse)}
        trace = prior.Trace(ready,reverse,permitted_shared_guards=False)
        for dest,guard in zip(prior.PRE_READ_COPY,(prior.Q,prior.S),strict=True):
            trace.exchange("copy the local comparison path",route,dest,((route,guard,1),),offered=mode in ("kept","hidden","returned"))
        prior._group(trace,data,ref,route,(1,1))
        for dest,guard in reversed(tuple(zip(prior.PRE_READ_COPY,(prior.Q,prior.S),strict=True))):
            trace.exchange("return the local comparison path record",route,dest,((route,guard,1),),offered=mode=="returned")
        held = tuple(trace.value(route,j) for j in prior.PRE_READ_COPY)
        assert held==(prior.BITS[path] if mode in ("kept","hidden") else (0,0))
        recombine = prior._basis_offer(trace.words[route],"three_way",inverse=True,reverse=reverse)
        for branch in recombine["all_four_basis_rows"]:
            if branch["ordinary_word"] is not None:
                assert tuple(prior._logical(branch["ordinary_word"],j,reverse) for j in prior.PRE_READ_COPY)==held
        rows.append({"input_path":path,"record_mode":mode,"retained_path_record_bits":held,
                     "addresses_at_the_local_recombiner":recombine,**trace.output()})
    return rows


def _ports_and_local_comparison():
    prior = _prior()
    ordinary,comparison,faults,binary_decode = {},[],[],[]
    for reverse in (False,True):
        entries = {}
        for analyzer, port, stages, read_kind in product(("binary_meter","reference_group"),WORDS,prior.STAGES,("full","predicate_only")):
            marked = "b" if analyzer=="binary_meter" else "a"
            result = prior._port(prior._basis(port,reverse),marked,stages,reverse,complete=read_kind=="full")
            assert result["physical_completed_receipt"]==0
            key = f"{analyzer}/{port}/{int(stages[0])}{int(stages[1])}/{read_kind}"
            entries[key] = result
        for read in ("full","predicate_only"):
            words = [entries[f"reference_group/{j}/11/{read}"] for j in "bc"]
            assert (prior._workspace_check(words[0],reverse) == prior._workspace_check(words[1],reverse)) == (read=="predicate_only")
        ordinary[str(int(reverse))] = entries
        for input_word in WORDS:
            analyzer = prior._basis_offer(prior._basis(input_word,reverse),"real_ab",inverse=True,reverse=reverse)
            for branch in analyzer["all_four_basis_rows"]:
                port = branch["address"]
                if branch["ordinary_word"] is not None:
                    initial = entries[f"binary_meter/{port}/11/full"]["initial"]["A_record"]
                    assert branch["ordinary_word"]==initial
            binary_decode.append({"encoding_reversed":reverse,"meter_input":input_word,"analyzer":analyzer,
                                  "ordinary_writer_lookup_template":"binary_meter/{port}/{writer_connections}/full"})
        for target,reference,path,reverse_C,connected in product(WORDS,WORDS,WORDS,(-1,1),(False,True)):
            d,r,p = "A_data","A_reference","A_path"
            sim = prior.Trace({d:prior._basis(target,reverse),r:prior._basis(reference,reverse),p:prior._basis(path,reverse)},
                             reverse,permitted_shared_guards=False)
            prior._group(sim,d,r,p,(1,reverse_C),connected=connected)
            t = TRITS.index(path) if path in TRITS and connected else 0
            assert sim.address(d)==prior._cycle_address(target,t) and sim.address(r)==prior._cycle_address(reference,reverse_C*t)
            continuation = prior._basis_offer(sim.words[p],"three_way",inverse=True,reverse=reverse)
            comparison.append({"physical_inputs":(target,reference,path),"physically_reversed_reference":reverse_C,
                               "connected":connected,"path_returns_to_its_orthonormal_analyzer":continuation,**sim.output()})
        routes = prior._routes()
        ready = prior._basis("a",reverse)
        damaged = ready ^ (1<<routes._guard(prior.Q,reverse)[0])
        nonready = prior._basis("a",reverse,keeper="101",z=0)
        tests = {"no_address":(ready,"idle_reader"),"missing_target":(None,"target_missing"),
                 "missing_meter":(None,"meter_missing"),"dirty_target_record":(prior._basis("a",reverse,t=1),"target_has_unenrolled_record"),
                 "dirty_meter_record":(prior._basis("a",reverse,l=1),"meter_has_unenrolled_record"),
                 "damaged_target_code":(damaged,"damaged_register"),"damaged_meter_code":(damaged,"damaged_register"),
                 "not_ready_keeper":(nonready,"nonready_keeper"),"damaged_keeper":(prior._basis("a",reverse,keeper="111"),"damaged_keeper")}
        for who,code in product(("data","meter"),"cd"):
            tests[f"{who}_not_in_admitted_binary_code_{code}"] = (prior._basis(code,reverse),"out_of_code")
        for name,(value,status) in tests.items():
            observed = prior._failures(value,reverse) if value is not None else None
            if status in ("nonready_keeper","damaged_register","damaged_keeper"):
                assert routes._prep_status(value,reverse=reverse)==status
            faults.append({"attempt":name,"coordinate_reversed":reverse,"actual_law_failures":observed,
                           "initial_requested_bank":value,"terminal_requested_bank":value,"unchanged_independent_target_other_bank":ready,
                           "outcome":status,"ordinary_no_write":True,"local_record_generated":False})
    return {"local_port_word_dictionary":ordinary,"local_group_control_columns":comparison,"complete_no_read_cases":faults,
            "actual_admission_flag_columns":_admission_columns(),
            "local_which_route_physical_columns":_local_route_record_columns(),
            "binary_meter_analyzer_and_true_transpose":binary_decode,
            "coarse_which_record":"A simple predicate leaves the same non-pointer state in the two unmarked group sectors; resolved b and c have different physically held addresses.",
            "membership_filter":"Copy the conjunction of the local data and meter q marks to a fresh held flag. The four a,b pairs give exactly the same complete success record with their data and meter words unchanged. A full basis read is separate."}


def _classical_join(local):
    prior = _prior()
    outcomes, traces = [], {}
    a,b = "A_meter","B_meter"
    for scheme,codes in (("binary_meter",("a","b",None)),("reference_group",(*WORDS,None))):
        for reverse,left,right,send_a,send_b,stages_a,stages_b,only_keeper in product(
                (False,True),codes,codes,(False,True),(False,True),prior.STAGES,prior.STAGES,(False,True)):
            ports = local["local_port_word_dictionary"][str(int(reverse))]
            key = tuple(f"{scheme}/{code}/{int(stages[0])}{int(stages[1])}/full" if code is not None else None
                        for code,stages in ((left,stages_a),(right,stages_b)))
            measured = tuple(ports[k] if k is not None else None for k in key)
            delivered = tuple(bool(send and record and (not only_keeper or record["keeper_matches_flag"]))
                              for send,record in zip((send_a,send_b),measured,strict=True))
            source = tuple(record["final"]["A_record"] if record else prior._basis("c",reverse) for record in measured)
            both = all(delivered)
            expected = measured[0]["measured_flag"] ^ measured[1]["measured_flag"] if both else 0
            k = "011" if both and expected else "101" if both else "110"
            history = f"{int(reverse)}/{source[0]}/{source[1]}/{int(delivered[0])}{int(delivered[1])}"
            if history not in traces:
                banks = {a:source[0],b:source[1],"A_data":prior._basis("a",reverse),"B_data":prior._basis("b",reverse),
                         "message_A":prior._basis("c",reverse),"message_B":prior._basis("c",reverse),"collector":prior._basis("c",reverse)}
                sim = prior.Trace(banks,reverse)
                for bank,msg,present in zip((a,b),("message_A","message_B"),delivered,strict=True):
                    sim.exchange("disclose already measured classical T",msg,prior.T,((bank,prior.T,1),),offered=present)
                    sim.exchange("set physical message present register",msg,prior.L,offered=present)
                for msg in ("message_A","message_B"):
                    guard = (("message_A",prior.L,1),("message_B",prior.L,1),(msg,prior.T,1))
                    sim.exchange("classical XOR of present recorded bits","collector",prior.Q,guard)
                assert all(sim.words[bank]==banks[bank] for bank in (a,b,"A_data","B_data"))
                assert sim.value("collector",prior.Q)==expected
                sim.writes("collector",(both,both))
                assert prior._routes().decode(sim.words["collector"],reverse=reverse)["keeper"]==k
                traces[history] = sim.output()
            outcomes.append({"analyzer":scheme,"encoding_reversed":reverse,"actual_local_port_addresses":(left,right),
                             "local_word_dictionary_keys":key,"available_channels":(send_a,send_b),
                             "local_writer_connections":(stages_a,stages_b),"communication_reads_only_valid_keeper_records":only_keeper,
                             "physical_messages_delivered":delivered,"physical_word_history":history,
                             "local_keepers":tuple(record["keeper"] if record else "110" for record in measured),
                             "third_keeper":k,"combined_sign":(1-2*expected) if both else None})
    return {"all_classical_presence_and_keeper_columns":outcomes,
            "distinct_complete_physical_word_histories":traces,
            "labels":"When both records are present, XOR zero writes 101 (+), XOR one writes 011 (−). Missing either record leaves the third keeper 110.",
            "access":"An actually written T can be transmitted despite a writer fault. A stricter keeper-only control requires its own completed and correct K word.",
            "returned_data_is_never_a_target_or_a_control_of_classical_comparison":True}


def _repeat(local):
    prior = _prior()
    rows = []
    for reverse in (False,True):
        ports = local["local_port_word_dictionary"][str(int(reverse))]
        for kind,first,second,stages,resource in product(("binary_meter","reference_group"),(None,*WORDS),(None,*WORDS),prior.STAGES,("fresh","consumed","none")):
            first_record = ports[f"{kind}/{first}/{int(stages[0])}{int(stages[1])}/full"] if first is not None else None
            old_word = first_record["final"]["A_record"] if first_record else prior._basis("c",reverse)
            if resource == "fresh" and second is not None:
                transfer = prior._pointer_transfer(prior._basis(second,reverse),"bench_new","A_fresh",reverse)
                meter = transfer["final"]["A_fresh"]
                second_record = ports[f"{kind}/{second}/11/full"]
                assert meter==second_record["initial"]["A_record"]
                final_new = second_record["final"]["A_record"]
                state = "second_meter_analyzed"
                slots = transfer["slot_count"]
            else:
                final_new = prior._basis("c",reverse)
                if second is None:
                    state = "second_request_not_addressed"
                elif resource=="consumed":
                    state = "consumed_even_when_writer_disconnected" if first is not None else "no_reference_after_first_no_write"
                else:
                    state = "no_new_reference"
                slots = 6
            if first_record:
                assert prior._logical(old_word,prior.MEASURED_RECEIPT,reverse)==0
            rows.append({"analyzer":kind,"orientation":reverse,"first_address_or_no_write":first,"requested_second_address":second,
                         "old_meter_and_keeper_retained":old_word,"first_keeper":first_record["keeper"] if first_record else "110",
                         "second_resource":resource,"second_status":state,"meter_transfer_slots":slots,
                         "fresh_bank_final":final_new,"fresh_second_keeper":prior._routes().decode(final_new,reverse=reverse)["keeper"],
                         "reference_consumed_even_when_first_keeper_left_ready":first_record is not None and first_record["keeper"]=="110"})
    return {"all_first_and_second_ports_x_available_resources":rows,
            "data_stays_in_its_own_local_bank":"Only local meter coordinates move in these apparatus checks. Each coherent repeated read uses whatever data the first instrument returned.",
            "fresh_transfers":"All source basis transfers are the inherited six-slot complete word permutation, excluding old T, address work and K."}


def _source_correction(before,code,reverse,mode,*,deposited=False):
    prior = _prior()
    data = "B_meter" if deposited else "bench_meter"
    branch = "B_disclosed_branch" if deposited else "bench_branch"
    words = {data:before,branch:prior._basis(code,reverse)}
    encodings = {bank:reverse for bank in words}
    sums = defaultdict(lambda:ZERO)
    histories = []
    offered = mode!="no_correction"
    triggered_code = "a" if mode=="false_setting" else "b"
    for old,amp,leg in _h_options(words,data,encodings):
        trace = prior.Trace(old,reverse,permitted_shared_guards=False)
        trace.exchange("phase correction uses physical branch-selected P",data,prior.S,
                       ((data,prior.Q,1),*_addresses_guard(branch,triggered_code)),offered=offered)
        for end,weight,last in _h_options(trace.words,data,encodings):
            assert end[branch]==words[branch]
            amplitude = _mul(amp,weight)
            sums[end[data]] = _add(sums[end[data]],amplitude)
            histories.append({"output":end[data],"amplitude":_rationalized(amplitude),"slots":[leg,trace.output(),last]})
    signed = {w:a for w,a in sums.items() if a!=ZERO}
    sign = -1 if offered and code==triggered_code and prior._address(before,reverse)=="b" else 1
    assert signed=={before:_scaled(ONE,sign)}
    return {"input":words,"physical_signed_amplitude_after_full_Z":sign,"terminal_word":before,
            "actual_branches_before_addition":histories,"branch_explicitly_delivered":deposited}


def _bench_binary_source():
    prior = _prior()
    gates,source,tagged,coherent = {}, {},[],{}
    for reverse,word,port,mode,deposited in product((False,True),WORDS,WORDS,("correct","false_setting","no_correction"),(False,True)):
        result = _source_correction(prior._basis(word,reverse),port,reverse,mode,deposited=deposited)
        gates[f"{int(reverse)}/{word}/{port}/{mode}/{int(deposited)}"] = result
    for reverse,path,mode,port in product((False,True),WORDS,("plus_only","both_corrected","uncorrected","false_setting"),WORDS):
        a,b,p = "bench_A","bench_B","bench_path"
        sim = prior.Trace({a:prior._basis("a",reverse),b:prior._basis("a",reverse),p:prior._basis(path,reverse)},reverse)
        prior._group(sim,a,b,p,(1,1),binary=True)
        assert sim.address(a)==sim.address(b)==("b" if path=="b" else "a")
        port_basis = prior._basis_offer(sim.words[p],"real_ab",inverse=True,reverse=reverse)
        selected = port_basis["all_four_basis_rows"][WORDS.index(port)]
        read = port in "ab" and path in "ab"
        accept = read and (mode!="plus_only" or port=="a")
        correction = {"both_corrected":"correct","false_setting":"false_setting"}.get(mode,"no_correction")
        support_key = f"{int(reverse)}/{sim.address(b)}/{port}/{correction}/0"
        source[f"{int(reverse)}/{path}/{mode}/{port}"] = {
            "source_from_complete_aa":sim.output(),"incoming_path_address":path,"selected_terminal_path_basis_row":selected,
            "bench_port":port,"protocol":mode,"source_delivers_meter":accept,
            "physical_phase_correction_column":support_key if read else None,
            "benchmark_binary_source_only_uses_a_b_path_support":read}
    for reverse,mode in product((False,True),("plus_only","both_corrected","uncorrected","false_setting")):
        start_path = prior._basis("a",reverse)
        splitter = prior._basis_offer(start_path,"real_ab",inverse=False,reverse=reverse)
        port_columns = {}
        for port in WORDS:
            terms = []
            for leg in splitter["all_four_basis_rows"]:
                address = leg["address"]
                key = f"{int(reverse)}/{address}/{mode}/{port}"
                row = source[key]
                numerator,denominator = row["selected_terminal_path_basis_row"]["amplitude"]
                if not leg["amplitude"][0] or not numerator:
                    continue
                correction = gates[row["physical_phase_correction_column"]]
                assert leg["amplitude"]==[1,2] and denominator==2
                assert row["source_from_complete_aa"]["initial"]["bench_path"]==leg["ordinary_word"]
                final = row["source_from_complete_aa"]["final"]
                assert final["bench_B"]==correction["terminal_word"]
                amplitude = F(numerator*correction["physical_signed_amplitude_after_full_Z"],2)
                terms.append({"ordinary_prep_and_raw_recombiner_key":key,
                              "complete_meter_words":(final["bench_A"],final["bench_B"]),
                              "subnormalized_signed_amplitude":str(amplitude)})
            expected_sign = -1 if mode=="false_setting" or (port=="b" and mode!="both_corrected") else 1
            assert [F(row["subnormalized_signed_amplitude"]) for row in terms]==(
                [F(1,2),F(expected_sign,2)] if port in "ab" else [])
            port_columns[port] = {"signed_terms":terms,"observed_bench_receipt":prior._bench_port_word(port if terms else None,reverse),
                                  "physically_selected_delivery":bool(terms) and (mode!="plus_only" or port=="a")}
        coherent[f"{int(reverse)}/{mode}"] = {"initial_real_path_splitter":splitter,"all_final_ports":port_columns}
    for reverse,path,mode in product((False,True),WORDS,("kept","hidden","uncomputed","never_coupled","uncoupled_audit","disconnected")):
        a,b,p = "bench_A","bench_B","bench_path"
        words = {a:prior._basis("a",reverse),b:prior._basis("a",reverse),p:prior._basis(path,reverse)}
        sim = prior.Trace(words,reverse)
        if mode != "never_coupled" and mode!="uncoupled_audit":
            sim.exchange("physical capture of the b path",p,prior.L,_addresses_guard(p,"b"),offered=mode!="disconnected")
        prior._group(sim,a,b,p,(1,1),binary=True)
        if mode=="uncomputed":
            sim.exchange("physical return of the old b path mark",p,prior.L,_addresses_guard(p,"b"))
        assert sim.value(p,prior.L)==(mode in ("kept","hidden") and path=="b")
        recombine = prior._basis_offer(sim.words[p],"real_ab",inverse=True,reverse=reverse)
        for leg in recombine["all_four_basis_rows"]:
            if leg["ordinary_word"] is not None:
                assert prior._logical(leg["ordinary_word"],prior.L,reverse)==sim.value(p,prior.L)
        tagged.append({"actual_mode":mode,"ordinary_source_path":path,"marked_path_exists_on_final_word":bool(sim.value(p,prior.L)),
                       "recombination_of_actual_path_word":recombine,**sim.output()})
    return {"binary_z_gate_on_each_basis_and_herald":gates,"preparation_and_port_branch_supports":source,
            "complete_binary_source_through_both_physical_heralds":coherent,
            "physical_which_arm_captures":tagged,
            "ancestors":"The two old P,Q complete gated exchanges and the B291 real binary splitter are used. A post-deposition Z acts only if that control is expressly given the actual bench branch."}


def _local_share_execution(target,ref,u,v,reverse,frame_a,frame_b,policy):
    old = _prior()
    a,b,j_bank = "bench_A","bench_B","bench_j"
    j = (u+v)%3
    source = {a:old._basis(target,reverse),b:old._basis(ref,reverse),j_bank:old._basis(TRITS[j],reverse)}
    bench = old.Trace(source,reverse)
    _power(bench,a,j_bank,frame_a)
    bench.exchange("same fixed source B transposition",b,old.S,((b,old.Q,1),))
    # Independently prepare u, preserve j, and place v=j-u on a fresh ordinary register.
    prep = old.Trace({"bench_j":old._basis(TRITS[j],reverse),"bench_u":old._basis(TRITS[u],reverse),"bench_v":old._basis("c",reverse)},reverse)
    for reg in (old.Q,old.S):
        prep.exchange("copy the initially named j to the v register", "bench_v",reg,(("bench_j",reg,1),))
    _power(prep,"bench_v","bench_u",-1)
    assert prep.address("bench_v")==TRITS[v]
    words = {"bench_A":bench.words[a],"bench_B":bench.words[b],"bench_u":prep.words["bench_u"],"bench_v":prep.words["bench_v"],
             "A_pointer":old._basis("c",reverse),"B_pointer":old._basis("c",reverse),
             "A_share":old._basis("c",reverse),"B_share":old._basis("c",reverse)}
    transport = old.Trace(words,reverse)
    send_u,send_v = policy not in ("none","only_v"),policy not in ("none","only_u")
    for donor,out,active in ((a,"A_pointer",True),(b,"B_pointer",True),
                              ("bench_u","A_share",send_u),("bench_v","B_share",send_v)):
        transport.move_pointer(donor,out,offered=active)
    for share,active in (("A_share",send_u),("B_share",send_v)):
        transport.exchange("declare actual local receipt of a classical share",share,old.T,offered=active)
        assert transport.value(share,old.T)==active
    kept = {name:w for name,w in transport.words.items() if not name.startswith("bench_")}
    operation = old.Trace(kept,reverse,permitted_shared_guards=False)
    if policy=="both_local":
        operation.exchange("undo actual B a,b transposition","B_pointer",old.S,(("B_pointer",old.Q,1),("B_share",old.T,1)))
        _power(operation,"A_pointer","A_share",-frame_a,guards=(("A_share",old.T,1),))
        _power(operation,"B_pointer","B_share",frame_b,guards=(("B_share",old.T,1),))
        assert operation.address("A_pointer")==old._cycle_address(target,frame_a*v)
        assert operation.address("B_pointer")==old._cycle_address(ref,frame_b*v)
    else:
        operation.exchange("optional B correction bypass","B_pointer",old.S,(("B_pointer",old.Q,1),),offered=False)
        _power(operation,"A_pointer","A_share",-frame_a,offered=False)
        _power(operation,"B_pointer","B_share",frame_b,offered=False)
        assert operation.words==kept
    return {"j_u_v":(j,u,v),"physical_untwirled_reference_addresses":(target,ref),"cycle_directions_after_recalibration":(frame_a,frame_b),
            "registered_share_policy":policy,"physical_source_twirl_and_transposition":bench.output(),"preparing_classical_v":prep.output(),
            "pointer_and_classical_share_delivery":transport.output(),"local_share_only_work":operation.output(),
            "share_present_at_A_B":(send_u,send_v),
            "local_pointer_names_after_work":(operation.address("A_pointer"),operation.address("B_pointer"))}


def _gathered_share_undo(reverse):
    old = _prior()
    result = []
    for u,v,send_a,send_b in product(range(3),range(3),(False,True),(False,True)):
        gather = old.Trace({"measured_A_share":old._basis(TRITS[u],reverse),"measured_B_share":old._basis(TRITS[v],reverse),
                           "collector_u":old._basis("c",reverse),"collector_j":old._basis("c",reverse),
                           "A_disclosed_j":old._basis("c",reverse),"B_disclosed_ready":old._basis("c",reverse)},reverse)
        for sender,dest,sent in (("measured_A_share","collector_u",send_a),("measured_B_share","collector_j",send_b)):
            for reg in (old.Q,old.S):
                gather.exchange("copy measured trit bits only",dest,reg,((sender,reg,1),),offered=sent)
            gather.exchange("physically mark message arrival",dest,old.L,offered=sent)
        base_words = dict(gather.words)
        present = (("collector_u",old.L,1),("collector_j",old.L,1))
        _power(gather,"collector_j","collector_u",1,guards=present)
        inferred = (u+v)%3 if send_a and send_b else None
        assert inferred is None or gather.address("collector_j")==TRITS[inferred]
        if inferred is None:
            assert gather.words["collector_j"]==base_words["collector_j"]
        for reg in (old.Q,old.S):
            gather.exchange("communicate the reconstructed j only in the two-message case",
                            "A_disclosed_j",reg,(*present,("collector_j",reg,1)))
        for receipt in ("A_disclosed_j","B_disclosed_ready"):
            gather.exchange("announce availability of the two-share correction",receipt,old.T,present)
            assert gather.value(receipt,old.T)==(inferred is not None)
        assert gather.words["A_disclosed_j"]==old._basis(TRITS[inferred] if inferred is not None else "c",reverse,t=int(inferred is not None))
        local_repairs = []
        example = None
        for a,b in product(WORDS,repeat=2):
            j = (u+v)%3
            a_bench = old._cycle_address(a,j)
            b_bench = {"a":"b","b":"a"}.get(b,b)
            ready = {"A_pointer":old._basis(a_bench,reverse),"A_disclosed_j":gather.words["A_disclosed_j"],
                     "B_pointer":old._basis(b_bench,reverse),"B_disclosed_ready":gather.words["B_disclosed_ready"]}
            local = old.Trace(ready,reverse,permitted_shared_guards=False)
            _power(local,"A_pointer","A_disclosed_j",-1,guards=(("A_disclosed_j",old.T,1),))
            local.exchange("undo actual B transposition only on successful joint disclosure","B_pointer",old.S,
                           (("B_pointer",old.Q,1),("B_disclosed_ready",old.T,1)))
            output = (local.address("A_pointer"),local.address("B_pointer"))
            assert output==((a,b) if inferred is not None else (a_bench,b_bench))
            local_repairs.append({"untwirled_addresses":(a,b),"initial":ready,"final":dict(local.words),"decoded_addresses":output,"recipe_slots":len(local.steps)})
            if (a,b)==("a","b"):
                example = local.output()
        row = {"share_labels":(u,v),"classical_channels":(send_a,send_b),"j_delivered_to_local_A":inferred,
               "physical_classical_gather":gather.output(),"all_bypass_or_repair_columns":local_repairs,
               "actual_local_repair_example":example}
        result.append(row)
    return result


def _single_trit_cut():
    old = _prior()
    modes = ("pre_twirl_cut","original_hidden_twirl","disclosed_correctly_used","disclosed_bypassed",
             "copy_returned_before_delivery","disclosed_and_traced","disclosed_kept_unread")
    summary_rows, traces = [], {}
    for reverse,j,mode,a,b in product((False,True),range(3),modes,WORDS,WORDS):
        twirl,disclose = mode!="pre_twirl_cut",mode.startswith("disclosed")
        copied,corrected = disclose or mode=="copy_returned_before_delivery",mode=="disclosed_correctly_used"
        words = {"bench_A":old._basis(a,reverse),"bench_B":old._basis(b,reverse),"bench_j":old._basis(TRITS[j],reverse),
                 "bench_copy":old._basis("c",reverse),**{k:old._basis("c",reverse) for k in ("A_pointer","B_pointer","A_trit","B_trit_receipt")}}
        bench = old.Trace(words,reverse)
        _power(bench,"bench_A","bench_j",1,offered=twirl)
        bench.exchange("fixed source B transposition","bench_B",old.S,(("bench_B",old.Q,1),),offered=twirl)
        for reg in (old.Q,old.S):
            bench.exchange("capture the actual source twirl coordinates","bench_copy",reg,(("bench_j",reg,1),),offered=copied)
        for reg in (old.S,old.Q):
            bench.exchange("return the captured coordinates while the original is still present","bench_copy",reg,
                           (("bench_j",reg,1),),offered=mode=="copy_returned_before_delivery")
        for before,after,active in (("bench_A","A_pointer",True),("bench_B","B_pointer",True),("bench_copy","A_trit",disclose)):
            bench.move_pointer(before,after,offered=active)
        for dest in ("A_trit","B_trit_receipt"):
            bench.exchange("announce receipt of the deliberate trit disclosure",dest,old.T,offered=disclose)
        delivered = {k:value for k,value in bench.words.items() if not k.startswith("bench_")}
        assert delivered["A_trit"]==old._basis(TRITS[j] if disclose else "c",reverse,t=int(disclose))
        assert bench.words["bench_copy"]==words["bench_copy"]
        local = old.Trace(delivered,reverse,permitted_shared_guards=False)
        _power(local,"A_pointer","A_trit",-1,guards=(("A_trit",old.T,1),),offered=corrected)
        local.exchange("return B transposition in the announced two-reader calibration","B_pointer",old.S,
                       (("B_pointer",old.Q,1),("B_trit_receipt",old.T,1)),offered=corrected)
        expected = (old._cycle_address(a,j),{"a":"b","b":"a"}.get(b,b)) if twirl and not corrected else (a,b)
        assert tuple(local.words[k] for k in ("A_pointer","B_pointer"))==tuple(old._basis(w,reverse) for w in expected)
        certificate = f"{int(reverse)}/{j}/{mode}"
        if (a,b)==("a","b"):
            traces[certificate] = {"before_and_through_delivery":bench.output(),"local_offers":local.output()}
        summary_rows.append({"physical_control_calibration":certificate,"input_addresses":(a,b),
                             "only_independent_receiver_words_after_each_lawful_local_offer":tuple(local.words.values()),
                             "actual_labels_at_A_and_B":(TRITS[j] if disclose else None,disclose),
                             "physical_label_kept_in_the_joint_word_even_when_traced_by_evaluator":disclose,
                             "ordinary_addresses_after_work":expected})
    by_key = {(r["physical_control_calibration"], r["input_addresses"]):r for r in summary_rows}
    for reverse,j,a,b in product((False,True),range(3),WORDS,WORDS):
        clean,returned = (by_key[(f"{int(reverse)}/{j}/{mode}",(a,b))]["only_independent_receiver_words_after_each_lawful_local_offer"]
                          for mode in ("original_hidden_twirl","copy_returned_before_delivery"))
        assert clean==returned
    return {"representative_complete_transition_histories":traces,"all_ordinary_complete_receiver_columns":summary_rows,
            "same_complete_receiver_words_for_returned_or_never_copied_hidden_trit":True}


def _shares():
    old = _prior()
    rows,harmless,delivered,common_harmless = [],[],{},[]
    for reverse,u,v in product((False,True),range(3),range(3)):
        chosen = _local_share_execution("a","b",u,v,reverse,1,1,"both_local")
        rows.append(chosen)
        for policy in ("both_bypass","only_u","only_v","none"):
            rows.append(_local_share_execution("a","b",u,v,reverse,1,1,policy))
        attached = {key:chosen["pointer_and_classical_share_delivery"]["final"][key] for key in ("A_share","B_share")}
        for independent_j in range(3):
            independent = old.Trace({"bench_A":old._basis("a",reverse),"bench_j":old._basis(TRITS[independent_j],reverse)},reverse)
            _power(independent,"bench_A","bench_j",1)
            harmless.append({"independent_j":independent_j,"uncorrelated_u_v":(u,v),"same_pair_of_classical_share_words":attached,**independent.output()})
    for reverse,j,label in product((False,True),range(3),range(3)):
        words = {"bench_A":old._basis("a",reverse),"bench_j":old._basis(TRITS[j],reverse),
                 "bench_label":old._basis(TRITS[label],reverse),"A_label":old._basis("c",reverse),"B_label":old._basis("c",reverse)}
        independent = old.Trace(words,reverse)
        _power(independent,"bench_A","bench_j",1)
        for dest in ("A_label","B_label"):
            for reg in (old.Q,old.S):
                independent.exchange("disclose the freely drawn shared trit",dest,reg,(("bench_label",reg,1),))
            assert independent.words[dest]==words["bench_label"]
        common_harmless.append({"shared_trit":label,"independent_source_twirl":j,**independent.output()})
    # Change each physical cycle independently. Record every basis output; retrieve complete moves
    # from the individually verified old P,Q and fixed-alphabet exponent recipes.
    orientation_controls = []
    for reverse,da,db,u,v,a,b in product((False,True),(-1,1),(-1,1),range(3),range(3),WORDS,WORDS):
        goal = (old._cycle_address(a,da*v),old._cycle_address(b,db*v))
        if a=="a" and b=="b":
            actual = _local_share_execution(a,b,u,v,reverse,da,db,"both_local")
            assert actual["local_pointer_names_after_work"]==goal
            delivered[f"{int(reverse)}/{da}/{db}/{u}{v}"] = actual
        else:
            pa = old.Trace({"A_pointer":old._basis(a,reverse),"A_share":old._basis(TRITS[u],reverse),
                            "A_source_selector":old._basis(TRITS[(u+v)%3],reverse)},reverse,permitted_shared_guards=False)
            pb = old.Trace({"B_pointer":old._basis(b,reverse),"B_share":old._basis(TRITS[v],reverse)},reverse,permitted_shared_guards=False)
            _power(pa,"A_pointer","A_source_selector",da)
            for op in ("prepare with","undo"):
                pb.exchange(f"{op} the actual B transposition","B_pointer",old.S,(("B_pointer",old.Q,1),))
            _power(pa,"A_pointer","A_share",-da)
            _power(pb,"B_pointer","B_share",db)
            assert (pa.words["A_pointer"],pb.words["B_pointer"])==tuple(old._basis(w,reverse) for w in goal)
        orientation_controls.append({"reverse_naming":reverse,"independent_cycle_directions":(da,db),"shares":(u,v),
                                     "untwirled_words":(a,b),"actual_corrected_words":goal,
                                     "complete_output_words":[old._basis(w,reverse) for w in goal]})
    return {"all_nine_share_pairs_and_missing_channel_controls":rows,"independently_drawn_harmless_labels":harmless,
            "one_common_independent_classical_label":common_harmless,
            "independently_reversed_cycle_calibration":orientation_controls,"representative_full_reversed_traces":delivered,
            "both_shares_classically_gathered_or_missing":{str(int(r)):_gathered_share_undo(r) for r in (False,True)},
            "single_trit_and_pre_twirl_cut":_single_trit_cut(),
            "classical_label_formula":"The actual v register stores j-u modulo three. Local C^(-u), C^(+v) after B's ordinary inverse yields the same v advance on both original pointers at the forward calibration."}


def _physical_cut_and_source_refusals():
    prior = _prior()
    rows = []
    receipts = (
        ("local_plus_plus", ("a","a",None),False), ("local_plus_minus", ("a","b",None),False),
        ("local_minus_plus", ("b","a",None),False), ("group_0",("b","b","a"),True),
        ("group_1",("b","b","b"),False), ("group_2",("b","b","c"),False), ("group_d_zero_control",("b","b","d"),False),
        ("binary_plus",("a",None,None),True), ("binary_minus_retained_and_corrected",("b",None,None),True),
        ("binary_plus_only_rejects_minus",("b",None,None),False), ("source_absent",(None,None,None),False),
    )
    for r,a,b,(source,flags,accepted) in product((False,True),WORDS,WORDS,receipts):
        w = {"bench_A":prior._basis(a,r),"bench_B":prior._basis(b,r),"A_meter":prior._basis("c",r),"B_meter":prior._basis("c",r),
             "A_data":prior._basis("a",r),"B_data":prior._basis("b",r),"A_public":prior._basis("c",r),"B_public":prior._basis("c",r)}
        w.update({f"bench_port_{i}":prior._bench_port_word(port,r)["final"]["bench_port"] for i,port in enumerate(flags)})
        sim = prior.Trace(w,r)
        for side in "AB":
            sim.move_pointer("bench_"+side,side+"_meter",offered=accepted)
            sim.exchange("write explicitly public admission flag",side+"_public",prior.T,offered=accepted)
            assert sim.words[side+"_data"]==w[side+"_data"]
            assert sim.value(side+"_public",prior.T)==accepted
            if not accepted:
                assert sim.words[side+"_meter"]==w[side+"_meter"]
                assert prior._routes().decode(sim.words[side+"_meter"],reverse=r)["keeper"]=="110"
        rows.append({"source_record":source,"actual_physically_held_bench_heralds":flags,"transfer_admitted":accepted,
                     "same_independent_target_and_the_held_meter_stays_idle_on_source_rejection":not accepted,
                     "delivered_only":{k:v for k,v in sim.words.items() if not k.startswith("bench_")},**sim.output()})
    matched = [row for row in rows if not row["transfer_admitted"]]
    for reverse in (False,True):
        assert len({tuple(row["delivered_only"].values()) for row in matched if row["coordinate_reversed"]["A_meter"]==reverse})==1
    return {"bench_source_failures_and_padded_deliveries":rows,"primary_cut_delivers_only_new_meters_and_public_admission":True,
            "old_target_banks_are_already_at_readers_before_source_delivery":True,
            "registered_source_probabilities_belong_to_the_independent_instrument_calculation":True}


def hardware_checks():
    """Exact, self-described physical gate columns, word histories and old sign links."""
    prior = _prior()
    local = _ports_and_local_comparison()
    sources = (Path(__file__).resolve(),HERE/"preregistration.md",HARDWARE,OLD/"sources_and_reads.py",OLD/"reference_controls.py",
               OLD/"real_algebra.py",ERASURE,prior.KEEPER_PATH,prior.CYCLE_PATH,OLD_CYCLE,CLOSURE,ASSIGNMENT)
    return {"target_assignment":_target(),"signed_gate_calibrations":_guarded_gate_calibrations(),"encoded_W":_encoding_calibration(),
            "local_interface":local,"classical_sign_keeper":_classical_join(local),"repeat":_repeat(local),
            "source_binary_correction":_bench_binary_source(),"source_reference_shares":_shares(),
            "controller_holdings":prior._ancestor_and_cut_checks(),"matched_physical_cut":_physical_cut_and_source_refusals(),
            "source_digests":{str(s.relative_to(ROOT)):sha256(s.read_bytes()).hexdigest() for s in sources},
            "scope_and_labels":{"ordinary_word_width":44,"physical_controller_laws":LAWS,"logical_address_bits":prior.BITS,
                                "binary_letters":"a is zero, b is one; c and d remain valid physical words outside the registered active code.",
                                "complete_word_grammar":"Each bank carries a full 44-bit physical word. Old gate traces list actual target names, unchanged guards, offer flags and per-slot word changes.",
                                "signed_amplitudes":"Pair of rational strings r,s represents r+s sqrt(2) in the direct binary gate tables. The inherited U and W list n,d for n/sqrt(d).",
                                "holding_boundary":"The complete controller includes the workspace's named code registers. Their old decoded computational preload is not a separate six-row law.",
                                "no_ordinary_growth_trigger_for_a_pulse":True}}


def _smoke():
    old = _prior()
    for rev,word,gate in product((False,True),"ab",("CJ","C_minus_J")):
        banks = {"A_data":old._basis(word,rev),"A_meter":old._basis("b",rev)}
        result,_ = _exact_gate(banks,{k:rev for k in banks},GATES[gate])
        label = "a" if word=="b" else "b"
        assert result=={(old._basis(label,rev),banks["A_meter"]):_scaled(ONE,-1 if (word=="b")==(gate=="CJ") else 1)}
        k = old._port(old._basis(label,rev),"b",(True,True),rev,complete=True)["keeper"]
        assert k==("101" if label=="a" else "011")
    assert _target()["owners"]==(16,17)
    assert _encoding_calibration()["physically_reversing_C_at_fixed_W_negates_J"]
    return {"binary_signed_columns":8,"physical_signed_products":18,"W_and_inverse_checked":True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke",action="store_true",help="run a small exact physical gate and linked-holder check")
    opt = parser.parse_args()
    if opt.smoke:
        print(json.dumps(_smoke(),sort_keys=True))
    else:
        data = json.dumps(hardware_checks(),sort_keys=True,separators=(",",":")).encode()
        print(f"hardware_checks {sha256(data).hexdigest()} over {len(data)} canonical JSON bytes")


if __name__ == "__main__":
    main()
