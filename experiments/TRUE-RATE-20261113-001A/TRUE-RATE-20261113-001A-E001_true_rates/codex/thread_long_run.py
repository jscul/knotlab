"""Thread-written launcher (not Codex's): run run_rate.py as a background job.

Codex's runner caps one foreground command at 1190 s and each process at
2304 MiB, which suits a Codex session but not the thread's long background
run.  This wrapper changes only those resource constants and the two size
caps of run_family; the science code is untouched and every row still records
its limits.  Usage, from the repository root:

  .venv/bin/python -B .../codex/thread_long_run.py --memory-mib 7168 \
      --table-limit 2000000 --node-limit 20000000 -- \
      --workers 2 --seconds-limit 1800 --command-seconds 7000 \
      --output true_rate_flat4.jsonl --only 269 302 642 908
"""
import argparse
import functools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run_rate  # noqa: E402
import true_rate  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--memory-mib", type=int, required=True)
    parser.add_argument("--table-limit", type=int, default=true_rate.TABLE_LIMIT)
    parser.add_argument("--node-limit", type=int, default=true_rate.NODE_LIMIT)
    parser.add_argument("rest", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    rest = args.rest[1:] if args.rest[:1] == ["--"] else args.rest
    run_rate.MEMORY_MIB = args.memory_mib
    run_rate.MAX_COMMAND_SECONDS = 1e6
    true_rate.run_family = functools.partial(
        true_rate.run_family, table_limit=args.table_limit, node_limit=args.node_limit)
    return run_rate.main(rest)


if __name__ == "__main__":
    sys.exit(main())
