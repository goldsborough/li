#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test classes for errors.py"""

import pytest
import re
import sys

from tests import paths

from li.errors import LicenseError

def test_error_message_contains_wanted():
    try:
        raise LicenseError('foo')
    except LicenseError:
        _,e,_ = sys.exc_info()
        assert hasattr(e, 'message')
        assert re.search(r'foo', e.message) is not None

def test_error_message_contains_error_preamble():
    try:
        raise LicenseError('foo')
    except LicenseError:
        _,e,_ = sys.exc_info()
        assert hasattr(e, 'message')
        assert re.search(r'Error.*:', e.message) is not None

def test_error_message_preamble_is_formatted_well():
    try:
        raise LicenseError('foo')
    except LicenseError:
        _,e,_ = sys.exc_info()
        assert hasattr(e, 'message')
        assert re.search(r'\033\[91mError\033\[0;m.*:', e.message) is not None

def test_error_message_is_fine_all_together():
    try:
        raise LicenseError('foo')
    except LicenseError:
        _,e,_ = sys.exc_info()
        assert hasattr(e, 'message')
        assert e.message == "\033[91mError\033[0;m: foo"
