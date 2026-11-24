# Two large files are stored compressed

Done by the thread on 2026-11-23 after every run had finished and every summary was written. Nothing here changes a result.

| Stored | Restores to | Size restored | SHA-256 of the restored file |
| --- | --- | --- | --- |
| `census/results.jsonl.gz` | `census/results.jsonl` (the shared runner's records of the census, 432 blocks) | 67,558,327 bytes | `a5bc20b2ab498f6d0a963f5f382e9ba3f27041999b04763021ef85feb563a345` |
| `b3_a4.json.gz` | `b3_a4.json` (the rerun of ticket A's 70 laws for prediction P3) | 26,962,230 bytes | `d92e368cc6551f4e490355c5ad7efcd3a26bbe27ecadf58d43edfd381d6037ee` |

Restore both with `gunzip -k` before running `summarize.py`, `p3_detail.py` or `extra_blocks.py --verify`. The summaries
(`summary.json`, `census_tables.json`, `p3_census_detail.json`, `summarize.log`) were made from the restored files.
