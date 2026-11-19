import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import equation as Q
for v in json.load(open(HERE / 'cat_6.json')):
    print(v['sizes'], v['edges'], Q.equation(v['sizes'], [tuple(e) for e in v['edges']]))
