"""Finite sign instruments, with integer amplitudes before normalization."""
from functools import cache
from fractions import Fraction
from itertools import product
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name
RESEARCH = ROOT / "research" / TICKET
OUT = ROOT / "artifacts" / TICKET / HERE.name


def fraction(numerator, denominator):
    return str(Fraction(int(numerator), int(denominator)))


def expand(word, places):
    return sum(((word >> i) & 1) << place for i, place in enumerate(places))


@cache
def indices(width, erased):
    removed = [i for i in range(width) if (erased >> i) & 1]
    other = [i for i in range(width) if not (erased >> i) & 1]
    return np.asarray([[expand(z, removed) | expand(r, other) for r in range(1 << len(other))]
                       for z in range(1 << len(removed))], dtype=np.int64)


@cache
def characters(size):
    return np.asarray([[(-1) ** ((h & z).bit_count()) for z in range(size)] for h in range(size)], dtype=np.int64)


def arrays(values, width, erased):
    fibers = values[indices(width, erased)]
    return fibers, characters(len(fibers)) @ fibers


def census():
    """Compare amplitudes against full-space projectors and reduced matrices for every signed array."""
    report = {}
    for width in (1, 2, 3):
        count = dict(signed_sources=0, unsigned_sources=0, masks=0, unsigned_masks=0,
                     character_outcomes=0, zero_character_outcomes=0, binary_outcomes=0)
        checksum = hashlib.sha256()
        for coefficients in product((-1, 0, 1), repeat=1 << width):
            if next((x for x in coefficients if x), 0) != 1:
                continue
            values = np.array(coefficients, dtype=np.int64)
            norm = int(values @ values)
            positive = -1 not in coefficients
            count["signed_sources"] += 1
            count["unsigned_sources"] += positive
            for mask in range(1 << width):
                fibers, transformed = arrays(values, width, mask)
                size = len(fibers)
                squares = np.sum(transformed * transformed, axis=1)
                assert sum(squares) == size * norm
                assert np.array_equal(transformed.T @ transformed, size * (fibers.T @ fibers))
                if positive:
                    assert (transformed[0] != 0).tolist() == np.any(fibers, axis=0).tolist()
                    assert np.all(transformed[0] == np.sum(fibers, axis=0))
                full_flip = values[np.arange(len(values)) ^ mask]
                moment = int(values @ full_flip)
                for port, sign in enumerate((1, -1)):
                    choose = [h for h in range(size) if h.bit_count() % 2 == port]
                    selected = transformed[choose, :]
                    # Distinct actual instruments: compare complete ordinary-word projection
                    # after taking the partial trace, never identify their retained states.
                    projected = fibers + sign * fibers[::-1]
                    assert np.array_equal(size * (projected.T @ projected), 4 * (selected.T @ selected))
                    assert 2 * sum(int(squares[h]) for h in choose) == size * (norm + sign * moment)
                    if positive:
                        assert moment == sum(coefficients[w] and coefficients[w ^ mask] for w in range(len(values)))
                checksum.update(bytes(int(x) + 8 for x in transformed.flat))
                count["masks"] += 1
                count["unsigned_masks"] += positive
                count["character_outcomes"] += size
                count["binary_outcomes"] += 2
                count["zero_character_outcomes"] += int(np.sum(squares == 0))
        count["all_character_amplitudes_sha256"] = checksum.hexdigest()
        report[str(width)] = count
    return report


def knotlab(width, support):
    variables = [f"b{i}" for i in range(width)]
    forbidden = sorted(set(range(1 << width)) - set(support))
    clauses = [" ".join(("~" if (w >> i) & 1 else "") + variable for i, variable in enumerate(variables)) for w in forbidden]
    cmd = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
           "--loops", *variables[:-1], "--contact", variables[-1], "--json"]
    env = dict(os.environ, PYTHONPATH=str(ROOT / "tools"))
    answer = json.loads(subprocess.check_output(cmd, cwd=ROOT, env=env, text=True))
    return {key: answer[key] for key in ("binding", "loss_on_erasure", "coexistence", "is_knot")}


def instrument(values, width, erased):
    values = np.asarray(values, dtype=np.int64)
    norm = int(values @ values)
    fibers, transformed = arrays(values, width, erased)
    H = len(fibers)
    char_rows = []
    for h, row in enumerate(transformed):
        mass = int(row @ row)
        char_rows.append(dict(h=h, chance=fraction(mass, H * norm), remaining_numerators=row.tolist(),
                              state_squared_normalizer=mass or None))
    flips = values[np.arange(len(values)) ^ erased]
    joint = []
    for sign in (1, -1):
        post = values + sign * flips
        mass = int(post @ post)
        joint.append(dict(sign=sign, chance=fraction(mass,4*norm), retained_numerators=post.tolist(),
                          state_squared_normalizer=mass or None))
    return dict(mask=erased, exterior_indices=[i for i in range(width) if not (erased >> i) & 1],
                characters=char_rows, binary=joint)


