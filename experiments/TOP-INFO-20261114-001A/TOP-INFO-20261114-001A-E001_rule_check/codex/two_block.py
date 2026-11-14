"""Exact two-block windows, retaining every distinction of main's flat block.

The transferred state is (J, partition), with J a table from a whole main
assignment to the current S copy's three ports.  For main == S, depth zero
is one copy, and positive depths start by opening a call in that same main
block.  Later transfers are CARRY's unchanged exact per-call relations.
"""
from __future__ import annotations

from functools import lru_cache
import importlib
from itertools import combinations
import json
from pathlib import Path
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CARRY = ROOT / "experiments/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/codex"
SECONDS = 585
MEMORY_BYTES = 2_800_000_000
MAX_STATES = 200_000
MAX_LEVELS = 2000
MAX_SIZE = 6


class InputAmbiguity(ValueError):
    """A covered-copy convention that cannot be selected implicitly."""


@lru_cache(maxsize=1)
def load_dependencies():
    """Import prerequisite implementations read-only; never copy their data."""
    if str(CARRY) not in sys.path:
        sys.path.append(str(CARRY))
    source_inputs = importlib.import_module("inputs")
    if Path(source_inputs.__file__).resolve() != CARRY / "inputs.py":
        raise ImportError("the generic inputs module is not CARRY's prerequisite")
    paths = source_inputs.load_paths()
    source_window = importlib.import_module("window")
    if Path(source_window.__file__).resolve() != CARRY / "window.py":
        raise ImportError("the generic window module is not CARRY's prerequisite")
    limits = importlib.import_module("limits")
    return SimpleNamespace(inputs=source_inputs, window=source_window, paths=paths,
                           relations=source_inputs.load_relations(), np=source_window.np,
                           Limits=limits.Limits, LimitReached=limits.LimitReached)


def prepare(family):
    """Accept a CARRY Preparation, exact key, raw definition list, or key row."""
    if hasattr(family, "flat") and hasattr(family, "G"):
        return family
    if isinstance(family, dict):
        if "key" in family:
            family = family["key"]
        elif "defs" in family:
            family = family["defs"]
        else:
            raise ValueError("family mapping needs key or defs")
    definitions = json.loads(family) if isinstance(family, str) else family
    return load_dependencies().paths.Preparation(definitions)


def body_allowed(prep, definition=None, *, skip_call=None, checkpoint=lambda: None):
    """CARRY's full flat-block table, optionally omitting one selected call."""
    deps = load_dependencies()
    definition = prep.S if definition is None else definition
    if skip_call is None:
        result = deps.window.body_allowed(prep, definition)
        checkpoint()
        return result
    block = prep.flat(definition)
    if not 0 <= skip_call < len(block["calls"]):
        raise ValueError("selected flat call outside block")
    if (1 << block["V"]) * 40 > MEMORY_BYTES:
        raise deps.LimitReached("memory", "block truth-table allocation exceeds case memory")
    np = deps.np
    values = np.arange(1 << block["V"], dtype=np.int64)
    allowed = np.ones(len(values), dtype=bool)
    for j, (callee, arguments) in enumerate(block["calls"]):
        if j == skip_call:
            continue
        local = sum(((values >> v) & 1) << b for b, v in enumerate(arguments))
        allowed &= (deps.paths.L.NAE if callee == "K" else prep.G[callee])[local]
        checkpoint()
    return block, values[allowed]


def start_state(prep, entry_index, checkpoint=lambda: None):
    """One whole-main context per direct S-call, for wrappers and main == S."""
    deps = load_dependencies()
    main = prep.flat(prep.main)
    entries = [j for j, (callee, _) in enumerate(main["calls"]) if callee == prep.S]
    if not isinstance(entry_index, int) or isinstance(entry_index, bool) or not 0 <= entry_index < len(entries):
        raise ValueError("entry_index outside main's direct S-call ordinals")
    selected = entries[entry_index]
    arguments = main["calls"][selected][1]
    if len(arguments) != 3:
        raise ValueError("the selected S copy does not have three ports")
    _, allowed = body_allowed(prep, prep.main, skip_call=selected, checkpoint=checkpoint)
    # Each byte is the 8-state row at one exact main-block assignment.
    packed = bytearray(1 << main["V"])
    for assignment in allowed:
        value = int(assignment)
        outgoing = sum(((value >> v) & 1) << b for b, v in enumerate(arguments))
        packed[value] = 1 << outgoing
        checkpoint()
    partition = deps.window.canonical_partition(list(range(main["V"])) + list(arguments))
    return int.from_bytes(packed, "little"), partition


