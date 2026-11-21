"""Ordinary word supports and physical records of the separate-pointer protocol."""

import argparse
from functools import cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ROUTES_PATH = ROOT / "research/ERASURE-AND-CLOSING-SIGNS-20261121-001A/ordinary_routes.py"
CYCLE_PATH = ROOT / "research/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001A/cyclic_pointer.py"
PHYSICAL_PATH = ROOT / "research/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001A/physical_composition.py"
KEEPER_PATH = ROOT / "research/ERASURE-AND-CLOSING-SIGNS-20261121-001A/keeper.py"
WIDTH = 44
READY_DATA = 245
ADDRESSES = ("a", "b", "c", "d")
BITS = dict(zip(ADDRESSES, ((1, 0), (1, 1), (0, 0), (0, 1)), strict=True))
ADDRESS = {v: k for k,v in BITS.items()}
Q, T, L, S = 9, 10, 11, 12
ADDRESS_RECORD = (3, 8)
PRE_READ_COPY = (L, 1)
MEASURED_RECEIPT = 4  # Preloaded at one. A completed analysis exchanges it to zero.
STAGES = tuple(product((False, True), repeat=2))
LAWS = ("parity", "nae")


@cache
def _load(name, path):
    spec = spec_from_file_location(name, path)
    mod = module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _routes():
    return _load("b291_ancestor_routes", ROUTES_PATH)


def _old_physical():
    return _load("b291_ancestor_physical", PHYSICAL_PATH)


def _mask(places):
    return sum(1 << j for j in places)


def _bit(word, place):
    return (word >> place) & 1


@cache
def _failures(word, reverse):
    return {law: tuple(_routes()._failed_physical(word, law, reverse)) for law in LAWS}


def _basis(label="c", reverse=False, **overrides):
    q,s = BITS[label]
    return _routes().encode(overrides.pop("data", READY_DATA), q=q, s=s, reverse=reverse, **overrides)


def _logical(word, register, reverse):
    return _bit(word,_routes()._guard(register,reverse)[0])


def _address(word, reverse):
    return ADDRESS[tuple(_logical(word,j,reverse) for j in (Q,S))]


def _cycle_address(address, power):
    return address if address == "d" else ADDRESSES[(ADDRESSES.index(address)+power) % 3]


class Trace:
    """Record at most one active target holder per offered exchange.

    A control in another controller is checked at its own holder and issued
    as a supplied synchronized offer. It is never installed in the target
    holder or counted as an ordinary growth event.
    """

    def __init__(self, words, reverse=False, *, permitted_shared_guards=True, encodings=None):
        self.words = dict(words)
        self.initial = dict(words)
        self.encodings = {b: reverse for b in words} if encodings is None else dict(encodings)
        if self.encodings.keys() != self.words.keys():
            raise ValueError("each physical bank needs an encoding")
        self.permitted_shared_guards = permitted_shared_guards
        self.steps = []

    def value(self, bank, register):
        return _logical(self.words[bank],register,self.encodings[bank])

    def address(self, bank):
        return _address(self.words[bank],self.encodings[bank])

    def exchange(self, name, target, register, guards=(), *, offered=True):
        routes = _routes()
        before = self.words[target]
        reverse = self.encodings[target]
        pair = routes._places(routes.REGISTERS[register][:2],reverse)
        local, active = [], []
        external_match = True
        for bank,reg,wanted in guards:
            mark = routes._guard(reg,self.encodings[bank])[0]
            observed = self.value(bank,reg)
            assert mark in routes._holding("H",self.encodings[bank])
            active.append([bank,mark,wanted,observed])
            if bank == target:
                assert mark not in pair
                local.append((mark,wanted))
            else:
                external_match &= observed == wanted
                if not self.permitted_shared_guards and bank.split("_",1)[0] != target.split("_",1)[0]:
                    raise ValueError("a control crossed the declared reader cut")
        assert routes._exchange_supported(pair,tuple(local),"H",reverse)
        candidate, enabled, changed = routes.exchange(before,pair,guard=tuple(local),
                                                       connected=offered and external_match,reverse=reverse)
        if offered:
            assert not any(_failures(before,reverse).values()) and not any(_failures(candidate,reverse).values())
        else:
            assert candidate==before and not enabled and not changed
        self.words[target] = candidate
        assert all(self.value(bank,reg) == observed for (bank,reg,_),(*_,observed) in zip(guards,active,strict=True))
        self.steps.append({"offer":name,"target_bank":target,"target_ordinary_pair":pair,
                           "local_and_supplied_guards":active,"cross_controller_control":any(b != target for b,_,_ in guards),
                           "offered":offered,"enabled":enabled,"fired":changed,"before":before,"after":candidate,
                           "guard_values_at_a_disconnected_slot_are_audit_only":not offered})

    def cycle(self, bank, direction=1, guards=(), *, offered=True):
        operations = ((S,Q,1,"P"),(Q,S,0,"Q"))
        if direction == -1:
            operations = operations[::-1]
        elif direction != 1:
            raise ValueError("cycle requires one of the two registered directions")
        for target,control,wanted,name in operations:
            self.exchange(name,bank,target,((bank,control,wanted),*guards),offered=offered)

    def swap(self, left_bank, left_reg, right_bank, right_reg, *, offered=True):
        """Swap arbitrary encoded bits using three actual conditional offers."""
        left, right = self.value(left_bank,left_reg), self.value(right_bank,right_reg)
        for target,r,control,g in ((right_bank,right_reg,left_bank,left_reg),
                                   (left_bank,left_reg,right_bank,right_reg),
                                   (right_bank,right_reg,left_bank,left_reg)):
            self.exchange("encoded bit swap",target,r,((control,g,1),),offered=offered)
        expected = (right,left) if offered else (left,right)
        assert (self.value(left_bank,left_reg),self.value(right_bank,right_reg)) == expected

    def move_pointer(self, former, receiver, *, offered=True):
        for reg in (Q,S):
            self.swap(former,reg,receiver,reg,offered=offered)

    def _append_old_write(self, bank, row):
        self.steps.append({"offer":row["action"],"target_bank":bank,"before":row["before"],"after":row["after"],
                           "offered":row["offered"],"enabled":row["enabled"],"fired":row["changed"],"old_writer_detail":row})

    def writes(self, bank, stages):
        word, steps = _routes().write_keeper(self.words[bank],stages=stages,reverse=self.encodings[bank])
        assert not any(_failures(word,self.encodings[bank]).values())
        self.words[bank] = word
        for step in steps:
            self._append_old_write(bank,step)

    def output(self):
        return {"initial":self.initial,"final":dict(self.words),"coordinate_reversed":self.encodings,
                "physical_mark_offsets":{bank:WIDTH*i for i,bank in enumerate(self.initial)},
                "offers":list(self.steps),"slot_count":len(self.steps)}


