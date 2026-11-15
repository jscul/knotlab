#!/usr/bin/env python3
"""Check one source-zero closure's exact file bindings; no scientific theorem claim."""
from pathlib import Path
import hashlib
import json
import sys
sys.dont_write_bytecode = True
base = Path(__file__).resolve().parent
root = base.parents[2]
inputs = json.loads((base / 'ledger_inputs.json').read_text())
checks = {}
for item in inputs['evidence']:
    ticket = item['ticket_id']
    values = {}
    node = json.loads((root / 'tickets' / (ticket + '.json')).read_text())
    values['ticket_digest'] = hashlib.sha256((root / 'tickets' / (ticket + '.json')).read_bytes()).hexdigest() == item['ticket_sha256']
    values['terminal_status_class'] = node.get('status_class') == item['status_class'] and node.get('status_class') in {'proved', 'refuted', 'obstructed', 'supported', 'closed-null', 'complete'}
    values['accepted_identity'] = node.get('fields', {}).get('accepted_artifact_id') == item['artifact_id']
    for label, binding in item['files'].items():
        path = root / binding['path']
        values[label + '_digest'] = path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == binding['sha256']
    manifest = json.loads((root / item['files']['manifest']['path']).read_text())
    values['terminal_manifest'] = manifest.get('status') in {'Proved', 'Obstructed'}
    values['manifest_identity'] = manifest.get('artifact_id') == item['artifact_id'] and manifest.get('ticket') == ticket
    result = json.loads((root / item['files']['result']['path']).read_text())
    values['passing_result'] = result.get('status') == 'passed'
    checks[ticket] = {'pass': all(values.values()), 'checks': values}
for index, binding in enumerate(inputs.get('notes', [])):
    path = root / binding['path']
    checks['note_' + str(index)] = {'pass': path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == binding['sha256'], 'path': binding['path']}
passed = bool(inputs['evidence']) and all(item['pass'] for item in checks.values())
print(json.dumps({'status': 'passed' if passed else 'failed', 'checks': checks}, indent=2, sort_keys=True))
sys.exit(0 if passed else 1)
