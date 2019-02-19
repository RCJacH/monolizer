#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()

doclink = """
Documentation
-------------

The full documentation is at http://monolizer.rtfd.org."""

history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='monolizer',
    version='0.1.1a1',
    description='Identify and convert fake stereo audio files to mono-channel ones, and delete empty audio files.',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='RCJacH',
    author_email='RCJacH@outlook.com',
    url='https://github.com/RCJacH/monolizer',
    packages=[
        'monolizer',
    ],
    # package_dir={'monolizer': 'monolizer'},
    include_package_data=True,
    install_requires=[
        'PySoundFile>=0.9.0',
        'numpy',
    ],
    extras_require={
        'testing': [
            'pytest>=3.0.0',
        ]
    },
    license='MIT',
    zip_safe=False,
    keywords='monolizer monolize wave audio mono stereo music',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Artistic Software',
        'Topic :: Multimedia :: Sound/Audio',
    ],
)