def start_states(prep, checkpoint=lambda: None):
    entries = [callee for callee, _ in prep.flat(prep.main)["calls"] if callee == prep.S]
    if not entries:
        raise InputAmbiguity("main has no direct S entry under the covered-copy convention")
    return tuple(start_state(prep, j, checkpoint) for j in range(len(entries)))


def step(prep, state, call):
    """Extend the exact context while retaining top identities separately."""
    return load_dependencies().window.step(state, call, prep.flat(prep.main)["V"])


def project_same_copy(prep, body=None, checkpoint=lambda: None):
    """Depth zero when main == S: both block names denote the same identities."""
    if prep.main != prep.S:
        raise ValueError("the same-copy projection requires main == S")
    block, allowed = body_allowed(prep, prep.S, checkpoint=checkpoint) if body is None else body
    labels = list(range(block["V"]))
    checkpoint()
    return dict(labels=labels, allowed=list(map(int, allowed)), main_aliases=labels,
                end_aliases=labels, root_labels=list(range(prep.k)),
                own_labels=list(range(3, block["V"])), top_width=block["V"],
                root_width=prep.k, same_copy=True)


def project_state(prep, state, body=None, checkpoint=lambda: None):
    """Exact whole-main/end-block rows with aliases merged by identity."""
    deps = load_dependencies()
    np = deps.np
    block, allowed = body_allowed(prep, prep.S, checkpoint=checkpoint) if body is None else body
    if block["k"] != 3:
        raise ValueError("the specified S does not have three ports")
    width = prep.flat(prep.main)["V"]
    joint, partition = state
    if len(partition) != width + 3 or tuple(partition[:width]) != tuple(range(width)):
        raise ValueError("state partition does not retain the complete main block")
    end_aliases = list(partition[width:]) + [width + v for v in range(3, block["V"])]
    labels = sorted(set(range(width)) | set(end_aliases))
    indices = {label: i for i, label in enumerate(labels)}
    rows = []
    port_values = allowed & 7
    for top in range(1 << width):
        exits = (joint >> (8 * top)) & 255
        if not exits:
            continue
        selected = np.array([bool(exits >> value & 1) for value in range(8)])[port_values]
        for j, alias in enumerate(partition[width:]):
            if alias < width:
                selected &= ((allowed >> j) & 1) == ((top >> alias) & 1)
            else:
                selected &= ((allowed >> j) & 1) == ((allowed >> (alias - width)) & 1)
        assignments = allowed[selected]
        packed = np.full(len(assignments), top, dtype=np.int64)
        for v, alias in enumerate(end_aliases):
            if alias >= width:
                packed |= ((assignments >> v) & 1) << indices[alias]
        # Every retained distinction occurs in labels, so this map is injective.
        for offset in range(0, len(packed), 4096):
            rows.extend(map(int, packed[offset:offset + 4096]))
            checkpoint()
        checkpoint()
    return dict(labels=labels, allowed=sorted(set(rows)), main_aliases=list(range(width)),
                end_aliases=end_aliases, root_labels=list(range(prep.k)),
                own_labels=[width + v for v in range(3, block["V"])],
                top_width=width, root_width=prep.k, same_copy=False)


