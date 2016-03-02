#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A license fetcher."""

import click
import ecstasy
import re
import os

from datetime import date

KINDS = []
for path in os.listdir(os.path.join(os.pardir, 'files')):
    kind = os.path.splitext(os.path.basename(path))[0]
    KINDS.append(kind)

class LicenseError(Exception):
    """Any Error thrown by the license utility."""

    ERROR = ecstasy.beautify('<Error>', ecstasy.RED)

    def __init__(self, message):
        """
        Initializes the Exception super class.

        A LicenseError may be thrown in any situation where the license utility
        is no longer able to function normally. Such a situation may be, for
        example, a cache miss or a connection timeout.
        """

        super(LicenseError, self).__init__(ERROR + message)

class Cache(object):

    CACHE_PATH = os.path.join('$HOME', '.license')

    HIT_MESSAGE  = ecstasy.beautify('Cache-<Hit>  for {0}: {1}.', ecstasy.GREEN)
    MISS_MESSAGE = ecstasy.beautify('Cache-<Miss> for {0}.', ecstasy.RED)

    def __init__(self):
        if not os.path.exists(CACHE_PATH):
            raise LicenseError('No cache found. You must supply all arguments.')

    def read(self, author, year, kind):
        """
        Attempts to read the cache to fetch missing arguments.

        This method will attempt to find a '.license' file in the
        'CACHE_DIRECTORY', to read any arguments that were not passed to the
        license utility.

        Arguments:
           author (str): The author passed, if any.
           year (str):   The year passed, if any.
           kind (str):   The kind of license passed, if any.

        Throws:
          LicenseError, if there was a cache miss or I/O error.
        """

        cache = self.__read_cache()

        if author is None:
           author = self.read_author(cache)
        if year is None:
           year = self.read_year(cache)
        if kind is None:
           kind = self.read_kind(cache)

        return author, year, kind

    def read_author(self, cache):
        match = re.search(r'\s*author\s*=\s*([a-zA-Z]+)', cache)
        if match is None:
            raise LicenseError(MISS_MESSAGE.format('author')
                               'You must supply an author with the -a switch. ')
        author = match.group(1)
        click.echo(HIT_MESSAGE.format('author', author))

        return author

    def read_year(self, cache):
        match = re.search(r'\s*year\s*=\s*(\d{4})', cache)
        if match is None:
            year = date.today().year
            click.echo(MISS_MESSAGE.format('year')
                       'Using current year: {0}'.format(year))
        else:
            year = match.group(1)
            click.echo(HIT_MESSAGE.format('year', year))

        return year

    def read_kind(self, cache):
        match = re.search(r'\s*kind\s*=\s*(\w+)', cache)
        if match is None:
            raise LicenseError(MISS_MESSAGE.format('kind')
                               'You must supply a kind with the -k switch.')
        kind = match.group(1)
        click.echo(HIT_MESSAGE.format('kind', kind))

        return kind

    def write(self, author, year, kind):
        assert(all(i is not None for i in [author, year, kind]))

        template = 'author={0}\nyear={1}\nkind={2}'
        with open(CACHE_PATH, 'wt') as destination:
            destination.write(template.format(author, year, kind))

    def __read_cache(self):
        cache = None
        try:
            with open(CACHE_PATH, 'rt') as source:
                cache = source.read()
        except IOError:
            raise LicenseError('Could not read from cache!')

        return cache

def validate_input(author, year, kind):
    if not re.match(r'[a-zA-Z]+', author):
        raise LicenseError("Invalid author: {0}. ".format(author)
                           "Must match '[a-zA-Z]+'.")
    if not re.match(r'\d{4}', year):
        raise LicenseError("Invalid year: {0}. ".format(author)
                           "Must match '\d+'.")

    if not re.match(r'\d{4}', kind):
        raise LicenseError("Invalid kind: {0}. ".format(author)
                           "Must match '\d+'.")



@click.group(help='License file fetcher.')
@click.option('-a',
              '--author',
              nargs=1,
              help='The name of the author.')
@click.option('-y',
              '--year',
              nargs=1,
              default=date.today().year,
              help='The year the program was created in.')
@click.option('-k',
              '--kind',
              nargs=1,
              help='The kind of license to fetch.')
def license(author, year, kind):
    cache = Cache()
    if not author or not year or not kind:
        author,year,kind = cache.read(author, year, kind)

    validate_input(author, year, kind)
    template = fetch(kind)
    text = process(template, author, year)

    cache.write(text)
    click.echo(text)

if __name__ == '__main__':
    license()
