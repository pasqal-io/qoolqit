
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./docs/extras/assets/logo/qoolqit_logo_white.svg" width="65%">
    <source media="(prefers-color-scheme: light)" srcset="./docs/extras/assets/logo/qoolqit_logo_darkgreen.svg" width="65%">
    <img alt="Qoolqit logo" src="./docs/assets/logo/qoolqit_logo_darkgreen.svg" width="65%">
  </picture>
</p>

<p align="center">
  <strong>
    **QoolQit** is a Python library for algorithm development in the Rydberg Analog Model.
  </strong>
</p>

**For more detailed information, [check out the documentation](https://pasqal-io.github.io/qoolqit/latest/)**.

## Install from PyPi
QoolQit can be installed from PyPi with your favorite pyproject-compatible Python manager.
On `pip`, for example:

```sh
pip install qoolqit
```

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

2) Setup an environment for developing. From your `qoolqit` folder, again install with your favorite environment/package managers.
  On `venv`/`pip`, for example:

  ```sh
  python -m venv .venv
  source .venv/bin/activate
  pip install -e .[dev]
  ```


# Getting in touch

- [Pasqal Community Portal](https://community.pasqal.com/) (forums, chat, tutorials, examples, code library).
- [GitHub Repository](https://github.com/pasqal-io/qoolqit/) (source code, issue tracker).
- [Professional Support](https://www.pasqal.com/contact-us/) (if you need tech support, custom licenses, a variant of this library optimized for your workload, your own QPU, remote access to a QPU, ...)
