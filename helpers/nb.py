"""The four things every notebook does before it does anything else.

`bootstrap()` derives the repo root by walking up from the working directory, so
the same notebook works whether Jupyter was started at the repo root or in a
subfolder. That is the whole trick.

Tier 1: stdlib + python-dotenv only.
"""

from __future__ import annotations

import sys
from pathlib import Path

from .config import Config, from_env

_MARKER = "pyproject.toml"


def find_root(start: Path | None = None) -> Path:
    """Walk up from a notebook to the repo root.

    Walks up from the working directory, so it still finds the repo when Jupyter
    was started inside a subfolder.
    """
    if start is None:
        start = Path.cwd()

    for candidate in (start, *start.parents):
        if (candidate / _MARKER).exists() and (candidate / "helpers").is_dir():
            return candidate

    raise RuntimeError(
        f"Could not find the repo root above {start}.\n"
        f"Expected a directory containing both {_MARKER} and helpers/."
    )


def bootstrap(*, require: tuple[str, ...] = (), start: Path | None = None) -> Config:
    """Locate the repo root, load `.env`, check required keys, return the config.

    Args:
        require: env var names that must be set. Fails loudly and early with a
            message naming `.env.template`, rather than at the first model call
            with a 401 from somewhere three frames down.

    Returns:
        A `Config` with resolved paths and model settings.
    """
    root = find_root(start)

    # Put the repo root on the path so `from helpers import ...` keeps working in
    # cells that run after this one.
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError:  # pragma: no cover
        raise ModuleNotFoundError(
            "python-dotenv is missing. From the repo root, run `make setup`\n"
            "(or `uv sync`) and start the notebook again."
        ) from None

    load_dotenv(root / ".env")
    load_dotenv()  # a .env beside the notebook wins nothing, but is allowed

    import os

    missing = [name for name in require if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            f"Missing required environment variable(s): {', '.join(missing)}.\n"
            f"Copy {root / '.env.template'} to {root / '.env'} and fill it in."
        )

    return from_env(root)