def port_only_projection(projection):
    """Forget main's nonports and restore CARRY's original canonical labels."""
    roots = list(projection["root_labels"])
    width = len(roots)
    alias_to_label = {alias: j for j, alias in enumerate(roots)}
    end_aliases = []
    for v, alias in enumerate(projection["end_aliases"]):
        end_aliases.append(alias_to_label.setdefault(alias, width + v))
    labels = sorted(alias_to_label.values())
    old_indices = {label: j for j, label in enumerate(projection["labels"])}
    new_indices = {label: j for j, label in enumerate(labels)}
    rows = sorted({sum(((row >> old_indices[alias]) & 1) << new_indices[label]
                       for alias, label in alias_to_label.items()) for row in projection["allowed"]})
    return dict(labels=labels, allowed=rows, main_aliases=list(range(width)),
                end_aliases=end_aliases, root_labels=list(range(width)),
                own_labels=sorted({alias_to_label[v] for v in projection["own_labels"]}))


def bond_from_projection(projection, checkpoint=lambda: None):
    """Least K1--K3 bond through size six meeting a main port and target own."""
    deps = load_dependencies()
    np = deps.np
    labels, rows = projection["labels"], projection["allowed"]
    if not rows:
        raise ValueError("empty two-block projection in a living family")
    indices = {label: i for i, label in enumerate(labels)}
    values = np.asarray(rows, dtype=np.int64)
    roots, own = set(projection["root_labels"]), set(projection["own_labels"])
    cache = {(): True}

    def shattered(support):
        if support not in cache:
            if len(values) < 1 << len(support):
                cache[support] = False
            else:
                mapped = sum(((values >> indices[label]) & 1) << j for j, label in enumerate(support))
                cache[support] = len(np.unique(mapped)) == 1 << len(support)
        return cache[support]

    for size in range(2, min(MAX_SIZE, len(labels)) + 1):
        for support in combinations(labels, size):
            if not roots.intersection(support) or not own.intersection(support):
                continue
            checkpoint()
            if not shattered(support) and all(shattered(support[:j] + support[j + 1:]) for j in range(size)):
                return dict(U2=size, witness=list(support), allowed_count=len(rows), labels=labels)
    return dict(U2="> 6", witness=None, allowed_count=len(rows), labels=labels)


def project_word(family, word, *, entry_index=None, calls=None, body=None, checkpoint=lambda: None):
    """Project one covered word; s is CARRY's word length, before wrapper shift."""
    deps = load_dependencies()
    prep = prepare(family)
    word = tuple(word)
    calls = deps.relations.per_call(prep, checkpoint) if calls is None else calls
    if any(not isinstance(letter, int) or isinstance(letter, bool) or not 0 <= letter < len(calls)
           for letter in word):
        raise ValueError("word letter outside the S-call alphabet")
    if prep.main == prep.S:
        if entry_index not in (None, 0):
            raise ValueError("self-holding main has no wrapper entry choice")
        if not word:
            projection = project_same_copy(prep, body, checkpoint)
            state = None
        else:
            state = start_state(prep, word[0], checkpoint)
            for letter in word[1:]:
                state = step(prep, state, calls[letter])
                checkpoint()
            projection = project_state(prep, state, body, checkpoint)
    else:
        entries = [callee for callee, _ in prep.flat(prep.main)["calls"] if callee == prep.S]
        if entry_index is None:
            if len(entries) != 1:
                raise InputAmbiguity("multiple direct wrapper S entries require entry_index")
            entry_index = 0
        state = start_state(prep, entry_index, checkpoint)
        for letter in word:
            state = step(prep, state, calls[letter])
            checkpoint()
        projection = project_state(prep, state, body, checkpoint)
    return dict(projection, status="ok", word=list(word), s=len(word),
                depth=len(word) + int(prep.main != prep.S), entry_index=entry_index,
                state=None if state is None else dict(J=hex(state[0]), partition=list(state[1])))


