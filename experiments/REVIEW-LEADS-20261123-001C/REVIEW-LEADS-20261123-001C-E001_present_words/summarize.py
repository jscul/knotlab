"""Collect the numbers of all runs into one JSON and a markdown table (printed)."""
import glob, json
import common as c

def load(pattern):
    return [json.load(open(f)) for f in sorted(glob.glob(f'{c.ART}/{pattern}'))]

def agg(ss):
    t = dict(files=len(ss), exact_tables=ss[0]['exact_tables'], nonempty_tables=ss[0]['nonempty_tables'], projective_tables=ss[0]['projective_tables'],
             tables_combined=ss[0]['tables_combined'], allocation_tables=ss[0]['allocation_tables'], sym=ss[0]['sym'], hidden_only=ss[0].get('hidden_only', False))
    for k in ('pairs_evaluated', 'pairs_with_no_word', 'alloc_pairs', 'pairs_hidden', 'pairs_hidden_alloc', 'n_hidden_gt2', 'n_hidden_gt2_alloc',
              'n_all_gt2', 'n_all_gt2_alloc', 'n_control_gt2'):
        t[k] = sum(s[k] for s in ss)
    for k in ('unique_M', 'unique_M_hidden', 'unique_M_alloc', 'unique_M_hidden_alloc', 'n_hidden_ge2', 'n_hidden_ge2_alloc'):
        t[k + '_sum_over_files'] = sum(s[k] for s in ss)
    for k in ('max_score_hidden', 'max_score_hidden_alloc', 'max_score_all', 'max_score_all_alloc', 'max_control_all', 'max_control_hidden'):
        t[k] = max((s[k] or 0) for s in ss)
    t['exact_gt2_among_hidden_reaching_2'] = sum(s['hidden_reaching_2_exact_check']['exact_gt2'] for s in ss)
    t['seconds_max_run'] = max(s['seconds'] for s in ss)
    return t

out = {}
for name, pat in [('census_c1', 'pairs_c1_k3_i3_0_*_summary.json'), ('census_c2', 'pairs_c2_k3_i3_0_*_summary.json'),
                  ('ext_c1', 'pairs_c1_k4_i5_sym_0_*_summary.json'), ('ext_c2', 'pairs_c2_k4_i5_sym_*_summary.json'),
                  ('targeted_c1_alloc', 'pairs_c1_t6alloc_sym_*_summary.json'), ('targeted_c2_alloc', 'pairs_c2_t6alloc_sym_*_summary.json'),
                  ('targeted_c1_free', 'pairs_c1_t6free_sym_*_summary.json'), ('targeted_c2_free', 'pairs_c2_t6free_sym_*_summary.json'),
                  ('targeted_b_c1_alloc', 'pairs_c1_t6allocb_sym_*_summary.json'), ('targeted_b_c2_alloc', 'pairs_c2_t6allocb_sym_*_summary.json'),
                  ('targeted_b_c1_free', 'pairs_c1_t6freeb_sym_*_summary.json'), ('targeted_b_c2_free', 'pairs_c2_t6freeb_sym_*_summary.json')]:
    ss = load(pat)
    if ss: out[name] = agg(ss)
json.dump(out, open(f'{c.ART}/summary_all.json', 'w'), indent=1)
for k, v in out.items():
    print('==', k); print(json.dumps(v, default=str))
