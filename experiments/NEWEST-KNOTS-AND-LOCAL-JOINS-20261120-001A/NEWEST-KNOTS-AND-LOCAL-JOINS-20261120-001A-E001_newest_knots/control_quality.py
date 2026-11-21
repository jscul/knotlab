"""Independent family counting and checks of transported sample rates."""

from functools import cache
from hashlib import sha256

from control_draws import OUT, read, save
from control_family_screen import candidate_options, mask
from control_verify import verify_named_sample


def count_disjoint_by_conflicts(options):
    masks = tuple(mask(h) for h, _, _ in options)
    incompatible = tuple(mask(i for i, m in enumerate(masks) if m & h) for h in masks)

    @cache
    def count(available):
        if not available:
            return 1
        chosen = (available & -available).bit_length() - 1
        return count(available ^ (1 << chosen)) + count(available & ~incompatible[chosen])

    return count((1 << len(options)) - 1) - 1


def main():
    draws = read(OUT / 'control_draws.json.gz')
    family = read(OUT / 'control_family_screen.json')
    audited = named = 0
    max_families = max_width = 0
    for panel, sample in draws['nae'].items():
        detail = {(r['draw'], r['age']): r for r in family['panels'][panel]['details']}
        for trial in sample['draws']:
            for stage in trial['stages']:
                key = trial['draw'], stage['age']
                measured = stage['weights']['inherited']
                assert 'undecided' not in detail[key] and 'unread' not in measured
                options = candidate_options(measured, tuple(range(stage['width'])))
                count = count_disjoint_by_conflicts(options)
                assert count == sum(detail[key]['family_count_by_reason'].values())
                assert set(detail[key]['remaining_false_indices']) | set(detail[key]['removed_false_indices']) == set(measured['all_sign']['remaining_spent'])
                audited += 1
                named += count
                max_families = max(max_families, count)
                max_width = max(max_width, stage['width'])
    named_rates = {law: {panel: verify_named_sample(sample, law) for panel, sample in panels.items()}
                   for law, panels in draws.items()}
    receipts = ('reference.json', 'target_uniform.json', 'target_inherited.json', 'control_target.json',
                'control_references.json', 'control_draws.json.gz', 'control_draw_summary.json', 'control_family_screen.json')
    save(OUT / 'control_validation.json', dict(family_observations=audited, family_occurrences=named,
         max_families_in_one_observation=max_families, max_family_width=max_width, named_pair_replay=named_rates,
         sha256={name: sha256((OUT / name).read_bytes()).hexdigest() for name in receipts}))
    print(audited, named, max_families, max_width, named_rates, flush=True)


if __name__ == '__main__':
    main()
