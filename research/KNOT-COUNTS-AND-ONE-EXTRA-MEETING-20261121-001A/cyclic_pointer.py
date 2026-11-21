"""All outcomes of the three-cycle amplitude construction.

Each registered operator is a polynomial in the actual cycle C. The full
off-diagonal density block is stored, or factored into two stored blocks for
fresh pointers. Scalars are elements of Q(zeta_12).
"""

from functools import lru_cache
from fractions import Fraction as Rat
from itertools import product
import sys
from knot_counts import field
from native_counts import apparatus

F = field(12)
ZERO, ONE = F.zero, F.one
HALF = Rat(1, 2)
NAMES = ("a", "b", "c", "d")
QS = ((1, 0), (1, 1), (0, 0), (0, 1))


def cpower(j, s):
    return (j + s) % 3 if j < 3 else j


@lru_cache(5000)
def operator(s, flag, eta=0, phase=0, direction=1, order=3):
    """K_flag(s)=(I+(-1)^flag e^(i phase) (e^(i eta) C)^s)/2."""
    vals = [ZERO] * order
    vals[0] = F.scale(HALF, ONE)
    a = s * direction % order
    vals[a] = F.add(vals[a], F.scale(HALF * (-1) ** flag, F.root(phase + eta * s)))
    return tuple(vals)


@lru_cache(10000)
def compose(left, right):
    n = len(left)
    out = [ZERO] * n
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            out[(i + j) % n] = F.add(out[(i + j) % n], F.mul(x, y))
    return tuple(out)


def pointer_densities():
    order = 4

    def matrix(fn):
        return tuple(tuple(fn(j, k) for k in range(order)) for j in range(order))

    def pure(vec, den):
        return matrix(lambda j, k: F.scale(Rat(1, den), F.mul(vec[j], F.conj(vec[k]))))

    state = {}
    for j, name in enumerate(NAMES):
        state["basis_" + name] = pure([ONE if k == j else ZERO for k in range(4)], 1)
    state["positive_all_three"] = pure([ONE, ONE, ONE, ZERO], 3)
    state["real_minus"] = pure([ONE, F.root(6), ZERO, ZERO], 2)
    state["herald_plus_real"] = pure([ONE, ONE, ZERO, ZERO], 2)
    for label, angle in (("oriented_plus", 4), ("oriented_minus", -4)):
        state[label] = pure(
            [F.root(-angle * j) if j < 3 else ZERO for j in range(4)], 3
        )
    state["unobserved_charge_mixture"] = matrix(
        lambda j, k: F.scale(
            HALF, F.add(state["oriented_plus"][j][k], state["oriented_minus"][j][k])
        )
    )
    return state


RHO = pointer_densities()


@lru_cache(45000)
def block(pointer, ls, rs):
    """Left times rho times right dagger, including pointer phases left behind."""
    r = RHO[pointer]
    out = [[ZERO] * 4 for _ in range(4)]
    for i, a in enumerate(ls):
        if a == ZERO:
            continue
        for j, b in enumerate(rs):
            if b == ZERO:
                continue
            c = F.mul(a, F.conj(b))
            for h in range(4):
                if not any(t != ZERO for t in r[h]):
                    continue
                for g, v in enumerate(r[h]):
                    if v != ZERO:
                        x, y = cpower(h, i), cpower(g, j)
                        out[x][y] = F.add(out[x][y], F.mul(c, v))
    return tuple(tuple(row) for row in out)


@lru_cache(32000)
def trace(u):
    return F.sum(u[j][j] for j in range(len(u)))


def serialized(m):
    return [[F.serialize(v) for v in row] for row in m]


class Catalog:
    def __init__(self):
        self.ids = {}
        self.matrices = []

    def keep(self, mat):
        if mat not in self.ids:
            self.ids[mat] = len(self.ids)
            self.matrices.append(serialized(mat))
        return self.ids[mat]


