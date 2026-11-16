"""Specified threshold-only adaptation of the census job.py compute function."""
import ast
import hashlib
import json
from pathlib import Path
import time

from reuse import SOURCE, pattern, certificates as cert, search
from retention import context


def _load_census_compute():
    """Reuse the actual compute body; change only the requested query controls."""
    tree = ast.parse((SOURCE / 'job.py').read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'compute')
    text = ast.unparse(node)
    substitutions = [
        ('histograms=True)', 'histograms=False, k_max=3, selected_s=None)'),
        ("'k_max': 10", "'k_max': k_max"),
        ('for s in range(1, S + 1):', 'for s in (range(1, S + 1) if selected_s is None else selected_s):'),
        ('engine.search(A, B, deadline=deadline)', 'engine.search(A, B, kmax=k_max, deadline=deadline)'),
        ('target_result = engine.search(A, B, allowed=range((1 << k0 + s + 1) - 1), deadline=deadline)',
         "target_result = {'L': 'not_requested', 'reason': 'threshold-only query'}"),
    ]
    # AST unparse's parentheses are version-dependent; locate the target RHS structurally.
    for old, new in substitutions[:4]:
        if text.count(old) != 1:
            raise RuntimeError(('census compute changed: expected unique source fragment', old))
        text = text.replace(old, new)
    lines = text.splitlines()
    matches = [i for i, line in enumerate(lines) if line.strip().startswith('target_result = engine.search(')]
    if len(matches) != 1:
        raise RuntimeError('census compute changed: target search not unique')
    i = matches[0]
    lines[i] = ' ' * (len(lines[i]) - len(lines[i].lstrip())) + "target_result = {'L': 'not_requested', 'reason': 'threshold-only query'}"
    adapted = '\n'.join(lines) + '\n'
    import collections
    namespace = {'time': time, 'collections': collections,
                 'pattern': pattern.pattern, 'level_ids': pattern.level_ids, 'level': pattern.level,
                 'flags': pattern.flags, 'classes': pattern.classes,
                 'union_fate': cert.union_fate, 'SearchEngine': search.SearchEngine,
                 'verify_bond_certificate': cert.verify_bond_certificate, 'BUDGET': 300.0}
    exec(compile(adapted, str(Path(__file__).resolve()) + ':adapted_compute', 'exec'), namespace)
    return namespace['compute'], namespace, adapted


CENSUS_COMPUTE, NAMESPACE, ADAPTED_SOURCE = _load_census_compute()


def query(key, workdir, store, k0, s_values, k_max=3, budget=300):
    """Each selected s has its own deadline, with every refutation certified."""
    NAMESPACE['BUDGET'] = float(budget)
    # The census body owns the deadlines. Hook search to communicate that same
    # deadline to the retention wrapper on its internal SAT calls.
    original = search.SearchEngine.search

    def retained_search(engine, *args, **kwargs):
        with context(store, kwargs.get('deadline')):
            return original(engine, *args, **kwargs)

    search.SearchEngine.search = retained_search
    try:
        with context(store):
            result = CENSUS_COMPUTE(key, workdir, N=9, k0=k0, S=max(s_values),
                                    histograms=False, k_max=k_max, selected_s=s_values)
    finally:
        search.SearchEngine.search = original
    for row in result['levels']:
        value = row['L_N']
        row['thresholds'] = {}
        for threshold in (3, 4) if k_max == 4 else (k_max,):
            if isinstance(value, int):
                verdict = 'yes' if value <= threshold else 'no'
            elif value == 'none' or (isinstance(value, str) and value.startswith('> ')):
                verdict = 'no'
            else:
                verdict = 'undecided'
            row['thresholds'][str(threshold)] = verdict
    result['adaptation'] = {'source_job_sha256': hashlib.sha256((SOURCE / 'job.py').read_bytes()).hexdigest(),
                            'adapted_compute_sha256': hashlib.sha256(ADAPTED_SOURCE.encode()).hexdigest(),
                            'target_restricted_search': False, 'histograms': False}
    return result
