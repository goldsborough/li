#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest2
import collections

sys.path.insert(0, os.path.abspath('..'))

import ecstasy.parser as parser
import ecstasy.errors as errors
import ecstasy.flags as flags

class TestParserGetFlags(unittest2.TestCase):

	def setUp(self):

		self.non_nested_positionals = [
			flags.Style.Dim,
			flags.Color.Red
		]

		self.first_positionals = [
			flags.Style.Blink | flags.Color.Red,
			flags.Color.Blue,
			flags.Fill.Green
		]

		self.second_positionals = [flags.Style.Underline]

		self.nested_positionals = [
			self.first_positionals,
			self.second_positionals
		]

		self.free_positional = flags.Fill.Black

		self.tuple_always = ("b", "c")

		self.dict_always = {
			"a": flags.Color.Blue,
			self.tuple_always: flags.Fill.Yellow
		}

		self.parser = parser.Parser([self.non_nested_positionals,
									 self.nested_positionals,
									 self.free_positional,
									 self.dict_always],
									 {"free": flags.Style.Hidden})

	def test_handles_free_positionals_correctly(self):

		self.assertIn(flags.Fill.Black, self.parser.positional)

	def test_handles_free_always_correctly(self):

		self.assertIn("free", self.parser.always)

		self.assertEqual(self.parser.always["free"], flags.Style.Hidden)

	def test_expands_non_nested_positionals_correctly(self):

		for flag in self.non_nested_positionals:
			self.assertIn(flag, self.parser.positional)

	def test_expands_nested_positionals_correctly(self):

		for i in self.nested_positionals:
			for flag in i:
				self.assertIn(flag, self.parser.positional)

	def test_expands_non_tuple_dictionary_always_correctly(self):

		self.assertIn("a", self.parser.always)

		self.assertEqual(self.dict_always["a"],
						 self.parser.always["a"])

	def test_expands_tuple_dictionary_always_correctly(self):

		for i in self.tuple_always:

			self.assertIn(i, self.parser.always)

			self.assertEqual(self.dict_always[self.tuple_always],
							 self.parser.always[i])

class TestEmptyParserGetFlags(unittest2.TestCase):

	def setUp(self):
		self.parser = parser.Parser(None, None)

	def test_accepts_any_iterable(self):

		positional = self.parser.get_flags([1, 2])

		self.assertListEqual(positional, [1, 2])

		self.parser.get_flags((1, 2))

		self.assertListEqual(positional, [1, 2])

		self.parser.get_flags(set([1, 2]))

		self.assertListEqual(positional, [1, 2])

		Iterable = collections.namedtuple("Iterable", "x, y")

		self.parser.get_flags(Iterable(1, 2))

		self.assertListEqual(positional, [1, 2])

	def test_recognizes_invalid_flag_combination(self):

		self.assertRaises(errors.FlagError,
						  self.parser.get_flags,
						  [-1])

		self.assertRaises(errors.FlagError,
						  self.parser.get_flags,
						  [flags.LIMIT])

		self.assertRaises(errors.FlagError,
						  self.parser.get_flags,
						  [flags.LIMIT + 100])

	def test_recognizes_invalid_argument(self):

		self.assertRaises(errors.EcstasyError,
						  self.parser.get_flags,
						  [parser.Phrase()])

		self.assertRaises(errors.EcstasyError,
						  self.parser.get_flags,
						  [None])

	def test_recognizes_invalid_dictionary_key(self):

		self.assertRaises(errors.EcstasyError,
						  self.parser.get_flags,
						  [{1: flags.Style.Bold}])

		self.assertRaises(errors.EcstasyError,
						  self.parser.get_flags,
						  [{None: flags.Style.Bold}])

class TestBeautify(unittest2.TestCase):

	def setUp(self):

		self.parser = parser.Parser([flags.Color.Red,
									 flags.Fill.White],
									None)

	def test_ignores_empty_string(self):

		self.assertEqual(self.parser.beautify(""), "")

	def test_does_nothing_when_no_phrases(self):

		self.assertEqual(self.parser.beautify("batman spiderman"),
						 "batman spiderman")

