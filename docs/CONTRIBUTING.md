# How to Contribute

We're grateful for your interest in contributing to QoolQit! Please follow our guidelines to ensure a smooth contribution process.

## Reporting an Issue or Proposing a Feature

Your course of action will depend on your objective, but generally, you should start by creating an issue. If you've discovered a bug or have a feature you'd like to see added, feel free to create an issue on [the issue tracker](https://github.com/pasqal-io/qoolqit/issues). Here are some steps to take:

1. Quickly search the existing issues using relevant keywords to ensure your issue hasn't been addressed already.
2. If your issue is not listed, create a new one. Try to be as detailed and clear as possible in your description.

- If you're merely suggesting an improvement or reporting a bug, that's already excellent! We thank you for it. Your issue will be listed and, hopefully, addressed at some point.
- However, if you're willing to be the one solving the issue, that would be even better! In such instances, you would proceed by preparing a [Pull Request](#submitting-a-pull-request).

## Submitting a Pull Request

We're excited that you're eager to contribute to QoolQit! To contribute, create a branch on the repository and once you are satisfied with your feature and all the tests pass create a [Pull Request](https://github.com/pasqal-io/qoolqit/pulls).

Here's the process for making a contribution:

Make a new branch via

```shell
git branch <your initials>/<branch name>
```

Next, checkout your new branch, and associate a branch to it on the GitHub server:

```shell
git checkout <your initials>/<branch name>
git push --set-upstream origin <your initials>/<branch name>
```

## Setting up your development environment

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

### Useful Things for your workflow: Linting and Testing

Use `pre-commit` hooks to make sure that the code is properly linted before pushing a new commit. Make sure that the unit tests and type checks are passing since the merge request will not be accepted if the automatic CI/CD pipeline do not pass.

```shell
pip install pre-commit
pre-commit install
pre-commit run --all-files
pytest
```