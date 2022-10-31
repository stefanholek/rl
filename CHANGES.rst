Changelog
=========

3.1 - 2022-10-31
----------------

- Include GNU Readline 8.2.
  [stefan]

- Improve documentation and example code. Promote using ``generator`` as a
  decorator.
  [stefan]

- Document how ``directory_completion_hook`` interacts with new hooks added
  in version 3.0.
  [stefan]

- Implement Python 3.6 ``readline.set_auto_history`` and the corresponding
  ``history.auto``.
  [stefan]

- Fall back to ncurses if termcap auto-detection fails. This at least produces
  a linker error instead of silently borking the extension.
  [stefan]

- Replace deprecated ``python setup.py test`` in tox.ini.
  [stefan]

- Remove deprecated ``test_suite`` from setup.py.
  [stefan]

- Remove setuptools from ``install_requires``.
  [stefan]

- Add a pyproject.toml file.
  [stefan]

- Include tests in sdist but not in wheel.
  [stefan]


3.0 - 2019-03-20
----------------

- rl is now GPLv3 because it statically links to GNU Readline.
  [stefan]

- Include GNU Readline 8.0.
  [stefan]

- Support Python 3.6 os.PathLike objects for filenames.
  [stefan]

- Handle new GIL checks in Python 3.6. See `PYTHONMALLOC`_.
  [stefan]

- Add ``history.max_file`` and ``history.append_file``.
  [stefan]

- Add ``directory_rewrite_hook``, ``filename_rewrite_hook``, and
  ``filename_stat_hook``.
  [stefan]

- Catch up with bug fixes applied to the standard library readline module.
  [stefan]

- Stop using 2to3.
  [stefan]

- Remove ``reset`` APIs from the documentation. They override
  ``~/.inputrc`` and should only be used in tests.
  [stefan]

.. _`PYTHONMALLOC`: https://docs.python.org/3/whatsnew/3.6.html


2.4 - 2012-10-05
----------------

- Update to Python 3.3 Unicode C-API.
  [stefan]


2.3 - 2012-07-18
----------------

- Implement history iterators in C instead of relying on
  intermediate lists.
  [stefan]

- Raise a more informative error when history slicing is attempted.
  [stefan]


2.2 - 2012-05-10
----------------

- Restore support for gcc < 4.2.
  [stefan]

- Switch to a happier looking Sphinx theme.
  [stefan]


2.1 - 2012-04-27
----------------

- Force a static build if the RL_BUILD_STATIC_READLINE environment
  variable is set.
  [stefan]

- Include readline 6.2 patches in static builds.
  [stefan]

- Suppress compiler warnings on more platforms.
  [stefan]


2.0.1 - 2011-10-06
------------------

- Fix a C compiler issue under Python 3 on Linux.
  [stefan]


2.0 - 2011-10-06
----------------

- Drop support for cmd.Cmd. You now must derive your command
  interpreters from `kmd.Kmd`_ to use rl features.
  [stefan]

- Accept None as argument to file operations under Python 3.
  [stefan]

- Switch to pretty Sphinx-based docs.
  [stefan]


1.16 - 2011-07-28
-----------------

- Tilde-expand filenames in ``read_history_file`` and ``write_history_file``.
  [stefan]


1.15.2 - 2011-07-03
-------------------

- Silence a second C compiler warning in function ``get_y_or_n``.
  [stefan]


1.15.1 - 2011-07-03
-------------------

- Silence a C compiler warning in function ``get_y_or_n``.
  [stefan]


1.15 - 2011-06-04
-----------------

- Fix memory leaks in ``py_remove_history``, ``py_replace_history``, and
  ``py_clear_history`` which can occur when history entries are edited.
  See Python `issue 12186`_.
  [stefan]

- Add a default ``display_matches_hook`` that behaves exactly like readline
  behaves in Bash.
  [stefan]

- Add ``reset`` functions to completer, completion, and history.
  [stefan]

.. _`issue 12186`: https://bugs.python.org/issue12186


1.14 - 2011-05-05
-----------------

- Add xfree.c to sources when building GNU Readline 6.2.
  [stefan]

- Allow history indexes of type long.
  [stefan]


1.13 - 2011-03-11
-----------------

- Use a custom build_ext command to find the best termcap library.
  [stefan]

- Update static builds to GNU Readline 6.2.
  [stefan]


1.12 - 2010-08-04
-----------------

- Fix memory leaks in ``py_remove_history`` and ``py_replace_history``.
  See Python `issue 9450`_.
  [stefan]

.. _`issue 9450`: https://bugs.python.org/issue9450


1.11 - 2010-05-21
-----------------

- Update README, API documentation, and examples.
  [stefan]

- MacPython detection caught other framework builds as well.
  [stefan]


1.10 - 2010-05-05
-----------------

- Rework the history interface: Implement iteration and remove redundant APIs.
  [stefan]

- History stifling could cause duplicate history entries.
  [stefan]

