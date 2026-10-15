"""Zensical macros for the QoolQit documentation."""

from __future__ import annotations

import base64
import hashlib
import mimetypes
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbconvert import MarkdownExporter


def define_env(env):
    """Register the documentation macros."""

    @env.macro
    def notebook(path: str) -> str:
        """Execute a notebook (path relative to docs/) and render it as Markdown."""
        nb_path = Path(env.project_dir) / env.conf.get("docs_dir", "docs") / path
        # Cache on the notebook content so only edited notebooks are re-executed;
        # `zensical build --clean` wipes .cache and forces a full re-run.
        cached = (
            Path(env.project_dir)
            / ".cache"
            / "notebooks"
            / (hashlib.sha256(nb_path.read_bytes()).hexdigest() + ".md")
        )
        if cached.is_file():
            return cached.read_text()
        nb = nbformat.read(nb_path, as_version=4)
        NotebookClient(nb, resources={"metadata": {"path": str(nb_path.parent)}}).execute()
        body, resources = MarkdownExporter().from_notebook_node(nb)
        # Inline extracted images so the page needs no extra files.
        for name, data in resources.get("outputs", {}).items():
            mime = mimetypes.guess_type(name)[0]
            body = body.replace(
                f"]({name})", f"](data:{mime};base64,{base64.b64encode(data).decode()})"
            )
        cached.parent.mkdir(parents=True, exist_ok=True)
        cached.write_text(body)
        return body
