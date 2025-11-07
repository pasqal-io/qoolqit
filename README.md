
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./docs/extras/assets/logo/qoolqit_logo_white.svg" width="75%">
    <source media="(prefers-color-scheme: light)" srcset="./docs/extras/assets/logo/qoolqit_logo_darkgreen.svg" width="75%">
    <img alt="Qoolqit logo" src="./docs/assets/logo/qoolqit_logo_darkgreen.svg" width="75%">
  </picture>
</p>

**QoolQit** is a Python package designed for algorithm development in the Rydberg Analog Model.


**For more detailed information, [check out the documentation](https://pasqal-io.github.io/qoolqit/latest/)**.

# Installation

QoolQit can be installed from PyPi with `pip` as follows

```sh
$ pip install qoolqit

# or

$ pipx install qoolqit
```

## Install from source

If you wish to install directly from the source, for example, if you are developing code for QoolQit, you can:

1) Clone the [QoolQit GitHub repository](https://github.com/pasqal-io/qoolqit)

```sh
git clone https://github.com/pasqal-io/qoolqit.git
```

2) Setup an environment for developing. We recommend using [Hatch](https://hatch.pypa.io/latest/). With Hatch installed, you can enter the `qoolqit` repository and run

```sh
hatch shell
```

This will automatically take you into an environment with the necessary dependencies. Alternatively, if you wish to use a different environment manager like `conda` or `venv`, you can instead enter the `qoolqit` repository from within the environment and run

```sh
pip install -e .
```

## Using any pyproject-compatible Python manager

For usage within a project with a corresponding `pyproject.toml` file, you can add

```sh
  "qoolqit"
```

to the list of `dependencies`.


# Getting in touch

- [Pasqal Community Portal](https://community.pasqal.com/) (forums, chat, tutorials, examples, code library).
- [GitHub Repository](https://github.com/pasqal-io/qoolqit/) (source code, issue tracker).
- [Professional Support](https://www.pasqal.com/contact-us/) (if you need tech support, custom licenses, a variant of this library optimized for your workload, your own QPU, remote access to a QPU, ...)
