"""On-disk, embedded Qdrant — embed the corpus once into a local folder, then every
notebook (and every cell re-run) reads it back in milliseconds. No server, no per-query
network round-trip, so retrieval cost no longer scales with how far away a box is or how
big `k` is.

Qdrant's local mode is single-writer: only one process may hold the folder open at a
time. ``local_client`` keeps a notebook to ONE cached handle, so re-running a connect
cell is safe. If you hit ``Storage folder ... already accessed by another instance``,
another notebook's kernel is holding it — restart that kernel (or this one).
"""
from pathlib import Path

from helpers.config import ROOT

LOCAL_QDRANT = ROOT / ".qdrant_local"   # gitignored; persists across sessions
COLLECTION = "eu_ai_act"

_clients: dict[str, object] = {}


def local_client(path=LOCAL_QDRANT):
    """One embedded ``QdrantClient`` per path per process.

    Re-running a connect cell returns the same handle instead of opening a second one
    and tripping Qdrant's single-writer lock.
    """
    from qdrant_client import QdrantClient

    key = str(path)
    if key not in _clients:
        Path(key).mkdir(parents=True, exist_ok=True)
        _clients[key] = QdrantClient(path=key)
    return _clients[key]


def load_local_store(embeddings, *, collection=COLLECTION, path=LOCAL_QDRANT):
    """Wrap an already-built local collection as a LangChain ``QdrantVectorStore``.

    Raises if the index isn't there yet — Demo 04 builds it; 06 and 08 reuse it.
    """
    from langchain_qdrant import QdrantVectorStore

    client = local_client(path)
    if not (client.collection_exists(collection) and client.count(collection).count):
        raise RuntimeError(
            f"No local '{collection}' index at {path} yet — run Demo 04 first to build it."
        )
    return QdrantVectorStore(client=client, collection_name=collection, embedding=embeddings)
