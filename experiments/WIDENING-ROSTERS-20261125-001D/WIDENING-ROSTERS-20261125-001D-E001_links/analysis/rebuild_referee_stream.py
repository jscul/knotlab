"""Restore the optional combined referee gzip exactly from the hash-matched primary streams."""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import shutil


def rebuild(artifacts,destination):
    if destination.exists():
        raise FileExistsError(destination)
    second=artifacts/'referee'
    first=artifacts/'projection'
    rows=[json.loads(l) for l in (second/'cases.jsonl').read_text().splitlines()]
    with destination.open('xb') as out:
        for row in rows:
            if row['rule']!='MOST':
                continue
            start=out.tell()
            assert start==row['projection_gzip_offset']
            source=first/'triples'/(row['projection_sha256']+'.jsonl.gz')
            with gzip.open(source,'rb') as inp, gzip.GzipFile(fileobj=out,mode='wb',filename='',compresslevel=1,mtime=0) as member:
                shutil.copyfileobj(inp,member,1024*1024)
            assert out.tell()-start==row['projection_gzip_bytes']
    expected=json.loads((second/'summary.json').read_text())['files_sha256']['literal_masks.jsonl.gz']
    h=sha256()
    with destination.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    if h.hexdigest()!=expected:
        raise ValueError('reconstructed referee file differs in SHA-256')
    print(expected,destination.stat().st_size)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifacts',type=Path)
    parser.add_argument('destination',type=Path)
    args=parser.parse_args()
    rebuild(args.artifacts,args.destination)
