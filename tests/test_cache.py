#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test classes for cache.py"""

import pytest
import re
import sys

import paths

from license import cache
from license import errors

@pytest.fixture
def contents():
    cache.CACHE_PATH = '.license'
    text = 'author=Foo Bar\nkind=Cat'
    with open('.license', 'wt') as destination:
        destination.write(text)

    return text

def test_read_throws_for_non_existant_cache():
    cache.CACHE_PATH = ''
    with pytest.raises(errors.LicenseError):
        cache.read(None, None)

def test_can_read_cache(contents):
    assert contents == cache.read_cache()

def test_read_author_returns_correctly_when_wanted(contents):
    assert cache.read_author(contents) == 'Foo Bar'

def test_read_author_raises_when_no_match():
    with pytest.raises(errors.LicenseError):
        cache.read_author('kind=Cat')

def test_read_kind_returns_correctly_when_wanted(contents):
    print(contents)
    assert cache.read_kind(contents) == 'Cat'

def test_read_kind_raises_when_no_match():
    with pytest.raises(errors.LicenseError):
        cache.read_kind('author=foo')

def test_read_does_nothing_when_both_arguments_not_none():
    assert cache.read('Chicken Man', 'Elephant') == ('Chicken Man', 'Elephant')

def test_read_replaces_author_when_none():
    assert cache.read(None, 'Elephant') == ('Foo Bar', 'Elephant')

def test_read_replaces_kind_when_none():
    assert cache.read('Chicken Man', None) == ('Chicken Man', 'Cat')

def test_write(contents):
    cache.write('A B C', 'D')
    with open(cache.CACHE_PATH) as source:
        assert source.read() == 'author=A B C\nkind=D'
