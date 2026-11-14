"""Independent full-CNF checks of a two-block window through word depth three.

Projection construction imports only CARRY's independent raw-definition
unfolder.  It does not use transfer relations, Q iteration, or the producer's
identity partition.  No official 30-family sample is selected in this file.
"""
from __future__ import annotations

from functools import lru_cache
import hashlib
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "experiments/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/codex/brute.py"
DEFAULT_CAPS = dict(max_variables=15_000, max_clauses=100_000,
                    max_copies=25_000, max_rows=1 << 20)


@lru_cache(maxsize=1)
def load_brute():
    name = "top_info_independent_carry_brute"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, SOURCE)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load independent prerequisite: {SOURCE}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def project_word(family, word, *, entry_index=None, cutoff_depth=None,
                 max_variables=15_000, max_clauses=100_000, max_copies=25_000,
                 max_rows=1 << 20, checkpoint=lambda: None):
    """Exact projection onto the whole unfolded main block and one end block.

    s is word length and absolute end depth is s + (main != S).  The default
    cutoff includes every block through the end copy's children, with exact
    usual-limit relations below that cutoff, as in CARRY's independent check.
    Identical variables receive their first label in main[0:V], end[0:V].
    """
    brute = load_brute()
    word = tuple(word)
    caps = dict(max_variables=max_variables, max_clauses=max_clauses,
                max_copies=max_copies, max_rows=max_rows)
    try:
        prep = brute.prepare_family(family)
        target_depth = len(word) + int(prep.main != prep.S)
        cutoff = target_depth + 1 if cutoff_depth is None else int(cutoff_depth)
        if cutoff < target_depth:
            raise brute.ComputationAmbiguity("cutoff_depth does not include the selected end block")
        pattern = brute.unfold_pattern(prep, cutoff, target_depth=target_depth, word=word,
                                       entry_index=entry_index, max_variables=max_variables,
                                       max_clauses=max_clauses, max_copies=max_copies)
        if pattern["end"] is None:
            raise brute.ComputationAmbiguity("explicit unfolding has no selected covered S copy")
        main_copy = pattern["copies"][0]
        if main_copy["address"] or main_copy["definition"] != prep.main:
            raise AssertionError("the first unfolded block is not main")
        top_variables = tuple(main_copy["ports"]) + tuple(main_copy["own"])
        end_variables = tuple(pattern["end"])
        width = len(top_variables)
        actual_to_label, label_to_actual = {}, {}
        main_aliases, end_aliases = [], []
        for symbol, actual in list(enumerate(top_variables)) + [
                (width + v, actual) for v, actual in enumerate(end_variables)]:
            if actual not in actual_to_label:
                actual_to_label[actual] = symbol
                label_to_actual[symbol] = actual
            if symbol < width:
                main_aliases.append(actual_to_label[actual])
            else:
                end_aliases.append(actual_to_label[actual])
        checkpoint()
        labels = sorted(label_to_actual)
        allowed = brute.enumerate_projection(pattern["clauses"], pattern["n"],
                                             tuple(label_to_actual[label] for label in labels),
                                             max_rows=max_rows)
        checkpoint()
        return dict(status="ok", word=list(word), s=len(word), depth=target_depth,
                    cutoff_depth=cutoff, blocks_through_cutoff_inclusive=True,
                    entry_index=pattern["entry_index"], main=prep.main, S=prep.S,
                    labels=labels, main_aliases=main_aliases, end_aliases=end_aliases,
                    root_labels=main_aliases[:len(pattern["roots"])],
                    own_labels=sorted(set(end_aliases[pattern["end_flat"]["k"]:])),
                    top_width=width, root_width=len(pattern["roots"]),
                    same_copy=prep.main == prep.S and not word,
                    allowed=allowed, variables=pattern["n"], clauses=len(pattern["clauses"]),
                    copies=len(pattern["copies"]), limits=caps, backend="glucose42",
                    usual_limit_alive=prep.alive)
    except brute.ComputationAmbiguity as exc:
        return dict(status="not_computed", reason=str(exc), word=list(word), limits=caps)
    except brute.CalculationCap as exc:
        return dict(status="cap", cap=exc.record(), word=list(word), limits=caps)


def minimum_bond(projection, checkpoint=lambda: None):
    """Independent set-based K1--K3 check on the enumerated CNF relation."""
    labels, allowed = projection["labels"], projection["allowed"]
    if not allowed:
        raise ValueError("an empty independent projection has no living bond")
    indices = {label: j for j, label in enumerate(labels)}
    roots, own = set(projection["root_labels"]), set(projection["own_labels"])
    cache = {}

    def full(support):
        if support not in cache:
            rows = {tuple((row >> indices[label]) & 1 for label in support) for row in allowed}
            cache[support] = len(rows) == 2 ** len(support)
        return cache[support]

    for size in range(2, min(6, len(labels)) + 1):
        for support in combinations(labels, size):
            if not roots.intersection(support) or not own.intersection(support):
                continue
            checkpoint()
            if full(support):
                continue
            if all(full(tuple(label for label in support if label != removed)) for removed in support):
                return size
    return "> 6"


