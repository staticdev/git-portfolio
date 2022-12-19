# Git Portfolio

[![PyPI](https://img.shields.io/pypi/v/git-portfolio.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/git-portfolio.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/git-portfolio)][pypi status]
[![License](https://img.shields.io/pypi/l/git-portfolio)][license]

[![Read the documentation at https://git-portfolio.readthedocs.io/](https://img.shields.io/readthedocs/git-portfolio/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/staticdev/git-portfolio/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/staticdev/git-portfolio/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/git-portfolio/
[read the docs]: https://git-portfolio.readthedocs.io/
[tests]: https://github.com/staticdev/git-portfolio/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/staticdev/git-portfolio
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Features

- Configure multiple working repositories.
- Batch [git] commands with subcommands: `add`, `branch`, `checkout`, `commit`, `diff`, `fetch`, `init`, `merge`, `mv`, `pull`, `push`, `rebase`, `reset`, `rm`, `show`, `switch`, `status` and `tag`.
- Batch API calls on [GitHub]: create/close/reopen `issues`, create/close/reopen/merge `pull requests` and delete `branches` by name.
- Batch [Poetry] commands such as: `add`, `version patch`, `install` or `update`.

## Requirements

- [Create an auth token for GitHub], with the `repo` privileges enabled by clicking on Generate new token. You will be asked to select scopes for the token. Which scopes you choose will determine what information and actions you will be able to perform against the API. You should be careful with the ones prefixed with write:, delete: and admin: as these might be quite destructive. You can find description of each scope in docs here.

Important: safeguard your token (once created you won't be able to see it again).

- Install [git] (optional) -  this is needed for all [git] commands. For colored outputs please use the configuration:

```console
$ git config --global color.ui always
```

## Installation

You can install *Git Portfolio* via [pip] from [PyPI]:

```console
$ pip install git-portfolio
```

% basic-usage

## Basic usage

1. Create initial configuration with:

```console
$ gitp config init
```

2. Execute all the commands you want. Eg.:

```console
$ gitp issues create  # create same issue for all projects
$ gitp checkout -b new-branch  # checks out new branch new-branch in all projects
$ gitp poetry version minor  # bumps minor version of all projects that have pyproject.toml version
```

Note: by convention GitHub commands are always the resource name and action: eg. `branches delete`, `issues create` and `prs merge` (for pull requests).
This avoid conflicts with batch git commands, as in `gitp branch` (executes git command) and `gitp branches delete` (execute operations using GitHub API).

% end-basic-usage

Complete instructions can be found at [git-portfolio.readthedocs.io].

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT] license,
*Git Portfolio* is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

% github-only

[@cjolowicz]: https://github.com/cjolowicz
[contributor guide]: https://git-portfolio.readthedocs.io/en/latest/contributing.html
[cookiecutter]: https://github.com/audreyr/cookiecutter
[create an auth token for github]: https://github.com/settings/tokens
[file an issue]: https://github.com/staticdev/git-portfolio/issues
[git]: https://git-scm.com
[git-portfolio.readthedocs.io]: https://git-portfolio.readthedocs.io
[github]: https://github.com
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[mit]: https://opensource.org/licenses/MIT
[pip]: https://pip.pypa.io/
[poetry]: https://python-poetry.org/
[pypi]: https://pypi.org/
