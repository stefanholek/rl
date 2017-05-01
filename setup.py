# On Linux, install libreadline-dev before attempting to build rl.
# On Mac OS X, make sure you have Xcode Tools installed.

from __future__ import with_statement

import sys
import os
import re

from setuptools import setup
from setuptools import find_packages
from setuptools import Extension
from setuptools.command.build_ext import build_ext

from distutils.sysconfig import get_config_var
from distutils.sysconfig import get_config_vars
from distutils.spawn import find_executable
from distutils import log

from os.path import join, exists

version = '2.5'


class ReadlineExtension(Extension):

    static_readline = False
    static_termcap = False

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

        # Use Mac Python library dir
        if sys.platform == 'darwin':
            if self.sys_path_contains('/Library/Frameworks/Python.framework'):
                self.library_dirs.append(
                    '/Library/Frameworks/Python.framework/Versions/%d.%d/lib' % sys.version_info[:2])

        # Build statically on readthedocs.io
        if os.environ.get('READTHEDOCS') == 'True' and self.have_curl():
            self.use_static_readline()
            self.use_static_termcap()

        # Force static build if environment variable is set
        elif os.environ.get('RL_BUILD_STATIC_READLINE') and self.have_curl():
            self.use_static_readline()

        # Mac OS X ships with libedit which we cannot use
        elif sys.platform == 'darwin':
            # System Python
            if self.sys_path_contains('/System/Library/Frameworks/Python.framework'):
                self.use_static_readline()
            # Mac Python
            elif self.sys_path_contains('/Library/Frameworks/Python.framework'):
                self.use_static_readline()
            # MacPorts Python
            elif '/opt/local/include' in self.include_dirs:
                pass
            # Fink Python
            elif '/sw/include' in self.include_dirs:
                pass
            # Other Python
            else:
                self.use_static_readline()

        self.suppress_warnings()

    def sys_path_contains(self, string):
        for dir in sys.path:
            if dir.startswith(string):
                return True

    def have_curl(self):
        if not find_executable('curl'):
            log.warn('WARNING: Cannot build statically. Command not found: curl')
            return False
        return True

    def use_include_dirs(self):
        cflags = ' '.join(get_config_vars('CPPFLAGS', 'CFLAGS'))

        for match in re.finditer(r'-I\s*(\S+)', cflags):
            if '/include' in match.group(1):
                self.include_dirs.append(match.group(1))

    def use_library_dirs(self):
        ldflags = get_config_var('LDFLAGS')

        for match in re.finditer(r'-L\s*(\S+)', ldflags):
            self.library_dirs.append(match.group(1))

    def suppress_warnings(self):
        cflags = ' '.join(get_config_vars('CPPFLAGS', 'CFLAGS'))
        cflags = cflags.split()

        if self.static_readline and '-Wall' in cflags:
            self.extra_compile_args.append('-Wno-all')
        if '-Wstrict-prototypes' in cflags:
            self.extra_compile_args.append('-Wno-strict-prototypes')
        if '-Wsign-compare' in cflags:
            self.extra_compile_args.append('-Wno-sign-compare')

    def use_static_readline(self):
        self.static_readline = True

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
            'build/readline/colors.c',
            'build/readline/parse-colors.c',
        ])

        self.define_macros.extend([
            ('HAVE_CONFIG_H', None),
            ('RL_LIBRARY_VERSION', '"6.3"'),
        ])

        self.include_dirs = ['build', 'build/readline'] + self.include_dirs
        self.libraries.remove('readline')

    def use_static_termcap(self):
        self.static_termcap = True