def single_charge(cat):
    result = {}
    for pointer in RHO:
        ptr = {}
        for direction, eta, offset in product((1, -1), (0, 4, 8), (0, 3, 6, 9)):
            tests = {}
            for flag in (0, 1):
                arm = {}
                for s, t in product(range(4), repeat=2):
                    u = block(
                        pointer,
                        operator(s, flag, eta, offset, direction),
                        operator(t, flag, eta, offset, direction),
                    )
                    arm[f"{s}/{t}"] = [cat.keep(u), F.serialize(trace(u))]
                tests[flag] = arm
            assert all(
                F.add(
                    trace(
                        block(
                            pointer,
                            operator(s, 0, eta, offset, direction),
                            operator(s, 0, eta, offset, direction),
                        )
                    ),
                    trace(
                        block(
                            pointer,
                            operator(s, 1, eta, offset, direction),
                            operator(s, 1, eta, offset, direction),
                        )
                    ),
                )
                == ONE
                for s in range(4)
            )
            ptr[f"C{direction}/eta{eta}/source_minus_analyzer{offset}"] = tests
        result[pointer] = ptr
    return result


def keep_quadratures(g00, g11, g01):
    # Matrix entries are rho[0,0], rho[1,1], rho[0,1]. A final inverse
    # sqrt-X maps q=1 to (g00+g11+2 Im rho[0,1])/2, with phase on q=1.
    norm = F.add(g00, g11)
    values = {}
    for exp in (0, 3):
        lo = F.mul(g01, F.root(-exp))
        twice_im = F.mul(F.root(-3), F.sub(lo, F.conj(lo)))
        yes = F.add(norm, twice_im)
        values[str(exp)] = {
            "K011": F.ratio(yes, F.scale(2, norm)),
            "K101": F.ratio(F.sub(norm, twice_im), F.scale(2, norm)),
            "K110": "0" if norm != ZERO else None,
        }
    return values


def double_charge(cat):
    # For every word density entry, table[s(x),s(x')] gives the
    # UNNORMALIZED output pointer block multiplying that input entry.
    counts = {x: ((x & 7).bit_count(), (x & 25).bit_count()) for x in range(32)}
    vals = sorted(set(counts.values()))
    valid = {x for x, c in counts.items() if all(0 < s < 3 for s in c)}
    frequency = {c: sum(d == c for d in counts.values()) for c in vals}
    legal_count = {c: sum(counts[x] == c for x in valid) for c in vals}
    # Probe v=0 with b1,b3=1 and b2,b4=0. Two counts 1,1 or 2,2.
    pinned = ((1, 1), (2, 2))
    data = {}
    for pointer in RHO:
        if pointer not in (
            "real_minus",
            "unobserved_charge_mixture",
            "oriented_plus",
            "oriented_minus",
            "basis_a",
            "positive_all_three",
            "herald_plus_real",
        ):
            continue
        for reused in (False, True):
            by_flags = {}
            normalizers = {}
            for flags in product((0, 1), repeat=2):
                records = []
                gram = {}
                for s, t in product(vals, repeat=2):
                    lo = tuple(operator(u, f) for u, f in zip(s, flags))
                    ro = tuple(operator(u, f) for u, f in zip(t, flags))
                    if reused:
                        u = block(pointer, compose(*lo), compose(*ro))
                        i = cat.keep(u)
                        g = trace(u)
                    else:
                        u = block(pointer, lo[0], ro[0])
                        v = block(pointer, lo[1], ro[1])
                        i = [cat.keep(u), cat.keep(v)]
                        g = F.mul(trace(u), trace(v))
                    records.append([i, F.serialize(g)])
                    gram[s, t] = g
                pp = F.sum(F.scale(frequency[c], gram[c, c]) for c in vals)
                legal = F.sum(F.scale(legal_count[c], gram[c, c]) for c in vals)
                normalizers[flags] = pp
                h, j = pinned
                by_flags["".join(map(str, flags))] = {
                    "full_pointer_block_and_its_trace_by_lex_countpair": records,
                    "unconditional_flag_full_binary_input": F.ratio(
                        pp, F.scale(32, ONE)
                    ),
                    "unconditional_flag_uniform_lawful_input": F.ratio(
                        legal, F.scale(len(valid), ONE)
                    ),
                    "probability_flag_and_pinned_exterior_from_full_input": F.ratio(
                        F.add(gram[h, h], gram[j, j]), F.scale(32, ONE)
                    ),
                    "pinned_complete_reduced_data_unnormalized": serialized(
                        ((gram[h, h], gram[h, j]), (gram[j, h], gram[j, j]))
                    ),
                    "pinned_keeper_after_flag_only": keep_quadratures(
                        gram[h, h], gram[j, j], gram[h, j]
                    ),
                }
            assert F.sum(normalizers.values()) == F.scale(32, ONE)
            data[f"{pointer}/{'reused' if reused else 'fresh'}"] = by_flags

    def reduced(rec):
        return [x[-1] for x in rec["full_pointer_block_and_its_trace_by_lex_countpair"]]

    weights = {}
    for tag in ("00", "01", "10", "11"):
        for mode in ("fresh", "reused"):
            r = data[f"real_minus/{mode}"][tag]
            m = data[f"unobserved_charge_mixture/{mode}"][tag]
            assert reduced(r) == reduced(m)
        # For the single common classic draw, the two oriented components have
        # orthogonal pointer eigenvectors, and all later operators commute with C.
        wsp = data["unobserved_charge_mixture/reused"][tag]
        left = counts[10]
        right = counts[11]
        weights[tag] = {
            "classical_shared_charge_same_reduced_data_as": "unobserved_charge_mixture/reused",
            "independent_classical_charges_same_reduced_data_as": "unobserved_charge_mixture/fresh",
            "fresh_real_vs_reused_reduced_data_agree": reduced(
                data["real_minus/fresh"][tag]
            )
            == reduced(data["real_minus/reused"][tag]),
            "plus_vs_real_joint_pointer_and_data_agree": data["oriented_plus/reused"][
                tag
            ]
            == data["real_minus/reused"][tag],
            "shared_charge_pinned_K": wsp["pinned_keeper_after_flag_only"],
        }
    return {
        "word_counts": counts,
        "lexicographic_address_pairs": vals,
        "allowed_words": sorted(valid),
        "protocols": data,
        "comparisons": weights,
        "normalization": "Multiplying each listed block by the data input density entry gives the joint data/pointer result for that flag. Sum its diagonal data blocks for the residual pointer state. Divide either retained substate by the flag probability to condition. A fresh pair entry contains tensor-factor IDs; a reused entry contains one matrix ID.",
    }


