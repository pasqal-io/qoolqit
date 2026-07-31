window.MathJax = {
  tex: {
    inlineMath: [
      ["\\(", "\\)"],
      ["$", "$"]
    ],
    displayMath: [
      ["\\[", "\\]"],
      ["$$", "$$"]
    ],
    processEscapes: true,
    processEnvironments: true
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass:
      "arithmatex|jp-RenderedMarkdown|jp-RenderedHTMLCommon"
  }
};

function normalizeNotebookMath() {
  document
    .querySelectorAll(".jp-RenderedMarkdown, .jp-RenderedHTMLCommon")
    .forEach(container => {
      const walker = document.createTreeWalker(
        container,
        NodeFilter.SHOW_TEXT
      );

      const nodes = [];

      while (walker.nextNode()) {
        nodes.push(walker.currentNode);
      }

      nodes.forEach(node => {
        if (node.parentElement?.closest("code, pre, script, style")) {
          return;
        }

        node.nodeValue = node.nodeValue
          .replace(/\$\$`([\s\S]*?)`\$\$/g, "\\[$1\\]")
          .replace(/\$`([^`\n]+?)`\$/g, "\\($1\\)");
      });
    });
}

document$.subscribe(() => {
  normalizeNotebookMath();
  MathJax.typesetClear();
  MathJax.texReset();
  MathJax.typesetPromise().catch(error => console.error(error));
});
