#!/usr/bin/env python3
"""Publish the research workspace's committed record here, then start the jscul.dev sync.

Usage: python3 scripts/publish.py --workspace DIR [--no-push] [--sync-site]

The workspace's epic-closure command (scripts/commit_epic.py, through scripts/publish_records.py)
runs this after every closed epic, so each one is published without anyone asking; it can also be
run by hand. Each step is skipped when there is nothing to do:

1. Copy from the workspace's HEAD every dated folder in proofs/, experiments/, artifacts/ and
   research/ from 19 October 2026 on, the tickets of those folders and their epics, and the four
   documents in docs/. Only committed files are read, so work in progress never leaves the workspace.
2. Refuse anything that looks like a credential or an email address, and files over 50 MB.
3. Rebuild the generated files (scripts/build.py) and run the tests. A failing record test stops the
   run and undoes its changes; a failing curation test is reported, because only a person can update
   a THEORY.md card.
4. Commit and push this repository.
5. Start the sync-knotlab workflow of jscul/jscul-dev, which copies what the site shows from this
   repository, checks it (lint, build, deploy:check and HTTP checks) and pushes; Cloudflare deploys
   the push. The workflow also runs every six hours, so a missed start only delays the site.
   --sync-site starts it even when nothing new was published here, for instance after a hand edit
   to THEORY.md.

Each run appends to .git/publish.log and writes .git/publish-status.json. Runs never overlap: a run
that finds another in progress leaves a flag, and the running one goes round again.
"""
import argparse
import fcntl
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

K = Path(__file__).resolve().parent.parent
GIT_DIR = K / ".git"
LOG = GIT_DIR / "publish.log"
STATUS = GIT_DIR / "publish-status.json"
LOCK = GIT_DIR / "publish.lock"
PENDING = GIT_DIR / "publish.pending"

TOPS = ("proofs", "experiments", "artifacts", "research")
DOCS = ("docs/KNOT_INTUITION.md", "docs/FOUNDATIONAL_THESIS.md", "docs/FOUNDATION_READING.md", "docs/COMMON_VERBIAGE.md")
MANAGED = (*TOPS, "tickets", "docs", "data", "RESULTS.md", "RANKING.md", "README.md")
DATED = re.compile(r"-(20\d{6})-\d{3}[A-Z]?$")
FIRST_DATE = "20261019"  # the knot test became canonical; earlier work is not published
MAX_BYTES = 50 * 1024 * 1024
BINARY = {".gz", ".pdf", ".png", ".jpg", ".npz", ".npy", ".pkl", ".zip", ".xz", ".bz2", ".olean"}
SECRET = re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}"
                    rb"|\bsk-[A-Za-z0-9_-]{32,}|\bAKIA[0-9A-Z]{16}\b|\bntn_[A-Za-z0-9]{30,}|\bxox[abprs]-[A-Za-z0-9-]{10,}")
