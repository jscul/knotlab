#!/usr/bin/env python3
"""Publish the research workspace's committed record here, then update jscul.dev.

Usage: python3 scripts/publish.py --workspace DIR [--site DIR] [--no-push] [--no-site]

The workspace's post-commit hook (scripts/install_hook.py) runs this in the background, so every
closed epic is published without anyone asking; it can also be run by hand. Each step is skipped when
there is nothing to do:

1. Copy from the workspace's HEAD every dated folder in proofs/, experiments/, artifacts/ and
   research/ from 19 October 2026 on, the tickets of those folders and their epics, and the four
   documents in docs/. Only committed files are read, so work in progress never leaves the workspace.
2. Refuse anything that looks like a credential or an email address, and files over 50 MB.
3. Rebuild the generated files (scripts/build.py) and run the tests. A failing record test stops the
   run and undoes its changes; a failing curation test is reported, because only a person can update
   a THEORY.md card.
4. Commit and push this repository.
5. Sync the site from this repository (npm run sync:knotlab), check it (lint, build, deploy:check and
   HTTP checks), commit and push. Cloudflare deploys the push.

Each run appends to .git/publish.log and writes .git/publish-status.json. Runs never overlap: a run
that finds another in progress leaves a flag, and the running one goes round again.
"""
import argparse
import fcntl
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
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
SITE_PATHS = ("src/content", "public/notes")
LIVE_PAGE = "https://jscul.dev/proofs"


class Stop(Exception):
    """The run cannot continue; the message says why."""


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log(message):
    line = f"{now()} {message}"
    print(line, flush=True)
    with LOG.open("a") as handle:
        handle.write(line + "\n")


def run(cmd, cwd, env=None, timeout=1800, check=True, binary=False):
    result = subprocess.run(cmd, cwd=cwd, env={**os.environ, **(env or {})}, capture_output=True,
                            text=not binary, timeout=timeout)
    if check and result.returncode != 0:
        output = result.stdout + result.stderr if not binary else b""
        tail = "\n".join(str(output).strip().splitlines()[-25:])
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
    """Steps 1 to 4. Returns this repository's commit and the epics newly published."""
    ensure_ready(K, "knotlab")
    commit = git(ws, "rev-parse", "HEAD").stdout.strip()
    folders, tickets, docs = workspace_paths(ws, commit)
    fresh = new_epics(folders)
    with tempfile.TemporaryDirectory(prefix="knotlab-publish-") as tmp:
        extract(ws, commit, [*folders, *tickets, *docs], Path(tmp))
        changed = mirror(Path(tmp), folders, [*tickets, *docs])
    if not changed:
        log(f"knotlab already holds workspace {commit[:9]}")
        return git(K, "rev-parse", "HEAD").stdout.strip(), []
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
    curation = run([sys.executable, "-B", "-m", "unittest", *CURATION_TESTS], cwd=K, check=False)
    if curation.returncode != 0:
        log("curation check failed: a THEORY.md card cites a record that is now superseded or qualified; "
            "it needs a person to update it\n" + "\n".join((curation.stdout + curation.stderr).strip().splitlines()[-12:]))
    git(K, "add", "--all", "--", *MANAGED)
    if git(K, "diff", "--cached", "--quiet", check=False).returncode == 0:
        log(f"knotlab already holds workspace {commit[:9]}")
        return git(K, "rev-parse", "HEAD").stdout.strip(), []
    subject = f"Publish {', '.join(fresh)}" if fresh else "Update the published record"
    body = (f"Copied from the research workspace at commit {commit[:9]}: {len(changed)} files changed.\n"
            "Published automatically by scripts/publish.py.")
    git(K, "commit", "--quiet", "-m", subject, "-m", body)
    if push_enabled:
        push(K, "knotlab")
    head = git(K, "rev-parse", "HEAD").stdout.strip()
    log(f"knotlab {head[:9]}: {subject.lower()} ({len(changed)} files)")
    return head, fresh


def site_step(site, knotlab_commit, push_enabled):
    """Step 5. Returns the site's new commit, or None when the site already matches."""
    ensure_ready(site, "jscul-dev")
    npm = {"KNOTLAB_DIR": str(K)}
    run(["npm", "run", "--silent", "sync:knotlab", "--", "--from", str(K), "--commit", knotlab_commit], cwd=site, env=npm)
    if not git(site, "status", "--porcelain").stdout.strip():
        log("jscul.dev already matches knotlab")
        return None
    try:
        for script in ("check:intuitions", "check:theory", "lint", "build", "deploy:check", "check:http"):
            run(["npm", "run", "--silent", script], cwd=site, env=npm, timeout=1800)
    except Stop:
        undo(site, SITE_PATHS)
        raise
    git(site, "add", "--all", "--", *SITE_PATHS)
    git(site, "commit", "--quiet", "-m", f"Sync knotlab {knotlab_commit[:7]}",
        "-m", "Synced automatically by knotlab's scripts/publish.py after lint, build, deploy:check and HTTP checks.")
    if push_enabled:
        push(site, "jscul-dev")
    head = git(site, "rev-parse", "HEAD").stdout.strip()
    log(f"jscul-dev {head[:9]}: synced knotlab {knotlab_commit[:9]}")
    return head


def wait_until_live(titles, minutes=10):
    """Poll the live proofs page until it lists the newest titles; Cloudflare usually takes a minute or two."""
    deadline = time.time() + minutes * 60
    while time.time() < deadline:
        try:
            page = urllib.request.urlopen(LIVE_PAGE, timeout=30).read().decode("utf-8", "replace")
            if all(title in page for title in titles):
                return True
        except OSError:
            pass
        time.sleep(30)
    return False


def newest_titles(epics):
    titles = []
    for epic in epics:
        for path in sorted((K / "research" / epic / "discoveries").glob("*.json")):
            titles.append(html.escape(json.loads(path.read_text())["title"]))
    return titles[:3]


def publish_once(args):
    status = {"started": now(), "workspace": str(args.workspace)}
    try:
        knotlab_commit, fresh = publish_records(args.workspace, not args.no_push)
        status.update(knotlab=knotlab_commit, published=fresh)
        if not args.no_site:
            site_commit = site_step(args.site, knotlab_commit, not args.no_push)
            status["site"] = site_commit
            if site_commit and not args.no_push:
                live = wait_until_live(newest_titles(fresh)) if fresh else True
                status["live"] = live
                log("jscul.dev is live" if live else "jscul.dev has not shown the new results yet")
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
    parser.add_argument("--site", type=Path, default=K.parent / "jscul-dev", help="jscul-dev's checkout")
    parser.add_argument("--no-push", action="store_true", help="commit locally but push nothing")
    parser.add_argument("--no-site", action="store_true", help="publish this repository only")
    args = parser.parse_args()
    args.workspace, args.site = args.workspace.resolve(), args.site.resolve()
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