- Make sure ``begidx`` and ``endidx`` completion variables are reset to 0.
  [stefan]


1.9 - 2010-04-02
----------------

- Remove unused defines; we don't support libedit or readline < 5.0.
  [stefan]

- Improve performance of ``get_current_history_length``.
  [stefan]


1.8 - 2010-03-14
----------------

- Make ``get_history_item`` zero-based and remove ``get_history_base``.
  [stefan]


1.7 - 2010-03-09
----------------

- Support installation into MacPython for Mac OS X.
  [stefan]


1.6 - 2010-03-07
----------------

- The history size can now be limited ("stifled") by setting
  ``history.max_entries``. This supersedes ``history.length`` which has been
  removed.
  [stefan]

- Close a memory leak in ``get_current_history_length``. Also see Python
  `issue 8065`_.
  [stefan]

.. _`issue 8065`: https://bugs.python.org/issue8065


1.5.4 - 2010-03-01
------------------

- Avoid segfaults during codec lookup by calling ``PyGILState_Ensure`` in all
  the right places. Fixes rl `issue/5`_. Removes the workaround introduced in
  1.5.2.
  [stefan]


1.5.3 - 2010-02-26
------------------

- Re-release with link to the correct issue.
  [stefan]


1.5.2 - 2010-02-26
------------------

- Work around segfaults under Python 3 on Linux, which are caused by bad or
  missing codecs. This restricts Linux to UTF-8 and Latin-1 locales only.
  Also see rl `issue/5`_.
  [stefan]

.. _`issue/5`: https://github.com/stefanholek/rl/issues#issue/5


1.5.1 - 2010-02-25
------------------

- Switch readline download location to ftp.gnu.org for speed.
  [stefan]


1.5 - 2010-02-25
----------------

- In Python 3, convert to and from Unicode using filesystem encoding
  and "surrogateescape" error handler. See `PEP 383`_ for the low-down.
  [stefan]

.. _`PEP 383`: https://www.python.org/dev/peps/pep-0383/


1.4.1 - 2010-02-13
------------------

- Fix GPL trove classifier.
  [stefan]


1.4 - 2010-02-13
----------------

- rl can now be installed into the system Python on Mac OS X, the only
  dependency being Xcode Tools.
  [stefan]

- Change license to PSF or GPL.
  [stefan]


1.3 - 2010-01-03
----------------

- Fix header detection under Fink on Mac OS X.
  [stefan]

- Add ``readline_version`` API.
  [stefan]


1.2 - 2009-11-24
----------------

- Improve API documentation and examples.
  [stefan]


1.1 - 2009-11-16
----------------

- Remove all occurrences of old-style function typedefs to silence
  compiler warnings.
  [stefan]

- Make the ``display_matches_hook`` work in Python 2.5. Fixes rl `issue/1`_.
  [stefan]

- No longer auto-refresh the prompt at the end of ``display_match_list``.
  Applications should call ``redisplay(force=True)`` to restore the prompt.
  [stefan]

.. _`issue/1`: https://github.com/stefanholek/rl/issues#issue/1


1.0 - 2009-11-08
----------------

- No changes since 1.0a8.


1.0a8 - 2009-11-07
------------------

- Close a memory leak in ``word_break_hook``. Three cheers for Xcode's
  ``leaks`` tool.
  [stefan]


1.0a7 - 2009-11-05
------------------

- Rename ``_readline`` module to ``readline`` since it's not private.
  [stefan]

- Remove ``dump`` and ``read_key`` APIs from public interfaces.
  [stefan]


1.0a6 - 2009-10-30
------------------

- Unclutter the ``completer`` interface by removing settings that can
  just as well be made with ``parse_and_bind``.
  [stefan]

- Fix a memory leak in ``username_completion_function`` and
  ``filename_completion_function``.
  [stefan]

- Add a custom epydoc stylesheet to make its reST rendering more pleasant.
  [stefan]


1.0a5 - 2009-10-29
------------------

- Make all ``completion`` properties writable. While not useful in
  production, this allows us to write better tests.
  [stefan]

- Improve API documentation and add a call graph for the completion
  process. This goes a long way in explaining how readline completion
  works.
  [stefan]


1.0a4 - 2009-10-27
------------------

- Implement the ``generator`` factory using an iterator instead of a list.
  [stefan]

- Remove ``find_completion_word`` so people don't get ideas.
  [stefan]

- Don't list distribute as dependency, setuptools will do the
  right thing.
  [stefan]


1.0a3 - 2009-10-22
------------------

- Add ``__slots__`` to interface objects to make them immutable.
  [stefan]

- Support Python 2.5, 2.6, and 3.1 (thanks to distribute).
  [stefan]

- Approach something like test coverage.
  [stefan]


1.0a2 - 2009-10-08
------------------

- Make the ``generator`` factory work for all types of callables.
  [stefan]

- Improve examples.
  [stefan]


1.0a1 - 2009-10-04
------------------

- Initial release.
