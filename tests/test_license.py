#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test classes for license.py"""

import pytest
import re
import os

from collections import namedtuple
from datetime import date

from tests import paths

from li import license
from li import cache
from li.errors import LicenseError

@pytest.fixture()
def fixture():
    Fixture = namedtuple('Fixture', [
        'author',
        'year',
        'kind',
        'expected'
    ])

    with open(os.path.join(paths.TEST_PATH, 'test.txt')) as source:
        test = source.read()

    return Fixture(
        'Bat Man',
        str(date.today().year),
        'mit',
        test
    )

@pytest.fixture
def cache_fixture(request):
    cache.CACHE_PATH = os.path.join(paths.TEST_PATH, '.license')

    text = 'author=Bat Man\nkind=mit'
    with open(cache.CACHE_PATH, 'wt') as destination:
        destination.write(text)

    def finalize():
        os.remove(cache.CACHE_PATH)

    request.addfinalizer(finalize)

@pytest.fixture()
def mit():
    with open(os.path.join(paths.ROOT_PATH, 'files', 'mit.txt')) as source:
        return source.read()


def test_validate_author_good_patterns(fixture):
    try:
        license.validate(fixture.author, fixture.year, fixture.kind)
    except LicenseError:
        assert False

    try:
        license.validate('Bat', fixture.year, fixture.kind)
    except LicenseError:
        assert False

    try:
        license.validate('Bat Man-Dog', fixture.year, fixture.kind)
    except LicenseError:
        assert False

    try:
        license.validate(
            'Really Long-Weird Name-Or-So',
            fixture.year,
            fixture.kind
        )
    except LicenseError:
        assert False

    try:
        license.validate('Bat-Man Dog-Cat', fixture.year, fixture.kind)
    except LicenseError:
        assert False


def test_validate_author_bad_patterns(fixture):
    with pytest.raises(LicenseError):
        license.validate('', fixture.year, fixture.kind)

    with pytest.raises(LicenseError):
        license.validate('123', fixture.year, fixture.kind)

    with pytest.raises(LicenseError):
        license.validate('B4t M4n69', fixture.year, fixture.kind)

    with pytest.raises(LicenseError):
        license.validate('B%m M!(n', fixture.year, fixture.kind)

    with pytest.raises(LicenseError):
        license.validate(
            'No_Real_Name_Has_Underscores',
            fixture.year,
            fixture.kind
        )


def test_validate_year_good_patterns(fixture):
    try:
        license.validate(fixture.author, fixture.year, fixture.kind)
    except LicenseError:
        assert False

    try:
        license.validate(fixture.author, '1234', fixture.kind)
    except LicenseError:
        assert False

    try:
        license.validate(fixture.author, '0000', fixture.kind)
    except LicenseError:
        assert False


def test_validate_year_bad_patterns(fixture):
    with pytest.raises(LicenseError):
        license.validate(fixture.author, '', fixture.kind)

    with pytest.raises(LicenseError):
        license.validate(fixture.author, '123', fixture.kind)

    with pytest.raises(LicenseError):
        license.validate(fixture.author, '0', fixture.kind)

    with pytest.raises(LicenseError):
        license.validate(fixture.author, '4BxY', fixture.kind)

    with pytest.raises(LicenseError):
        license.validate(fixture.author, '@#$%', fixture.kind)


def test_validate_kind_good_patterns(fixture):
    for kind in license.LICENSE_KINDS:
        try:
            license.validate(fixture.author, fixture.year, kind)
        except LicenseError:
            assert False


def test_validate_kind_bad_patterns(fixture):
    with pytest.raises(LicenseError):
        license.validate(fixture.author, fixture.year, '')

    with pytest.raises(LicenseError):
        # should be lower-case
        license.validate(fixture.author, fixture.year, 'MIT')

    with pytest.raises(LicenseError):
        license.validate(fixture.author, fixture.year, 'm1t')

    with pytest.raises(LicenseError):
        license.validate(fixture.author, fixture.year, '123')

    with pytest.raises(LicenseError):
        license.validate(fixture.author, fixture.year, 'Whatever')


def test_fetch(fixture, mit):
    assert license.fetch(fixture.kind) == mit


def test_insert(fixture, mit):
    assert license.insert(mit, fixture.author, fixture.year) == fixture.expected

def test_get_does_does_not_modfiy_author_if_ok(fixture):
    text = license.get(fixture.author, fixture.year, fixture.kind)

    assert fixture.author in text

def test_get_does_does_not_modfiy_year_if_ok(fixture):
    text = license.get(fixture.author, fixture.year, fixture.kind)

    assert fixture.year in text

def test_get_gets_right_license(fixture):
    result = license.get(fixture.author, fixture.year, fixture.kind)
    assert result == fixture.expected

def test_get_reads_cache_when_author_is_none(fixture, cache_fixture):
    assert fixture.expected == license.get(None, fixture.year, fixture.kind)

def test_get_reads_cache_when_kind_is_none(fixture, cache_fixture):
    assert fixture.expected == license.get(fixture.author, fixture.year, None)

def test_get_fails_when_year_is_none(fixture):
    with pytest.raises(AssertionError):
        license.get(fixture.author, None, fixture.kind)
