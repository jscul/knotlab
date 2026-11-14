"""Losslessly compact this referee's large outputs, checking round-trip hashes."""
import gzip,hashlib,json,shutil
from pathlib import Path
P=Path(__file__).resolve().parent
receipts=[]
for name in ['min_path_results.jsonl','lasso_automaton_results.jsonl']:
    p=P/name;q=P/(name+'.gz')
    if not p.exists():continue
    before=hashlib.sha256(p.read_bytes()).hexdigest()
    with p.open('rb') as src,gzip.open(q,'wb',compresslevel=6) as dst:shutil.copyfileobj(src,dst)
    with gzip.open(q,'rb') as src:after=hashlib.file_digest(src,'sha256').hexdigest()
    assert before==after
    receipts.append(dict(file=q.name,uncompressed_sha256=before,uncompressed_bytes=p.stat().st_size,compressed_bytes=q.stat().st_size,round_trip_verified=True))
    p.unlink() # only our own, byte-for-byte preserved output
(P/'compression_receipt.json').write_text(json.dumps(receipts,indent=2)+'\n')
print(json.dumps(receipts))
