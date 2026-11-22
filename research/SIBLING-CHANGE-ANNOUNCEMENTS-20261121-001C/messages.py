"""One fixed classical message from the spent eraser, independent of the sibling word."""
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.with_name(HERE.name[:-1] + 'B')
sys.path.insert(0, str(BASE))
from signed_counts import ZERO, add, allowed_old, build_records, forms, matrix, multiply, score, signed_table, sum_forms
from select_flags import rates
sys.path.pop(0)

F = Fraction
H = range(16)
K = range(512)
MODES = ('deterministic', 'randomized')
PAIRS = tuple(combinations(H, 2))


def encode_partition(groups):
    """Order nonempty classes by their smallest physical h and use a contiguous message alphabet."""
    labels = [None] * 16
    for message, group in enumerate(sorted(groups, key=min)):
        for h in group:
            assert labels[h] is None
            labels[h] = message
    assert None not in labels
    return tuple(labels)


def one_collision(pair):
    return encode_partition([pair] + [(h,) for h in H if h not in pair])


def coordinate_subset(shown):
    return encode_partition([tuple(h for h in H if h & shown == v) for v in H if v & shown == v])


def pool(cube, code):
    groups = [[] for _ in range(max(code) + 1)]
    for h, message in enumerate(code):
        groups[message].append(h)
    return {512 * m + k: cube[group[0]][k] if len(group) == 1 else sum_forms(cube[h][k] for h in group)
            for m, group in enumerate(groups) for k in K}