class build_rl_ext(build_ext):

    def build_extension(self, ext):
        # Add FreeBSD include dir
        if '/usr/local/lib' in self.compiler.library_dirs:
            if '/usr/local/include' not in self.compiler.include_dirs:
                if '/usr/local/include' not in ext.include_dirs:
                    ext.include_dirs.append('/usr/local/include')

        # Find a termcap library
        termcap = self.find_termcap(ext)

        if termcap:
            ext.libraries.append(termcap)
        else:
            log.warn('WARNING: Failed to find a termcap library')

        # Build a static termcap library as last resort
        if not termcap and ext.static_termcap:
            self._build_static_tinfo()
            ext.library_dirs = ['build/ncurses/lib'] + ext.library_dirs
            ext.libraries.append('tinfo')

        # Prepare the source tree
        if ext.static_readline:
            self.configure_static_readline()

        return build_ext.build_extension(self, ext)

    def find_termcap(self, ext):
        lib_dirs = []

        # Debian/Ubuntu multiarch
        multiarch = get_config_var('MULTIARCH')
        if multiarch:
            lib_dirs.extend(['/lib/'+multiarch, '/usr/lib/'+multiarch])

        lib_dirs.extend(['/lib64', '/usr/lib64', '/lib', '/usr/lib', '/usr/local/lib'])
        lib_dirs = ext.library_dirs + self.compiler.library_dirs + lib_dirs

        lib_dynload = join(sys.exec_prefix, 'lib', 'python%d.%d' % sys.version_info[:2], 'lib-dynload')
        ext_suffix = get_config_var('EXT_SUFFIX') or '.so'

        termcap = ''

        if self.can_inspect_libraries():
            if not ext.static_readline:
                readline = self.find_library_file(lib_dirs, 'readline')
                termcap = self.get_termcap_from(readline)
            if not termcap:
                pyreadline = join(lib_dynload, 'readline' + ext_suffix)
                termcap = self.get_termcap_from(pyreadline)
            if not termcap:
                pycurses = join(lib_dynload, '_curses' + ext_suffix)
                termcap = self.get_termcap_from(pycurses)
            if termcap and not self.find_library_file(lib_dirs, termcap):
                termcap = ''

        if not termcap:
            for name in ['tinfo', 'ncursesw', 'ncurses', 'cursesw', 'curses', 'termcap']:
                if self.find_library_file(lib_dirs, name):
                    termcap = name
                    break

        return termcap

    def find_library_file(self, lib_dirs, name):
        # e.g. Fedora has only libtinfo.so.6 and no libtinfo.so
        if sys.platform.startswith('linux'):
            lib_name = self.compiler.library_filename(name, 'shared')
            libs = []
            for dir in lib_dirs:
                if os.path.isdir(dir):
                    for entry in os.listdir(dir):
                        if entry.startswith(lib_name):
                            libs.append(os.path.join(dir, entry))
                    if libs:
                        libs.sort(key=lambda x: len(x))
                        return libs[0]

        return self.compiler.find_library_file(lib_dirs, name)

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
                 if self.compiler.library_filename(name, 'shared') in libraries:
                     return name
        return ''

    def configure_static_readline(self):
        tarball = 'https://ftp.gnu.org/gnu/readline/readline-6.3.tar.gz'
        patches = 'https://ftp.gnu.org/gnu/readline/readline-6.3-patches'
        have_patch = find_executable('patch') and 'True' or 'False'
        stdout = ''

        if not self.distribution.verbose:
            stdout = '>%s' % os.devnull

        if not exists(join('build', 'readline', 'config.h')):
            os.system("""\
            mkdir -p build
            cd build
            rm -rf readline-6.3 readline
            echo downloading %(tarball)s %(stdout)s
            curl --connect-timeout 30 -s %(tarball)s | tar zx
            mv readline-6.3 readline
            cd readline
            if [ "%(have_patch)s" = "True" ]; then
                curl --connect-timeout 30 -s %(patches)s/readline63-001 | patch -p0 %(stdout)s
                curl --connect-timeout 30 -s %(patches)s/readline63-002 | patch -p0 %(stdout)s
                curl --connect-timeout 30 -s %(patches)s/readline63-003 | patch -p0 %(stdout)s
                curl --connect-timeout 30 -s %(patches)s/readline63-004 | patch -p0 %(stdout)s
                curl --connect-timeout 30 -s %(patches)s/readline63-005 | patch -p0 %(stdout)s
                curl --connect-timeout 30 -s %(patches)s/readline63-006 | patch -p0 %(stdout)s
                curl --connect-timeout 30 -s %(patches)s/readline63-007 | patch -p0 %(stdout)s
                curl --connect-timeout 30 -s %(patches)s/readline63-008 | patch -p0 %(stdout)s
            fi
            ./configure %(stdout)s
            """ % locals())

    def _build_static_tinfo(self):
        tarball = 'https://ftp.gnu.org/gnu/ncurses/ncurses-5.9.tar.gz'
        stdout = ''

        if not self.distribution.verbose:
            stdout = '>%s' % os.devnull

        if not exists(join('build', 'ncurses', 'lib', 'libtinfo.a')):
            os.system("""\
            mkdir -p build
            cd build
            rm -rf ncurses-5.9 ncurses
            echo downloading %(tarball)s %(stdout)s
            curl --connect-timeout 30 -s %(tarball)s | tar zx
            mv ncurses-5.9 ncurses
            cd ncurses
            ./configure --with-termlib --without-debug %(stdout)s
            cd ncurses
            make libs %(stdout)s
            """ % locals())


setup(name='rl',
      version=version,
      description='Alternative Python bindings for GNU Readline',
      long_description=open('README.rst').read() + '\n' +
                       open('CHANGES.rst').read(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'License :: OSI Approved :: Python Software Foundation License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Programming Language :: C',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      keywords='gnu readline bindings',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='https://github.com/stefanholek/rl',
      license='GPL or PSF',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='rl.tests',
      ext_modules=[
          ReadlineExtension('rl.readline'),
      ],
      cmdclass={
          'build_ext': build_rl_ext,
      },
      install_requires=[
          'setuptools',
          'six',
      ],
)

