from setuptools import setup, find_packages, Extension
from os.path import join, exists
from sys import platform

version = '1.0a6'


# On Linux, install libreadline5-dev (or equivalent) before attempting to
# build rl. On Mac OS X, you need a Python built with MacPorts or Fink,
# as the system Python is linked to the BSD editline library and not
# GNU readline.

include_dirs = []
library_dirs = []

libraries = ['readline', 'ncurses']

if platform == 'darwin':
    # MacPorts
    if exists('/opt/local/include'):
        include_dirs = ['/opt/local/include']
        library_dirs = ['/opt/local/lib']
    # Fink
    elif exists('/sw/local/include'):
        include_dirs = ['/sw/local/include']
        library_dirs = ['/sw/local/lib']

    libraries = ['readline', 'ncursesw']


readline = \
Extension(name='rl._readline',
          sources=[join('rl', '_readline.c')],
          libraries=libraries,
          include_dirs=include_dirs,
          library_dirs=library_dirs,
)


setup(name='rl',
      version=version,
      description='Python readline interface focusing on completion',
      long_description=open('README.txt').read() + '\n' +
                       open('CHANGES.txt').read(),
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: C',
          'Operating System :: Unix',
          'Operating System :: MacOS :: MacOS X',
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: BSD License',
      ],
      keywords='gnu readline completion interface',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='http://pypi.python.org/pypi/rl',
      license='BSD',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      use_2to3=True,
      test_suite='rl.tests',
      ext_modules=[
          readline,
      ],
      install_requires=[
          'setuptools',
      ],
)

