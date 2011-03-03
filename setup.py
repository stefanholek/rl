# On Linux, install libreadline5-dev (or equivalent) before attempting
# to build rl. On Mac OS X, make sure you have Xcode Tools installed.

import sys
import os
import re

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
from distutils.sysconfig import get_config_vars
from distutils.spawn import find_executable
from os.path import join, exists

version = '1.13'


def sys_path_contains(string):
    for dir in sys.path:
        if dir.startswith(string):
            return True


class ReadlineExtension(Extension):

    def __init__(self, name):
        sources = ['rl/readline.c', 'rl/stringarray.c', 'rl/unicode.c']
        libraries = ['readline']
        Extension.__init__(self, name, sources, libraries=libraries)

        self.use_cppflags()
        self.use_ldflags()

        if sys.platform == 'darwin':
            # System Python
            if sys_path_contains('/System/Library/Frameworks/Python.framework'):
                self.use_static_readline()
            # Mac Python
            elif sys_path_contains('/Library/Frameworks/Python.framework'):
                self.use_static_readline()
                self.library_dirs.extend([
                    '/Library/Frameworks/Python.framework/Versions/%s/lib' % sys.version[:3]])
            # MacPorts
            elif '/opt/local/include' in self.include_dirs:
                pass
            # Fink
            elif '/sw/include' in self.include_dirs:
                pass
            # Other Python
            else:
                self.use_static_readline()

    def use_cppflags(self):
        cppflags, srcdir = get_config_vars('CPPFLAGS', 'srcdir')

        for match in re.finditer(r'-I\s*(\S+)', cppflags):
            if match.group(1) not in ['.', 'Include', '%s/Include' % srcdir]:
                self.include_dirs.extend([match.group(1)])

    def use_ldflags(self):
        ldflags, = get_config_vars('LDFLAGS')

        for match in re.finditer(r'-L\s*(\S+)', ldflags):
            self.library_dirs.extend([match.group(1)])

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

        self.define_macros.extend([
            ('HAVE_CONFIG_H', None),
            ('RL_LIBRARY_VERSION', '"6.2"'),
        ])

        self.include_dirs = ['build', 'build/readline'] + self.include_dirs
        self.libraries.remove('readline')

        if sys.platform == 'darwin':
            self.extra_compile_args.extend(['-Wno-all', '-Wno-strict-prototypes'])


class BuildReadlineExtension(build_ext):

    def build_extension(self, ext):
        lib_dynload = join(sys.exec_prefix, 'lib', 'python%s' % sys.version[:3], 'lib-dynload')
        lib_dirs = ['/lib64', '/usr/lib64', '/lib', '/usr/lib', '/usr/local/lib']
        lib_dirs = ext.library_dirs + self.compiler.library_dirs + lib_dirs
        termcap = ''

        # Find a termcap library
        if 'readline' in ext.libraries:
            readline = self.compiler.find_library_file(lib_dirs, 'readline')
            termcap = self.get_termcap_from(readline)

        if not termcap:
            pyreadline = join(lib_dynload, 'readline.so')
            termcap = self.get_termcap_from(pyreadline)

        if not termcap:
            pycurses = join(lib_dynload, '_curses.so')
            termcap = self.get_termcap_from(pycurses)

        if not termcap:
            for name in ['tinfo', 'ncursesw', 'ncurses', 'cursesw', 'curses', 'termcap']:
                if self.compiler.find_library_file(lib_dirs, name):
                    termcap = name
                    break

        if termcap:
            ext.libraries.extend([termcap])

        # Prepare the source tree
        if 'readline' not in ext.libraries:
            self.configure_static_readline()

        return build_ext.build_extension(self, ext)

    def get_termcap_from(self, module):
        if module and exists(module):
            fp = None
            if sys.platform == 'darwin':
                if find_executable('otool'):
                    fp = os.popen('otool -L "%s"' % module)
            elif find_executable('ldd'):
                fp = os.popen('ldd "%s"' % module)
            if fp is not None:
                libraries = fp.read()
                fp.close()
                for name in ['tinfo', 'ncursesw', 'ncurses', 'cursesw', 'curses', 'termcap']:
                     if 'lib%s.' % name in libraries:
                        return name
        return ''

    def configure_static_readline(self):
        url = 'http://ftp.gnu.org/gnu/readline/readline-6.2.tar.gz'
        stdout = ''

        if not self.distribution.verbose:
            stdout = '>%s' % os.devnull

        if not exists(join('build', 'readline', 'config.h')):
            os.system("""\
            mkdir -p build
            cd build
            rm -rf readline-6.2 readline
            echo downloading %(url)s %(stdout)s
            curl --connect-timeout 30 -s %(url)s | tar zx
            mv readline-6.2 readline
            cd readline
            ./configure %(stdout)s
            """ % locals())


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
          ReadlineExtension(name='rl.readline'),
      ],
      cmdclass={
          'build_ext': BuildReadlineExtension,
      },
      install_requires=[
          'setuptools',
      ],
)

