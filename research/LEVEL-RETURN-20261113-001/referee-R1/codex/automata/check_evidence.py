"""Focused integrity, scalar-control, and displayed-formula checks."""
from hashlib import sha256
from pathlib import Path
import json

from vector_levels import scalar_word

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def value(kind, y, n):
    if kind == "parity":
        return y.bit_count() % 2
    return ((y >> (n - 1)) ^ y) & 1


def main():
    product = json.loads((HERE / "product_results.json").read_text())
    vector = json.loads((HERE / "vector_levels_22.json").read_text())
    json_paths = sorted(HERE.glob("*.json"))
    for path in json_paths:
        json.loads(path.read_text())
    assert product["source_sha256"] == sha256((HERE / "product_proof.py").read_bytes()).hexdigest()
    assert vector["source_sha256"] == sha256((HERE / "vector_levels.py").read_bytes()).hexdigest()
    for source in product["sources"].values():
        assert sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["sha256"]
    words = [()] + [(q,) for q in range(3)] + [(q, r) for q in range(3) for r in range(3)]
    controls = []
    for control in product["controls"]:
        witness = control["witness"]
        name = "three" if "#3" in control["description"] else "two"
        key = product["families"][name]["key"]
        string = witness["shortest_bad_input"]
        x, n = int(string, 2), len(string)
        selected = [words[i] for i in witness["placement"]]
        if witness["replace_identity"]:
            selected = [(0,) if not w else w for w in selected]
        images = [scalar_word(key, w, x, n) for w in selected]
        values = [value(witness["state_kind"], y, n) for y in images]
        assert len(set(values)) == 1
        assert not witness["exclude_equal"] or len(set(images)) == 3
        assert n >= witness["minimum"] and n % 2 == witness["length_parity"]
        controls.append({"description": control["description"], "input": string,
                         "images": images, "values": values,
                         "all_images_distinct": len(set(images)) == 3})
    key = product["families"]["two"]["key"]
    formulas_checked = []
    for n in range(4, 23):
        for b in (0, 1):
            x = 2 + b
            images = [scalar_word(key, words[i], x, n) for i in (0, 8, 10)]
            formula_strings = ["0" * (n - 2) + "1" + str(b),
                               "00" + "1" * (n - 4) + "0" + str(1 ^ b),
                               "0" + "1" * (n - 3) + "0" + str(b)]
            assert images == [int(s, 2) for s in formula_strings]
            assert len(set(images)) == 3
            formulas_checked.append({"level": n, "b": b, "images": images})
    result = {"status": "passed", "parsed_json_files": [p.name for p in json_paths],
              "source_and_input_hashes_match": True, "scalar_controls": controls,
              "displayed_special_image_formulas_checked": formulas_checked,
              "note": "Supplementary check imports only this lane's scalar implementation"}
    (HERE / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": "passed", "scalar_controls": len(controls),
                      "formula_cases": len(formulas_checked)}))


if __name__ == "__main__":
    main()
