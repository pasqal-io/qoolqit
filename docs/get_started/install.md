## Install from PyPi
QoolQit can be installed from PyPi with your favorite pyproject-compatible Python manager.
On `pip`, for example:

```sh
pip install qoolqit
```

!!! tip "Don't forget to create a virtual environment fist!"

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
If you wish to install directly from the source, for example, if you are developing code for QoolQit, you can:

1) Clone the [QoolQit GitHub repository](https://github.com/pasqal-io/qoolqit)

  ```sh
  git clone https://github.com/pasqal-io/qoolqit.git
  ```

2) Setup an environment for developing. From your `qoolqit` folder run:

  ```sh
  python -m venv .venv
  source .venv/bin/activate
  pip install -e .[dev]
  ```

  Alternatively, you can use [Hatch](https://hatch.pypa.io/latest/):

  ```sh
  hatch shell
  ```
