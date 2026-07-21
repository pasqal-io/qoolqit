## Install from PyPI
QoolQit can be installed from PyPI with your favorite pyproject-compatible Python manager.
Using `pip`, for example:

```sh
pip install qoolqit
```

!!! tip "Don't forget to create a virtual environment first!"

## Add QoolQit as a dependency
For usage within a project with a corresponding `pyproject.toml` file, you can add
`qoolqit` to the list of dependencies as follows:

```toml
[project]
dependencies = [
  "qoolqit"
]
```

## Install from source
If you are developing code for QoolQit, you can install it directly from source:

1) Clone the [QoolQit GitHub repository](https://github.com/pasqal-io/qoolqit)

  ```sh
  git clone https://github.com/pasqal-io/qoolqit.git
  ```

2) From your `qoolqit` folder, create a virtual environment and install the project in editable mode.
  Using `venv` and `pip`, for example:

  ```sh
  python -m venv .venv
  source .venv/bin/activate
  pip install -e .[dev]
  ```
