#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A license fetcher."""

import click
import sys

from datetime import date

import license

from errors import LicenseError

@click.command(help='A license fetcher.')
@click.option('-a',
              '--author',
              nargs=1,
              help='The name of the author.')
@click.option('-y',
              '--year',
              nargs=1,
              default=str(date.today().year),
              help='The year the program was created in.')
@click.option('-k',
              '--kind',
              nargs=1,
              help='The kind of license to fetch.',
              type=click.Choice(license.LICENSE_KINDS))
def li(author, year, kind):
    try:
        result = license.get(author, year, kind.lower() if kind else None)
        click.echo(result, nl=False)
    except LicenseError:
        # Cross-version way of retrieving the exception instance
        _,e,_ = sys.exc_info()
        click.echo(e.message)


if __name__ == '__main__':
    li()
