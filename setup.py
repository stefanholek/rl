from setuptools import setup, find_packages, Extension
from os.path import join, exists
from sys import platform

version = '1.0'


# On Linux, install libreadline5-dev (or equivalent) before attempting to
# build completion. On Mac OS X, you need a Python built with MacPorts or
# Fink, as the system Python is linked to the BSD editline library and not
# GNU readline.

include_dirs = []
library_dirs = []

if platform == 'darwin':
    # MacPorts
    if exists('/opt/local/include'):
        include_dirs += ['/opt/local/include']
        library_dirs += ['/opt/local/lib']
    # Fink
    if exists('/sw/local/include'):
        include_dirs += ['/sw/local/include']
        library_dirs += ['/sw/local/lib']


_readline = \
Extension(name='completion._readline',
          sources=[join('completion', '_readline.c')],
          libraries=['readline', 'ncursesw'],
          include_dirs=include_dirs,
          library_dirs=library_dirs,
)


setup(name='completion',
      version=version,
      description='Alternative Python-Readline interface focused on completion',
      long_description=open('README.txt').read() + '\n' +
                       open('CHANGES.txt').read(),
      classifiers=[
          'Programming Language :: Python',
      ],
      keywords='gnu readline completion interface',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='http://pypi.python.org/pypi/completion',
      license='Python',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      test_suite='completion.tests',
      ext_modules=[
          _readline,
      ],
      install_requires=[
          'setuptools',
      ],
)

