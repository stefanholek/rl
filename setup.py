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

from os.path import join, exists, isdir

version = '2.5'
readline_version = '7.0'


class ReadlineExtension(Extension):

    def __init__(self, name):
        # Describe the extension
        sources = [
            'rl/readline.c',
            'rl/stringarray.c',
            'rl/unicode.c',
            'rl/iterator.c',
        ]
        libraries = []
        Extension.__init__(self, name, sources)

        # Use include and library dirs from Python build
        self.use_include_dirs()
        self.use_library_dirs()

        # Use Mac Python library dir
        if sys.platform == 'darwin':
            if self.sys_path_contains('/Library/Frameworks/Python.framework'):
                self.library_dirs.append(
                    '/Library/Frameworks/Python.framework/Versions/%d.%d/lib' % sys.version_info[:2])

        # Strip debug symbols
        if sys.platform == 'darwin':
            stripflag = '-S'
        else:
            stripflag = get_config_var('STRIPFLAG') or '-s'
        self.extra_link_args.extend(['-Xlinker', stripflag])

        self.use_static_readline()
        self.suppress_warnings()

    def sys_path_contains(self, string):
        for dir in sys.path:
            if dir.startswith(string):
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

        if '-Wall' in cflags or sys.platform.startswith('freebsd'):
            self.extra_compile_args.append('-Wno-all')
        if '-Wstrict-prototypes' in cflags:
            self.extra_compile_args.append('-Wno-strict-prototypes')
        if '-Wsign-compare' in cflags:
            self.extra_compile_args.append('-Wno-sign-compare')
        if '-Wunreachable-code' in cflags:
            self.extra_compile_args.append('-Wno-unreachable-code')
        if '-Wshorten-64-to-32' in cflags:
            self.extra_compile_args.append('-Wno-shorten-64-to-32')

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
            'build/readline/colors.c',
            'build/readline/parse-colors.c',
        ])

        self.define_macros.extend([
            ('HAVE_CONFIG_H', None),
            ('RL_LIBRARY_VERSION', '"%s"' % readline_version),
        ])

        self.include_dirs = ['build', 'build/readline'] + self.include_dirs


class build_rl_ext(build_ext):

    def build_extension(self, ext):
        # Find a termcap library
        if os.environ.get('RL_TERMCAP'):
            termcap = os.environ.get('RL_TERMCAP')
        else:
            termcap = self.find_termcap(ext)

        if termcap:
            ext.libraries.append(termcap)
        else:
            log.warn('WARNING: Failed to find a termcap library')

        # Prepare the source tree
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
                if isdir(dir):
                    for entry in os.listdir(dir):
                        if entry.startswith(lib_name):
                            libs.append(join(dir, entry))
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
                if 'lib%s.' % name in libraries:
                    return name
        return ''

    def configure_static_readline(self):
        srcdir = os.getcwd()
        version = readline_version
        stdout = ''

        cc = os.environ.get('CC') or get_config_var('CC') or 'cc'

        if not self.distribution.verbose:
            stdout = '>%s' % os.devnull

        if not exists(join('build', 'readline', 'config.h')):
            os.system("""\
            mkdir -p build
            cd build
            rm -rf readline-%(version)s readline
            tar zxf %(srcdir)s/readline-%(version)s.tar.gz
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
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: MacOS',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Operating System :: POSIX :: Linux',
          'Operating System :: POSIX :: BSD',
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
      license='GPL',
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