def _signature(projection):
    payload = {name: projection[name] for name in
               ("labels", "main_aliases", "end_aliases", "root_labels", "own_labels", "allowed")}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _compare_rows(produced, independent):
    names = ("labels", "main_aliases", "end_aliases", "root_labels", "own_labels", "allowed")
    failures = [name for name in names if produced[name] != independent[name]]
    result = dict(passed=not failures, differing_fields=failures,
                  produced_sha256=_signature(produced), independent_sha256=_signature(independent),
                  produced_allowed_count=len(produced["allowed"]),
                  independent_allowed_count=len(independent["allowed"]))
    if "allowed" in failures:
        produced_rows, independent_rows = set(produced["allowed"]), set(independent["allowed"])
        result["first_missing_rows"] = sorted(independent_rows - produced_rows)[:5]
        result["first_extra_rows"] = sorted(produced_rows - independent_rows)[:5]
    return result


def compare_family(key, *, max_s=3, checkpoint=lambda: None, **cap_overrides):
    """Check all covered words and every direct wrapper entry for this family.

    This callable deliberately accepts a family rather than selecting an
    official sample: the frozen preregistration does not define brute30's
    population or sampling order.  Capped checks remain unknown.
    """
    if not isinstance(max_s, int) or isinstance(max_s, bool) or not 0 <= max_s <= 3:
        raise ValueError("the bounded comparison permits max_s from zero through three")
    unknown_caps = set(cap_overrides) - set(DEFAULT_CAPS)
    if unknown_caps:
        raise ValueError(f"unknown independent projection caps: {sorted(unknown_caps)}")
    caps = dict(DEFAULT_CAPS, **cap_overrides)
    # Producer imports belong to this comparison wrapper only.  project_word
    # and minimum_bond above remain independently callable without them.
    import two_block
    deps = two_block.load_dependencies()
    brute = load_brute()
    budget = deps.Limits(two_block.SECONDS, two_block.MEMORY_BYTES)

    def tick():
        budget.checkpoint()
        checkpoint()

    result = dict(key=key, max_s=max_s, complete=False, passed=False, checks=[],
                  caps=[], ambiguities=[], limits=caps, all_direct_entries=True,
                  depth_convention="s is word length; absolute depth is s + wrapper shift")
    try:
        prep = two_block.prepare(key)
        independent_prep = brute.prepare_family(key)
        body = two_block.body_allowed(prep, prep.S, checkpoint=tick)
        calls = deps.relations.per_call(prep, tick)
        independent_calls = [callee for callee, _ in independent_prep.flat(independent_prep.S)["calls"]
                             if callee == independent_prep.S]
        if len(calls) != len(independent_calls):
            raise AssertionError("producer and independent S-call alphabets have different sizes")
        if prep.main == prep.S:
            entries = [None]
        else:
            entries = list(range(sum(callee == prep.S for callee, _ in prep.flat(prep.main)["calls"])))
            if not entries:
                result["ambiguities"].append("main has no direct S entry under the covered-copy convention")
                return result
        result["wrapper"] = prep.main != prep.S
        result["expected_checks"] = len(entries) * sum(len(calls) ** s for s in range(max_s + 1))
        for s in range(max_s + 1):
            for entry in entries:
                for word in product(range(len(calls)), repeat=s):
                    tick()
                    independent = project_word(independent_prep, word, entry_index=entry,
                                               checkpoint=tick, **caps)
                    check = dict(s=s, depth=s + int(prep.main != prep.S), word=list(word),
                                 entry_index=entry, status=independent["status"], passed=False)
                    if independent["status"] != "ok":
                        check.update({name: independent[name] for name in ("cap", "reason") if name in independent})
                        result["checks"].append(check)
                        if independent["status"] == "cap":
                            result["caps"].append(dict(word=list(word), entry_index=entry, **independent["cap"]))
                        else:
                            result["ambiguities"].append(independent["reason"])
                        continue
                    produced = two_block.project_word(prep, word, entry_index=entry, calls=calls,
                                                       body=body, checkpoint=tick)
                    check["projection"] = _compare_rows(produced, independent)
                    independent_minimum = minimum_bond(independent, tick)
                    produced_minimum = two_block.bond_from_projection(produced, tick)["U2"]
                    check["minimum"] = dict(passed=independent_minimum == produced_minimum,
                                             independent=independent_minimum, produced=produced_minimum)
                    old_state = deps.window.start_state(prep, entry)
                    for letter in word:
                        old_state = deps.window.step(old_state, calls[letter], prep.k)
                    old_projection = deps.window.project_state(prep, old_state, body)
                    check["port_only"] = _compare_rows(two_block.port_only_projection(produced), old_projection)
                    check["passed"] = all(check[name]["passed"] for name in ("projection", "minimum", "port_only"))
                    check["variables"] = independent["variables"]
                    check["clauses"] = independent["clauses"]
                    check["copies"] = independent["copies"]
                    result["checks"].append(check)
        result["complete"] = (len(result["checks"]) == result["expected_checks"] and
                              all(check["status"] == "ok" for check in result["checks"]))
        result["passed"] = result["complete"] and all(check["passed"] for check in result["checks"])
    except (two_block.InputAmbiguity, brute.ComputationAmbiguity) as exc:
        result["ambiguities"].append(str(exc))
    except deps.LimitReached as exc:
        result["caps"].append(str(exc))
    except brute.CalculationCap as exc:
        result["caps"].append(exc.record())
    except MemoryError:
        result["caps"].append("Python MemoryError")
    finally:
        result.update(budget.metrics())
    return result