def tag_and_single_readout(cat):
    result = {}
    # At a kept orthogonal path record the sum/difference alternatives cease to
    # interfere. Include the full environment blocks before the tag is dropped.
    for pointer in RHO:
        rr = {}
        for signed in (-1, 1):
            for s, t in product(range(4), repeat=2):
                words = []
                for b, c in product(range(2), repeat=2):
                    left = tuple(
                        F.scale(HALF * (signed**b), ONE) if j == (b * s) % 3 else ZERO
                        for j in range(3)
                    )
                    right = tuple(
                        F.scale(HALF * (signed**c), ONE) if j == (c * t) % 3 else ZERO
                        for j in range(3)
                    )
                    words.append(block(pointer, left, right))
                # Four matrix IDs are in physical (tag-row,tag-column) order.
                ignored = F.add(trace(words[0]), trace(words[3]))
                coherent = F.sum(trace(m) for m in words)
                flags = 0 if signed == 1 else 1
                original = block(pointer, operator(s, flags), operator(t, flags))
                assert coherent == trace(original)
                rr[f"{flags}/{s}/{t}"] = {
                    "orthogonal_tag_block_ids": [cat.keep(m) for m in words],
                    "kept_orthogonal_tag_traced_out": F.serialize(ignored),
                    "all_copies_returned_or_disconnected": F.serialize(coherent),
                }
        diag = {}
        for flag in (0, 1):
            blocks = {
                (s, t): block(pointer, operator(s, flag), operator(t, flag))
                for s, t in product(range(4), repeat=2)
            }
            h, j = 1, 2
            diag[flag] = {
                "all_classical_singletons": [
                    F.serialize(trace(blocks[s, s])) for s in range(4)
                ],
                "pinned_K": keep_quadratures(
                    trace(blocks[h, h]), trace(blocks[j, j]), trace(blocks[h, j])
                ),
                "unconditional_uniform_8": F.ratio(
                    F.sum(
                        F.scale(q, trace(blocks[s, s]))
                        for s, q in enumerate((1, 3, 3, 1))
                    ),
                    F.scale(8, ONE),
                ),
                "unconditional_positive_uniform_allowed": F.ratio(
                    F.add(trace(blocks[1, 1]), trace(blocks[2, 2])), F.scale(2, ONE)
                ),
            }
        result[pointer] = {"matrices": rr, "single_holder": diag}
    singletons = lambda p: [
        result[p]["single_holder"][j]["all_classical_singletons"] for j in (0, 1)
    ]
    assert (
        singletons("oriented_plus")
        == singletons("oriented_minus")
        == singletons("real_minus")
        == singletons("unobserved_charge_mixture")
    )
    return result


