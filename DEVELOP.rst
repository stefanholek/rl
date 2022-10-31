==========
Develop rl
==========

Repository
==========

Clone from GitHub::

    git clone git@github.com:stefanholek/rl

Development
===========

Create a virtualenv::

    cd rl
    python3.10 -m venv .venv
    source .venv/bin/activate

Build in place::

    pip install -e . -v

Run tests::

    python -m unittest

Run tests with tox::

    tox -e py27 -e py310

Documentation
=============

Build Spinx documentation locally::

    tox -e docs [-r]

View documentation::

    open docs/_build/html/index.html

Pushing to main triggers readthedocs.io latest build::

    git push origin

Debugging
=========

Start with a clean slate::

    rm -rf build
    rm -rf rl.egg-info
    rm rl/*.so

Temporarily remove pyproject.toml for the raw setuptools experience::

    rm pyproject.toml

Get it back with::

    git restore pyproject.toml

