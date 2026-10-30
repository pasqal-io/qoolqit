"""Zensical macros for the QoolQit documentation.

Zensical cannot render notebooks, so each `docs/<page>.ipynb` has a `docs/<page>.md`
placeholder calling `{{ notebook("<page>.ipynb") }}`: the macro executes the notebook
at build time and returns it as Markdown.
"""

from __future__ import annotations

import base64
import hashlib
import mimetypes
import time
from pathlib import Path

import matplotlib
import nbformat
from nbclient import NotebookClient
from nbconvert import MarkdownExporter
from traitlets.config import Config

# markdown-exec runs page code inside the docs build: keep Matplotlib off interactive GUI
# backends (TkAgg locally), as on headless CI
matplotlib.use("agg")


def define_env(env):
    """Register the macros; called by Zensical."""
    root = Path(env.conf.get("root_dir", "."))
    docs_dir = root / env.conf.get("docs_dir", "docs")
    # Wiped by `zensical build --clean`, which forces every notebook to run again.
    cache_dir = root / ".cache" / "notebooks"

    @env.macro
    def notebook(path: str) -> str:
        """Execute a notebook (path relative to docs/) and render it as Markdown."""
        nb_path = docs_dir / path
        # Keyed on the notebook content, so only edited notebooks are executed again.
        cached = cache_dir / f"{hashlib.sha256(nb_path.read_bytes()).hexdigest()}.md"
        if not cached.is_file():
            cached.parent.mkdir(parents=True, exist_ok=True)
            start = time.perf_counter()
            cached.write_text(_render(nb_path))
            print(f"✓ {path} ({time.perf_counter() - start:.1f}s)", flush=True)
        return cached.read_text()


def _render(nb_path: Path) -> str:
    """Execute the notebook and convert it to Markdown, with its images inlined."""
    nb = nbformat.read(nb_path, as_version=4)
    # Encrypt kernel traffic with CurveZMQ, which also stops ipykernel's plain-TCP warning.
    config = Config({"KernelManager": {"transport_encryption": "auto"}})
    NotebookClient(
        nb, config=config, resources={"metadata": {"path": str(nb_path.parent)}}
    ).execute()
    markdown, resources = MarkdownExporter().from_notebook_node(nb)
    # The exporter extracts images to separate files: embed them so the page is self-contained.
    for name, data in resources.get("outputs", {}).items():
        markdown = markdown.replace(f"]({name})", f"]({_data_uri(name, data)})")
    return markdown


def _data_uri(name: str, data: bytes) -> str:
    """Encode a file's bytes as a data URI, with the MIME type guessed from its name."""
    mime = mimetypes.guess_type(name)[0]
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"