def parity_cycle():
    # A two-word swap. Both eigenvalues and both outcomes remain recorded.
    result = {}
    for m, charge in product(range(2, 9), (0, 6)):
        flags = {}
        for flag in (0, 1):
            vals = [
                F.scale(HALF, F.add(ONE, F.scale((-1) ** flag, F.root(charge * s))))
                for s in range(m + 1)
            ]
            flags[flag] = {
                "amplitudes": list(map(F.serialize, vals)),
                "definite_word_flags": list(map(F.serialize, map(F.sq, vals))),
            }
            if charge == 6 and flag == 0:
                assert all(
                    v == (ONE if j % 2 == 0 else ZERO) for j, v in enumerate(vals)
                )
        result[f"{m}/charge{charge}"] = flags
    return result


def quantum_cycle_checks():
    cat = Catalog()
    one = single_charge(cat)
    two = double_charge(cat)
    tag = tag_and_single_readout(cat)
    return {
        "field": 12,
        "matrix_order": NAMES,
        "pointer_densities": {k: serialized(v) for k, v in RHO.items()},
        "single_controlled_all_phase_frames": one,
        "separately_set_source_and_analyzer":{f"gamma={g},delta={v}":(g-v)%12 for g in (0,3,9) for v in (0,3,9)},
        "two_ternary_shared_distinction": two,
        "registered_which_path_tag": tag,
        "complete_complementary_parity_ports": parity_cycle(),
        "one_fixed_address_reverse_only_remote_root": crossed_orientation_check(),
        "pointer_matrix_library": cat.matrices,
        "phase_convention": "C sends a->b->c->a. Exponents of zeta_12 parametrize eta and gamma-delta. For root lambda the active arm contains (eta lambda)^s. Input ordinary and pointer bases are always held fixed unless stated.",
    }