def _selector_guards(bank, address):
    return ((bank,Q,BITS[address][0]),(bank,S,BITS[address][1]))


def _group(trace, a, b, path, directions, *, binary=False, connected=True):
    # Each path has the same slots, even when a selector leaves that slot idle.
    schedule = ("b",) if binary else ("b","c","c")
    for address in schedule:
        controls = _selector_guards(path,address)
        trace.cycle(a,directions[0],controls,offered=connected)
        trace.cycle(b,directions[1],controls,offered=connected)


def _source_cycle_checks():
    ancestor = _old_physical()
    routes = _routes()
    same_device, local_source, shared_source, raw_guards = {}, {}, {}, {}
    for reverse in (False,True):
        key = str(int(reverse))
        reference = ancestor.basis_words(reverse)
        one, local, shared, raw = [], [], [], []
        for address, direction in product(ADDRESSES,(-1,1)):
            full = _basis(address,reverse)
            assert full == reference[address]
            sim = Trace({"pointer":full},reverse)
            history = []
            for repeat in range(3):
                sim.cycle("pointer",direction)
                current = sim.address("pointer")
                assert current == _cycle_address(address,direction*(repeat+1))
                prior_word, _ = ancestor._program(reference[_cycle_address(address,direction*repeat)],
                                                   "PQ" if direction == 1 else "QP",reverse)
                assert sim.words["pointer"] == prior_word
                history.append(current)
            assert sim.words["pointer"] == full
            one.append({"address":address,"direction":direction,"addresses_after_each_offer":history,**sim.output()})
        for address, path, direction, connected in product(ADDRESSES,ADDRESSES,(-1,1),(False,True)):
            sim = Trace({"pointer":_basis(address,reverse),"path":_basis(path,reverse)},reverse)
            sim.cycle("pointer",direction,_selector_guards("path","b"),offered=connected)
            endpoint = _cycle_address(address,direction * (path == "b") * connected)
            assert sim.address("pointer") == endpoint and sim.address("path") == path
            local.append({"address":address,"path":path,"direction":direction,"connected":connected,"endpoint":endpoint,**sim.output()})
        for a,b,path,da,db,kind,connected in product(ADDRESSES,ADDRESSES,ADDRESSES,(-1,1),(-1,1),("binary","ternary"),(False,True)):
            sim = Trace({"left":_basis(a,reverse),"right":_basis(b,reverse),"path":_basis(path,reverse)},reverse)
            _group(sim,"left","right","path",(da,db),binary=kind=="binary",connected=connected)
            exponent = ({"b":1} if kind=="binary" else {"b":1,"c":2}).get(path,0) * connected
            expected = (_cycle_address(a,da*exponent),_cycle_address(b,db*exponent))
            assert (sim.address("left"),sim.address("right")) == expected and sim.address("path") == path
            shared.append({"input_addresses":(a,b,path),"directions":(da,db),"selector_kind":kind,"connected":connected,
                           "exponent":exponent,"output_addresses":expected,**sim.output()})
        h_marks = routes._holding("H",reverse)
        q_names,s_names = (routes._places(routes.REGISTERS[j][:2],reverse) for j in (Q,S))
        for law,bits in product(LAWS,product((0,1),repeat=4)):
            prescribed = dict(zip((*q_names,*s_names),bits,strict=True))
            prescribed[routes.H_PRIVATE] = sum(bits)%2 if law == "parity" else 1
            word = routes.extend_holding("H",_mask(i for i,b in enumerate(h_marks) if prescribed.get(b,0)),law,reverse=reverse)
            source = word
            states = {"initial":word}
            for program in ("PQ","QP","PQPQPQ"):
                retrieved, status = ancestor._program(word,program,reverse)
                assert all(not row["physical_law_failures"][law] for row in status)
                states[program] = retrieved
            _,undo = ancestor._program(states["PQ"],"QP",reverse)
            assert undo[-1]["after"] == source
            raw.append({"law":law,"physically_held_q0_q1_s0_s1":bits,"on_complementary_basis":bits[0]!=bits[1] and bits[2]!=bits[3],
                        "states":states,"returns_in_three":states["PQPQPQ"]==source})
        same_device[key], local_source[key], shared_source[key], raw_guards[key] = one, local, shared, raw
    return {"old_single_cycles":same_device, "local_binary_source_columns":local_source,
            "controlled_group_columns":shared_source,"unrestricted_guard_extensions":raw_guards,
            "group_schedule": {"binary":["b"],"ternary":["b","c","c"], "slots_per_cycle_pair":4}}


