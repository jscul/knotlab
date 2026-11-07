#!/usr/bin/env python3
"""Install the post-commit hook that publishes the research workspace's record automatically.

Usage: python3 scripts/install_hook.py --workspace DIR [--site DIR] [--force]

After any commit in the workspace that touches proofs/, experiments/, artifacts/, research/, tickets/
or docs/, the hook starts scripts/publish.py in the background (as a transient systemd user unit when
it can, so it outlives the session that made the commit) and returns at once. Set KNOTLAB_PUBLISH=off
in a commit's environment to skip it.
"""
import argparse
import shlex
import stat
import sys
from pathlib import Path

K = Path(__file__).resolve().parent.parent

HOOK = """#!/bin/sh
# Installed by knotlab's scripts/install_hook.py. After a commit that touches the research record,
# publish it to knotlab and jscul.dev in the background. Set KNOTLAB_PUBLISH=off to skip.
[ "${{KNOTLAB_PUBLISH:-on}}" = off ] && exit 0
git diff-tree --root --no-commit-id --name-only -r HEAD \\
  | grep -qE '^(proofs|experiments|artifacts|research|tickets|docs)/' || exit 0
PUBLISH={publish}
SITE={site}
STATUS={status}
[ -f "$PUBLISH" ] || exit 0
WS="$(git rev-parse --show-toplevel)"
if [ -f "$STATUS" ] && grep -q '"result": "failed"' "$STATUS"; then
  echo "knotlab: the last publication failed; see {log}" >&2
fi
if systemd-run --user --quiet --collect --no-block --setenv=PATH="$PATH" --setenv=HOME="$HOME" \\
    python3 -B "$PUBLISH" --workspace "$WS" --site "$SITE" >/dev/null 2>&1; then
  :
else
  nohup setsid python3 -B "$PUBLISH" --workspace "$WS" --site "$SITE" >/dev/null 2>&1 &
fi
echo "knotlab: publishing this commit in the background (log: {log})" >&2
exit 0
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--site", type=Path, default=K.parent / "jscul-dev")
    parser.add_argument("--force", action="store_true", help="replace a different existing hook")
    args = parser.parse_args()
    hooks = args.workspace.resolve() / ".git" / "hooks"
    if not hooks.is_dir():
        sys.exit(f"not a git checkout: {args.workspace}")
    text = HOOK.format(publish=shlex.quote(str(K / "scripts" / "publish.py")),
                       site=shlex.quote(str(args.site.resolve())),
                       status=shlex.quote(str(K / ".git" / "publish-status.json")),
                       log=K / ".git" / "publish.log")
    target = hooks / "post-commit"
    if target.exists() and target.read_text() != text and not args.force:
        sys.exit(f"{target} exists and differs; rerun with --force to replace it")
    target.write_text(text)
    target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"installed {target}")


if __name__ == "__main__":
    main()