def ordinary_cycle_checks():
    physical, routes = apparatus()

    def controls(g, rev):
        return tuple(routes._guard(j, rev, val) for j, val in g)

    def exchange(word, target, g, rev, name, connected=True):
        row = routes._exchange_trace(
            word,
            routes._places(routes.REGISTERS[target][:2], rev),
            name,
            guard=controls(g, rev),
            reverse=rev,
            connected=connected,
        )
        assert (
            row["supported"]
            and row["unchanged_guard"]
            and all(not bad for bad in row["physical_law_failures"].values())
        )
        return row["after"], [
            word,
            name,
            target,
            g,
            int(row["enabled"]),
            row["after"],
            row["toggled"],
        ]

    def cycle(word, which, g, rev, direction=1, connected=True):
        q, s = which
        seq = [(s, [(q, 1)], "P"), (q, [(s, 0)], "Q")]
        if direction < 0:
            seq.reverse()
        hist = []
        for target, guard, op in seq:
            word, step = exchange(word, target, guard + g, rev, op, connected)
            hist.append(step)
        return word, hist

    def swap(word, u, v, rev):
        hist = []
        for target, guard in ((v, u), (u, v), (v, u)):
            word, step = exchange(word, target, [(guard, 1)], rev, "swap")
            hist.append(step)
        return word, hist

    physical_basis = {}
    for rev in (False, True):
        sampled = []
        for (j, (q, s)), bit, path, active in product(
            enumerate(QS), range(2), range(2), (False, True)
        ):
            old = routes.encode(bit, q=q, s=s, t=path, reverse=rev)
            for direction in (-1, 1):
                word = old
                history = []
                visits = []
                for reps in range(3):
                    word, trace_ = cycle(
                        word,
                        (routes.Q, routes.S),
                        [(0, 1), (routes.T, 1)],
                        rev,
                        direction,
                        active,
                    )
                    history.append(trace_)
                    visits.append(word)
                    target = (
                        cpower(j, (reps + 1) * direction) if bit * path * active else j
                    )
                    assert word == routes.encode(
                        bit, q=QS[target][0], s=QS[target][1], t=path, reverse=rev
                    )
                assert word == old
                sampled.append(
                    {
                        "initial_pointer": NAMES[j],
                        "data": bit,
                        "path": path,
                        "connected": active,
                        "direction": direction,
                        "all_actual_terminal_words": visits,
                        "offered_stages": history,
                    }
                )
        dual = []
        for x, t1, t2 in product(range(32), range(2), range(2)):
            # Pointer 2 uses registers 5,6. q=s selection for initial label a.
            initial_data = x | (1 << 5) | (t2 << 8)
            old = routes.encode(initial_data, q=1, s=0, t=t1, reverse=rev)
            hist = []
            word = old
            for which, path, indices in (
                ((routes.Q, routes.S), routes.T, (0, 1, 2)),
                ((5, 6), 8, (0, 3, 4)),
            ):
                for b in indices:
                    word, h = cycle(word, which, [(b, 1), (path, 1)], rev)
                    hist.extend(h)
            two = routes.decode(word, reverse=rev)
            j1 = cpower(0, t1 * ((x & 7).bit_count()))
            j2 = cpower(0, t2 * ((x & 25).bit_count()))
            assert (two["q"], two["s"]) == QS[j1] and (
                (two["data"] >> 5) & 1,
                (two["data"] >> 6) & 1,
            ) == QS[j2]
            from_s, hs = swap(word, routes.S, 7, rev)
            final, hq = swap(from_s, 0, routes.Q, rev)
            d = routes.decode(final, reverse=rev)
            assert (
                d["q"] == (x & 1)
                and d["s"] == 0
                and ((d["data"] >> 7) & 1) == QS[j1][1]
                and (d["data"] & 1) == QS[j1][0]
            )
            end, writer = routes.write_keeper(final, reverse=rev)
            keeper = routes.decode(end, reverse=rev)
            assert keeper["keeper"] == ("011" if x & 1 else "101")
            dual.append(
                {
                    "data": x,
                    "two_initialized_flags": [t1, t2],
                    "initial_full_word": old,
                    "two_final_pointers": [j1, j2],
                    "controlled_offers": hist,
                    "true_transfer_of_pointer_and_variable": hs + hq,
                    "before_writer": final,
                    "terminal_word": end,
                    "K": keeper["keeper"],
                    "physical_writer_steps": writer,
                }
            )
        other = []
        for q, s, v, work in product(range(2), repeat=4):
            o = routes.encode(v | (work << 7), q=q, s=s, reverse=rev)
            w, hs = swap(o, routes.S, 7, rev)
            w, hq = swap(w, 0, routes.Q, rev)
            d = routes.decode(w, reverse=rev)
            assert (
                d["q"] == v
                and d["s"] == work
                and d["data"] & 1 == q
                and (d["data"] >> 7) & 1 == s
            )
            other.append([o, w, hs, hq])
        tags = []
        for path, latch, connected in product(range(2), range(2), (False, True)):
            w = routes.encode(0, t=path, l=latch, reverse=rev)
            w1, step = exchange(
                w, routes.L, [(routes.T, 1)], rev, "copy path t into l", connected
            )
            w2, undo = exchange(
                w1, routes.L, [(routes.T, 1)], rev, "undo path copy", connected
            )
            assert w == w2 and routes.decode(w1, reverse=rev)["l"] == (
                latch ^ (path * connected)
            )
            tags.append([path, latch, connected, step, undo])
        physical_basis[int(rev)] = {
            "C_on_actual_complete_words": sampled,
            "two_actual_controlled_pointers_and_transfer": dual,
            "swap_complete_truth_table": other,
            "actual_path_record_controls": tags,
        }
    return physical_basis


