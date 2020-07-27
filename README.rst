Git Portfolio
=============

|Status| |PyPI| |Python Version| |License|

|Read the Docs| |Tests| |Codecov|

|pre-commit| |Black|

.. |Status| image:: https://badgen.net/badge/status/alpha/d8624d
   :target: https://badgen.net/badge/status/alpha/d8624d
   :alt: Project Status
.. |PyPI| image:: https://img.shields.io/pypi/v/git-portfolio.svg
   :target: https://pypi.org/project/git-portfolio/
   :alt: PyPI
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/git-portfolio
   :target: https://pypi.org/project/git-portfolio
   :alt: Python Version
.. |License| image:: https://img.shields.io/pypi/l/git-portfolio
   :target: https://en.wikipedia.org/wiki/GNU_Lesser_General_Public_License
   :alt: License
.. |Read the Docs| image:: https://img.shields.io/readthedocs/git-portfolio/latest.svg?label=Read%20the%20Docs
   :target: https://git-portfolio.readthedocs.io/
   :alt: Read the documentation at https://git-portfolio.readthedocs.io/
.. |Tests| image:: https://github.com/staticdev/git-portfolio/workflows/Tests/badge.svg
   :target: https://github.com/staticdev/git-portfolio/actions?workflow=Tests
   :alt: Tests
.. |Codecov| image:: https://codecov.io/gh/staticdev/git-portfolio/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/staticdev/git-portfolio
   :alt: Codecov
.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Black


Features
--------

* Mass create issues.
* Mass create pull requests.
* Mass merge pull requests.
* Mass delete branches by name.


Requirements
------------

* `Create an auth token for GitHub`_, with the `repo` privileges enabled by clicking on Generate new token. You will be asked to select scopes for the token. Which scopes you choose will determine what information and actions you will be able to perform against the API. You should be careful with the ones prefixed with write:, delete: and admin: as these might be quite destructive. You can find description of each scope in docs here.

Important: safeguard your token (once created you won't be able to see it again).


Installation
------------

You can install *Git Portfolio* via pip_ from PyPI_:

.. code:: console

   $ pip install git-portfolio


Usage
-----

* TODO.


Contributing
------------

Contributions are very welcome.
To learn more, see the `Contributor Guide`_.


License
-------

Distributed under the terms of the LGPLv3_ license since it depends on PyGithub_,
*Git Portfolio* is free and open source software.


Issues
------

If you encounter any problems,
please `file an issue`_ along with a detailed description.


Credits
-------

This project was generated from `@cjolowicz`_'s `Hypermodern Python Cookiecutter`_ template.


.. _Create an auth token for GitHub: https://github.com/settings/tokens
.. _@cjolowicz: https://github.com/cjolowicz
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _LGPLv3: https://www.gnu.org/licenses/lgpl-3.0.en.html
.. _PyGithub: https://github.com/PyGithub/PyGithub
.. _PyPI: https://pypi.org/
.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python
.. _file an issue: https://github.com/staticdev/git-portfolio/issues
.. _pip: https://pip.pypa.io/
.. github-only
.. _Contributor Guide: CONTRIBUTING.rst
