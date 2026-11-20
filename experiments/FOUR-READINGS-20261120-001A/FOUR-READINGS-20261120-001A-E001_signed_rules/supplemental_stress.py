"""Post-freeze singleton stress replay. The original cohorts have separate records."""
import hashlib
import json
import os
import resource

os.environ['OPENBLAS_NUM_THREADS'] = '1'
budget = 4 * 1024**3
soft, hard = resource.getrlimit(resource.RLIMIT_AS)
resource.setrlimit(resource.RLIMIT_AS, (min(budget, soft) if soft >= 0 else budget, hard))

from census import HERE, ROOT, save
from growth import ARCHIVE, J, source


def main():
    archive = json.loads(ARCHIVE.read_text())['named_archive_starts']['start-03']
    assert archive['identifier'] == 'cap-7-06/163'
    assert archive['sizes'] == [5, 5, 7, 6, 4, 5]
    assert archive['meetings'] == [[0, 3], [0, 4], [1, 2], [1, 3], [2, 3], [2, 5], [4, 5]]
    stars = J.stars_from(archive['sizes'], archive['meetings'])
    assert stars == archive['gate']['literal_supports']
    result = source('cap-7-06/163', stars, 'separate_singleton_explosive_stress', 3,
                    {'selection': 'historically observed finite large parity jump', 'denominator': 1})
    prereg = ROOT/'research'/HERE.parent.name/'supplemental_stress_freeze.md'
    result['supplemental_freeze_sha256'] = hashlib.sha256(prereg.read_bytes()).hexdigest()
    result['archived_source_sha256'] = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    save('supplemental_stress.json', result)
    for law, outcome in result['laws'].items():
        print(law, outcome['source_full_knots'],
              [(r['status'], r.get('births'), r.get('holders'), r.get('distinctions')) for r in outcome['stages']])


if __name__ == '__main__':
    main()
