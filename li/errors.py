#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Error classes."""

import ecstasy

class LicenseError(Exception):
    """Any error thrown by the license utility."""

    ERROR = ecstasy.beautify('<Error>: ', ecstasy.Color.Red)

    def __init__(self, message):
        """
        Initializes the Exception super class.

        A LicenseError may be thrown in any situation where the license utility
        is no longer able to function normally. Such a situation may be, for
        example, a cache miss or a connection timeout.
        """

        super(LicenseError, self).__init__(self.ERROR + message)