def pack_mask(mask, size):
    raw = bytearray((size + 7) // 8)
    boundary = []
    for key, v in mask.items():
        if v == 1:
            raw[key // 8] |= 1 << (key % 8)
        elif v:
            boundary.append([key, str(v)])
    return {'number_of_entries': size, 'certain_go_bits_little_endian_hex': raw.hex(),
            'partial_go_records': boundary, 'unlisted_entries': 'zero'}


def unpack_mask(packed):
    raw = bytes.fromhex(packed['certain_go_bits_little_endian_hex'])
    n = packed['number_of_entries']
    out = {i: 1 for i in range(n) if raw[i // 8] & 1 << (i % 8)}
    out.update((i, F(v)) for i, v in packed['partial_go_records'])
    return out


def select_row(cube, row):
    return sum_forms(multiply(p, cube[k]) for k, p in row.items() if p)


def mask_at_h(code, mask):
    parts = [{} for _ in range(max(code) + 1)]
    for key, p in mask.items():
        m, k = divmod(key, 512)
        parts[m][k] = p
    return [parts[m] for m in code]


def packet(law, g, den, c, full=False):
    w, d = score(law, g, c)
    v = F(w + d, 28)
    answer = {'p_t_q': g, 'raw_weight': w, 'scaled_surplus': d, 'wI': v,
              'per_original': F(w, den), 'conditional_I': v/w if w else None}
    if full:
        table = signed_table(law, g)
        assert all(sum(line) == w and min(line) >= 0 for line in table)
        answer.update(raw_gram=matrix(law, g), raw_8_settings_and_8_answers=table,
                      conditional_table=[[q/w for q in line] for line in table] if w else None)
    return answer


def price(law, src, c):
    weights = {key: score(law, g, c) for key, g in src.items()}
    return {mode: rates(weights, mode) for mode in MODES}


def selected_packet(law, src, rule, c, den):
    mask = rule['mask']
    go = sum_forms(multiply(a, src[key]) for key, a in mask.items())
    w, d = score(law, go, c)
    assert (w, d) == (rule['weight'], rule['scaled_surplus'])
    packed = pack_mask(mask, len(src))
    assert unpack_mask(packed) == mask
    q = {'go': packet(law, go, den, c), 'mask': packed, 'certificate': rule['certificate']}
    assert q['go']['raw_weight'] == rule['certificate']['lower_equals_upper_raw']
    return q


def complement_mask(mask):
    return {512 * (i // 512) + ((i % 512) ^ 510): p for i, p in mask.items()}


def named_packets(law, cube, code, mask, c, den):
    masks = mask_at_h(code, mask)
    by_h = []
    for h in H:
        keep = select_row(cube[h], masks[h]); whole = sum_forms(cube[h]); no = add(whole, multiply(-1, keep))
        by_h.append({'true_h': h, 'encoded_message': code[h], 'go': packet(law, keep, den, c),
                     'decline': packet(law, no, den, c), 'source_probability': F(score(law, whole, c)[0], den)})
    out = {t: packet(law, sum_forms(row[t]['p_t_q'] for row in by_h), den, c, True) for t in ('go', 'decline')}
    assert out['go']['per_original'] + out['decline']['per_original'] == 1
    out['true_unreceived_h_contributions'] = by_h
    out['reachable_message_probabilities'] = [sum(row['source_probability'] for row in by_h if row['encoded_message']==m)
                                              for m in range(max(code) + 1)]
    assert min(out['reachable_message_probabilities']) > 0
    return out


def signed_at_other_address(law, name):
    """Build the two ordinary completions at the physical changed address in its own name order."""
    ordinary = [i for i in range(7, 16) if i != name]
    by_k = []
    for ubits in product((0, 1), repeat=8):
        fixed = dict(zip(ordinary, ubits, strict=True))
        paths = [allowed_old(tuple(t if i == name else fixed[i] for i in range(7, 16)), law) for t in (0, 1)]
        for b in (0,1):
            signed = tuple(v + (-1)**b * w for v, w in zip(*paths, strict=True))
            by_k.append(forms(signed))
    return tuple(zip(*by_k, strict=True))


def check_source(law, previous):
    source = previous['literal_physical_audit']; record = source['laws'][law]
    cube = build_records(law, 'mixed'); physical = record['views']['mixed']
    den = physical['launch_denominator']; assert den == 32 * record['N']
    for h in H:
        for k in K:
            g = cube[h][k]; idx = physical['gram_ids'][h][k]
            assert matrix(law, g) == tuple(map(tuple, source['gram_library'][idx]))
            assert cube[h][k^510] == (g[2],g[1],g[0])
            raw = source['grade_library'][idx]
            for c in (0,1):
                assert score(law,g,c) == (raw['weight'], 28 * F(raw['wI'+str(c)]) - raw['weight'])
    assert sum(score(law, g, 0)[0] for row in cube for g in row) == den
    transports={}
    for name in range(7,16):
        metadata = record['changed_name_placements'][str(name)]
        dest = signed_at_other_address(law, name)
        hh = metadata['paid_character_image']; kk = metadata['mixed_record_image']
        assert sorted(hh)==list(H) and sorted(kk)==list(K)
        assert all(dest[hh[h]][kk[k]] == cube[h][k] for h in H for k in K)
        transports[str(name)]={'physical_paid_and_all_names':metadata['physical_name_image'],
                                'true_h_image':hh,'k_image':kk,'matched_grams':8192}
    return cube, den, transports


def display(law, code):
    """Single-launch fixed length, clock-independent inter-device word and downstream public bit."""
    M=max(code)+1; bits=(M-1).bit_length()
    valid={i for i in range(8) if (i.bit_count()%2==0 if law=='parity' else i not in (0,7))}
    assert {6,5,3} <= valid and len(valid)<8
    assert all(len({v & ~(1<<i) for v in valid})==4 for i in range(3))
    frames=[tuple(5 if (m>>(bits-1-i))&1 else 3 for i in range(bits)) for m in range(M)]
    assert len(set(frames))==M
    def put(start, word):
        if start!=6: return start,False
        assert word in (5,3) and (start^word).bit_count()==2 and (start&(start^word)).bit_count()==1
        return start^(start^word),True
    def receive(h, k, policy=True, sent=True, public=True, busy_message=False, busy_public=False, source_ready=True):
        m=code[h]
        prior=tuple(5 if i==0 and busy_message else 6 for i in range(bits))
        # All physical signs have one private input here. The symbol lookup and fixed turn have no k argument.
        written=[put(v,t) if sent and source_ready else (v,False) for v,t in zip(prior,frames[m],strict=True)]
        frame=tuple(v for v,_ in written)
        complete=source_ready and (bits==0 or (sent and all(ok for _,ok in written)))
        decoded=frames.index(frame) if complete else None
        accepted=(decoded is not None and k is not None)
        want=(5 if policy else 3)
        old=5 if busy_public else 6
        new,ok=put(old,want) if accepted and public else (old,False)
        assert all(v in valid for v in (*prior,*frame,old,new))
        return {'message_frame':frame,'fresh_symbol_bits':tuple(ok for _,ok in written),'decoded_or_none':decoded,
                'public_word':new,'fresh_public_write':ok,'delivered_go':bool(ok and new==5)}
    normal={}
    for h in H:
        a,b=(receive(h,k,ans) for k,ans in ((0,True),(511,False)))
        assert a['message_frame']==b['message_frame'] and a['decoded_or_none']==b['decoded_or_none']==code[h]
        assert a['delivered_go'] and b['fresh_public_write'] and not b['delivered_go']
        normal[str(h)]={'normal_go':a,'normal_decline':b}
    faults={label:receive(0,k,**kwargs) for label,k,kwargs in (
        ('eraser_link_down',0,{'sent':False}),('first_symbol_bank_already_go',0,{'busy_message':True}),
        ('missing_k',None,{}),('source_absent',None,{'source_ready':False}),('public_link_down',0,{'public':False}),('public_bank_already_go',0,{'busy_public':True}))}
    assert all(not case['delivered_go'] for reason,case in faults.items() if bits or reason not in ('eraser_link_down','first_symbol_bank_already_go'))
    return {'symbols':M,'fixed_bits_per_original':bits,'encoded_messages_in_h_order':code,'physical_ternary_law_words':sorted(valid),
        'wire_addresses':[[16+3*i+t for t in range(3)] for i in range(bits)],'public_ternary_names':list(range(16+3*bits,19+3*bits)),
        'one_lawful_fixed_example_for_both_public_writes':normal,'faults':faults,
        'zero_bit_frame':'A constant message requires no physical symbol wire. Source and k and a fresh public write remain necessary.'}
