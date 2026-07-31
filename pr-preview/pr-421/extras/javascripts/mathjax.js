window.MathJax = {
  tex: {
    inlineMath: [
      ["\\(", "\\)"],
      ["$`", "`$"],
      ["$", "$"]
    ],
    displayMath: [
      ["\\[", "\\]"],
      ["$$`", "`$$"],
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

document$.subscribe(() => {
  MathJax.typesetClear();
  MathJax.texReset();
  MathJax.typesetPromise().catch(error => console.error(error));
});
