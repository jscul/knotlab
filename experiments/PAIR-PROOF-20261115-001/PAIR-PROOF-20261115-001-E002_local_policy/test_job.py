"""Synthetic runner checks only; never open training or blind study artifacts."""
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "job.py"
MODES = ("ordinary", "compact", "no-proof", "balanced", "fixed", "same-menu", "learned")
FIELDS = {"n", "upstream_count", "gates", "frontier", "outputs", "pieces"}


def new_job():
    name = "_pair_e002_synthetic_job"
    spec = importlib.util.spec_from_file_location(name, SOURCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def dump(path, value):
    path.write_text(json.dumps(value))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public_rows():
    return [dict(id=name, n=3, upstream_count=0, gates=[], frontier=[0, 1, 2],
                 outputs=[0, 0], pieces=[], seed="ignored-by-policy", role="never-pass",
                 edits=[dict(id="a", gate=5, pin=0, to=0, role="never-pass"),
                        dict(id="b", gate=5, pin=1, to=1, role="never-pass")])
            for name in ("p", "q")]


def prepare(destination, modes=MODES, rows=None):
    (destination / "blind").mkdir()
    public = destination / "blind/public.json"
    broken, model = destination / "broken.json", destination / "model.json"
    dump(public, rows if rows is not None else public_rows())
    dump(broken, {"p": "b", "q": "a"})
    dump(model, {"synthetic_weights": [1, -1]})
    design = dict(cpu=min(os.sched_getaffinity(0)), sources={str(SOURCE): sha(SOURCE)},
                  data={str(path): sha(path) for path in (public, broken, model)},
                  model=str(model), arms={name: dict(mode=name) for name in modes})
    dump(destination / "design.json", design)
    return design


def receipt(destination, result):
    with gzip.open(destination / result["file"], "rt") as file:
        return [json.loads(line) for line in file]


class MockRuntime:
    def __init__(self, testcase, failure=False):
        self.testcase, self.events, self.failure = testcase, [], failure
        outer = self

        class Parent:
            def __init__(self, original):
                testcase.assertEqual(set(original), FIELDS)
                outer.events.append(("parent", original))

            def edit(self, edit):
                testcase.assertEqual(set(edit), {"gate", "pin", "to"})
                outer.events.append(("edit", edit))
                return types.SimpleNamespace(edit=edit)

        class Checker:
            def __init__(self, case, **kwargs):
                outer.events.append(("checker", kwargs))

            def verify(self, edit, answer):
                outer.events.append(("verify", edit))
                return dict(exact=True)

        self.Parent, self.Checker = Parent, Checker
        self.policy = types.SimpleNamespace(propose=self.propose, fixed_actions=self.fixed_actions)

    def propose(self, model, original, edit):
        self.testcase.assertEqual(model, {"synthetic_weights": [1, -1]})
        return self._actions(original, edit)

    def fixed_actions(self, original, edit):
        return self._actions(original, edit)

    def _actions(self, original, edit):
        self.testcase.assertEqual(set(original), FIELDS)
        self.testcase.assertEqual(set(edit), {"gate", "pin", "to"})
        self.events.append(("propose", edit))
        if self.failure and edit["pin"] == 0:
            raise RuntimeError("synthetic inference failure")
        return [[0, 1, 0, 7]]

    def stage(self):
        return dict(status="exact", n=3, triple=[0, 1, 2], width=1, class_count=2,
                    summary_wires=[0], circuit=dict(n=3, gates=[], outputs=[0, 0]))

    def ordinary(self, state):
        self.events.append(("ordinary", state))
        return self.stage(), dict(primitive_work=1)

    def solve(self, state, mode, history=None, actions=None):
        self.events.append(("solve", mode, history, actions))
        return self.stage(), dict(proof_work=1)

    def attach(self, original, stage):
        return {**stage, "physical": dict(n=3, gates=[], outputs=[0, 0], summary_wires=[0], frontier=[0, 1, 2])}

    def imports(self, mode):
        return self.Parent, self.attach, self.Checker, self.ordinary, self.solve


class RunnerChecks(unittest.TestCase):
    def test_complete_paired_order_and_no_setup_solver_import(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            prepare(dest)
            module = new_job()
            with patch.object(module, "_imports", side_effect=AssertionError("setup imported solver")):
                module.setup(dict(data_dir=str(dest)))
            cases = list(module.cases())
            self.assertEqual(len(cases), 8 * 2 * 7)
            self.assertEqual(len({key for key, _ in cases}), len(cases))
            for block in range(8):
                for panel in ("mixed", "broken"):
                    group = [payload for _, payload in cases if payload["block"] == block and payload["panel"] == panel]
                    self.assertEqual({payload["arm"] for payload in group}, set(MODES))

    def test_routing_paid_model_and_stripped_upfront_policy(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            prepare(dest)
            for mode in MODES:
                with self.subTest(mode=mode):
                    module = new_job()
                    module.setup(dict(data_dir=str(dest), arms=mode, panels="mixed", count="1"))
                    runtime = MockRuntime(self)
                    with patch.object(module, "pin"), patch.object(module, "_imports", runtime.imports), \
                            patch.object(module, "_policy_import", return_value=runtime.policy), \
                            patch.object(module, "load", wraps=module.load) as reads:
                        result = module.run("mixed-0-" + mode, dict(panel="mixed", block=0, arm=mode))
                    rows = receipt(dest, result)
                    self.assertEqual(result["failures"], 0)
                    self.assertEqual((result["parents"], result["edits"]), (2, 4))
                    self.assertTrue(result["cpu_ns"] > 0 and result["wall_ns"] > 0)
                    paths = [Path(call.args[0]) for call in reads.call_args_list]
                    self.assertEqual(paths.count(dest / "blind/public.json"), 1)
                    self.assertEqual(paths.count(dest / "model.json"), int(mode == "learned"))
                    children = [child for row in rows for child in row["edits"]]
                    self.assertEqual(sum("propose" in child["phases"] for child in children),
                                     4 if mode in ("learned", "same-menu") else 0)
                    if mode in ("learned", "same-menu"):
                        labels = [event[0] for event in runtime.events if event[0] in ("propose", "edit")]
                        self.assertEqual(labels, ["propose", "edit"] * 4)
                    for event in runtime.events:
                        if event[0] == "solve":
                            self.assertEqual(event[1], "fresh" if mode == "fixed" else
                                             "advice" if mode in ("learned", "same-menu") else mode)

    def test_offline_filter_reversal_and_failure_retention(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            prepare(dest)
            module = new_job()
            module.setup(dict(data_dir=str(dest), arms="learned", panels="broken", begin="1", count="1"))
            runtime = MockRuntime(self, failure=True)
            with patch.object(module, "pin"), patch.object(module, "_imports", runtime.imports), \
                    patch.object(module, "_policy_import", return_value=runtime.policy):
                result = module.run("broken-1-learned", dict(panel="broken", block=1, arm="learned"))
            rows = receipt(dest, result)
            self.assertEqual([(row["id"], [child["id"] for child in row["edits"]]) for row in rows],
                             [("q", ["a"]), ("p", ["b"])])
            self.assertEqual(result["failures"], 1)
            self.assertIn("synthetic inference failure", rows[0]["edits"][0]["failure"])

    def test_hash_failures_and_private_grade_guard(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            design = prepare(dest)
            design["data"][str(dest / "model.json")] = "0" * 64
            dump(dest / "design.json", design)
            module = new_job()
            with patch.object(module, "sha", wraps=module.sha) as hashes:
                with self.assertRaisesRegex(ValueError, "frozen model"):
                    module.setup(dict(data_dir=str(dest)))
            self.assertNotIn(dest / "blind/public.json", [Path(call.args[0]) for call in hashes.call_args_list])
            design["data"][str(dest / "model.json")] = sha(dest / "model.json")
            design["data"][str(dest / "blind/grades.json")] = "0" * 64
            dump(dest / "design.json", design)
            with self.assertRaisesRegex(ValueError, "private grades"):
                new_job().setup(dict(data_dir=str(dest)))

    def test_one_case_per_process_without_unrelated_job_rejection(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            prepare(dest)
            module = new_job()
            module.setup(dict(data_dir=str(dest), arms="no-proof", panels="mixed", count="1"))
            runtime = MockRuntime(self)
            with patch.object(module, "pin"), patch.object(module, "_imports", runtime.imports), \
                    patch.dict(sys.modules, {"job": types.ModuleType("unrelated_job")}):
                payload = dict(panel="mixed", block=0, arm="no-proof")
                module.run("mixed-0-no-proof", payload)
                with self.assertRaisesRegex(RuntimeError, "fresh worker"):
                    module.run("mixed-0-no-proof", payload)

    def test_real_fresh_process_physical_smoke(self):
        # Two tiny synthetic parent circuits, not study examples.  Each edit
        # rewrites a pin to its current source; this checks physical plumbing.
        n, gates = 4, []
        def nand(a, b):
            gates.append([a, b])
            return n + 1 + len(gates)
        def xor(a, b):
            h = nand(a, b)
            return nand(nand(a, h), nand(b, h))
        parity = xor(xor(0, 1), 2)
        first = xor(parity, 3)
        h = nand(parity, 3)
        second = nand(h, h)
        gate = n + 1 + len(gates)
        rows = [dict(id=name, n=n, upstream_count=0, gates=gates, frontier=list(range(n)),
                     outputs=[first, second], pieces=[],
                     edits=[dict(id="a", gate=gate, pin=0, to=gates[-1][0]),
                            dict(id="b", gate=gate, pin=1, to=gates[-1][1])]) for name in ("p", "q")]
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            prepare(dest, modes=("no-proof",), rows=rows)
            completed = subprocess.run([sys.executable, "-B", str(SOURCE), "--data-dir", str(dest),
                                        "--panel", "mixed", "--arm", "no-proof", "--block", "0"],
                                       check=True, capture_output=True, text=True)
            result = json.loads(completed.stdout)
            self.assertEqual((result["parents"], result["edits"], result["failures"]), (2, 4, 0))
            for row in receipt(dest, result):
                for child in row["edits"]:
                    self.assertTrue(child["check"]["exact"])


if __name__ == "__main__":
    unittest.main()
