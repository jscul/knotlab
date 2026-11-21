"""Compute exact two-reader records on the actual ranked closure in the frozen panel."""

from collections import Counter
from fractions import Fraction
from functools import reduce
from itertools import combinations, product
from math import lcm
from pathlib import Path
import gzip
import json
import os
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
PREVIOUS = "FOUR-READINGS-20261120-001A"
sys.path.insert(0, str(ROOT / "experiments" / PREVIOUS / f"{PREVIOUS}-E001_signed_rules"))
from census import pauli_solution, product as pauli_product, verify_paulis

sys.path.insert(0, str(ROOT / "research" / "TWO-KNOTS-ONE-DECISION-20261121-001"))
import measurement
ROSTER_SOURCE = "CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001C"
sys.path.insert(0, str(ROOT / "experiments" / ROSTER_SOURCE / f"{ROSTER_SOURCE}-E001_wider_meetings"))
from census_stages import advance

IDENTITY = (0, 0, 0)


def write_json(name, value):
    data = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    (OUTPUT / name).write_bytes(gzip.compress(data, mtime=0) if name.endswith(".gz") else data)


def named_masks(rows):
    names = sorted({i for row in rows for i in row})
    positions = {name: j for j, name in enumerate(names)}
    return names, [sum(1 << positions[name] for name in row) for row in rows]


def affine_count(masks, polarities, width):
    pivots = {}
    for mask, rhs in zip(masks, polarities, strict=True):
        while mask:
            index = mask.bit_length() - 1
            if index not in pivots:
                pivots[index] = mask, rhs
                break
            previous, parity = pivots[index]
            mask ^= previous
            rhs ^= parity
        if not mask and rhs:
            return 0
    return 1 << (width - len(pivots))


def local_word(word, locations):
    return sum(((word >> position) & 1) << i for i, position in enumerate(locations))


def literal_words(masks, sign, width):
    return [w for w in range(1 << width)
            if all((w & mask).bit_count() % 2 == p for mask, p in zip(masks, sign, strict=True))]


def check_knot(rows, sign, support):
    clauses = []
    for row, rhs in zip(rows, sign, strict=True):
        for word in range(1 << len(row)):
            if word.bit_count() % 2 != rhs:
                clauses.append(" ".join(("-" if word & (1 << i) else "") + f"x{name}"
                                        for i, name in enumerate(row)))
    labels = [f"x{name}" for name in support]
    witnesses = sorted(set().union(*map(set, rows)) - set(support))
    command = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
               "--loops", *labels[:-1], "--contact", labels[-1], "--json"]
    if witnesses:
        command += ["--witnesses", *(f"x{name}" for name in witnesses)]
    result = json.loads(subprocess.check_output(command, cwd=ROOT,
                        env={**os.environ, "PYTHONPATH": str(ROOT / "tools")}))
    return {key: result[key] for key in ("binding", "loss_on_erasure", "coexistence",
                                        "invisible_in_parts", "allowed")}