EMAIL = re.compile(rb"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
ALLOWED_EMAIL = re.compile(rb"noreply|@example\.(?:com|org)$")
RECORD_TESTS = ("tests.test_records", "tests.test_theory", "tests.test_knotlab")
CURATION_TESTS = ("tests.test_curation",)
SITE_REPO = "jscul/jscul-dev"
SITE_WORKFLOW = "sync-knotlab.yml"


class Stop(Exception):
    """The run cannot continue; the message says why."""


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log(message):
    line = f"{now()} {message}"
    print(line, flush=True)
    with LOG.open("a") as handle:
        handle.write(line + "\n")


def run(cmd, cwd, env=None, timeout=1800, check=True):
    result = subprocess.run(cmd, cwd=cwd, env={**os.environ, **(env or {})}, capture_output=True,
                            text=True, timeout=timeout)
    if check and result.returncode != 0:
        tail = "\n".join((result.stdout + result.stderr).strip().splitlines()[-25:])
        raise Stop(f"{' '.join(cmd[:4])} failed in {cwd}:\n{tail}")
    return result


def git(repo, *args, **kw):
    return run(["git", "-C", str(repo), *args], cwd=repo, **kw)


def ensure_ready(repo, name):
    """A repository the run will commit to must be on main and clean, so only the run's changes get committed."""
    if git(repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip() != "main":
        raise Stop(f"{name} is not on main")
    if git(repo, "status", "--porcelain").stdout.strip():
        raise Stop(f"{name} has uncommitted changes; leaving it alone")
    for attempt in range(4):
        if git(repo, "fetch", "--quiet", "origin", "main", check=False).returncode == 0:
            break
        time.sleep(2 ** (attempt + 1))
    else:
        raise Stop(f"cannot fetch {name}")
    git(repo, "rebase", "--quiet", "origin/main")


def push(repo, name):
    for attempt in range(5):
        if git(repo, "push", "--quiet", "origin", "main", check=False).returncode == 0:
            return
        git(repo, "fetch", "--quiet", "origin", "main", check=False)
        git(repo, "rebase", "--quiet", "origin/main", check=False)
        time.sleep(2 ** (attempt + 1))
    raise Stop(f"cannot push {name}")


def undo(repo, paths):
    git(repo, "checkout", "--quiet", "--", *paths, check=False)
    git(repo, "clean", "-fdq", "--", *paths, check=False)


def workspace_paths(ws, commit):
    """The committed paths to publish: dated folders, their tickets and the working documents."""
    folders = []
    for top in TOPS:
        names = git(ws, "ls-tree", "-d", "--name-only", commit, f"{top}/").stdout.split()
        for path in names:
            match = DATED.search(path)
            if match and match.group(1) >= FIRST_DATE:
                folders.append(path)
    ids = {Path(p).name for p in folders}
    epics = {Path(p).name for p in folders if p.startswith("research/") and re.search(r"-\d{3}$", p)}
    tickets = {Path(p).stem for p in git(ws, "ls-tree", "--name-only", commit, "tickets/").stdout.split()}
    wanted = {t for t in tickets if t in ids or (len(t) > 1 and t[:-1] in epics and t[-1].isupper())}
    present_docs = [d for d in DOCS if git(ws, "cat-file", "-e", f"{commit}:{d}", check=False).returncode == 0]
    return sorted(folders), sorted(f"tickets/{t}.json" for t in wanted), present_docs


def extract(ws, commit, paths, dest):
    archive = subprocess.Popen(["git", "-C", str(ws), "archive", commit, "--", *paths], stdout=subprocess.PIPE)
    subprocess.run(["tar", "-x", "-C", str(dest)], stdin=archive.stdout, check=True)
    archive.stdout.close()
    if archive.wait() != 0:
        raise Stop("git archive failed")


def files_under(root):
    if not root.exists():
        return set()
    return {p.relative_to(root).as_posix() for p in root.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}


def mirror(src, folders, files):
    """Make each published folder and file equal to the workspace's; return the paths that changed."""
    changed = []
    for folder in folders:
        source, target = src / folder, K / folder
        wanted, present = files_under(source), files_under(target)
        for rel in sorted(wanted):
            new = (source / rel).read_bytes()
            if rel not in present or (target / rel).read_bytes() != new:
                (target / rel).parent.mkdir(parents=True, exist_ok=True)
                (target / rel).write_bytes(new)
                changed.append(f"{folder}/{rel}")
        for rel in sorted(present - wanted):
            (target / rel).unlink()
            changed.append(f"{folder}/{rel}")
    for rel in files:
        new = (src / rel).read_bytes()
        if not (K / rel).exists() or (K / rel).read_bytes() != new:
            (K / rel).parent.mkdir(parents=True, exist_ok=True)
            (K / rel).write_bytes(new)
            changed.append(rel)
    return changed


def screen(paths):
    """Refuse credentials, email addresses and oversized files among the changed files."""
    problems = []
    for rel in paths:
        path = K / rel
        if not path.exists():
            continue
        if path.stat().st_size > MAX_BYTES:
            problems.append(f"{rel}: larger than 50 MB")
            continue
        if path.suffix in BINARY:
            continue
        data = path.read_bytes()
        if SECRET.search(data):
            problems.append(f"{rel}: looks like a credential")
        for address in EMAIL.findall(data):
            if not ALLOWED_EMAIL.search(address):
                problems.append(f"{rel}: contains an email address")
                break
    return problems


def new_epics(folders):
    published = {p.name for p in (K / "research").iterdir()} if (K / "research").exists() else set()
    return sorted({Path(f).name for f in folders if f.startswith("research/") and re.search(r"-\d{3}$", f)} - published)


def publish_records(ws, push_enabled):
    """Steps 1 to 4. Returns the epics newly published, or None when this repository already held everything."""
    ensure_ready(K, "knotlab")
    commit = git(ws, "rev-parse", "HEAD").stdout.strip()
    folders, tickets, docs = workspace_paths(ws, commit)
    fresh = new_epics(folders)
    with tempfile.TemporaryDirectory(prefix="knotlab-publish-") as tmp:
        extract(ws, commit, [*folders, *tickets, *docs], Path(tmp))
        changed = mirror(Path(tmp), folders, [*tickets, *docs])
    if changed:
        try:
            problems = screen(changed)
            if problems:
                raise Stop("refusing to publish:\n" + "\n".join(problems[:20]))
            build = run([sys.executable, "-B", "scripts/build.py"], cwd=K)
            for line in build.stdout.splitlines():
                if line.startswith("placement:"):
                    log(line)
            run([sys.executable, "-B", "-m", "unittest", *RECORD_TESTS], cwd=K)
        except Stop:
            undo(K, MANAGED)
            raise
        git(K, "add", "--all", "--", *MANAGED)
    if not changed or git(K, "diff", "--cached", "--quiet", check=False).returncode == 0:
        log(f"knotlab already holds workspace {commit[:9]}")
        return None
    curation = run([sys.executable, "-B", "-m", "unittest", *CURATION_TESTS], cwd=K, check=False)
    if curation.returncode != 0:
        log("curation check failed: a THEORY.md card cites a record that is now superseded or qualified; "
            "it needs a person to update it\n" + "\n".join((curation.stdout + curation.stderr).strip().splitlines()[-12:]))
    subject = f"Publish {', '.join(fresh)}" if fresh else "Update the published record"
    body = (f"Copied from the research workspace at commit {commit[:9]}: {len(changed)} files changed.\n"
            "Published automatically by scripts/publish.py.")
    git(K, "commit", "--quiet", "-m", subject, "-m", body)
    if push_enabled:
        push(K, "knotlab")
    log(f"knotlab {git(K, 'rev-parse', 'HEAD').stdout.strip()[:9]}: {subject} ({len(changed)} files)")
    return fresh


def start_site_sync():
    """Step 5: start the site's sync workflow. Its six-hourly schedule covers a start that fails."""
    try:
        result = run(["gh", "workflow", "run", SITE_WORKFLOW, "--repo", SITE_REPO, "--ref", "main"], cwd=K,
                     check=False, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as error:
        result = None
        reason = str(error)
    else:
        reason = (result.stdout + result.stderr).strip().splitlines()[-1:] if result.returncode else ""
    if result is not None and result.returncode == 0:
        log(f"started {SITE_REPO}'s {SITE_WORKFLOW}")
        return "started"
    log(f"could not start {SITE_REPO}'s {SITE_WORKFLOW} ({reason}); its six-hourly run will sync the site")
    return "not started"


def publish_once(args):
    status = {"started": now(), "workspace": str(args.workspace)}
    try:
        fresh = publish_records(args.workspace, not args.no_push)
        status.update(knotlab=git(K, "rev-parse", "HEAD").stdout.strip(), published=fresh or [])
        if not args.no_push and (fresh is not None or args.sync_site):
            status["site"] = start_site_sync()
        status["result"] = "ok"
    except (Stop, subprocess.TimeoutExpired, OSError) as error:
        status.update(result="failed", error=str(error))
        log(f"failed: {error}")
    status["finished"] = now()
    STATUS.write_text(json.dumps(status, indent=1) + "\n")
    return status["result"] == "ok"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--workspace", type=Path, required=True, help="the research workspace's checkout")
    parser.add_argument("--no-push", action="store_true", help="commit here but push nothing and start no sync")
    parser.add_argument("--sync-site", action="store_true", help="start the site sync even if nothing new was published")
    args = parser.parse_args()
    args.workspace = args.workspace.resolve()
    with LOCK.open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            PENDING.write_text(now() + "\n")
            print("another publication is running; it will run again when it finishes")
            return 0
        ok = True
        while True:
            PENDING.unlink(missing_ok=True)
            ok = publish_once(args)
            if not ok or not PENDING.exists():
                break
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
