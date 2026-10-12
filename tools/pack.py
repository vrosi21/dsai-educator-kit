# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6", "pydantic>=2.7"]
# ///
"""Pack a course into the one file you hand in.

    uv run tools/pack.py rl

Runs the check first and refuses to pack a course that has errors. Then writes
`out/rl-<date>-<time>.zip` with the course's course.yaml and everything the site reads
under content/. Raw material (source/) is never packed.

Without uv: `pip install pyyaml pydantic`, then `python tools/pack.py rl`.
"""

import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check import ROOT, check, find  # noqa: E402
from rules import handin  # noqa: E402

OUT = ROOT / "out"


def main(argv=None):
    names = sys.argv[1:] if argv is None else argv
    if len(names) != 1:
        print("usage: tools/pack.py <course>      for example: tools/pack.py rl")
        return 1
    folder = find(names[0])
    if folder is None:
        print(f"{names[0]}: there is no course folder courses/{names[0]} with a course.yaml")
        return 1

    report, _bundle = check(folder)
    print(report.format())
    if not report.ok:
        print("\nNot packed: fix what is listed above and run this again.")
        return 1

    OUT.mkdir(exist_ok=True)
    target = OUT / f"{folder.name}-{datetime.now():%Y%m%d-%H%M}.zip"
    target.write_bytes(handin.pack(folder))
    count = sum(1 for _ in handin.course_files(folder))
    print(f"\nPacked {count} files into {target.relative_to(ROOT).as_posix()}")
    print("Hand that file in. Nothing from source/ is in it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
