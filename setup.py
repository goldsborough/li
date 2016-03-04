#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
setup.py script for setuptools.
"""

import re

from setuptools import setup, find_packages

with open('license/__init__.py') as init:
    version = re.search(
                r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        init.read(),
                re.MULTILINE
        ).group(1)

with open('README.rst') as readme:
    long_description = readme.read()

requirements = [
    "click<=6.3",
    "ecstasy==0.1.3"
]

test_requirements = [
    "pytest==2.8.7",
    "coveralls==1.1",
    "coverage==4.0.3"
]

setup(
    name='license',

    version=version,

    description='A tool to quickly fetch a license.',
    long_description=long_description,

    author='Peter Goldsborough',
    author_email='peter@goldsborough.me',

    url="https://github.com/goldsborough/license",

    license='MIT',

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

    keywords='license projects',

    include_package_data=True,

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    install_requires=requirements,

    test_suite="tests",

    tests_require=test_requirements
)
