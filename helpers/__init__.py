"""Shared helpers for the FDE curriculum.

Two tiers, and the split matters:

**Tier 1** — `nb`, `config`, `display`, `ui`. Needs only stdlib, `python-dotenv`,
and IPython. Re-exported here, so `from helpers import nb, show` works in a
Jupyter kernel started from this repo.

**Tier 2** — `judge`, `vectorstore`, `rag`, `sdg`. Pulls in litellm, a vector store,
and so on. Import these explicitly (`from helpers import judge`).

**This module must never import tier 2.** Doing so would drag litellm into every
notebook, including ones that never call a model.

The boundary rule for what belongs here at all: keep the from-scratch teaching code
in the notebook; only pure plumbing moves into `helpers/`. If reading it is the
lesson, it stays in the lesson.
"""

from .config import Config
from .display import show, stream_chat, stream_md
from .nb import bootstrap, find_root
from .ui import spinner, table, track

__all__ = [
    "Config",
    "bootstrap",
    "find_root",
    "show",
    "spinner",
    "stream_chat",
    "stream_md",
    "table",
    "track",
]
