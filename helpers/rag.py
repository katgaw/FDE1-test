"""Small RAG plumbing shared across the LangChain demos (04, 06)."""


def format_docs(docs) -> str:
    """Join retrieved LangChain documents into one context string."""
    return "\n\n".join(d.page_content for d in docs)