# An entry is integer numerator / sqrt(positive rational denominator).
ANALYZERS = {
    "ordinary": (((1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)),(1,1,1,1)),
    "real_ab": (((1,1,0,0),(1,-1,0,0),(0,0,1,0),(0,0,0,1)),(2,2,1,1)),
    "three_way": (((1,1,1,0),(1,-1,1,0),(1,0,-2,0),(0,0,0,1)),(3,2,6,1)),
}


def _matrix_entry(setting, row, col, inverse=False):
    values, roots = ANALYZERS[setting]
    if inverse:
        row,col = col,row
    return values[row][col],roots[col]


def _basis_offer(word, setting, *, inverse, reverse):
    """Check the actual lawful ordinary words of a supplied real gate column."""
    col = ADDRESSES.index(_address(word,reverse))
    alternatives = []
    for j,label in enumerate(ADDRESSES):
        n,d = _matrix_entry(setting,j,col,inverse)
        sim = Trace({"word":word},reverse)
        if n:
            for reg,wanted in zip((Q,S),BITS[label],strict=True):
                if sim.value("word",reg)!=wanted:
                    sim.exchange("ordinary support witness", "word",reg)
            ordinary = sim.words["word"]
            assert sim.address("word") == label
        else:
            ordinary = None
        alternatives.append({"address":label,"ordinary_word":ordinary,"amplitude":[n,d],
                             "ordinary_support_witness":list(sim.steps)})
    return {"gate":setting,"true_transpose":inverse,"initial_word":word,"all_four_basis_rows":alternatives,
            "ordinary_support_offers_do_not_supply_the_real_amplitudes":True}


