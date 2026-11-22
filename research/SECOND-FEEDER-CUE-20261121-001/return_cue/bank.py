"""Bind the frozen founder sampler to the independent repaired-return bank."""

from functools import lru_cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent
SCOPE = "SECOND-FEEDER-CUE-20261121-001B"
ORIGINAL_SHA256 = {
    "bank.py": "96722d6e53665d9f89143cbb7aef099a086d89babaa79103c621cd920a419f79",
    "bank.json": "777e6f04863a7d7e1a20b638714db875cf9da141e61bc029df55e6e9c3ed2a9a",
    "learning_train.py": "ef5ff6b467cb1cacda16d31a86cfd5806b5a965ec7bf82d5ceb1c764a52a5100",
    "survival_eval.py": "d28f66d8fd9e2d9ba4694f9a9cc6ec5ddf3384372be6e4fd7a02fcf33d967651",
    "device.py": "6c65130f278deab87acd2a7365880367beb4008b2884a66b13a4ec1197f735bf",
}


def _locked_bytes(filename):
    raw = (ORIGINAL / filename).read_bytes()
    if sha256(raw).hexdigest() != ORIGINAL_SHA256[filename]:
        raise RuntimeError(f"The original study's frozen {filename} changed.")
    return raw


def load_original(filename, bindings=None):
    """Load exact original source with private module identity and explicit imports."""
    raw = _locked_bytes(filename)
    path = ORIGINAL / filename
    name = f"_feeder_return_cue_original_{path.stem}"
    spec = spec_from_file_location(name, path)
    result = module_from_spec(spec)
    sys.modules[name] = result
    imports = {} if bindings is None else bindings
    missing = object()
    saved = {key: sys.modules.get(key, missing) for key in imports}
    sys.modules.update(imports)
    try:
        exec(compile(raw, str(path), "exec"), result.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    finally:
        for key, previous in saved.items():
            if previous is missing:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = previous
    return result


_original_manifest = json.loads(_locked_bytes("bank.json"))
_core = load_original("bank.py")


@lru_cache(maxsize=1)
def excluded_keys():
    previous = set(_original_manifest["excluded_keys"])
    previous.update(start["source_key"] for fold in _original_manifest["folds"].values() for start in fold)
    return frozenset(previous)


_core.HERE = HERE
_core.SCOPE = SCOPE
_core.excluded_keys = excluded_keys

Start = _core.Start
LAWS = _core.LAWS
TAPES = _core.TAPES
TARGETS = _core.TARGETS
derive_seed = _core.derive_seed
source_fold = _core.source_fold
candidate_starts = _core.candidate_starts
select_starts = _core.select_starts
movement_tape = _core.movement_tape
sample_pair = _core.sample_pair
load_bank = _core.load_bank


if __name__ == "__main__":
    _core.main()
