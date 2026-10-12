# Copied from the site's code by `manage.py export_authoring`. Do not edit here.
"""What a sync run found, phrased for whoever has to fix it — usually an AI reading stdout.

Every problem names the file, the line and the field, and where possible says what to do.
"""

from dataclasses import dataclass, field

ERROR = "error"
WARNING = "warning"


@dataclass
class Issue:
    level: str
    file: str
    message: str
    line: int | None = None
    where: str = ""
    hint: str = ""

    def format(self):
        location = self.file + (f":{self.line}" if self.line else "")
        head = f"  {self.level.upper():7} {location}"
        if self.where:
            head += f"  {self.where}"
        lines = [head, f"          {self.message}"]
        if self.hint:
            lines.append(f"          -> {self.hint}")
        return "\n".join(lines)


@dataclass
class Report:
    course: str
    issues: list[Issue] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    status: str = "pending"  # synced | unchanged | checked | failed
    notes: list[str] = field(default_factory=list)

    def error(self, file, message, *, line=None, where="", hint=""):
        self.issues.append(Issue(ERROR, file, message, line, where, hint))

    def warn(self, file, message, *, line=None, where="", hint=""):
        self.issues.append(Issue(WARNING, file, message, line, where, hint))

    @property
    def errors(self):
        return [issue for issue in self.issues if issue.level == ERROR]

    @property
    def warnings(self):
        return [issue for issue in self.issues if issue.level == WARNING]

    @property
    def ok(self):
        return not self.errors

    def format(self):
        summary = {
            "synced": "synced",
            "unchanged": "unchanged since last sync",
            "checked": "valid (check only, database not touched)",
            "failed": "FAILED - database not updated for this course",
        }.get(self.status, self.status)
        tally = []
        if self.errors:
            tally.append(f"{len(self.errors)} error{'s' * (len(self.errors) != 1)}")
        if self.warnings:
            tally.append(f"{len(self.warnings)} warning{'s' * (len(self.warnings) != 1)}")
        head = f"{self.course}: {summary}"
        if tally:
            head += f" ({', '.join(tally)})"
        lines = [head]
        if self.counts and self.ok:
            parts = [f"{count} {name}" for name, count in self.counts.items() if count]
            if parts:
                lines.append("  " + ", ".join(parts))
        lines += [f"  {note}" for note in self.notes]
        # Errors first: they are what blocks the sync.
        ordered = sorted(self.issues, key=lambda i: (i.level != ERROR, i.file, i.line or 0))
        lines += [issue.format() for issue in ordered]
        return "\n".join(lines)
