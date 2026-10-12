# Copied from the site's code by `manage.py export_authoring`. Do not edit here.
"""Read YAML strictly, and remember where every value came from.

PyYAML's `safe_load` gives data but no positions and no record of how a string was quoted.
Both matter here: errors must point at a line, and a double-quoted string is where LaTeX gets
silently destroyed ("\\theta" becomes a TAB followed by "heta"). So the text is parsed twice:
once into PyYAML's node graph, which is walked for positions and style checks, and once into
plain data.
"""

from dataclasses import dataclass, field
from typing import Any

import yaml

BLOCK_HINT = "write it as a block scalar:  key: |-   then the text indented on the lines below"


@dataclass
class Loaded:
    data: Any
    # Field path -> 1-based line of the value. Paths look like ("cards", 3, "a").
    lines: dict[tuple, int] = field(default_factory=dict)
    # Field path -> line on which the text of a string value starts (differs for block scalars).
    text_lines: dict[tuple, int] = field(default_factory=dict)
    # Field path -> the value exactly as typed, before YAML turned `yes` into True.
    raw: dict[tuple, str] = field(default_factory=dict)

    def line(self, path):
        """Line of the nearest known ancestor of `path`."""
        path = tuple(path)
        while path and path not in self.lines:
            path = path[:-1]
        return self.lines.get(path)

    def text_line(self, path):
        return self.text_lines.get(tuple(path)) or self.line(path) or 1


def load_yaml(text, *, file, report, line_offset=0):
    """Parse `text`; report problems against `file`. Returns None when it cannot be parsed."""
    try:
        for event in yaml.parse(text, Loader=yaml.SafeLoader):
            if isinstance(event, yaml.AliasEvent) or getattr(event, "anchor", None):
                report.error(
                    file,
                    "YAML anchors and aliases (&name, *name) are not allowed",
                    line=event.start_mark.line + 1 + line_offset,
                    hint="write the value out in full where it is used",
                )
        root = yaml.compose(text, Loader=yaml.SafeLoader)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        problem = getattr(exc, "problem", None) or str(exc)
        report.error(
            file,
            f"not valid YAML: {problem}",
            line=(mark.line + 1 + line_offset) if mark else None,
            hint="check indentation (2 spaces, no tabs) and that every key ends with a colon",
        )
        return None

    loaded = Loaded(data=None)
    if root is None:
        return loaded
    _walk(root, (), text, file, report, loaded, line_offset)
    loaded.data = yaml.load(text, Loader=yaml.SafeLoader)  # noqa: S506 - SafeLoader
    return loaded


def _walk(node, path, text, file, report, loaded, offset):
    line = node.start_mark.line + 1 + offset
    loaded.lines[path] = line

    if isinstance(node, yaml.MappingNode):
        seen = {}
        for key_node, value_node in node.value:
            key_line = key_node.start_mark.line + 1 + offset
            if not isinstance(key_node, yaml.ScalarNode):
                report.error(file, "a key must be a plain word", line=key_line)
                continue
            key = key_node.value
            if key == "<<":
                report.error(file, "YAML merge keys (<<) are not allowed", line=key_line)
                continue
            if key in seen:
                report.error(
                    file,
                    f"the key '{key}' appears twice in the same block",
                    line=key_line,
                    where=_dotted(path + (key,)),
                    hint=f"it is first set on line {seen[key]}; YAML would silently keep only one",
                )
            seen[key] = key_line
            _walk(value_node, path + (key,), text, file, report, loaded, offset)

    elif isinstance(node, yaml.SequenceNode):
        for index, item in enumerate(node.value):
            _walk(item, path + (index,), text, file, report, loaded, offset)

    elif isinstance(node, yaml.ScalarNode):
        # In a block scalar the indicator (| or >) sits on the key's line; the text starts below.
        loaded.text_lines[path] = line + 1 if node.style in ("|", ">") else line
        if node.style is None:
            loaded.raw[path] = node.value
        if node.style == '"':
            raw = text[node.start_mark.index : node.end_mark.index]
            if "\\" in raw:
                report.error(
                    file,
                    "double-quoted text contains a backslash. YAML treats it as an escape "
                    '("\\t" is a TAB, "\\f" a form feed), which silently corrupts LaTeX',
                    line=line,
                    where=_dotted(path),
                    hint=BLOCK_HINT,
                )


def _dotted(path):
    out = ""
    for part in path:
        out += f"[{part}]" if isinstance(part, int) else (f".{part}" if out else str(part))
    return out


dotted = _dotted


def split_front_matter(text):
    """Split a Markdown file into (yaml text, body, line the body starts on).

    Returns (None, text, 1) when the file does not open with a `---` line.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text, 1
    for index in range(1, len(lines)):
        if lines[index].strip() in ("---", "..."):
            front = "\n".join(lines[1:index])
            body = "\n".join(lines[index + 1 :])
            return front, body, index + 2
    return None, text, 1
