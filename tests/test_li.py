#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test classes for li.py"""

import pytest
import os

from collections import namedtuple

import paths

from license import li
from license.errors import LicenseError

@pytest.fixture()
def fixture():
    Fixture = namedtuple('Fixture', [
        'author',
        'year',
        'kind',
        'license'
    ])

    with open(os.path.join(paths.TEST_PATH, 'test.txt')) as source:
        test = source.read()

    return Fixture('Bat Man', '2016', 'mit', test)


@pytest.fixture()
def mit():
    with open(os.path.join(paths.ROOT_PATH, 'files', 'mit.txt')) as source:
        return source.read()


def test_validate_author_good_patterns(fixture):
    try:
        li.validate(fixture.author, fixture.year, fixture.kind)
    except LicenseError:
        assert False

    try:
        li.validate('Bat', fixture.year, fixture.kind)
    except LicenseError:
        assert False

    try:
        li.validate('Bat Man-Dog', fixture.year, fixture.kind)
    except LicenseError:
        assert False

    try:
        li.validate('Really Long-Weird Name-Or-So', fixture.year, fixture.kind)
    except LicenseError:
        assert False

    try:
        li.validate('Bat-Man Dog-Cat', fixture.year, fixture.kind)
    except LicenseError:
        assert False


def test_validate_author_bad_patterns(fixture):
    with pytest.raises(LicenseError):
        li.validate('', fixture.year, fixture.kind)

    with pytest.raises(LicenseError):
        li.validate('123', fixture.year, fixture.kind)

    with pytest.raises(LicenseError):
        li.validate('B4t M4n69', fixture.year, fixture.kind)

    with pytest.raises(LicenseError):
        li.validate('B%m M!(n', fixture.year, fixture.kind)

    with pytest.raises(LicenseError):
        li.validate('No_Real_Name_Has_Underscores', fixture.year, fixture.kind)


def test_validate_year_good_patterns(fixture):
    try:
        li.validate(fixture.author, fixture.year, fixture.kind)
    except LicenseError:
        assert False

    try:
        li.validate(fixture.author, '1234', fixture.kind)
    except LicenseError:
        assert False

    try:
        li.validate(fixture.author, '0000', fixture.kind)
    except LicenseError:
        assert False


def test_validate_year_bad_patterns(fixture):
    with pytest.raises(LicenseError):
        li.validate(fixture.author, '', fixture.kind)

    with pytest.raises(LicenseError):
        li.validate(fixture.author, '123', fixture.kind)

    with pytest.raises(LicenseError):
        li.validate(fixture.author, '0', fixture.kind)

    with pytest.raises(LicenseError):
        li.validate(fixture.author, '4BxY', fixture.kind)

    with pytest.raises(LicenseError):
        li.validate(fixture.author, '@#$%', fixture.kind)


def test_validate_kind_good_patterns(fixture):
    for kind in li.LICENSE_KINDS:
        try:
            li.validate(fixture.author, fixture.year, kind)
        except LicenseError:
            assert False


def test_validate_kind_bad_patterns(fixture):
    with pytest.raises(LicenseError):
        li.validate(fixture.author, fixture.year, '')

    with pytest.raises(LicenseError):
        # should be lower-case
        li.validate(fixture.author, fixture.year, 'MIT')

    with pytest.raises(LicenseError):
        li.validate(fixture.author, fixture.year, 'm1t')

    with pytest.raises(LicenseError):
        li.validate(fixture.author, fixture.year, '123')

    with pytest.raises(LicenseError):
        li.validate(fixture.author, fixture.year, 'Whatever')


def test_fetch(fixture, mit):
    assert li.fetch(fixture.kind) == mit


def test_insert(fixture, mit):
    assert li.insert(mit, fixture.author, fixture.year) == fixture.license
