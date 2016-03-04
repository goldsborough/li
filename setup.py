#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
setup.py script for setuptools.
"""

import re
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

with open('li/__init__.py') as init:
    version = re.search(
                r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        init.read(),
                re.MULTILINE
        ).group(1)

with open('README.rst') as readme:
    long_description = readme.read()

class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['tests']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='li',

    version=version,

    description='A tool to quickly fetch a license.',
    long_description=long_description,

    url="https://github.com/goldsborough/li",
    license='MIT',

    author='Peter Goldsborough',
    author_email='peter@goldsborough.me',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    keywords='li projects',

    packages=find_packages(exclude=['tests', 'files']),

    cmdclass=dict(test=PyTest),

    include_package_data=True,
    package_data=dict(li=[
        '../README.rst',
        '../LI.txt',
        '../Makefile',
        '../files/*'
    ]),

    test_suite="tests",
    tests_require=[
        "pytest==2.8.7"
    ],

    install_requires=[
        'click==6.3',
        'docopt==0.6.2',
        'ecstasy==0.1.3',
        'enum34==1.1.2'
    ],
    entry_points=dict(console_scripts=['li = li.cli:li'])
)
