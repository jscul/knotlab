"""Amendment (logged in contract.json, 2026-11-19, after the read-out): the frozen scorer merge.py with its three slips fixed.
The frozen verdicts stay the record; this adds the fixed ones beside them.
- C2: W recomputed to 120 terms where the frozen 30-term W disagreed (it cut an endless chain's series).
- I2: loop knots are the knots on the loop's cycle (merge.py also took the side knots of its blocks), and the path of two's factor
  is the pre-registration's (1 + y)/(1 - y) (merge.py kept the advisor's (1 + y)^2).
- R1: for the even rings, whose two loops the frozen W left uncomputed, the rate is compared with the root of y^(n/2)(1 + y) = 1.
python3 -B merge_fixed.py <runner out dir> <results_fixed.json>"""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def main():
    M = load('lc_merge', HERE / 'merge.py')
    P = load('lc_posthoc', HERE / 'posthoc.py')
    out_dir, dest = sys.argv[1], Path(sys.argv[2])
    tmp = dest.with_suffix('.frozen.json')
    sys.argv = ['merge.py', out_dir, str(tmp)]
    M.main()
    frozen = json.loads(tmp.read_text())
    tmp.unlink()
    sys.argv = ['posthoc.py', out_dir, str(dest.with_suffix('.posthoc.json'))]
    P.main()
    ph = json.loads(dest.with_suffix('.posthoc.json').read_text())
    dest.with_suffix('.posthoc.json').unlink()
    fixed = dict(frozen['verdicts'])
    c2 = frozen['C2']
    fixed['C2'] = c2['agree'] + sum(d['agree'] for d in ph['C2*']) == c2['checked']
    fixed['I2'] = ph['I2*']['n'] > 0 and ph['I2*']['agree'] == ph['I2*']['n']
    r1 = frozen['R1']
    fixed['R1'] = r1['held'] + sum(abs(d['rule_rate'] - d['predicted']) < 1e-5 for d in ph['R1*']) == r1['n']
    frozen['fixed'] = {'verdicts': fixed, 'C2*': ph['C2*'], 'I2*': ph['I2*'], 'R1*': ph['R1*']}
    dest.write_text(json.dumps(frozen, indent=1, default=str))
    print(json.dumps({'frozen': frozen['verdicts'], 'fixed': fixed}))


if __name__ == '__main__':
    main()