def iterate(prep, calls, checkpoint=lambda: None, *, max_states=MAX_STATES, max_levels=MAX_LEVELS):
    """Repeat complete Q_s sets, with the same stored-state and level caps as CARRY."""
    body = body_allowed(prep, prep.S, checkpoint=checkpoint)
    levels, early, cache, seen = [], [], {}, {}
    stored = 0
    if prep.main == prep.S:
        zero = bond_from_projection(project_same_copy(prep, body, checkpoint), checkpoint)
        levels.append(dict(s=0, depth=0, states=1, U2=zero["U2"]))
        early.append(dict(s=0, same_copy=True, state=None, **zero))
        stored = 1
    current = frozenset(start_states(prep, checkpoint))
    complete, cap = False, None
    preperiod = period = None
    try:
        while current not in seen:
            if len(levels) >= max_levels or stored + len(current) > max_states:
                cap = "Q_s level cap" if len(levels) >= max_levels else "Q_s stored-state cap"
                break
            s = len(levels)
            seen[current] = s
            stored += len(current)
            minima = []
            for state in sorted(current):
                checkpoint()
                if state not in cache:
                    projection = project_state(prep, state, body, checkpoint)
                    cache[state] = bond_from_projection(projection, checkpoint)
                answer = cache[state]
                minima.append(answer["U2"])
                if s <= 3:
                    early.append(dict(s=s, same_copy=False, J=hex(state[0]),
                                      partition=list(state[1]), **answer))
            finite = [value for value in minima if isinstance(value, int)]
            levels.append(dict(s=s, depth=s + int(prep.main != prep.S), states=len(current),
                               U2=min(finite) if finite else "> 6"))
            following = set()
            for state in current:
                for call in calls:
                    following.add(step(prep, state, call))
                    if stored + len(following) > max_states:
                        cap = "Q_s construction stored-state cap"
                        break
                    checkpoint()
                if cap:
                    break
            if cap:
                break
            current = frozenset(following)
        else:
            complete = True
            preperiod = seen[current]
            period = len(levels) - preperiod
    except load_dependencies().LimitReached as exc:
        cap = str(exc)
    except MemoryError:
        cap = "Python MemoryError"
    residues = []
    if complete:
        residues = [dict(residue=j, s_mod_period=row["s"] % period, **row)
                    for j, row in enumerate(levels[preperiod:])]
    finite = [row["U2"] for row in residues if isinstance(row["U2"], int)]
    verdict = ("undecided" if not complete else "bounded" if len(finite) == period else
               "progressions" if finite else "none")
    return dict(complete=complete, cap=cap, caps=[] if cap is None else [cap], verdict=verdict,
                preperiod=preperiod, period=period, repeat_at=len(levels) if complete else None,
                levels=levels, residues=residues, maximum=max(finite) if finite else None,
                stored_states=stored, unique_states=len(cache), early_states=early,
                iteration_start_s=int(prep.main == prep.S), root_width=prep.k,
                top_width=prep.flat(prep.main)["V"], end_width=body[0]["V"])


def run_family(key, raw=None, checkpoint=lambda: None):
    """Compact exact result; raw is source metadata and never changes the key's relation."""
    deps = load_dependencies()
    budget = deps.Limits(SECONDS, MEMORY_BYTES)

    def tick():
        budget.checkpoint()
        checkpoint()

    result = dict(key=key, complete=False, caps=[], ambiguities=[], verdict="undecided",
                  levels=[], residues=[], preperiod=None, period=None,
                  limits=dict(seconds=SECONDS, memory_bytes=MEMORY_BYTES,
                              stored_states=MAX_STATES, levels=MAX_LEVELS, bond_size=MAX_SIZE))
    try:
        budget.checkpoint(True)
        prep = prepare(key)
        result["preparation"] = prep.info()
        result["wrapper"] = prep.main != prep.S
        result["start_depth"] = int(prep.main != prep.S)
        result["depth"] = dict(word_s0_copy_depth=int(prep.main != prep.S), word_length="s",
                               absolute_copy_depth="s+1" if prep.main != prep.S else "s")
        if prep.S is None or not prep.alive or not prep.G[prep.S].any():
            result["ambiguities"].append("a living reachable S is required")
            return result
        calls = deps.relations.per_call(prep, tick)
        result["R_i"] = [call["hex"] for call in calls]
        result.update(iterate(prep, calls, tick))
    except InputAmbiguity as exc:
        result["ambiguities"].append(str(exc))
    except deps.LimitReached as exc:
        result["caps"].append(str(exc))
    except MemoryError:
        result["caps"].append("Python MemoryError")
    finally:
        result.update(budget.metrics())
    return result
