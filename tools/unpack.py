# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6", "pydantic>=2.7"]
# ///
"""Put the site's version of your course into the kit.

    uv run tools/unpack.py ~/Downloads/rl.zip

The zip is what "Download the course files" on the site's Educators page gives you. This
unpacks it into courses/rl/ and commits that state in your copy of the kit, so that from
then on `git diff` shows exactly what you have added. Nothing is pushed anywhere.

Use it the first time, and again whenever the site says the course has changed:

    git stash                        set your work aside
    uv run tools/unpack.py rl.zip    bring in the site's version
    git stash pop                    put your work back on top

It refuses to run over work that is not committed (that is what `git stash` is for;
`--force` unpacks anyway). If the site's version lacks lines that your last commit had,
it tells you which: git still has them. Your source/ folder is never touched.

Without uv: `pip install pyyaml pydantic`, then `python tools/unpack.py ...`.
"""

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
COURSES = ROOT / "courses"
sys.path.insert(0, str(HERE))

from rules import handin  # noqa: E402


def git(*args):
    """Run git in the kit. Returns (ok, output); (False, "") when there is no git."""
    try:
        done = subprocess.run(
            ["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=False
        )
    except OSError:
        return False, ""
    return done.returncode == 0, done.stdout


def main(argv=None):
    parser = argparse.ArgumentParser(description="Put the site's version of a course into the kit.")
    parser.add_argument("zip", help="The file downloaded from the site's Educators page.")
    parser.add_argument("--force", action="store_true", help="Unpack over your own changes.")
    options = parser.parse_args(argv)

    source = Path(options.zip).expanduser()
    if not source.is_file():
        print(f"{source}: there is no such file")
        return 1
    try:
        slug, files = handin.unzip(source)
    except handin.HandInError as error:
        print(f"{source.name}: {error}")
        print("  -> use the zip from 'Download the course files' on the site")
        return 1

    target = COURSES / slug
    path = f"courses/{slug}"
    if target.is_dir() and not options.force:
        _ok, pending = git("status", "--porcelain", "--", path)
        if pending.strip():
            print(f"{path} has work that is not committed:")
            print("".join(f"  {line}\n" for line in pending.splitlines()[:12]), end="")
            print("Set it aside first, then put it back on top of the site's version:")
            print(f"  git stash\n  uv run tools/unpack.py {options.zip}\n  git stash pop")
            return 1
    # What the site's version takes away from the last commit here. Usually someone
    # removed it on the site; it could also be work committed here and never handed in.
    lost = handin.compare(handin.files_of(target), files).lost if target.is_dir() else []

    # Out go the files the site no longer has; in come the site's. Only the kinds of file
    # a course is made of: source/ and anything else of yours stays where it is.
    if target.is_dir():
        for existing, name in list(handin.course_files(target)):
            if name not in files:
                existing.unlink()
    for name, data in files.items():
        (target / name).parent.mkdir(parents=True, exist_ok=True)
        (target / name).write_bytes(data)
    (target / "source").mkdir(exist_ok=True)
    print(f"Unpacked {len(files)} files into {path}/")

    git("add", "-A", "--", path)
    _ok, staged = git("diff", "--cached", "--name-only", "--", path)
    if not staged.strip():
        print("It is what your copy already had: nothing to commit.")
    else:
        message = f"{slug}: the site's version of {date.today():%d %B %Y}"
        ok, _out = git("commit", "-m", message, "--", path)
        if ok:
            print(f'Committed in your copy (on this computer only): "{message}"')
        else:
            print("Could not commit (is git set up? `git config user.name` and user.email).")
            print(f'Do it yourself: git commit -m "{message}" -- {path}')
    if lost:
        print("Note: the site's version no longer has this, which your last commit had:")
        print("".join(f"  {line}\n" for line in lost[:15]), end="")
        print("If someone removed it on the site, that is as it should be. If it was work")
        print(f"you committed without handing in, git still has it: git log -p -- {path}")
    print(f"Put the lecture material in {path}/source/ . It never leaves your computer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
