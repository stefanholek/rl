import sys
import os

from setuptools import setup, find_packages, Extension
from os.path import join, exists

version = '2.0'


# Builds rl.readline with a static readline-6.1.

sources = [
    'build/readline/bind.c',
    'build/readline/callback.c',
    'build/readline/compat.c',
    'build/readline/complete.c',
    'build/readline/display.c',
    'build/readline/funmap.c',
    'build/readline/histexpand.c',
    'build/readline/histfile.c',
    'build/readline/history.c',
    'build/readline/histsearch.c',
    'build/readline/input.c',
    'build/readline/isearch.c',
    'build/readline/keymaps.c',
    'build/readline/kill.c',
    'build/readline/macro.c',
    'build/readline/mbutil.c',
    'build/readline/misc.c',
    'build/readline/nls.c',
    'build/readline/parens.c',
    'build/readline/readline.c',
    'build/readline/rltty.c',
    'build/readline/savestring.c',
    'build/readline/search.c',
    'build/readline/shell.c',
    'build/readline/signals.c',
    'build/readline/terminal.c',
    'build/readline/text.c',
    'build/readline/tilde.c',
    'build/readline/undo.c',
    'build/readline/util.c',
    'build/readline/vi_mode.c',
    'build/readline/xmalloc.c',
    'rl/readline.c',
]

define_macros = [
    ('HAVE_CONFIG_H', None),
    ('RL_LIBRARY_VERSION', '"6.1"'),
    ('HAVE_RL_CALLBACK', None),
    ('HAVE_RL_CATCH_SIGNAL', None),
    ('HAVE_RL_COMPLETION_APPEND_CHARACTER', None),
    ('HAVE_RL_COMPLETION_DISPLAY_MATCHES_HOOK', None),
    ('HAVE_RL_COMPLETION_MATCHES', None),
    ('HAVE_RL_COMPLETION_SUPPRESS_APPEND', None),
    ('HAVE_RL_PRE_INPUT_HOOK', None),
]

include_dirs = ['build', 'build/readline']
libraries = ['ncurses']


configure = False
quiet = ''

for arg in sys.argv[1:]:
    if arg.startswith(('bdist', 'build', 'develop', 'test', 'install')):
        configure = True
    if arg in ('-q', '--quiet'):
        quiet = '>' + os.devnull

if configure and not exists(join('build', 'readline', 'config.h')):
    os.system("""\
    mkdir -p build
    cd build
    rm -rf readline-6.1 readline
    tar xzf ../thirdparty/readline-6.1.tar.gz
    mv readline-6.1 readline
    cd readline
    ./configure %(quiet)s
    """ % locals())


rl_readline = \
Extension(name='rl.readline',
          sources=sources,
          define_macros=define_macros,
          include_dirs=include_dirs,
          libraries=libraries,
)


setup(name='rl',
      version=version,
      description='Python readline interface focusing on completion',
      long_description=open('README.txt').read() + '\n' +
                       open('CHANGES.txt').read(),
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: C',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: Python Software Foundation License',
          'License :: OSI Approved :: GNU General Public License',
      ],
      keywords='gnu readline completion interface',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='http://pypi.python.org/pypi/rl',
      license='PSF or GPL',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      use_2to3=True,
      test_suite='rl.tests',
      ext_modules=[
          rl_readline,
      ],
      install_requires=[
          'setuptools',
      ],
)