class TestParserParse(unittest2.TestCase):

	def setUp(self):

		self.parser = parser.Parser([flags.Color.White], { })

	def test_parses_only_non_nested_simple_phrases(self):
		
		results = self.parser.parse("<abc>\n <def>")[1]

		self.assertEqual(len(results), 2)

		expected = [
			parser.Phrase(0, 4, "abc"),
			parser.Phrase(7, 11, "def")
		]

		for phrase, wanted in zip(results, expected):
			self.assertEqual(phrase, wanted)

	def test_parses_only_nested_simple_phrase(self):

		results = self.parser.parse("<<abc> <def> ghi>")[1]

		self.assertEqual(len(results), 1)

		self.assertEqual(len(results[0].nested), 2)

		results = [results[0], results[0].nested[0], results[0].nested[1]]

		expected = [
			parser.Phrase(0, 16, "<abc> <def> ghi"),
			parser.Phrase(0, 4, "abc"),
			parser.Phrase(6, 10, "def")
		]

		expected[0].nested = expected[1:]

		for phrase, wanted in zip(results, expected):
			self.assertEqual(phrase, wanted)

	def test_parses_only_non_nested_argument_phrases(self):

		results = self.parser.parse("<(+)abc><(1,2,3)def><(-1, -2!)ghi>")[1]

		self.assertEqual(len(results), 3)

		expected = [
			parser.Phrase(0, 4, "abc", increment=True),
			parser.Phrase(5, 9, "def", args=[1,2,3]),
			parser.Phrase(10, 14, "ghi", args=[-1,-2], override=True)
		]

		for phrase, wanted in zip(results, expected):
			self.assertEqual(phrase, wanted) 

	def test_parses_only_nested_argument_phrases(self):

		results = self.parser.parse("<(+)<(-1!)abc> <(12345)def> ghi>")[1]

		self.assertEqual(len(results), 1)

		self.assertEqual(len(results[0].nested), 2)

		expected = [parser.Phrase(0, 16, "<abc> <def> ghi", increment=True)]

		expected[0].nested = [
			parser.Phrase(0, 4, "abc", args=[-1], override=True),
			parser.Phrase(6, 10, "def", args=[12345])
		]

		for phrase, wanted in zip(results, expected):
			self.assertEqual(phrase, wanted)

	def test_parses_non_nested_simple_and_argument_phrases(self):

		results = self.parser.parse("<(0)abc> <def> <(-1, -2!)ghi>")[1]

		self.assertEqual(len(results), 3)

		expected = [
			parser.Phrase(0, 4, "abc", args=[0]),
			parser.Phrase(6, 10, "def"),
			parser.Phrase(12, 16, "ghi", args=[-1, -2], override=True)
		]

		for phrase, wanted in zip(results, expected):
			self.assertEqual(phrase, wanted) 

	def test_parses_nested_simple_and_argument_phrases(self):

		results = self.parser.parse("jkl < <(0) <(-1!)abc> <def> ghi> >")[1]

		self.assertEqual(len(results), 1)

		self.assertEqual(len(results[0].nested), 1)

		self.assertEqual(len(results[0].nested[0].nested), 2)

		expected = [parser.Phrase(4, 25, " < <abc> <def> ghi> ")]

		expected[0].nested = [parser.Phrase(1, 18, " <abc> <def> ghi", args=[0])]

		expected[0].nested[0].nested = [
			parser.Phrase(1, 5, "abc", args=[-1], override=True),
			parser.Phrase(7, 11, "def")
		]

		for phrase, wanted in zip(results, expected):
			self.assertEqual(phrase, wanted)

	def test_raises_when_no_closing_tag(self):

		self.assertRaises(errors.ParseError,
						  self.parser.parse,
						  "<abc")

		self.assertRaises(errors.ParseError,
						  self.parser.parse,
						  "<abc <def>")

		self.assertRaises(errors.ParseError,
						  self.parser.parse,
						  "<abc <def <ghi>>")


	def test_parser_escapes_meta_characters(self):
		pass

	def test_warns_about_unescaped_meta_characters(self):

		self.assertWarns(Warning,
						 self.parser.parse,
						 " > abc")

		self.assertWarns(Warning,
						 self.parser.parse,
						 " <( abc>")

		self.assertWarns(Warning,
						 self.parser.parse,
						 " <abc> )")

	def test_raises_for_invalid_args(self):

		self.assertRaises(errors.ParseError,
						  self.parser.parse,
						  "<()asdf>")

		self.assertRaises(errors.ParseError,
						  self.parser.parse,
						  "<(nonsense)asdf>")

		self.assertRaises(errors.ParseError,
						  self.parser.parse,
						  "<(0+)asdf>")

		self.assertRaises(errors.ParseError,
						  self.parser.parse,
						  "<(?)asdf>")

