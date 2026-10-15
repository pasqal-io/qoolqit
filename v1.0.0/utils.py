from __future__ import annotations

from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def fig_to_html(fig: Figure) -> str:
    buffer = StringIO()
    fig.savefig(buffer, format="svg")
    plt.close()
    return buffer.getvalue()
