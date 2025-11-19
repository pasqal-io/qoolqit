---
template: home.html
title: Home
hide:
  - navigation
  - toc
---

## **Installation**

QoolQit can be installed from PyPi with `pip`/`pipx`/`uv` as follows

```sh
$ pip install qoolqit
```
```sh
$ pipx install qoolqit
```
```sh
$ uv pip install qoolqit
```


!!! info "Install from source"

    If you wish to install directly from the source, for example, if you are developing code for QoolQit, you can:

    1) Clone the [QoolQit GitHub repository](https://github.com/pasqal-io/qoolqit)

    ```sh
    $ git clone https://github.com/pasqal-io/qoolqit.git
    ```

    2) Setup an environment for developing. We recommend using [Hatch](https://hatch.pypa.io/latest/). From your `qoolqit` folder run

    ```sh
    $ hatch shell
    ```

    If you wish to use a different environment manager like `conda` or `venv`, activate your environment and run

    ```sh
    $ pip install -e .
    ```

!!! tip "Using any pyproject-compatible Python manager"

    For usage within a project with a corresponding `pyproject.toml` file, you can add

    ```toml
      "qoolqit"
    ```

    to the list of `dependencies`.