def read_whole(raw):
    physical = [tuple(row) for row in raw["after_rows"]]
    ids = raw["component_holders"]
    rows = [physical[h] for h in ids]
    assert raw["holder"] in ids and len(physical) == len(raw["before_rows"]) + 1
    assert tuple(map(tuple, raw["before_rows"])) == tuple(physical[:-1])
    assert set(ids) == set(range(len(physical)))
    closing = ids.index(raw["holder"])
    assert closing == len(rows) - 1 and raw["fresh"] == 0
    names, masks = named_masks(rows)
    positions = {name: j for j, name in enumerate(names)}
    local_rows = [tuple(positions[name] for name in row) for row in rows]
    ends = [tuple(i for i, row in enumerate(rows) if name in row) for name in names]
    assert all(len(pair) == 2 for pair in ends)
    assert reduce(int.__xor__, masks[:-1], 0) == masks[-1]
    result = {}
    signs = [[int(i == closing and odd) for i in range(len(rows))] for odd in (False, True)]
    even_words = None
    for odd, sign in enumerate(signs):
        size = affine_count(masks, sign, len(names))
        deleted = [affine_count(masks[:h] + masks[h+1:], sign[:h] + sign[h+1:], len(names))
                   for h in range(len(rows))]
        expected = 1 << (len(names) - len(rows) + 1)
        assert size == (0 if odd else expected) and deleted == [expected] * len(rows)
        if len(names) > 20:
            raise ValueError("Use the registered rank-only representation for this observed width.")
        words = literal_words(masks, sign, len(names))
        assert len(words) == size
        if not odd:
            even_words = words
        deletion_checks = []
        for h in range(len(rows)):
            remain = literal_words(masks[:h] + masks[h+1:], sign[:h] + sign[h+1:], len(names))
            assert len(remain) == deleted[h]
            deletion_checks.append({"holder": ids[h], "global_word_count": len(remain),
                                    "least_completion": min(remain)})
        standalone = check_knot([rows[closing]], [odd], rows[closing])
        ambient = check_knot(rows, sign, rows[closing])
        assert standalone["binding"] and standalone["loss_on_erasure"] and standalone["coexistence"]
        assert ambient["coexistence"] == (not odd)
        result["odd" if odd else "even"] = {
            "polarities": sign, "admitted_complete_words": size, "word_integers": words,
            "per_deleted_physical_rule": deletion_checks,
            "closing_rule_in_isolation": standalone, "closing_projection_in_full_whole": ambient,
        }
    pre = literal_words(masks[:-1], signs[0][:-1], len(names))
    assert pre == even_words
    holder_values = Counter(local_word(w, local_rows[closing]) for w in pre)
    assert set(holder_values) == {a for a in range(1 << len(rows[closing])) if a.bit_count() % 2 == 0}
    result["before_closure"] = {
        "old_state_count": len(pre),
        "input_word_multiplicities_in_local_slot_order": [holder_values[a] for a in range(1 << len(rows[closing]))],
        "each_old_word_even_extensions": 1, "each_old_word_single_odd_extensions": 0,
        "ordinary_zero_grant": raw["fresh"], "no_ordinary_answer_trigger_in_roster": True,
        "closed_odd_post_step_trial_count": 0,
    }
    return rows, local_rows, names, ends, closing, even_words, result