def balanced_source_calibration():
    # Preceding z=1 or z=e^(i*pi/4) vocabulary, exact arithmetic copied by import.
    physical, routes = apparatus()
    import composition as prior

    ret = {}
    for k in (0, 1):
        bp = prior.rim("P", k)
        bj = prior.rim((1, 3), k)
        true_j = prior.rim((1, 3), full=True)
        program = prior.program(bp, bj, bj, prior.adjoint(true_j))
        columns = {
            w: [prior.printable(x) for x in prior.apply(program, prior.basis(j))]
            for j, w in enumerate(NAMES)
        }
        # Hardware layout here is (path,scratch) in the order a,b,c,d used by
        # the original four-word checker. An unconditional t flip swaps a,c and b,d.
        path_flip = prior.identity(4)
        pair = (2, 3, 0, 1)
        path_flip = tuple(
            tuple(
                prior.HALF
                if i == j
                else prior.mult(prior.HALF, prior.zeta(2))
                if i == pair[j]
                else prior.ZERO
                for j in range(4)
            )
            for i in range(4)
        )
        physical_s = prior.program(bp, bp, prior.adjoint(prior.rim("P", full=True)))
        splitter = prior.program(path_flip, prior.adjoint(physical_s))
        true_inverse = prior.adjoint(splitter)
        assert prior.program(splitter, true_inverse) == prior.identity(4)
        # For every basis |t,l> and t=0 prestate compute the incoherently
        # observed path alternative too. A disconnected path yields unchanged a
        # at the source; the formerly requested minus then cannot herald.
        path_reads = {}
        for scratch in range(2):
            j0 = 2 + scratch
            j1 = scratch
            for conn in (False, True):
                # t=0,+1 arms. S_t data are fully restored even for l=1.
                init = prior.apply(splitter, prior.basis(j0))
                joint = {}
                for j in (j0, j1):
                    ptr = 1 if j == j1 and conn else 0
                    for o in (j0, j1):
                        joint[o, ptr] = prior.add(
                            joint.get((o, ptr), prior.ZERO),
                            prior.mult(true_inverse[o][j], init[j]),
                        )
                waves = {}
                for o in (j0, j1):
                    v = [joint.get((o, p), prior.ZERO) for p in range(4)]
                    prob = prior.total(prior.born(v))
                    waves[str(int(o == j1))] = {
                        "unconditional_probability": prior.printable(prob),
                        "conditional_pointer_before_normalizing": list(
                            map(prior.printable, v)
                        ),
                        "initial_scratch": scratch,
                        "final_scratch": o % 2,
                        "all_intermediate_paths_recorded_joint": {
                            f"t{int(j == j1)}/a{int(j == j1 and conn)}": prior.printable(
                                prior.mult(x, prior.conjugate(x))
                            )
                            for j in (j0, j1)
                            for x in [prior.mult(true_inverse[o][j], init[j])]
                        },
                    }
                    if conn and o == j1:
                        assert v[1] == prior.scaled(-1, v[0]) and prob == prior.scaled(
                            HALF, prior.ONE
                        )
                path_reads[f"{scratch}/{int(conn)}"] = waves
        ready = physical.basis_words()["a"]
        ret[k] = {
            "two_step_route_all_columns": columns,
            "complete_scratch_phase_matrix": prior.matrix_out(physical_s),
            "actual_real_splitter": prior.matrix_out(splitter),
            "true_analyzer": prior.matrix_out(true_inverse),
            "herald_both_outcomes": path_reads,
            "missing_request": physical.readout_word(None),
            "ready_codeword": ready,
            "unavailable_which_data": physical.readout_word(ready, present=False),
            "nonready": physical.readout_word(routes.encode(245, keeper="011")),
            "without_t_preparation_or_analyzer": {
                "t0_probability": "1",
                "t1_probability": "0",
                "pointer": "a",
            },
            "all_intermediates_read_as_ordinary": {
                "scope": "Every intermediate physical t,l,pointer word is read; probabilities computed by squared pulse transition kernels.",
                "phase_scratch_kernel": _observed_kernel(k, prior),
            },
        }
    return ret