def _real_basis_checks():
    grams = {}
    for name,(a,d) in ANALYZERS.items():
        gram = [[sum(a[k][i]*a[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
        assert gram == [[d[i]*(i==j) for j in range(4)] for i in range(4)]
        grams[name] = gram
    return {"integer_numerator_grams_before_column_normalization":grams,
            "coherent_amplitude_encoding":"The two numbers are n,d for n/sqrt(d). Zero rows retained.",
            "all_supplied_real_gate_basis_columns":{
                f"{int(reverse)}/{name}/{label}/{int(inverse)}":_basis_offer(_basis(label,reverse),name,inverse=inverse,reverse=reverse)
                for reverse,name,label,inverse in product((False,True),ANALYZERS,ADDRESSES,(False,True))}}


def _write_flag(sim, bank, stages):
    old = sim.address(bank)
    t = sim.value(bank,T)
    sim.swap(bank,Q,bank,T)
    before = sim.words[bank]
    assert sim.value(bank,Q) == t and sim.value(bank,T) == BITS[old][0]
    sim.writes(bank,stages)
    after = sim.words[bank]
    sim.swap(bank,Q,bank,T)
    assert sim.address(bank) == old and sim.value(bank,T) == t
    return before,after


def _port(word, marked, stages, reverse, *, complete):
    sim = Trace({"A_record":word},reverse,permitted_shared_guards=False)
    bank = "A_record"
    addressed = sim.address(bank)
    assert sim.value(bank,T) == 0 and all(sim.value(bank,k)==0 for k in ADDRESS_RECORD)
    assert sim.value(bank,MEASURED_RECEIPT) == 1
    sim.exchange("mark completed local analysis",bank,MEASURED_RECEIPT)
    if complete:
        for target,control in zip(ADDRESS_RECORD,(Q,S),strict=True):
            sim.exchange("copy the resolved address",bank,target,((bank,control,1),))
    sim.exchange("copy only the requested predicate to T",bank,T,_selector_guards(bank,marked))
    assert sim.value(bank,T) == (addressed==marked)
    before, after = _write_flag(sim,bank,stages)
    old = _routes()
    start = old.decode(word,reverse=reverse)
    ending = old.decode(sim.words[bank],reverse=reverse)
    observed = [sim.value(bank,k) for k in ADDRESS_RECORD]
    assert observed == (list(BITS[addressed]) if complete else [0,0])
    assert ending["l"] == start["l"] and _logical(sim.words[bank],1,reverse) == _logical(word,1,reverse)
    out = ending["keeper"]
    return {"independent_local_only":True,"address":addressed,"marked_predicate":marked,"measured_flag":int(addressed==marked),
            "physical_address_workspace": observed,"address_measurement_resolved":complete,"before_writer":before,"after_writer":after,
            "physical_completed_receipt":sim.value(bank,MEASURED_RECEIPT),
            "keeper":out,"keeper_wrote":out!="110","keeper_matches_flag":out==("011" if addressed==marked else "101"),
            "final_fields":ending, "writer_connections":stages, **sim.output()}


def _local_faults(reverse):
    prior = _routes()
    a = _basis("a",reverse)
    ready = _basis("c",reverse)
    damaged_bit = a ^ (1 << prior._guard(Q,reverse)[0])
    dirty_record = a ^ _mask(prior._places(prior.REGISTERS[ADDRESS_RECORD[0]][:2],reverse))
    nonready = _basis("a",reverse,keeper="101",z=0)
    trials = {
        "idle_request": (a,"idle"),"missing_remote_address":(a,"address_absent"),
        "analyzer_disconnected":(a,"disconnected_read"),"missing_public_launch":(ready,"source_rejected_no_pointer_delivered"),
        "nonready_keeper":(nonready,prior._prep_status(nonready,reverse=reverse)),
        "damaged_keeper":(_basis("a",reverse,keeper="111"),"damaged_keeper"),
        "damaged_binary_register":(damaged_bit,prior._prep_status(damaged_bit,reverse=reverse)),
        "preoccupied_record_workspace":(dirty_record,"address_workspace_not_blank"),
        "preoccupied_flag":(_basis("a",reverse,t=1),"flag_not_blank"),
    }
    out = {}
    for name,(word,status) in trials.items():
        result = prior.decode(word,reverse=reverse)
        out[name] = {"admission":0 if name=="missing_public_launch" else 1,"status":status,
                     "initial":word,"terminal":word,"resolved_address":None,"recorded_flag":None,
                     "physical_completed_receipt":_logical(word,MEASURED_RECEIPT,reverse),
                     "keeper":result["keeper"],"writer_fired":False,"actual_law_failures":_failures(word,reverse)}
    assert out["nonready_keeper"]["status"] == "nonready_keeper"
    assert out["damaged_binary_register"]["status"] == "damaged_register"
    return out


def _workspace_check(row, reverse):
    word = row["final"]["A_record"]
    return word & ~_mask(_routes()._places((*_routes().REGISTERS[Q][:2],*_routes().REGISTERS[S][:2]),reverse))


def _local_checks():
    by_orientation = {}
    for reverse in (False,True):
        columns, prepared_flags, binary_calibration = {},[],{}
        for address, marked, stages, full in product(ADDRESSES,ADDRESSES,STAGES,(False,True)):
            row = _port(_basis(address,reverse),marked,stages,reverse,complete=full)
            key = f"{address}/{marked}/{int(stages[0])}{int(stages[1])}/{int(full)}"
            columns[key] = row
        for address, t, stages in product(ADDRESSES,(0,1),STAGES):
            sim = Trace({"A_record":_basis(address,reverse,t=t)},reverse,permitted_shared_guards=False)
            prev,post = _write_flag(sim,"A_record",stages)
            final = _routes().decode(sim.words["A_record"],reverse=reverse)
            prepared_flags.append({"address":address,"physical_flag_supplied":t,"keeper":final["keeper"],
                                   "z":final["z"],"arrived_at_writer":prev,"left_writer":post,"connections":stages,
                                   **sim.output()})
        for flag, cohort in product((0,1),("b_c_complement","all_addresses")):
            addresses = ("b","c") if cohort=="b_c_complement" and flag==0 else (("a",) if flag==1 else ("b","c","d"))
            binary,complete = [],[]
            for j in addresses:
                binary.append(_workspace_check(columns[f"{j}/a/11/0"],reverse))
                complete.append(_workspace_check(columns[f"{j}/a/11/1"],reverse))
            assert len(set(binary))==1 and len(set(complete))==len(addresses)
            binary_calibration[f"{cohort}/{flag}"] = {"words":addresses,"binary_held_non_pointer":binary,
                                                       "full_held_non_pointer":complete,
                                                       "b_c_complement_can_retain_coherence_only_without_the_address_copy":cohort=="b_c_complement" and flag==0}
        by_orientation[str(int(reverse))] = {"basis_columns":columns,"both_values_on_a_prepared_output_flag":prepared_flags,
                                            "binary_complement_and_full_address_workspaces":binary_calibration,
                                            "local_faults_and_idle":_local_faults(reverse)}
    return {"old_data_marks_used_as_actual_address_record":ADDRESS_RECORD,"separate_optional_pre_read_copy":PRE_READ_COPY,
            "physical_completed_receipt_register":MEASURED_RECEIPT,
            "local_analyzer_interface":by_orientation,
            "lawful_preparation_source":"The reversible guarded copy records the addressed post-analyzer outcome. No pre-analysis copy is made in the clean or binary arms.",
            "frozen_flag_mapping":"An admitted blank T receives one exactly when the resolved word equals the chosen mark. Q and T are returned before O returns the pointer."}


def _pointer_transfer(word, old, destination, reverse, *, offered=True, separate=True):
    sim = Trace({old:word,destination:_basis("c",reverse)},reverse,permitted_shared_guards=separate)
    sim.move_pointer(old,destination,offered=offered)
    if offered:
        q,s = _address(word,reverse),sim.address(old)
        assert s == "c" and sim.address(destination) == q
    else:
        assert sim.words == sim.initial
    for bank in sim.words:
        changed = sim.initial[bank] ^ sim.words[bank]
        q_s = _mask(_routes()._places((*_routes().REGISTERS[Q][:2],*_routes().REGISTERS[S][:2]),reverse))
        assert changed & ~q_s == 0
    return sim.output()


def _repeat_checks(local):
    repeats, unreturned, tagged = {}, {}, {}
    for reverse, setting, first,marked,stages in product((False,True),ANALYZERS,ADDRESSES,ADDRESSES,STAGES):
        current = local["local_analyzer_interface"][str(int(reverse))]["basis_columns"]
        flags = f"{int(stages[0])}{int(stages[1])}"
        first_key = f"{first}/{marked}/{flags}/1"
        full = current[first_key]
        outgoing = full["final"]["A_record"]
        actual_returns = _basis_offer(outgoing,setting,inverse=False,reverse=reverse)
        transfers = []
        for row in actual_returns["all_four_basis_rows"]:
            if row["ordinary_word"] is not None:
                physical = _pointer_transfer(row["ordinary_word"],"A_first","A_fresh",reverse,separate=False)
                assert _logical(physical["final"]["A_first"],T,reverse) == full["measured_flag"]
                assert _routes().decode(physical["final"]["A_first"],reverse=reverse)["keeper"] == full["keeper"]
                assert physical["final"]["A_fresh"] == _basis(row["address"],reverse)
                transfers.append({"address":row["address"],"term":row["amplitude"],**physical})
        # O transpose O returns the actual resolved address, including when its first keeper was disconnected.
        possible_second_ports = {address:{"certain_if_same_setting":address==first,
                                          "fresh_hardware_column":f"{address}/{marked}/11/1"} for address in ADDRESSES}
        repeats[f"{int(reverse)}/{setting}/{first_key}"] = {"first_hardware_column":first_key,"physical_full_return":actual_returns,
                   "return_terms_transferred_without_old_T_K_or_address":transfers,"fresh_second_port_columns":possible_second_ports,
                   "no_old_record_crosses_the_repeat_transfer":True}

    for reverse in (False,True):
        tails = []
        for first in ("a","b"):
            row = local["local_analyzer_interface"][str(int(reverse))]["basis_columns"][f"{first}/a/11/1"]
            actual = _pointer_transfer(row["final"]["A_record"],"A_first","A_fresh",reverse,separate=False)
            second = _basis_offer(actual["final"]["A_fresh"],"real_ab",inverse=True,reverse=reverse)
            assert [r["address"] for r in second["all_four_basis_rows"] if r["amplitude"][0]] == ["a","b"]
            tails.append({"first_measured_address":first,"first_hardware_column":f"{first}/a/11/1",
                          "skipped_that_physical_O_return":True,"literal_local_transfer":actual,"second_inverse":second})
        unreturned[str(int(reverse))] = {"launch":_basis("a",reverse),"first_inverse":_basis_offer(_basis("a",reverse),"real_ab",inverse=True,reverse=reverse),
                                        "first_outcome_columns":tails}
        tag_rows = []
        for code, mode in product(ADDRESSES,("retained","hidden","returned","disconnected","absent")):
            sim = Trace({"A_first":_basis(code,reverse)},reverse,permitted_shared_guards=False)
            fields = list(zip(PRE_READ_COPY,(Q,S),strict=True))
            if mode != "absent":
                for target,control in fields:
                    sim.exchange("copy preanalysis pointer coordinate", "A_first",target,(("A_first",control,1),),offered=mode!="disconnected")
            at_copy = sim.words["A_first"]
            saved = tuple(sim.value("A_first",i) for i in PRE_READ_COPY)
            if mode == "returned":
                for target,control in reversed(fields):
                    sim.exchange("unlink actual preanalysis pointer copy", "A_first",target,(("A_first",control,1),))
            if mode in ("returned","disconnected","absent"):
                assert sim.words == sim.initial
            final_word = sim.words["A_first"]
            full_columns = {}
            for setting in ANALYZERS:
                columns = []
                for arm in _basis_offer(final_word,setting,inverse=True,reverse=reverse)["all_four_basis_rows"]:
                    if arm["ordinary_word"] is None:
                        continue
                    port = _port(arm["ordinary_word"],"a",(True,True),reverse,complete=True)
                    shown = port["final"]["A_record"]
                    assert tuple(_logical(shown,i,reverse) for i in PRE_READ_COPY) == tuple(sim.value("A_first",i) for i in PRE_READ_COPY)
                    columns.append({"address":arm["address"],"amplitude":arm["amplitude"],"full_final_ordinary_word":shown})
                full_columns[setting] = columns
            tag_rows.append({"ordinary_before_analyzer":code,"record_mode":mode,"at_copy":at_copy,"purported_record":saved,
                             "physical_preanalysis_tag_survives":mode in ("retained","hidden"),"access_to_old_tag":mode=="retained",
                             "nonzero_analyzer_basis_columns_with_preserved_tag":full_columns,
                             **sim.output()})
        tagged[str(int(reverse))] = tag_rows
    return {"repeat_columns":repeats,"literal_unreturned_ab_on_a":unreturned,"optional_preanalysis_copies":tagged,
            "second_port_failure_rule":"An absent or refused second request has the fresh no-write row. Writer faults on either read only affect its own keeper.",
            "same_setting_reason":"The transferred pointer support is the measured real-basis vector from applying O to j, so the next O transpose selects j. The canonical complete receiver column is reused exactly."}


def _bench_tags():
    records,reactive = {},{}
    for reverse in (False,True):
        all_paths = []
        for source, path, variant, mode in product(("a","d"),ADDRESSES,("binary","ternary"),("absent","audit","kept","hidden","returned","disconnected")):
            sim = Trace({"bench_left":_basis(source,reverse),"bench_right":_basis(source,reverse),"bench_path":_basis(path,reverse)},reverse)
            path_bank = "bench_path"
            coords = ((T,Q),(L,S))
            if mode not in ("absent","audit"):
                for target,control in coords:
                    sim.exchange("copy actual bench path",path_bank,target,((path_bank,control,1),),offered=mode!="disconnected")
            before_program = dict(sim.words)
            _group(sim,"bench_left","bench_right",path_bank,(1,1),binary=variant=="binary")
            if mode in ("kept","hidden","returned","disconnected"):
                for target,control in reversed(coords):
                    sim.exchange("return actual path copy",path_bank,target,((path_bank,control,1),),offered=mode=="returned")
            copied = [sim.value(path_bank,j) for j in (T,L)]
            assert copied == (list(BITS[path]) if mode in ("kept","hidden") else [0,0])
            all_paths.append({"initial_pointers":source,"ordinary_path":path,"actual_record_mode":mode,"selector_kind":variant,
                              "tag_before_group":before_program,"physical_tag_after_group":copied,
                              "local_visibility_of_tag":mode=="kept","uncoupled_simulator_log_is_not_a_pointer":True,**sim.output()})
        all_clocks = []
        for address,path,returned in product(ADDRESSES,ADDRESSES,(False,True)):
            sim = Trace({"bench_left":_basis(address,reverse),"bench_right":_basis(address,reverse),"bench_path":_basis(path,reverse)},reverse)
            a,b,p = "bench_left","bench_right","bench_path"
            # On this complementary input first P fires exactly at q=1 and path=b.
            local_guard = ((a,Q,1),*_selector_guards(p,"b"))
            sim.exchange("record whether first P actually fires",p,T,local_guard)
            _group(sim,a,b,p,(1,1),binary=True)
            assert sim.value(p,T) == sim.steps[1]["fired"]
            _group(sim,a,b,p,(-1,-1),binary=True,connected=returned)
            sim.exchange("uncompute first-firing record with restored controls",p,T,local_guard,offered=returned)
            _group(sim,a,b,p,(1,1),binary=True,connected=returned)
            expected = _cycle_address(address,int(path=="b"))
            assert sim.address(a)==sim.address(b)==expected
            assert sim.value(p,T) == int(not returned and path=="b" and BITS[address][0])
            all_clocks.append({"ordinary_inputs":(address,path),"physical_clock_returned":returned,"final_clock":sim.value(p,T),**sim.output()})
        assert len({r["slot_count"] for r in all_clocks})==1
        records[str(int(reverse))],reactive[str(int(reverse))] = all_paths,all_clocks
    return {"bench_route_copy_columns":records,"reactive_clock_padded":reactive,
            "primary_slot_clock_does_not_deliver_firing_flags":True}


def _bench_port_word(label, reverse):
    source = _basis(label or "c",reverse)
    sim = Trace({"bench_port":source},reverse)
    bank = "bench_port"
    sim.exchange("mark measured bench port",bank,MEASURED_RECEIPT,offered=label is not None)
    for target,guard in zip(ADDRESS_RECORD,(Q,S),strict=True):
        sim.exchange("copy actual resolved bench port",bank,target,((bank,guard,1),),offered=label is not None)
    assert sim.value(bank,MEASURED_RECEIPT) == (label is None)
    assert tuple(sim.value(bank,a) for a in ADDRESS_RECORD) == (BITS[label] if label else (0,0))
    return sim.output()


def _transfer_checks():
    truth,launches,four,bench_receipts = [],{},[],{}
    for rs,rr,a,b,offered in product((False,True),(False,True),ADDRESSES,ADDRESSES,(False,True)):
        sim = Trace({"bench_pointer":_basis(a,rs),"A_receiver":_basis(b,rr)},
                    encodings={"bench_pointer":rs,"A_receiver":rr})
        sim.move_pointer("bench_pointer","A_receiver",offered=offered)
        assert (sim.address("bench_pointer"),sim.address("A_receiver")) == ((b,a) if offered else (a,b))
        assert sim.words["bench_pointer"] == _basis(b if offered else a,rs)
        assert sim.words["A_receiver"] == _basis(a if offered else b,rr)
        truth.append({"old_and_new_encodings":(rs,rr),"input_addresses":(a,b),"transfer_enabled":offered,
                      "bench_restores_blank_only_if_incoming_receiver_was_blank":b=="c" if offered else a=="c",**sim.output()})

    stage_codes = [(f"positive_port_{j}",j in "ab",(j,None,None,None)) for j in ADDRESSES]
    stage_codes += [("missing_source",False,(None,)*4),("nonready_bench",False,(None,)*4),("damaged_bench",False,(None,)*4)]
    stage_codes += [(f"charge_local_herald_{a}_{b}",False,(None,a,b,None)) for a,b in product("ab",repeat=2) if (a,b)!=("b","b")]
    stage_codes += [(f"charge_both_local_minus_group_{j}",j=="a",(None,"b","b",j)) for j in ADDRESSES]
    for reverse in (False,True):
        cases = []
        bench = {label:_bench_port_word(label,reverse) for label in (*ADDRESSES,None)}
        bench_receipts[str(int(reverse))] = {label or "unmeasured":row for label,row in bench.items()}
        for a,b,(source_event,acceptance,heralds) in product(ADDRESSES,ADDRESSES,stage_codes):
            words = {"bench_A":_basis(a,reverse),"bench_B":_basis(b,reverse),"bench_selectors":_basis("b",reverse,t=1,l=1),
                     "A_target":_basis("c",reverse),"B_target":_basis("c",reverse),
                     "A_public":_basis("c",reverse),"B_public":_basis("c",reverse),
                     **{name:bench[j]["final"]["bench_port"] for name,j in zip(("bench_positive_port","bench_A_herald","bench_B_herald","bench_last_group_port"),heralds,strict=True)}}
            if source_event=="nonready_bench":
                words["bench_A"] = _basis(a,reverse,keeper="101",z=0)
            elif source_event=="damaged_bench":
                words["bench_A"] = _basis(a,reverse,keeper="111")
            elif source_event=="missing_source":
                words["bench_A"] = words["bench_B"] = _basis("c",reverse)
            sim = Trace(words,reverse)
            for side in ("A","B"):
                sim.move_pointer("bench_"+side,side+"_target",offered=acceptance)
                sim.exchange("deliver common admission bit",side+"_public",T,offered=acceptance)
            local = {b:w for b,w in sim.words.items() if not b.startswith("bench_")}
            assert sim.words["bench_selectors"] == words["bench_selectors"]
            assert all(sim.words[bank]==words[bank] for bank in ("bench_positive_port","bench_A_herald","bench_B_herald","bench_last_group_port"))
            assert all(sim.value(side+"_public",T)==acceptance for side in ("A","B"))
            for side,letter in (("A",a),("B",b)):
                assert local[side+"_target"] == _basis(letter if acceptance else "c",reverse)
                assert sim.words["bench_"+side] == (_basis("c",reverse) if acceptance else words["bench_"+side])
            cases.append({"source_event_on_bench":source_event,"public_admission":int(acceptance),
                          "bench_resolved_ports_in_order":heralds,"literal_source_present":source_event!="missing_source",
                          "complete_delivered_banks":local,"addressed_pointers_actually_delivered":acceptance,
                          "bench_flags_or_selectors_delivered":False,**sim.output()})
        launches[str(int(reverse))] = cases
        assert len({r["slot_count"] for r in cases})==1
        assert len({tuple(r["complete_delivered_banks"].values()) for r in cases if not r["public_admission"]})==1
        for a,b in product(ADDRESSES,repeat=2):
            accepted = [r for r in cases if r["public_admission"] and r["initial"]["bench_A"]==_basis(a,reverse) and r["initial"]["bench_B"]==_basis(b,reverse)]
            assert len(accepted)==3 and all(r["complete_delivered_banks"]==accepted[0]["complete_delivered_banks"] for r in accepted)

        for addresses in product(ADDRESSES,repeat=4):
            roles = ("A_target","B_target","A_reference","B_reference")
            initial = {**{"bench_"+key:_basis(value,reverse) for key,value in zip(roles,addresses,strict=True)},
                       **{key:_basis("c",reverse) for key in roles}}
            sim = Trace(initial,reverse)
            for bank,address in zip(roles,addresses,strict=True):
                sim.move_pointer("bench_"+bank,bank)
                assert sim.words[bank]==_basis(address,reverse) and sim.words["bench_"+bank]==_basis("c",reverse)
            four.append({"source_addresses_in_role_order":addresses,"roles":roles,"coordinate_reversed":reverse,
                         "slots":len(sim.steps),"delivered_complete_words":[sim.words[b] for b in roles],
                         "bench_complete_words":[sim.words["bench_"+b] for b in roles]})
    return {"all_complete_transfer_columns":truth,"matched_two_reader_launches":launches,"four_pointer_delivery_cartesian_check":four,
            "bench_physical_herald_receipts":bench_receipts,
            "transfer_slots_per_pointer":6,"public_admission_uses_a_separate_blank_T_at_each_reader":True,
            "full_word_histories_for_four_pointers":"The four transfers have disjoint target and source banks. Their 24 slots concatenate the checked single-transfer columns in role order."}


def _selection_and_disclosure():
    policies = ("no_B_transposition","transpose_B","fair_coin")
    by_encoding = {}
    for reverse in (False,True):
        tables, disclosed = [], []
        for a,b,trit,coin,policy in product(ADDRESSES,ADDRESSES,ADDRESSES,ADDRESSES,policies):
            words = {"bench_A":_basis(a,reverse),"bench_B":_basis(b,reverse),"bench_trit":_basis(trit,reverse),"bench_coin":_basis(coin,reverse)}
            sim = Trace(words,reverse)
            for address in ("b","c","c"):
                sim.cycle("bench_A",1,_selector_guards("bench_trit",address))
            control = (("bench_B",Q,1),)
            if policy == "fair_coin":
                control += _selector_guards("bench_coin","b")
            sim.exchange("B ordinary transposition or padded offer","bench_B",S,control,offered=policy!="no_B_transposition")
            j = {"b":1,"c":2}.get(trit,0)
            change = policy=="transpose_B" or (policy=="fair_coin" and coin=="b")
            expected_b = {"a":"b","b":"a"}.get(b,b) if change else b
            assert (sim.address("bench_A"),sim.address("bench_B")) == (_cycle_address(a,j),expected_b)
            assert sim.words["bench_trit"] == words["bench_trit"] and sim.words["bench_coin"] == words["bench_coin"]
            tables.append({"inputs":(a,b,trit,coin),"policy":policy,"admitted_selector_support":trit!="d" and coin in "ab",
                           "bench_address_outputs":(sim.address("bench_A"),expected_b),"selectors_delivered":False,**sim.output()})
        assert len({r["slot_count"] for r in tables})==1
        for trit,coin,which in product(ADDRESSES,ADDRESSES,("none","trit","coin","both")):
            orig = {"bench_trit":_basis(trit,reverse),"bench_coin":_basis(coin,reverse)}
            for side in "AB":
                for label in ("trit","coin"):
                    orig[f"{side}_{label}_record"] = _basis("c",reverse)
            sim = Trace(orig,reverse)
            for side in "AB":
                for label in ("trit","coin"):
                    for reg in (Q,S):
                        sim.exchange("copy expressly disclosed selector coordinate",f"{side}_{label}_record",reg,
                                     (("bench_"+label,reg,1),),offered=which in (label,"both"))
                    assert sim.address(f"{side}_{label}_record") == (sim.address("bench_"+label) if which in (label,"both") else "c")
            disclosed.append({"private_trit":trit,"private_coin":coin,"deliberately_delivered":which,**sim.output()})
        by_encoding[str(int(reverse))] = {"matched_bench_columns":tables,"deliberate_disclosure_columns":disclosed}
    return {"layouts":by_encoding,"trit_calibration":"U on a","coin_calibration":"binary Hadamard on a", "both_drawn_in_all_policies":True,
            "scope":"These word maps route already prepared selectors. Ignored selectors are retained at the bench under all matched policies."}


def _postcut_local_controls():
    rows,adaptation = [],{}
    for target_rev,reference_rev,path_rev,target,ref,path,da,db in product((False,True),(False,True),(False,True),
                                                                           ADDRESSES,ADDRESSES,ADDRESSES,(-1,1),(-1,1)):
        a,b,p = "A_target","A_reference","A_path"
        words = {a:_basis(target,target_rev),b:_basis(ref,reference_rev),p:_basis(path,path_rev)}
        encodings = dict(zip((a,b,p),(target_rev,reference_rev,path_rev),strict=True))
        sim = Trace(words,permitted_shared_guards=False,encodings=encodings)
        _group(sim,a,b,p,(da,db))
        j = {"b":1,"c":2}.get(path,0)
        expected = (_cycle_address(target,da*j),_cycle_address(ref,db*j),path)
        assert tuple(sim.address(x) for x in (a,b,p)) == expected
        rows.append({"input":(target,ref,path),"directions":(da,db),"encodings":encodings,
                     "output_addresses":expected,"complete_output_words":list(sim.words.values()),
                     "native_offers":len(sim.steps)})
        if (target,ref) == ("a","b"):
            key = f"{int(target_rev)}{int(reference_rev)}{int(path_rev)}/{da}/{db}/{path}"
            adaptation[key] = sim.output()
    remote = Trace({"A_target":_basis("a"),"B_path":_basis("b")},permitted_shared_guards=False)
    try:
        remote.cycle("A_target",1,_selector_guards("B_path","b"))
    except ValueError as error:
        assert str(error) == "a control crossed the declared reader cut"
        assert remote.words == remote.initial and not remote.steps
    else:
        raise AssertionError("a remote setting took part in a declared local gate")
    actual_port_product = []
    for left,right in product(ADDRESSES,repeat=2):
        # Every nonzero or zero-valued joint port uses the same local word dictionary.
        actual_port_product.append({"resolved_sites":(left,right),
                                    "left_independent_hardware_key":f"{left}/a/11/1",
                                    "right_independent_hardware_key":f"{right}/a/11/1"})
    return {"all_independent_target_reference_selector_namings_and_directions":rows,
            "representative_full_slot_traces":adaptation,
            "after_separation_guard_crossing_refused_unchanged":True,
            "complete_cartesian_port_address_book":actual_port_product,
            "allocation":"Each local comparison can act between the target, second actual pointer and the local path in the same lab. Replacing A bank names by B names produces the same disjoint blueprint."}


def _ancestor_and_cut_checks():
    routes = _routes()
    proof = routes._assembled_projections()
    duplicate_tensor = {}
    for reverse,law in product((False,True),LAWS):
        cohort = proof["corrected_projections"][f"{law}/{int(reverse)}"]
        first,second = [],[]
        for name in routes.SUBSTRATE:
            row = routes._holding(name,reverse)
            first.append({"holder":name,"names":row})
            second.append({"holder":name,"names":tuple(j+WIDTH for j in row)})
        roster = (*first,*second)
        owners = {i:sum(i in row["names"] for row in roster) for i in range(2*WIDTH)}
        assert all(value in (1,2) for value in owners.values())
        assert len(roster)==30 and len(cohort["full_ternary_projections"])==14
        duplicate_tensor[f"{law}/{int(reverse)}"] = {
            "distinct_physical_marks":tuple(owners),"incidence_multiplicity":owners,
            "disjoint_actual_holdings":roster,"both_H_full_projection_size":cohort["full_H_projection_size"],
            "independent_lawful_extension_of_one_bank_has_arbitrary_other_bank":True}
    return {"full_ancestor_projection_certificates":proof,"two_disjoint_ready_copies":duplicate_tensor,
            "larger_bank_assembly":"Each extra path, flag, comparator, repeat or reference is a disjoint copy. Scoped, marked execution of a supplied gate retains disjoint holding incidences.",
            "no_ordinary_birth_clock_or_payer_in_the_gate_traces":True}


def hardware_checks():
    """Return the exact ordinary basis-word and reversible hardware record."""
    local = _local_checks()
    paths = (Path(__file__).resolve(),HERE/"preregistration.md",ROUTES_PATH,CYCLE_PATH,PHYSICAL_PATH,KEEPER_PATH)
    return {"root_physical_word_width":WIDTH,"basis_addresses":BITS,
            "principal_blank_receiver_address":"c","basis_data_preload":READY_DATA,
            "exact_amplitude_lift_scope":"Real gate columns specify n/sqrt(d). Ordinary word witnesses test the connected holders and do not determine those amplitudes.",
            "history_reconstruction":"Each trace gives all initial words, their physical mark offsets, all offers and guard data, and the old/new word of the single target after each slot. Other banks remain unchanged until their named slot.",
            "holdings":_ancestor_and_cut_checks(),"real_gate_support":_real_basis_checks(),
            "source_cycle":_source_cycle_checks(),"source_tags":_bench_tags(),"separation_and_transfer":_transfer_checks(),
            "selector_twirl_and_disclosure":_selection_and_disclosure(),"local_readout":local,
            "retained_histories_and_repeat":_repeat_checks(local),"within_reader_comparators":_postcut_local_controls(),
            "source_digests":{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths}}


def _smoke():
    for rev,label in product((False,True),ADDRESSES):
        w = _basis(label,rev)
        sim = Trace({"A_first":w},rev,permitted_shared_guards=False)
        sim.cycle("A_first")
        assert sim.address("A_first") == _cycle_address(label,1)
        sim.cycle("A_first",-1)
        assert sim.words["A_first"]==w
        for mark in ADDRESSES:
            p = _port(w,mark,(True,True),rev,complete=True)
            assert p["keeper"] == ("011" if label==mark else "101")
            assert p["physical_completed_receipt"] == 0
    sample = _pointer_transfer(_basis("b"),"A_first","A_fresh",False,separate=False)
    assert sample["final"] == {"A_first":_basis("c"),"A_fresh":_basis("b")}
    return {"basis_cycles":8,"full_writer_checks":32,"fresh_transfer_checked":True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke",action="store_true",help="run the short physical replay")
    argv = parser.parse_args()
    if argv.smoke:
        print(json.dumps(_smoke(),sort_keys=True))
    else:
        record = json.dumps(hardware_checks(),sort_keys=True,separators=(",",":")).encode()
        print(f"hardware_checks {sha256(record).hexdigest()} over {len(record)} canonical JSON bytes")


if __name__ == "__main__":
    main()
