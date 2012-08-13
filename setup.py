# On Linux, install libreadline6-dev before attempting to build rl.
# On Mac OS X, make sure you have Xcode Tools installed.

from __future__ import with_statement

import sys
import os
import re

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
from distutils.sysconfig import get_config_var
from distutils.spawn import find_executable
from distutils import log
from os.path import join, exists

version = '2.4'


def sys_path_contains(string):
    for dir in sys.path:
        if dir.startswith(string):
            return True


class ReadlineExtension(Extension):

    def __init__(self, name):
        # Describe the extension
        sources = [
            'rl/readline.c',
            'rl/stringarray.c',
            'rl/unicode.c',
            'rl/iterator.c',
        ]
        libraries = ['readline']
        Extension.__init__(self, name, sources, libraries=libraries)

        # Use include and library dirs from Python build
        self.use_include_dirs()
        self.use_library_dirs()

        # Force static build if environment variable is set
        if os.environ.get('RL_BUILD_STATIC_READLINE') and self.have_curl():
            self.use_static_readline()

        # Mac OS X ships with libedit which we cannot use
        elif sys.platform == 'darwin':
            # System Python
            if sys_path_contains('/System/Library/Frameworks/Python.framework'):
                self.use_static_readline()
            # Mac Python
            elif sys_path_contains('/Library/Frameworks/Python.framework'):
                self.use_static_readline()
                self.library_dirs.append(
                    '/Library/Frameworks/Python.framework/Versions/%s/lib' % sys.version[:3])
            # MacPorts Python
            elif '/opt/local/include' in self.include_dirs:
                pass
            # Fink Python
            elif '/sw/include' in self.include_dirs:
                pass
            # Other Python
            else:
                self.use_static_readline()

    def have_curl(self):
        if not find_executable('curl'):
            log.warn('WARNING: Cannot build statically. Command not found: curl')
            return False
        return True

    def use_include_dirs(self):
        cppflags = get_config_var('CPPFLAGS')

        for match in re.finditer(r'-I\s*(\S+)', cppflags):
            if match.group(1) not in ['.', 'Include', './Include']:
                self.include_dirs.append(match.group(1))

    def use_library_dirs(self):
        ldflags = get_config_var('LDFLAGS')

        for match in re.finditer(r'-L\s*(\S+)', ldflags):
            self.library_dirs.append(match.group(1))

    def suppress_warnings(self):
        cflags = get_config_var('CFLAGS')
        cflags = cflags.split()

        # -Wno-all is not supported by gcc < 4.2
        if sys.platform == 'darwin':
            self.extra_compile_args.append('-Wno-all')

        if '-Wstrict-prototypes' in cflags:
            self.extra_compile_args.append('-Wno-strict-prototypes')

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
            'build/readline/xfree.c',
        ])

        self.define_macros.extend([
            ('HAVE_CONFIG_H', None),
            ('RL_LIBRARY_VERSION', '"6.2"'),
        ])

        self.include_dirs = ['build', 'build/readline'] + self.include_dirs
        self.libraries.remove('readline')

        self.suppress_warnings()


class ReadlineExtensionBuilder(build_ext):

    def build_extension(self, ext):
        lib_dynload = join(sys.exec_prefix, 'lib', 'python%s' % sys.version[:3], 'lib-dynload')
        lib_dirs = ['/lib64', '/usr/lib64', '/lib', '/usr/lib', '/usr/local/lib']
        lib_dirs = ext.library_dirs + self.compiler.library_dirs + lib_dirs

        # Find a termcap library
        termcap = ''

        if self.can_inspect_libraries():

            if 'readline' in ext.libraries:
                readline = self.compiler.find_library_file(lib_dirs, 'readline')
                termcap = self.get_termcap_from(readline)

            if not termcap:
                pyreadline = join(lib_dynload, 'readline.so')
                termcap = self.get_termcap_from(pyreadline)

            if not termcap:
                pycurses = join(lib_dynload, '_curses.so')
                termcap = self.get_termcap_from(pycurses)

            if termcap and not self.compiler.find_library_file(lib_dirs, termcap):
                termcap = ''

        if not termcap:
            for name in ['tinfo', 'ncursesw', 'ncurses', 'cursesw', 'curses', 'termcap']:
                if self.compiler.find_library_file(lib_dirs, name):
                    termcap = name
                    break

        if termcap:
            ext.libraries.append(termcap)
        else:
            log.warn('WARNING: Failed to find a termcap library')

        # Prepare the source tree
        if 'readline' not in ext.libraries:
            self.configure_static_readline()

        return build_ext.build_extension(self, ext)

    def can_inspect_libraries(self):
        if sys.platform == 'darwin':
            cmd = 'otool'
        else:
            cmd = 'ldd'
        if not find_executable(cmd):
            log.warn('WARNING: Command not found: %s' % cmd)
            return False
        return True

    def get_termcap_from(self, module):
        if module and exists(module):
            if sys.platform == 'darwin':
                cmd = 'otool -L "%s"' % module
            else:
                cmd = 'ldd "%s"' % module
            with os.popen(cmd) as fp:
                libraries = fp.read()
            for name in ['tinfo', 'ncursesw', 'ncurses', 'cursesw', 'curses', 'termcap']:
                 if 'lib%s.' % name in libraries:
                    return name
        return ''

    def configure_static_readline(self):
        tarball = 'http://ftp.gnu.org/gnu/readline/readline-6.2.tar.gz'
        patches = 'http://ftp.gnu.org/gnu/readline/readline-6.2-patches'
        have_patch = find_executable('patch') and 'True' or 'False'
        stdout = ''

        if not self.distribution.verbose:
            stdout = '>%s' % os.devnull

        if not exists(join('build', 'readline', 'config.h')):
            os.system("""\
            mkdir -p build
            cd build
            rm -rf readline-6.2 readline
            echo downloading %(tarball)s %(stdout)s
            curl --connect-timeout 30 -s %(tarball)s | tar zx
            mv readline-6.2 readline
            cd readline
            if [ "%(have_patch)s" = "True" ]; then
                curl --connect-timeout 30 -s %(patches)s/readline62-001 | patch -p0 %(stdout)s
                curl --connect-timeout 30 -s %(patches)s/readline62-002 | patch -p0 %(stdout)s
            fi
            ./configure %(stdout)s
            """ % locals())


setup(name='rl',
      version=version,
      description='Alternative Python bindings for GNU Readline',
      long_description=open('README.txt').read() + '\n' +
                       open('CHANGES.txt').read(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
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
          'build_ext': ReadlineExtensionBuilder,
      },
      install_requires=[
          'setuptools',
      ],
)