def law_table():
    laws = {}
    for width in (3, 4, 5):
        length = 1 << width
        for law in ("parity", "nae"):
            allowed = [w for w in range(length) if (w.bit_count() % 2 == 0 if law == "parity" else w not in (0, length-1))]
            indicator = [int(w in allowed) for w in range(length)]
            checker = knotlab(width, allowed)
            assert checker["is_knot"]
            masks = []
            for mask in range(length):
                row = instrument(indicator, width, mask)
                k = mask.bit_count()
                group = 1 << k
                for response in row["characters"]:
                    h = response["h"]
                    if k == 0:
                        expected = Fraction(1)
                    elif law == "parity":
                        expected = Fraction(int(h in (0, group-1)), 2)
                    elif k == width:
                        expected = (Fraction(length - 2, length) if h == 0 else
                                    Fraction(4 * int(h.bit_count() % 2 == 0), length * (length-2)))
                    else:
                        other = Fraction(2, group*(length-2))
                        expected = 1-(group-1)*other if h == 0 else other
                    assert Fraction(response["chance"]) == expected
                if law == "parity":
                    expected_plus = Fraction(1,2) if k % 2 else 1
                else:
                    expected_plus = 1 if k in (0,width) else Fraction(length-3,length-2)
                assert Fraction(row["binary"][0]["chance"]) == expected_plus
                masks.append(row)
            laws[f"{law}/{width}"] = dict(support=allowed, K1_K2_K3=checker, masks=masks)
    return laws


def ordinary_given_product_from_singleton():
    # For a complete singleton on two marks, keep the actual state on the marks.
    row = instrument([1, 0, 0, 0], 2, 3)
    result = []
    for port in (0, 1):
        joint = row["binary"][port]
        sharp = [fraction(x*x,joint["state_squared_normalizer"]) for x in joint["retained_numerators"]]
        selected = [h for h in range(4) if h.bit_count()%2==port]
        # Each measured pair of character eigenstates has uniform ordinary diagonal.
        pooled = [fraction(sum(int(characters(4)[h,w])**2 for h in selected),4*len(selected)) for w in range(4)]
        result.append(dict(port=port, probability=joint["chance"], measured_characters=selected,
                           ordinary_after_binary=sharp, ordinary_after_fine_pooled=pooled,
                           remaining_after_dropping_both_marks=[1]))
    assert row["characters"][0]["chance"] == "1/4"
    assert result[0]["ordinary_after_binary"] != result[0]["ordinary_after_fine_pooled"]
    return dict(all_clean_probability="1/4",branches=result)


def controls():
    pair_rows = {}
    for source, state in (("plus",(1,1)),("minus",(1,-1)),("u",(1,0)),("v",(0,1))):
        pair_rows[source] = instrument(state,1,1)
    pair_rows["dephased"] = {"probabilities":["1/2","1/2"],"conditional_survivor":"scalar for each outcome"}
    downstream = {}
    for law in ("parity","nae"):
        values = [int(w.bit_count()%2==0 if law=="parity" else w not in (0,7)) for w in range(8)]
        first = instrument(values,3,1)
        second_mask = 1 if law=="parity" else 3
        entries = []
        for c in first["characters"]:
            v = np.asarray(c["remaining_numerators"])
            second = instrument(v,2,second_mask)
            entries.append(dict(first=c["h"],p_first=c["chance"],remaining=v.tolist(),second_mask=second_mask,
                                p_second_plus=second["binary"][0]["chance"],p_second_minus=second["binary"][1]["chance"]))
        downstream[law]=entries
    bad = [1 if w in (0,3) else 0 for w in range(8)]
    # These two words fill both exterior values of bit 0 when bits 1 and 2 are forgotten.
    control = {str(e): instrument(bad,3,e)["characters"][0]["remaining_numerators"] for e in (1,2,4,6)}
    assert all(control["6"]) and any(not all(control[str(e)]) for e in (1,2,4))
    # Work in the Gaussian integers for (1,i), with squared normalization two.
    re, im = characters(2) @ np.array([1,0]), characters(2) @ np.array([0,1])
    imaginary_ports = [fraction(x*x+y*y,4) for x,y in zip(re,im)]
    assert imaginary_ports==["1/2","1/2"]
    # Independent changes of representatives implement a controlled sign on the residual pair address.
    source = [1,1,-1,-1]
    representations=[]
    for chosen in ((0,1),(0,2)):
        address = [source[w]-source[w^3] for w in chosen]
        mass=sum(x*x for x in address)
        address_flip=Fraction(2*address[0]*address[1],mass)
        representations.append(dict(representatives=chosen,minus_numerators=address,
                                    address_probabilities=[fraction(x*x,mass) for x in address],
                                    fixed_address_change_mean=str(address_flip)))
    assert representations[0]["address_probabilities"]==representations[1]["address_probabilities"]
    assert [c["fixed_address_change_mean"] for c in representations]==["1","-1"]
    # Applying the supplied two-port reader to the data in a tagged pair leaves (|0>±|1>) on the tag.
    # A second supplied complementary read of that tag resolves equal/opposite port signs.
    reciprocal={}
    for sign in (1,-1):
        weights=[[fraction((1+sign*((-1)**(a+b)))**2,8) for b in (0,1)] for a in (0,1)]
        assert sum(Fraction(q) for row in weights for q in row)==1
        reciprocal[str(sign)]=weights
    return dict(two_word=pair_rows,positive_marked_then_read=downstream,retained_singleton=ordinary_given_product_from_singleton(),
                cancelled_clean_on_minus=pair_rows["minus"]["characters"][0],imaginary_relative_phase_ports=imaginary_ports, surviving_pair_address_phase=representations,
                larger_erasure_does_not_imply_K2=dict(support=[0,3],counts_by_mask=control,canonical=knotlab(3,[0,3])),
                two_supplied_erasers_after_a_which_word_copy=reciprocal)


def run():
    return dict(census=census(),isolated_laws=law_table(),controls=controls())
