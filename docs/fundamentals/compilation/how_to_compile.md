
```python exec="on" source="material-block" result="json" session="drives"
from qoolqit import AnalogDevice

device = AnalogDevice()
program.compile_to(device)
print(program) # markdown-exec: hide
```

Now that the program has been compiled, we can inspect the compiled sequence, which is an instance of a Pulser `Sequence`.

```python exec="on" source="material-block" html="1" session="drives"
pulser_sequence = program.compiled_sequence
```

Finally, we can draw both the original program and the compiled sequence.

```python exec="on" source="material-block" html="1" session="drives"
import matplotlib.pyplot as plt # markdown-exec: hide
from docs.utils import fig_to_html # markdown-exec: hide
program.draw()
fig_original = program.draw(return_fig = True) # markdown-exec: hide
print(fig_to_html(fig_original)) # markdown-exec: hidee
```

```python exec="on" source="material-block" html="1" session="drives"
program.draw(compiled = True)
fig_compiled = program.draw(compiled = True, return_fig = True) # markdown-exec: hide
print(fig_to_html(fig_compiled)) # markdown-exec: hide
```
