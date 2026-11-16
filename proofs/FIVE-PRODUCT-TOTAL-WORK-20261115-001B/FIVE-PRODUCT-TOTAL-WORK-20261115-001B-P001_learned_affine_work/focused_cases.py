"""Actual priced routes for the two 5+13 sector candidates and their six orientations."""
import json
from pathlib import Path

import solver
import verifier


MENU = solver.AXES + (132,134,148,150)


def build():
    real = solver.Search(MENU)
    programs, report = {}, {}
    for b in (132,148):
        for g, l in ((2,b), (b,2), (2^b,2)):
            label = f'{g}=0 implies {l}=1'
            scores, proofs = real.single((g,0), (l,1))
            expected = [23,23,30,30] if g == 2 else [23,29,32,32]
            verifier.ensure(scores == expected, 'unexpected mixed-candidate minimum')
            for i, proof in proofs.items():
                verifier.ensure(verifier.inspect(proof)['cost'] == scores[i], 'mixed candidate witness')
            chosen = proofs[3]
            programs[label] = chosen
            detail = verifier.inspect(chosen)
            report[label] = {'scores':scores, 'training':detail['lemma_cost'], 'crossing_main':detail['main_cost'],
                             'ordinary_specialized_expansion':verifier.inspect(verifier.expand(chosen))['cost']}
    real_size = len(real.states)
    del real
    original = solver.old.evaluator_sets((1,6), 1)
    complements = {}
    local_examples = {}
    for b in (132,148):
        flat = solver.old.equation_points(2,0) & solver.old.equation_points(b,0)
        allowed = verifier.WORLD - (verifier.equation(2,0) & verifier.equation(b,0))
        filtered = solver.Search(MENU, {tag:rows & ~flat for tag, rows in original.items()})
        proof = {'root':filtered.ordinary(filtered.root)}
        cost = verifier.inspect(proof, retained=allowed)['cost']
        verifier.ensure(cost == 13, 'globally deleted sector failed its 13-unit positive control')
        try:
            verifier.inspect(proof)
        except ValueError as error:
            verifier.ensure('empty leaf' in str(error), 'wrong unfiltered failure')
        else:
            raise ValueError('deleted-sector proof survived the original source rows')
        programs[f'filter_{b}'] = proof
        complements[str(b)] = {'cost':cost, 'raw_unfiltered_replay': 'rejected', 'reachable_states':len(filtered.states)}
        del filtered
        left, right = verifier.sources(1).values()
        examples = []
        for raw in (verifier.equation(1,0) & verifier.equation(130,0),
                    verifier.equation(1,1) & verifier.equation(128,0)):
            checked = verifier.span(raw & left)
            cited = checked & verifier.equation(b,1)
            target = verifier.span(raw & left & allowed)
            verifier.ensure(not raw <= verifier.equation(2,0) and checked <= verifier.equation(2,0),
                            'guard should become available only after checking the source')
            verifier.ensure(verifier.fixed(cited) and verifier.fixed(checked) - cited, 'local citation must be live')
            if b == 132:
                verifier.ensure(verifier.span(cited & left) == target and verifier.span(cited & right) == cited,
                                'missing rich equation after the citation')
            else:
                verifier.ensure(cited == target, 'one citation failed to reproduce the modified rich hull')
            examples.append({'raw':len(raw), 'rich_check':len(checked), 'after_citation':len(cited),
                             'rich_hull_with_global_deletion':len(target), 'fixed_after_citation':len(verifier.fixed(cited))})
        local_examples[str(b)] = examples
    return programs, {'menu':list(MENU), 'original_states':real_size, 'orientations':report,
                      'complement_proofs':complements, 'local_legal_restorations':local_examples}


def audit():
    programs, result = build()
    saved = Path(__file__).with_name('focused_certificates.json')
    verifier.ensure(json.loads(saved.read_text()) == programs, 'focused saved proof changed')
    return result
