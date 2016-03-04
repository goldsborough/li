import os
import re
import sys

from li import cache

from li.errors import LicenseError

def get_license_kinds():
    kinds = set()
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
    for license_path in os.listdir(os.path.join(root, 'files')):
        name = os.path.splitext(os.path.basename(license_path))[0]
        kinds.add(name)

    return kinds

LICENSE_KINDS = get_license_kinds()


def get(author, year, kind):
    assert year is not None, "Year should have been defaulted by click"

    if not author or not kind:
        author, kind = cache.read(author, kind)

    validate(author, year, kind)
    template = fetch(kind)
    text = insert(template, author, year)

    cache.write(author, kind)

    return text


def validate(author, year, kind):
    author_pattern = r'^[a-zA-Z -]+$'
    year_pattern = r'^\d{4}$'

    if not re.match(author_pattern, author):
        raise LicenseError("Invalid author: {0}. ".format(author) +
                           "Must match '{0}'.".format(author_pattern))

    if not re.match(year_pattern, year):
        raise LicenseError("Invalid year: {0}. ".format(year) +
                           "Must match '{0}'.".format(year_pattern))

    if kind not in LICENSE_KINDS:
        raise LicenseError("Invalid license kind: {0}. ".format(kind) +
                           "Must be one of: " + ", ".join(LICENSE_KINDS))

def fetch(kind):
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        os.pardir,
        'files/{0}.txt'.format(kind)
    )
    with open(path, 'rt') as source:
        template = source.read()

    return template


def insert(template, author, year):
    template = re.sub(r'<author>', author, template)
    template = re.sub(r'<year>', year, template)

    return template
