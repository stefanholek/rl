import sys
import os
import re

from setuptools import setup
from setuptools import find_packages
from setuptools import Extension
from setuptools.command.build_ext import build_ext

from distutils.sysconfig import get_config_vars
from distutils import log

from os.path import join, exists

version = '3.1'
readline_version = '8.2'

readline_version_info = tuple(map(int, readline_version.split('.')))


def get_config_var(name, default=''):
    return get_config_vars().get(name) or default


def sys_path_contains(string):
    for dir in sys.path:
        if dir.startswith(string):
            return True


class readline_ext(Extension):

    def __init__(self, name):
        # Describe the extension
        sources = [
            'rl/readline.c',
            'rl/stringarray.c',
            'rl/unicode.c',
            'rl/iterator.c',
            'rl/modulestate.c',
        ]
        Extension.__init__(self, name, sources)

        # Use include and library dirs from Python build
        self.use_include_dirs()
        self.use_library_dirs()

        # Use Mac Python library dir
        if sys.platform == 'darwin':
            if sys_path_contains('/Library/Frameworks/Python.framework'):
                self.library_dirs.append(
                    '/Library/Frameworks/Python.framework/Versions/%d.%d/lib' % sys.version_info[:2])

        self.use_static_readline()
        self.suppress_warnings()
        self.strip_debug_symbols()

    def use_include_dirs(self):
        cflags = get_config_var('CPPFLAGS') + ' ' + get_config_var('CFLAGS')

        for match in re.finditer(r'-I\s*(\S+)', cflags):
            if '/include' in match.group(1):
                self.include_dirs.append(match.group(1))

    def use_library_dirs(self):
        ldflags = get_config_var('LDFLAGS')

        for match in re.finditer(r'-L\s*(\S+)', ldflags):
            self.library_dirs.append(match.group(1))

    def suppress_warnings(self):
        cflags = get_config_var('CFLAGS').split()

        if '-Wall' in cflags or '-Wsign-compare' in cflags or '-Wunreachable-code' in cflags:
            self.extra_compile_args.extend([
                '-Wno-sign-compare',
                '-Wno-unreachable-code',
                '-Wno-uninitialized',
                '-Wno-unused',
                '-Wno-parentheses',
                '-Wno-missing-braces',
            ])
        if '-Wstrict-prototypes' in cflags:
            self.extra_compile_args.append('-Wno-strict-prototypes')
        if '-Wshorten-64-to-32' in cflags:
            self.extra_compile_args.append('-Wno-shorten-64-to-32')

    def strip_debug_symbols(self):
        if sys.platform == 'darwin':
            stripflag = '-S'
        else:
            stripflag = get_config_var('STRIPFLAG', '-s')
        self.extra_link_args.extend(['-Xlinker', stripflag])

    def use_static_readline(self):
        self.sources.extend([
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

        if readline_version_info >= (6, 2):
            self.sources.extend([
                'build/readline/xfree.c',
            ])

        if readline_version_info >= (6, 3):
            self.sources.extend([
                'build/readline/colors.c',
                'build/readline/parse-colors.c',
            ])

        self.define_macros.extend([
            ('HAVE_CONFIG_H', None),
            ('RL_LIBRARY_VERSION', '"%s"' % readline_version),
        ])

        if sys.platform == "darwin" and readline_version_info < (7,):
            # Fix conditional include in rltty.c
            self.define_macros.extend([
                ('GWINSZ_IN_SYS_IOCTL', None),
            ])

        self.include_dirs = ['build', 'build/readline'] + self.include_dirs


class build_readline_ext(build_ext):

    def build_extension(self, ext):
        # Find a termcap library
        if os.environ.get('RL_TERMCAP'):
            termcap = os.environ.get('RL_TERMCAP')
        else:
            termcap = self.find_termcap(ext)

        if termcap:
            ext.libraries.append(termcap)
        else:
            # Take a good guess and produce a linker error at least
            log.warn('WARNING: Failed to detect a termcap library; falling back to ncurses')
            ext.libraries.append('ncurses')

        # Prepare the source tree
        self.configure_static_readline()

        return build_ext.build_extension(self, ext)

    def find_termcap(self, ext):
        lib_dirs = ext.library_dirs + self.compiler.library_dirs
        termcap = ''

        # Debian/Ubuntu multiarch
        multiarch = get_config_var('MULTIARCH')
        if multiarch:
            lib_dirs.extend(['/lib/'+multiarch, '/usr/lib/'+multiarch])

        # Standard locations
        lib_dirs.extend(['/lib64', '/usr/lib64', '/lib', '/usr/lib', '/usr/local/lib'])

        for name in ['tinfo', 'ncursesw', 'ncurses', 'cursesw', 'curses', 'termcap']:
            if self.compiler.find_library_file(lib_dirs, name):
                termcap = name
                break

        return termcap

    def configure_static_readline(self):
        srcdir = os.getcwd()
        version = readline_version
        stdout = ''

        cc = os.environ.get('CC') or get_config_var('CC', 'cc')

        if not self.distribution.verbose:
            stdout = '>%s' % os.devnull

        if not exists(join('build', 'readline', 'config.h')):
            os.system("""\
            mkdir -p build
            cd build
            rm -rf readline-%(version)s readline
            tar zxf '%(srcdir)s/readline-%(version)s.tar.gz'
            mv readline-%(version)s readline
            cd readline
            ./configure CC="%(cc)s" %(stdout)s
            """ % locals())


setup(name='rl',
      version=version,
      description='Alternative Python bindings for GNU Readline',
      long_description=open('README.rst').read() + '\n' +
                       open('CHANGES.rst').read(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Programming Language :: C',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: Implementation :: CPython',
      ],
      keywords='gnu, readline, bindings, gnureadline, completion, tab completion',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='https://github.com/stefanholek/rl',
      license='GPLv3',
      packages=find_packages(
          exclude=[
              'rl.tests',
          ],
      ),
      include_package_data=False,
      zip_safe=False,
      ext_modules=[
          readline_ext('rl.readline'),
      ],
      cmdclass={
          'build_ext': build_readline_ext,
      },
      python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
      project_urls={
          'Documentation': 'https://rl.readthedocs.io/en/stable/',
      },
      extras_require={
          'docs': [
              'sphinx == 5.3.0',
              'sphinx-rtd-theme == 1.0.0',
          ],
      },
)

