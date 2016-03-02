#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest2

sys.path.insert(0, os.path.abspath('..'))

import ecstasy.errors as errors


class TestErrors(unittest2.TestCase):

	def test_error_message_retrieval(self):

		try:
			raise errors.EcstasyError("message")

		except errors.EcstasyError as e:
			self.assertEqual(e.what, "message")

	def test_error_position_retrieval_is_none(self):
		self.assertIsNone(errors.position("", 666))

	def test_error_position_retrieval_raises(self):

		self.assertRaises(errors.InternalError,
						  errors.position,
						  "abc",
						  -1)

		self.assertRaises(errors.InternalError,
						  errors.position,
						  "abc",
						  3)

		self.assertRaises(errors.InternalError,
						  errors.position,
						  "abc",
						  5)

	def test_error_position_retrieval_is_correct(self):

		self.assertEqual(errors.position("abc", 1), "1")

		self.assertEqual(errors.position("abc\ndef\nghi", 5), "1:1")

		self.assertEqual(errors.position("abc\ndef\nghi", 2), "0:2")

		self.assertEqual(errors.position("abc\ndef\nghi", 8), "2:0")


	def test_spoken_word_number_retrieval(self):

		self.assertEqual(errors.number(0), "a 0th")

		self.assertEqual(errors.number(1), "a 1st")

		self.assertEqual(errors.number(2), "a 2nd")

		self.assertEqual(errors.number(3), "a 3rd")

		self.assertEqual(errors.number(5), "a 5th")

		self.assertEqual(errors.number(8), "an 8th")

		self.assertEqual(errors.number(11), "an 11th")

		self.assertEqual(errors.number(21), "a 21st")

		self.assertEqual(errors.number(32), "a 32nd")

		self.assertEqual(errors.number(56), "a 56th")

		self.assertEqual(errors.number(123), "a 123rd")

		self.assertEqual(errors.number(11000), "an 11,000th")

		self.assertEqual(errors.number(8000000), "an 8,000,000th")

def main():
	unittest2.main()

if __name__ == "__main__":
	main()