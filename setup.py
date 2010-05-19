# On Linux, install libreadline5-dev (or equivalent) before attempting
# to build rl. On Mac OS X, make sure you have Xcode Tools installed.

import sys
import os

from setuptools import setup, find_packages, Extension
from os.path import join, exists

version = '1.11'

sources = ['rl/readline.c', 'rl/stringarray.c', 'rl/unicode.c']
define_macros = []
include_dirs = []
libraries = ['readline', 'ncurses']
extra_compile_args = []


def system_python():
    for dir in sys.path:
        if dir.startswith('/System/Library/Frameworks/Python.framework'):
            return True


def mac_python():
    for dir in sys.path:
        if dir.startswith('/Library/Frameworks/Python.framework'):
            return True


def use_static_readline():
    sources.extend([
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
    ])

    define_macros.extend([
        ('HAVE_CONFIG_H', None),
        ('RL_LIBRARY_VERSION', '"6.1"'),
    ])

    include_dirs.extend(['build', 'build/readline'])
    libraries.remove('readline')

    if sys.platform == 'darwin':
        extra_compile_args.extend(['-Wno-all', '-Wno-strict-prototypes'])

    configure = False
    quiet = ''

    for arg in sys.argv[1:]:
        if arg.startswith(('bdist', 'build', 'develop', 'test', 'install')):
            configure = True
        if arg in ('-q', '--quiet'):
            quiet = '>' + os.devnull

    if configure and not exists(join('build', 'readline', 'config.h')):
        url = 'ftp://ftp.gnu.org/gnu/readline/readline-6.1.tar.gz'
        os.system("""\
        mkdir -p build
        cd build
        rm -rf readline-6.1 readline
        echo Downloading %(url)s
        curl --connect-timeout 30 -s %(url)s | tar xz
        mv readline-6.1 readline
        cd readline
        ./configure %(quiet)s
        """ % locals())


if sys.platform == 'darwin':
    # System
    if system_python() or mac_python():
        use_static_readline()
    # MacPorts
    elif exists('/opt/local/include'):
        include_dirs = ['/opt/local/include']
    # Fink
    elif exists('/sw/include'):
        include_dirs = ['/sw/include']


rl_readline = \
Extension(name='rl.readline',
          sources=sources,
          define_macros=define_macros,
          include_dirs=include_dirs,
          libraries=libraries,
          extra_compile_args=extra_compile_args,
)


setup(name='rl',
      version=version,
      description='Alternative Python bindings for GNU Readline',
      long_description=open('README.txt').read() + '\n' +
                       open('CHANGES.txt').read(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'License :: OSI Approved :: Python Software Foundation License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Programming Language :: C',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ],
      keywords='gnu readline bindings',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='http://pypi.python.org/pypi/rl',
      license='GPL or PSF',
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