def _observed_kernel(k, prior):
    allrows = {}

    def kernel(u):
        return tuple(tuple(prior.mult(x, prior.conjugate(x)) for x in row) for row in u)

    full = prior.rim("P", full=True)
    bm = prior.rim("P", k)
    bj = prior.rim((1, 3), k)
    j = prior.rim((1, 3), full=True)
    stages = [bm, bj, bj, prior.adjoint(j)]
    m = prior.program(*(kernel(g) for g in stages))
    allrows["deterministic_attempt"] = prior.matrix_out(m)
    phase = prior.program(kernel(bm), kernel(bm), kernel(prior.adjoint(full)))
    allrows["S_t_instrument"] = prior.matrix_out(phase)
    return allrows


def all_registers_measured():
    """Execute and retain every sensor branch between every elementary gate."""
    physical, routes = apparatus()
    result = {}
    # Forward and inverse balanced flips have identical definite-word kernels.
    seq = (
        "B_t",
        "full_L",
        "B_L_guard_t",
        "B_L_guard_t",
        "P_if_t",
        "Q_if_t",
        "B_L_guard_t",
        "B_L_guard_t",
        "full_L",
        "B_t",
    )
    for launch_l, scratch_connection, path_connection in product(
        range(2), (False, True), (False, True)
    ):
        paths = [((0, 0, launch_l), Rat(1), ())]
        for name in seq:
            next_paths = []
            for incoming, wt, history in paths:
                w, t, s = incoming
                if name == "B_t":
                    move = (w, t ^ 1, s) if path_connection else incoming
                    half = True
                elif name in ("full_L", "B_L_guard_t"):
                    move = (w, t, s ^ (t * scratch_connection))
                    half = name.startswith("B_")
                elif name == "P_if_t":
                    move = ((1, 0, 2, 3)[w], t, s) if t else incoming
                    half = False
                else:
                    move = ((2, 1, 0, 3)[w], t, s) if t else incoming
                    half = False
                opts = (
                    [(move, wt)]
                    if not half or move == incoming
                    else [(incoming, wt / 2), (move, wt / 2)]
                )
                for state, p in opts:
                    next_paths.append((state, p, history + (state,)))
            paths = next_paths
        prob = {}
        for state, p, h in paths:
            prob[state] = prob.get(state, Rat(0)) + p
        assert sum(prob.values()) == 1
        result[
            f"l{launch_l}/scratch{int(scratch_connection)}/path{int(path_connection)}"
        ] = {
            "initial_full_word": routes.encode(0, q=1, s=0, t=0, l=launch_l),
            "same_scheduled_offers": seq,
            "all_full_intermediate_word_histories": [
                {
                    "probability": str(p),
                    "history": [
                        routes.encode(0, q=QS[w][0], s=QS[w][1], t=t, l=l)
                        for w, t, l in h
                    ],
                }
                for _, p, h in paths
            ],
            "complete_joint_pointer_t_l": {
                f"{NAMES[w]}/{t}/{l}": str(p) for (w, t, l), p in sorted(prob.items())
            },
            "minus_requested_probability": str(
                sum(p for (w, t, l), p in prob.items() if t)
            ),
        }
    return result


def crossed_orientation_check():
    records = {}
    counts = {x: ((x & 7).bit_count(), (x & 25).bit_count()) for x in range(32)}
    for d in (1, -1):
        for flags in product((0, 1), repeat=2):

            def phase(s, fl, direction):
                return F.scale(
                    HALF, F.add(ONE, F.scale((-1) ** fl, F.root(4 * direction * s)))
                )

            a = {
                x: F.mul(phase(s, flags[0], 1), phase(t, flags[1], d))
                for x, (s, t) in counts.items()
            }
            weight = F.sum(F.sq(v) for v in a.values())
            champ = keep_quadratures(
                F.sq(a[10]), F.sq(a[11]), F.mul(a[10], F.conj(a[11]))
            )
            records[f"second_cycle_{d}/flags{flags}"] = {
                "ordinary_word_frequencies_before_normalization": {
                    x: F.serialize(F.sq(y)) for x, y in a.items()
                },
                "whole_stage_flag_rate_from_full_binary": F.ratio(
                    weight, F.scale(32, ONE)
                ),
                "unchanged_local_keeper_on_pinned_values": champ,
            }
    return records