def projector_coefficients(ops, outcome):
    # Numerator of the joint projector multiplied by 2 to the power of its arity.
    # Each commuting product is Hermitian; the trace with itself is its dimension.
    terms = Counter()
    for selection in range(1 << len(ops)):
        value = IDENTITY
        for i, op in enumerate(ops):
            if selection & (1 << i):
                value = pauli_product(value, op)
        phase, x, z = value
        canonical_phase = (x & z).bit_count() % 4
        residual = (phase - canonical_phase) % 4
        assert residual in (0, 2)
        exponent = (residual // 2 + (selection & outcome).bit_count()) % 2
        terms[x, z] += (-1) ** exponent
    return {key: value for key, value in terms.items() if value}


def compressed_table(data, left_size, right_size):
    denominator = lcm(*(q.denominator for q in data.values())) if data else 1
    nums = [int(data.get((a, b), 0) * denominator)
            for a, b in product(range(left_size), range(right_size))]
    assert min(nums) >= 0 and sum(nums) == denominator
    return {"shape": [left_size, right_size], "denominator": denominator, "numerators": nums}


def signed_settings(rows, local_rows, names, ends, closing, even_words):
    name_index = {v: i for i, v in enumerate(names)}
    operator = pauli_solution(ends, {closing})
    assert operator is not None
    verify_paulis(ends, operator, {closing})
    powers = max((x | z).bit_length() for _, x, z in operator)
    coefficients = [[projector_coefficients([operator[name_index[name]] for name in row], word)
                     for word in range(1 << len(row))] for row in rows]
    stats = {}
    encoded = {}
    for sign in ("even", "odd"):
        odd_at = closing if sign == "odd" else None
        # This second construction works on the actual named physical word carrier.
        device = measurement.compile_device(rows, measurement.law(rows, odd=odd_at))
        assert device.status == "ready" and (sign != "odd" or not device.diagonal)
        reader = measurement.QuantumReader(device, source="ordinary" if sign == "even" else "coherent")
        verification = measurement.check_returned_operations(device)
        left_laws, right_laws = {}, {}
        settings = []
        total_support = 0
        all_cells = 0
        common_checks = 0
        shapes = Counter()
        positivity = Counter()
        independently_equal = 0
        for h, k in product(range(len(rows)), repeat=2):
            left, right = rows[h], rows[k]
            shape = (1 << len(left), 1 << len(right))
            counts = Counter()
            if sign == "even":
                raw = Counter((local_word(w, local_rows[h]), local_word(w, local_rows[k])) for w in even_words)
                counts.update({pair: Fraction(n, len(even_words)) for pair, n in raw.items()})
            else:
                for (a, first), (b, second) in product(enumerate(coefficients[h]), enumerate(coefficients[k])):
                    numerator = sum(value * second.get(key, 0) for key, value in first.items())
                    if numerator:
                        counts[a, b] = Fraction(numerator, shape[0] * shape[1])
            second_path = measurement.joint_table(reader, h, k)
            assert counts == second_path
            independently_equal += shape[0] * shape[1]
            shared = sorted(set(left) & set(right))
            left_margin, right_margin = Counter(), Counter()
            for (a, b), prob in counts.items():
                assert prob > 0
                assert a.bit_count() % 2 == (h == odd_at) and b.bit_count() % 2 == (k == odd_at)
                for name in shared:
                    assert (a >> left.index(name)) & 1 == (b >> right.index(name)) & 1
                    common_checks += 1
                left_margin[a] += prob
                right_margin[b] += prob
            assert sum(counts.values()) == 1
            assert left_margin == left_laws.setdefault(h, left_margin)
            assert right_margin == right_laws.setdefault(k, right_margin)
            assert len(left_margin) == 1 << (len(left) - 1) and len(set(left_margin.values())) == 1
            assert len(right_margin) == 1 << (len(right) - 1) and len(set(right_margin.values())) == 1
            setting_type = "same" if h == k else ("different_sharing" if shared else "disjoint")
            shapes[setting_type] += 1
            positivity[(setting_type, len(counts))] += 1
            settings.append({"holders": [h, k], "common_names": shared,
                             **compressed_table(counts, *shape)})
            total_support += len(counts)
            all_cells += shape[0] * shape[1]
        repeat = {}
        for h, row in enumerate(rows):
            mass = Fraction()
            repeats = Counter()
            for first, idle, p, after in reader.step(reader.start(), h, None):
                for again, second_idle, q, later in reader.step(after, h, None):
                    assert idle is second_idle is None and again == first
                    mass += p*q
                    repeats[first] += p*q
            assert mass == 1 and repeats == left_laws[h]
            repeat[h] = str(mass)
        keeper = {}
        for policy in ("not_ready", "disconnected", "write"):
            mode = measurement.QuantumReader(device, source="ordinary" if sign == "even" else "coherent",
                                             writer=(policy, "write"))
            resolved = Counter()
            captured = {}
            for record, remote, weight, after in mode.step_detailed(mode.start(), closing, None):
                assert remote.status == "idle"
                local = mode.physical_fields(record, 0)
                bits = local["displayed_bit_holders"]
                if policy == "write":
                    word = record.displayed_word
                    assert record.status == "success" and local["physical_write"] == measurement.ONE
                    assert bits == tuple(measurement.latch_write((word >> i) & 1)[0] for i in range(len(rows[closing])))
                else:
                    word = None
                    assert local["physical_write"] == measurement.ZERO
                    assert bits == (measurement.READY,) * len(rows[closing])
                resolved[str(word)] += weight
                captured[str(word)] = {"status": record.status, "external_keeper_words":
                                       [format(w, "03b") for w in bits], "swap_at_used_places": record.fired_pairs}
            assert sum(resolved.values()) == 1
            keeper[policy] = {key: {**captured[key], "probability": str(v)} for key, v in resolved.items()}
        supervisor = measurement.QuantumReader(device, force_refusal=True)
        refused = list(supervisor.step_detailed(supervisor.start(), closing, closing))
        assert len(refused) == 1
        first, second, probability, missing = refused[0]
        assert probability == 1 and first.status == second.status == "no_source"
        assert first.latch_words == second.latch_words == (measurement.READY,) * len(rows[closing])
        keeper["external_failed_intake"] = {
            "external_status": first.status,
            "delivered_words":[first.displayed_word,second.displayed_word],
            "external_registers_per_side":[format(w,"03b") for w in first.latch_words],
            "physical_post_step_reader_in_the_empty_odd_ordinary_whole":False}
        encoded[sign] = settings
        stats[sign] = {
            "settings": len(settings), "settings_kind": shapes,
            "positive_cells": total_support, "all_cells": all_cells, "different_implementations_equal_cells": independently_equal,
            "positive_count_per_setting_by_kind": {f"{kind} {count}": freq for (kind,count), freq in positivity.items()},
            "support_sizes_by_holder": [len(left_laws[h]) for h in range(len(rows))],
            "local_answer_bits_entropy_per_holder": [len(row)-1 for row in rows],
            "remote_law_maximum_total_variation": "0", "checked_shared_bit_identities_on_nonzero_cells": common_checks,
            "full_same_holder_immediate_repeat": repeat,
            "named_carrier": {"allowed_before_signed_measurement": len(device.carrier), "source_acceptance": str(reader.acceptance),
                              "literal_physical_word_operations": verification,
                              "flips_in_increasing_physical_name_positions": device.flips, "signs": device.signs},
            "external_keeper_at_actual_closing_holder": keeper,
        }
    distinguish = {}
    combined = Fraction()
    for e, o in zip(encoded["even"], encoded["odd"], strict=True):
        assert (e["holders"],e["shape"]) == (o["holders"],o["shape"])
        h,k = e["holders"]
        discrepancy = sum(abs(Fraction(a,e["denominator"]) - Fraction(b,o["denominator"]))
                          for a,b in zip(e["numerators"], o["numerators"], strict=True)) / 2
        distinguish[f"{h},{k}"] = str(discrepancy)
        combined += discrepancy
    # Each complete local law is uniform on its parity class.
    # Verify its two proper marginal readings explicitly at every subset of named places.
    terminal_counts = []
    for odd in (0,1):
        allowed = [word for word in range(1 << len(rows[closing])) if word.bit_count() % 2 == odd]
        partials = {}
        for size in range(len(rows[closing])):
            for fields in combinations(range(len(rows[closing])), size):
                partials[fields] = Counter(local_word(word,fields) for word in allowed)
        terminal_counts.append(partials)
    assert terminal_counts[0] == terminal_counts[1]
    distance = combined / len(distinguish)
    return {"pauli_exponent_convention": "i^p X^x Z^z", "operator_tensor_bits": powers,
            "odd_sign_at_holder": closing, "operator_exponents_by_name": dict(zip(names, operator, strict=True)),
            "both_inputs_independent_uniform": f"1/{len(rows)**2}", "response_summary":stats,
            "sign_distinction_under_the_two_supplied_preparations":{
                "terminal_instrument_full_local_total_variation":"1",
                "terminal_proper_subreadings_checked":len(terminal_counts[0]),
                "terminal_proper_subreading_total_variation":"0",
                "total_variation_including_known_random_settings":str(distance),
                "all_settings_total_variation":distinguish,
                "best_joint_equal_prior_success_on_this_supplied_experiment":str((1+distance)/2)},
            "every_pair_exact_table":encoded}


def negative_check(case):
    import networkx as nx
    ids = case["component_holders"]
    rows = [case["after_rows"][h] for h in ids]
    names, masks = named_masks(rows)
    ends = [tuple(h for h, row in enumerate(rows) if name in row) for name in names]
    assert all(len(pair) == 2 for pair in ends)
    closing = ids.index(case["holder"])
    simple = nx.Graph(ends)
    planar, embedding = nx.check_planarity(simple)
    assert planar and pauli_solution(ends, {closing}) is None
    embedding.check_structure()
    even = affine_count(masks, [0]*len(rows), len(names))
    odd = affine_count(masks, [h == closing for h in range(len(rows))], len(names))
    assert even and not odd
    disjoint = next(((h,k) for h in range(len(rows)) for k in range(h+1,len(rows))
                     if not (set(rows[h]) & set(rows[k]))), None)
    separate = None
    if disjoint and len(names) <= 20:
        places = {name:i for i,name in enumerate(names)}
        h, k = disjoint
        a, b = [tuple(places[name] for name in rows[j]) for j in (h,k)]
        cnt = Counter((local_word(word,a), local_word(word,b)) for word in literal_words(masks, [0]*len(rows), len(names)))
        separate = {"actual_holders":[ids[h],ids[k]], "all_even":compressed_table(
            {key:Fraction(n,even) for key,n in cnt.items()}, 1 << len(a), 1 << len(b)),
            "odd":"strict preparation refused before either holder is requested"}
    return {"panel":case["panel"],"draw":case["draw"],"age":case["age"],"holders":ids,"component_place_names":names,
            "terminal":case["holder"],"ordinary_even_words":even,"ordinary_single_odd_words":odd,
            "operator_single_odd":False,"verified_cyclic_neighbor_orders":embedding.get_data(),
            "one_disjoint_pair_when_available":separate}


def positive_grant_check(case):
    before, after = case["before_rows"], case["after_rows"]
    holder = case["holder"]
    old_names = set().union(*map(set,before))
    new_names = set(after[holder]) - old_names
    assert len(new_names) == case["fresh"] > 0
    assert all(sum(name in row for row in after) == 1 for name in new_names)
    names, masks = named_masks(after)
    zero = affine_count(masks, [0]*len(after), len(names))
    changed = affine_count(masks, [i == holder for i in range(len(after))], len(names))
    before_names, before_masks = named_masks(before)
    prior_count = affine_count(before_masks, [0]*len(before), len(before_names))
    assert zero == changed > 0 and zero % prior_count == 0
    return {"panel":case["panel"],"draw":case["draw"],"age":case["age"],"holder":holder,"parents":case["parents"],
            "old_input_names":sorted(set(after[holder]) & old_names),"fresh_names":sorted(new_names),
            "chosen_fresh_coordinate_in_bijection":min(new_names),"prior_count":prior_count,
            "native_word_count":zero,"same_cut_with_this_sign_reversed":changed,
            "extensions_per_old_word_for_full_cut_at_either_sign":zero//prior_count,
            "local_extensions_per_given_old_input_at_either_sign":1 << (len(new_names)-1)}


def nae_comparison(case, parity_rows, closing):
    older = tuple(map(tuple,case["source_rows"]))
    history = []
    for age in range(1,case["age"]+1):
        status,current,births = advance(older,"nae")
        history.append({"age":age,"status":status,"names_before":len(set().union(*map(set,older))),
                        "new_rows":current[len(older):],
                        "births":[{"parents":parents,"fresh":fresh} for parents,fresh in births]})
        if status != "births":
            break
        older = current
    names, masks = named_masks(older)
    assert len(names) <= 20, "use an exact model counter if the selected matched cut exceeds width twenty"
    words = [w for w in range(1 << len(names)) if all((w & m) not in (0,m) for m in masks)]
    assert words
    parity_names, arrangement = named_masks(parity_rows)
    on_same_arrangement = [w for w in range(1 << len(parity_names))
                           if all((w & m) not in (0,m) for m in arrangement)]
    return {"same_initial_physical_names":case["source_rows"],"unsigned_growth_history":history,
            "unsigned_count_on_its_own_reached_cut":len(words),
            "unsigned_count_reinterpreting_the_closed_parity_holdings":len(on_same_arrangement),
            "reinterpreted_cut_was_an_ordinary_NAE_birth_at_that_step":list(map(list,older))==list(map(list,parity_rows)),
            "signed_admission":"inapplicable to the unsigned rule"}


def canonical_keeper():
    laws = {}
    for label,cnf in (("parity","a b -c;a -b c;-a b c;-a -b -c"),("nae","a b c;-a -b -c")):
        result = json.loads(subprocess.check_output(
            [sys.executable,"-B","-m","knotlab","check","--cnf",cnf,"--loops","a","b","--contact","c","--json"],
            cwd=ROOT,env={**os.environ,"PYTHONPATH":str(ROOT/"tools")}))
        assert result["binding"] and result["loss_on_erasure"] and result["coexistence"]
        laws[label]=result["allowed"]
    for bit in (0,1):
        new,swaps=measurement.latch_write(bit)
        assert (measurement.READY ^ sum(1 << (2-i) for i in swaps)) == new
        assert all(format(new,"03b") in allowed and "110" in allowed for allowed in laws.values())
    return {"physical_ternary_allowed_words":laws,"ready":"110","copied_zero":"101","copied_one":"011",
            "without_supplied_outcome_trigger":"110","outside_sampled_source":True,
            "ordinary_empty_odd_post_step_reader":"no complete state, no probability distribution or physical failure keeper",
            "supplied_failed_intake_status":"no_source; the external supervisor and previously prepared keeper are supplied"}


def disjoint_exposure(case):
    """An ordered disjoint setting at each available positive primary-panel minimum."""
    ids = case["component_holders"]
    rows = [tuple(case["after_rows"][h]) for h in ids]
    closing = ids.index(case["holder"])
    other = next((h for h,row in enumerate(rows) if not (set(row) & set(rows[closing]))), None)
    if other is None:
        return {"physical_holders":ids,"disjoint_from_closing_holder":[]}
    names,masks = named_masks(rows)
    place = {name:i for i,name in enumerate(names)}
    ends = [tuple(i for i,row in enumerate(rows) if name in row) for name in names]
    operator = pauli_solution(ends,{closing})
    assert operator is not None
    verify_paulis(ends,operator,{closing})
    axes = (rows[closing],rows[other])
    shape = tuple(1 << len(row) for row in axes)
    zero = [0]*len(rows)
    complete_count = affine_count(masks,zero,len(names))
    assert complete_count == 1 << (len(names)-len(rows)+1)
    assert not affine_count(masks,[i==closing for i in range(len(rows))],len(names))
    pins = [1 << place[e] for row in axes for e in row]
    coeffs = [[projector_coefficients([operator[place[e]] for e in row],a)
               for a in range(1 << len(row))] for row in axes]
    even, odd = {}, {}
    for a,b in product(range(shape[0]),range(shape[1])):
        fixed = [(w >> j) & 1 for w,row in zip((a,b),axes,strict=True) for j in range(len(row))]
        even[a,b] = Fraction(affine_count(masks+pins,zero+fixed,len(names)),complete_count)
        left,right = coeffs[0][a],coeffs[1][b]
        odd[a,b] = Fraction(sum(v*right.get(key,0) for key,v in left.items()),shape[0]*shape[1])
    for sign,tab in enumerate((even,odd)):
        support=[(a,b) for (a,b),p in tab.items() if p]
        assert all(a.bit_count()%2==sign and b.bit_count()%2==0 for a,b in support)
    return {"panel":case["panel"],"draw":case["draw"],"age":case["age"],"component_counts":[len(rows),len(names)],
            "whole_closed":case["whole_closed"],"ordered_physical_holder_requests":[ids[closing],ids[other]],
            "physical_places":axes,"ordinary_even_complete_words":complete_count,
            "even":compressed_table(even,*shape),"odd":compressed_table(odd,*shape)}


def main():
    witnesses=json.loads((OUTPUT/"panels_witnesses.json").read_text())
    chosen = witnesses["whole"]
    rows, locations, names, ends, closing, even_words, ordinary = read_whole(chosen)
    result={"choice":{item:chosen[item] for item in ("panel","draw","age","holder","parents","fresh")},
            "component_physical_holders":chosen["component_holders"],"physical_names_in_word_integer_order":names,
            "physical_rows_in_table_order":rows,"ordinary":ordinary,"keeper":canonical_keeper(),
            "signed":signed_settings(rows, locations, names, ends, closing, even_words),
            "sampled_controls":{"negative_odd_component":negative_check(witnesses["negative"]),
                                "actual_positive_grant":positive_grant_check(witnesses["positive_fresh"]),
                                "same_founder_under_NAE":nae_comparison(chosen,rows,closing),
                                "disjoint_settings_at_primary_positive_minima":{
                                    panel:disjoint_exposure(witnesses["panels"][panel]["component"])
                                    for panel in ("T","E","M") if witnesses["panels"][panel]["component"]}}}
    write_json("internal_receipts.json.gz",result)
    summary={**result,"signed":{k:v for k,v in result["signed"].items() if k!="every_pair_exact_table"}}
    for sign in ("even","odd"):
        del summary["ordinary"][sign]["word_integers"]
        del summary["signed"]["response_summary"][sign]["external_keeper_at_actual_closing_holder"]
    write_json("internal_summary.json",summary)
    print("selected",result["choice"],"ordinary words",len(even_words), "holder settings",len(rows)**2)


if __name__ == "__main__":
    main()
