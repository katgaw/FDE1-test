"""Small notebook affordances: progress, and tables that don't need pandas.

Tier 1: stdlib + IPython. `table()` deliberately takes plain dicts rather than a
DataFrame, so a notebook can show results without pulling pandas in.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from contextlib import contextmanager
from typing import Any


@contextmanager
def spinner(label: str = "Working..."):
    """Print a label while a slow block runs.

        with spinner("Embedding 400 chunks..."):
            vectors = embed(chunks)
    """
    print(label, flush=True)
    try:
        yield
    finally:
        print(f"{label} done", flush=True)


def track(items: Sequence[Any], label: str = "") -> Iterator[Any]:
    """Iterate with a progress count. Needs a sequence, not a bare generator."""
    total = len(items)
    prefix = f"{label} " if label else ""
    for index, item in enumerate(items, start=1):
        yield item
        print(f"\r{prefix}{index}/{total}", end="", flush=True)
    print()


def table(rows: Iterable[dict], *, title: str = "") -> Any:
    """Render a list of dicts as a markdown table.

    Column order follows first appearance across the rows, so the first dict's keys
    lead and any later additions get appended rather than silently dropped.
    """
    from IPython.display import Markdown

    rows = list(rows)
    if not rows:
        body = f"**{title}**\n\n_(no rows)_" if title else "_(no rows)_"
        return Markdown(body)

    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)

    def cell(value: Any) -> str:
        return "" if value is None else str(value).replace("|", r"\|")

    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    lines += [
        "| " + " | ".join(cell(row.get(col)) for col in columns) + " |" for row in rows
    ]

    body = "\n".join(lines)
    return Markdown(f"**{title}**\n\n{body}" if title else body)