class TestParserStringify(unittest2.TestCase):

	def setUp(self):

		self.positional = [
			flags.Color.Red | flags.Fill.Blue,
			flags.Style.Invert,
			flags.Style.Blink
		]

		self.codes = [flags.codify(i) for i in self.positional]

		self.always = {"always": flags.Color.White}

		self.always_code = flags.codify(self.always["always"])

		self.parser = parser.Parser(self.positional, self.always)

	def test_stringifies_non_nested_simple_phrases_correctly(self):

		result = self.parser.beautify("<abc> <def>")

		expected = "\033[{0}mabc\033[0;m ".format(self.codes[0])
		expected += "\033[{0}mdef\033[0;m".format(self.codes[1])

		self.assertEqual(result, expected)


	def test_stringifies_nested_simple_phrases_correctly(self):

		result = self.parser.beautify("<<abc> <def>>")

		# After a nested phrase, the parent style should be reset
		expected = "\033[{0}m\033[{1}mabc\033[0;{0}m".format(self.codes[0],
															 self.codes[1])

		expected += " \033[{0}mdef\033[0;{1}m\033[0;m".format(self.codes[2],
															self.codes[0])

		self.assertEqual(result, expected)

	def test_stringifies_non_nested_argument_phrases_correctly(self):
		
		result = self.parser.beautify("<(0)abc> <(-1)def>")

		expected = "\033[{0}mabc\033[0;m ".format(self.codes[0])
		expected += "\033[{0}mdef\033[0;m".format(self.codes[-1])

		self.assertEqual(result, expected)

	def test_stringifies_nested_argument_phrases_correctly(self):

		result = self.parser.beautify("<(1)<(0)abc> <(-2)def>>")

		# After a nested phrase, the parent style should be reset
		expected = "\033[{0}m\033[{1}mabc\033[0;{0}m".format(self.codes[1],
															 self.codes[0])

		expected += " \033[{0}mdef\033[0;{0}m\033[0;m".format(self.codes[-2],
															self.codes[1])

		self.assertEqual(result, expected)

	def test_stringifies_always_correctly(self):

		result = self.parser.beautify("<always>")

		expected = "\033[{0}malways\033[0;m".format(self.always_code)

		self.assertEqual(result, expected)

	def test_stringify_combines_always_with_argument_phrase_correctly(self):

		result = self.parser.beautify("<(0)always>")

		combined = flags.codify(self.always["always"] | self.positional[0])

		expected = "\033[{0}malways\033[0;m".format(combined)

		self.assertEqual(result, expected)


	def test_stringify_overrides_argument_phrase_style_correctly(self):

		result = self.parser.beautify("<(0!)always>")

		expected = "\033[{0}malways\033[0;m".format(self.codes[0])

		self.assertEqual(result, expected)

	def test_stringify_overrides_simple_phrase_style_correctly(self):

		# ! overrides the 'always'-style but does not increment the counter
		result = self.parser.beautify("<(!)always> <next>")

		expected = "\033[{0}malways\033[0;m ".format(self.codes[0])
		expected += "\033[{0}mnext\033[0;m".format(self.codes[0])

		self.assertEqual(result, expected)

	def test_stringify_increments_simple_phrase_correctly(self):

		result = self.parser.beautify("<(+)always> <next>")

		combined = flags.codify(self.always["always"] | self.positional[0])

		expected = "\033[{0}malways\033[0;m ".format(combined)
		expected += "\033[{0}mnext\033[0;m".format(self.codes[1])

		self.assertEqual(result, expected)

	def test_stringify_increments_and_overrides_simple_phrase_correctly(self):

		result = self.parser.beautify("<(!+)always> <next>")

		expected = "\033[{0}malways\033[0;m ".format(self.codes[0])
		expected += "\033[{0}mnext\033[0;m".format(self.codes[1])

		self.assertEqual(result, expected)

def main():
	unittest2.main()

if __name__ == "__main__":
	main()