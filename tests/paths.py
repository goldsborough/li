#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Convenience path declarations."""

import os
import sys

TEST_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.dirname(TEST_PATH)

sys.path.insert(0, ROOT_PATH)
