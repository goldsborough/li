#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A Cache Manager."""

import ecstasy
import click
import os
import re
import sys

from li.errors import LicenseError

CACHE_PATH = os.path.join(os.environ['HOME'], '.license')

HIT_MESSAGE = ecstasy.beautify(
    "Cache-<Hit> for {0}: '{1}'.",
    ecstasy.Color.Green
)

MISS_MESSAGE = ecstasy.beautify(
    'Cache-<Miss> for {0}.',
    ecstasy.Color.Red
)

def read(author, kind):
    """
    Attempts to read the cache to fetch missing arguments.

    This method will attempt to find a '.license' file in the
    'CACHE_DIRECTORY', to read any arguments that were not passed to the
    license utility.

    Arguments:
       author (str): The author passed, if any.
       kind (str):   The kind of license passed, if any.

    Throws:
      LicenseError, if there was a cache miss or I/O error.
    """

    if not os.path.exists(CACHE_PATH):
        raise LicenseError('No cache found. You must '
                           'supply at least -a and -k.')

    cache = read_cache()

    if author is None:
        author = read_author(cache)
    if kind is None:
        kind = read_kind(cache)

    return author, kind

def write(author, kind):
    assert all(i is not None for i in [author, kind])

    template = 'author={0}\nkind={1}'
    with open(CACHE_PATH, 'wt') as destination:
        destination.write(template.format(author, kind))


def read_author(cache):
    match = re.search(r'\s*author\s*=\s*([a-zA-Z -]+)', cache)
    if match is None:
        raise LicenseError(MISS_MESSAGE.format('author') +
                           'You must supply an author with the -a switch. ')
    author = match.group(1)
    click.echo(HIT_MESSAGE.format('author', author), file=sys.stderr)

    return author

def read_kind(cache):
    match = re.search(r'\s*kind\s*=\s*(\w+)', cache)
    if match is None:
        raise LicenseError(MISS_MESSAGE.format('kind') +
                           'You must supply a kind with the -k switch.')
    kind = match.group(1)
    click.echo(HIT_MESSAGE.format('kind', kind), file=sys.stderr)

    return kind


def read_cache():
    cache = None
    try:
        with open(CACHE_PATH, 'rt') as source:
            cache = source.read()
    except IOError:
        raise LicenseError('Could not read from cache.')

    return cache
