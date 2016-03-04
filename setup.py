#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
setup.py script for setuptools.
"""

import re
import setuptools

with open('li/__init__.py') as init:
    version = re.search(
                r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        init.read(),
                re.MULTILINE
        ).group(1)

with open('README.rst') as readme:
    long_description = readme.read()

requirements = [
    'click==6.3',
    'coverage==4.0.3',
    'coveralls==1.1',
    'docopt==0.6.2',
    'ecstasy==0.1.3',
    'enum34==1.1.2',
    'py==1.4.31',
    'pytest==2.8.7',
    'requests==2.9.1',
    'wheel==0.24.0'
]

test_requirements = [
    "pytest==2.8.7",
    "coveralls==1.1",
    "coverage==4.0.3"
]

setuptools.setup(
    name='li',

    version=version,

    description='A tool to quickly fetch a license.',
    long_description=long_description,

    author='Peter Goldsborough',
    author_email='peter@goldsborough.me',

    url="https://github.com/goldsborough/li",

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

    keywords='li projects',

    packages=setuptools.find_packages(exclude=['tests', 'files']),

    include_package_data=True,

    package_data=dict(li=[
        '../README.rst',
        '../LI.txt',
        '../Makefile',
        '../files/*'
    ]),

    install_requires=requirements,

    test_suite="tests",

    tests_require=test_requirements,

    entry_points=dict(console_scripts=['li = li.cli:li'])
)
