# -*- coding: utf-8 -*-

"""
The heart of the ecstasy package, containing the main *Parser* class.
"""

import re
import warnings
import collections

import ecstasy.flags as flags
import ecstasy.errors as errors

def beautify(string, *args, **kwargs):
	"""
		Convenient interface to the ecstasy package.

		Arguments:
			string (str): The string to beautify with ecstasy.
			args (list): The positional arguments.
			kwargs (dict): The keyword ('always') arguments.
	"""

	parser = Parser(args, kwargs)
	return parser.beautify(string)

class Phrase(object):
	"""
	Class describing a single parsed phrase.

	When a string is parsed in ecastasy, specially-marked regions of
	text are converted taken note of and converted into Phrase objects,
	which are later then used to replace the parsed strings (including any
	tags or arguments) with the string itself as well as the formatting
	codes specified by the arguments passed to Parser.beautify(), which
	are then interpreted by the command line.

	Attributes:
		string (str): The text of the phrase (between opening and closing tags).
		opening (int): The index of the opening tag.
		closing (int): The index of the closing tag.
		style (int): The formatting/style flag-combination of the phrase.
		nested (list): A list of nested Phrase objects (children).
		override (bool): The phrase's override specification.
	"""

	def __init__(self,
				 opening=None,
				 closing=None,
				 string="",
				 style=0,
				 args=None,
				 nested=None,
				 override=False,
				 increment=False):

		self.string = string

		self.opening = opening
		self.closing = closing

		self.style = style

		self.arguments = args if args else []

		self.nested = nested if nested else []

		self.override = override

		self.increment = increment

	def __str__(self):
		return self.string

	def __eq__(self, other):
		return (self.string == other.string			and
				self.opening == other.opening 		and
				self.closing == other.closing 		and
				self.style == other.style 			and
				self.arguments == other.arguments 	and
				self.nested == other.nested			and
				self.override == other.override		and
				self.increment == other.increment)

class Parser(object):
	"""
	Handles parsing and beautification of a string.

	This is the main class of the entire ecastasy package. It is
	initialized with a set of positional and keyword arguments that
	determine which styles (flag-combinations) are used for which
	phrases (tag-marked regions of text) found during parsing. Its
	beautify() method is then used to beautify a string according
	to the arguments passed to the constructor.

	Note:
		From the outside, the package-level beautify() method should
		handle the construction and beautify()-call process all-in-one
		(for convenience).

	Attributes:
		always: The list of 'always' (keyword) arguments.
		positional: The list of positional arguments.
		tags: A compiled regex matching opening or closing tags.
		argument: A compiled regex matching well-formed phrase arguments.
		counter: A counter for positional arguments.
	"""

	def __init__(self, args, kwargs):

		"""
		Initializes a Parser instance.

		Arguments:
			args (list): The positional arguments.
			kwargs (dict): The 'always' (keyword) arguments.
		"""

		self.always = kwargs

		self.positional = self.get_flags(args) if args else []

		self.meta = re.compile(r"[()<>]")

		self.arguments = re.compile(r"^(-?\d,?)+!?$|"
			 		 			    r"^!?(-?\d,?)+$|"
			 					    r"^(!\+?|\+!?)$")

		# Used in self.stringify to auto-increment
		# positional argument positions
		self.counter = 0

	def get_flags(self, args):

		"""
		Checks and retrieves positional and 'always' (keyword) flags
		from the many ways in which they may be passed to the
		constructor (or the beautify() method on package-level).

		Positional arguments can be passed either:

		* Individually, where each flag-combination is one positional argument.
		* Packaged inside a list, which is then expanded. There can be
		  multiple of such lists passed as arguments because it facilitates
		  interaction with the ecastasy module (one may want to organize
		  and update styles in certain ways depending on one's program), but
		  each list will be expanded and all flag-combinations found inside
		  each list will be interpreted as a single style argument, as if it
		  had been passed in the way desribed above (individually).

		'Always' arguments can be passed either:

		* Individually, with keyword-argument syntax, i.e. <word>=<style>
		* In a dictionary, which is expanded exactly like positional
		  arguments passed in lists (i.e. each key/value pair in the
		  dictionary is interpreted as if it had been passed individually,
		  as key=value to the constructor/the external beautify() method).

		Note:
			self.always is set equal to the keyword arguments passed to the
			constructor and then modified directly (when 'always'-arguments
			are found), while the positional arguments are put into a list
			here and returned (i.e. no interaction with self.positional).

		Arguments:
			args (list): The positional arguments passed to the constructor.

		Returns:
			The positional arguments.

		Raises:
			errors.FlagError: If an invalid (out-of-range)
							  flag combination was passed.

			errors.EcstasyError: If one of the arguments is of invalid type.

		"""

		positional = []

		for argument in args:
			# A flag is an instance of a subclass of
			# flags.Flags if it was passed alone
			if isinstance(argument, flags.Flags):
				positional.append(argument)

			# or is an integer if it was (bitwise) OR'd
			# with another flag (a "flag combination")
			elif isinstance(argument, int):
				if argument < 0 or argument >= flags.LIMIT:
					raise errors.FlagError("Flag value '{0}' is out of range "
										   "!".format(argument))
				positional.append(argument)

			# Dictionaries store 'always'-arguments
			elif isinstance(argument, dict):
				for key, value in argument.items():
					# Simple 'always'-argument where one string
					# is mapped to one formatting flag-combination
					if isinstance(key, str):
						self.always[key] = value

					# Complex 'always'-argument with a
					# tuple containing strings, each with the same
					# flag-combination (same value)
					elif isinstance(key, tuple):
						for i in key:
							self.always[i] = value
					else:
						raise errors.EcstasyError("Key '{0}' in dictionary "
												  "argument passed is neither "
												  "a string nor a tuple "
												  "of strings!".format(key))

			elif isinstance(argument, collections.Iterable):
				positional += self.get_flags(argument)

			else:
				raise errors.EcstasyError("Argument '{0}' is neither a flag, a "
										  "(bitwise) OR'd flag-combination, a "
										  "dictionary nor an  iterable of "
										  "positional arguments "
										  "!".format(argument))

		return positional

	def beautify(self, string):
		"""
		Wraps together all actions needed to beautify a string, i.e.
		parse the string and then stringify the phrases (replace tags
		with formatting codes).

		Arguments:
			string (str): The string to beautify/parse.

		Returns:
			The parsed, stringified and ultimately beautified string.

		Raises:
			errors.ArgumentError if phrases were found, but not a single style
			(flag combination) was supplied.
		"""

		if not string:
			return string

		# string may differ because of escaped characters
		string, phrases = self.parse(string)

		if not phrases:
			return string

		if not self.positional and not self.always:
			raise errors.ArgumentError("Found phrases, but no styles "
									   "were supplied!")

		return self.stringify(string, phrases)

	def parse(self, string, root=None):

		"""
		Parses a string to handle escaped tags and retrieve phrases.

		This method works recursively to parse nested tags. When escaped
		tags are found, those are removed from the string. Also argument
		sequences are removed from the string. The string returned can
		thus be quite different from the string passed.

		Arguments:
			string (str): The string to parse.
			root (Phrase): If in a recursive call, the root/parent phrase.

		Returns:
			For one, the escaped string (without escape characters and
			phrase arguments). For the other, it depends on the stack-depth.
			If this is the lowest recursion depth/level (i.e. the stack
			call resulting from the first function call in self.beautify()),
			it will return a list of phrases. For higher stack levels (
			i.e. resulting from recursive function calls from with
			self.parse(), for nested phrases), it returns exactly one
			Phrase instance.

		Raises:
			errors.ParseError: If no closing tag could be
							   found for an opening tag.
		"""

		phrases = []

		meta = self.meta.search(string)

		while meta:

			# Save some function calls
			pos = meta.start()

			if meta.group() == "<":
				string, child, meta = self.open_phrase(string, pos)

				if child and root:
					root.nested.append(child)
				elif child:
					phrases.append(child)

				# else it was escaped (+ new meta)
				continue

			elif root:

				if meta.group() == "(":
					meta = self.meta.search(string, pos + 1)
					if meta.group() == ")":
						string, root, meta = self.handle_arguments(string,
																   root,
																   pos,
																   meta.start())
						continue

				elif meta.group() == ">":
					string, phrase, meta = self.close_phrase(string,
															 root,
															 pos)
					if phrase:
						return string, phrase

					# else was escaped (+ new meta)
					continue

			string, meta = self.escape_meta(string, pos)

		if not root:
			return string, phrases

		# If this is not the first stack-depth the function should
		# have returned upon finding a closing tag,
		# i.e. we should never have gotten here.
		word = re.search(r"([\w\s]+)(?![\d]*>[\w\s]+>)", string)

		what = "No closing tag found for opening tag"

		if word:
			what += " after expression '{0}'".format(word.group())

		raise errors.ParseError(what + "!")

	def escape_meta(self, string, pos):

		"""
		Checks if a meta character is escaped or else warns about it.

		If the meta character has an escape character ('\') preceding it,
		the meta character is escaped. If it does not, a warning is emitted
		that the user should escape it.

		Arguments:
			string (str): The relevant string in which the character was found.
			pos (int): The index of the meta character within the string.

		Returns:
			The possibly escaped string and the next meta match.
		"""

		# Replace escape character
		if pos > 0 and string[pos - 1] == "\\":
			string = string[:pos - 1] + string[pos:]
		else:
			warnings.warn("Un-escaped meta-character: '{0}' (Escape"
						  " it with a '\\')".format(string[pos]),
						  Warning)
			pos += 1

		meta = self.meta.search(string, pos)

		return string, meta


	def open_phrase(self, string, pos):

		"""
		Helper function of self.parse() handling opening tags.

		Arguments:
			string (str): The string being parsed.
			pos (int): The index/position of the opening tag in the string.

		Returns:
			The (possibly) escaped string, a child phrase if the opening tag
			was not escaped and otherwise None, and a new tag match, either
			starting at one index passed the escaped tag or one index passed
			the closing tag of the child.
		"""

		# Check for escaping
		if string[pos - 1] == "\\":
			# Remove the escape character
			string = string[:pos - 1] + string[pos:]

			# When removing the escape character, the
			# pos tag index is pushed one back
			pos -= 1

			# If the escape character was not itself (double)
			# escaped we can look for the next tag
			if pos == 0 or string[pos - 1] != "\\":
				tag = self.meta.search(string, pos + 1)

				return string, None, tag

		child = Phrase(pos)

		escaped, child = self.parse(string[pos + 1:], child)

		string = string[:pos + 1] + escaped

		tag = self.meta.search(string, child.closing + 1)

		return string, child, tag

	def close_phrase(self, string, root, pos):

		"""
		Helper function of self.parse() handling closing tags.

		Arguments:
			string (str): The string being parsed.
			root (Phrase): The current root phrase.
			pos (int): The index/position of the closing tag in the string.

		Returns:
			Always the (possibly) escaped string, then either the fully
			formed phrase if the closing tag was not escaped (with its
			'closing' and 'string' attributes set) and otherwise None,
			and lastly the next tag if the closing tag was indeed escaped
			and otherwise None -- i.e. either the tuple
			(string, phrase, None) or (string, None, tag).
		"""

		# Whatever is between the opening tag and this closing tag
		substring = string[:pos]

		# Escape-character to escape the closing tag (/>)
		if substring.endswith("\\"):

			# Get rid of the escape character either way
			string = string[:pos - 1] + string[pos:]

			# Check if not double-escaped
			if not substring[:-1].endswith("\\"):
				# pos is now one index passed the closing tag
				tag = self.meta.search(string, pos)

				return string, None, tag

			# Double-escape means this is really supposed to be a
			# closing tag and thus we can return the phrase.
			else:
				# The closing position should be in the same scope
				# as the scope of the opening position (scope in
				# the sense of to which phrase the positions are
				# relative to). -1 due to the escaped character but
				# + 1 because index 0 is phrase.opening + 1
				root.closing = root.opening + pos
				root.string = string[:pos - 1]
		else:
			root.closing = root.opening + 1 + pos
			root.string = string[:pos]

		return string, root, None


	def handle_arguments(self, string, root, opening, closing):

		"""
		Handles phrase-arguments.

		Sets the override and increment flags if found. Also makes
		sure that the argument sequence is at the start of the phrase
		and else warns about the unescaped meta characters. If the
		arguments are indeed at the start but do not match the arguments
		regular expression, an error is raised.

		Arguments:
			string (str): The string being parsed.
			root (str): The current root phrase.
			opening (int): The index of the opening paranthese.
			closing (int): The index of the closing paranthese.

		Returns:
			The (possibly escaped) string, the root phrase (if no escaping,
			then with arguments and flags) and the next meta match.

		Raises:
			errors.ParseError: If the arguments are invalid.
		"""

		# The actual argument string (ignore whitespace)
		args = string[opening + 1 : closing].replace(" ", "")

		# The argument sequence must be at the start of the phrase
		# and must match the allowed argument regular expression
		if opening > 0 or not self.arguments.match(args):

			if opening == 0:
				raise errors.ParseError("Invalid argument sequence!")

			# If escape_meta does indeed escape a character and removes
			# a backward slash, the positions 'opening' and 'closing' are no
			# longer valid. escape_meta does a search for the next meta
			# character though, which is then the closing parantheses,
			# so we can use its index value (in the now escaped string)
			string, meta = self.escape_meta(string, opening)
			string, meta = self.escape_meta(string, meta.start())

			return string, root, meta

		if "!" in args:
			root.override = True
			args = args.replace("!", "")

		if "+" in args:
			root.increment = True
			args = args.replace("+", "")

		root.arguments = [int(i) for i in args.split(",") if i]

		# Remove the argument string including parantheses
		string = string[closing + 1:]

		meta = self.meta.search(string)

		return string, root, meta

	def stringify(self, string, phrases, parent=None):

		"""
		Stringifies phrases.

		After parsing of the string via self.parse(), this method takes the
		escaped string and the list of phrases returned by self.parse() and
		replaces the original phrases (with tags) with the Phrase-objects in
		the list and adds the appropriate flag-combinations as determined by
		the string or the position of the phrase (the string if it's in
		self.always, i.e. an 'always' argument). This method also works
		recursively to handle nested phrases (and resetting of parent-phrase
		styles).

		Arguments:
			string (str): The escaped string returned by self.parse().
			phrases (list): The list of Phrase-objects returned by self.parse().
			parent (Phrase): For recursive calls, the current parent Phrase.

		Returns:
			The finished, beautifully beautified string.

		Raises:
			errors.ArgumentError: If more positional arguments are requested
								  than were supplied.
		"""

		last_tag = 0

		beauty = ""

		for phrase in phrases:

			beauty += string[last_tag : phrase.opening]

			if phrase.string in self.always and not phrase.override:
				phrase.style = self.always[phrase.string]

			if phrase.arguments:
				combination = 0
				for i in phrase.arguments:
					try:
						combination |= self.positional[i]
					except IndexError:
						raise errors.ArgumentError("Positional argument '{0}' "
							 					   "is out of range"
							 					   "!".format(i))

				phrase.style |= combination

			elif (phrase.string not in self.always or
				  phrase.increment or phrase.override):
				try:
					combination = self.positional[self.counter]

					if phrase.increment or not phrase.override:
						self.counter += 1
				except IndexError:
					self.raise_not_enough_arguments(phrase.string)

				phrase.style |= combination

			phrase.style = flags.codify(phrase.style)

			if phrase.nested:
				phrase.string = self.stringify(phrase.string,
											   phrase.nested,
											   phrase)

			# After a nested phrase is over, we reset the style to the
			# parent style, this gives the notion of nested styles.
			reset = parent.style if parent else ""

			# \033[ signifies the start of a command-line escape-sequence
			beauty += "\033[{0}m{1}\033[0;{2}m".format(phrase.style,
													   phrase,
													   reset)
			last_tag = phrase.closing + 1

		beauty += string[last_tag:]

		return beauty

	def raise_not_enough_arguments(self, string):

		"""
		Raises an errors.ArgumentError if not enough arguments were supplied.

		Takes care of formatting for detailed error messages.

		Arguments:
			string (str): The string of the phrase for which there weren't enough
						  arguments.

		Raises:
			errors.ArgumentError with a detailed error message.
		"""

		requested = errors.number(self.counter + 1)

		number = len(self.positional)

		verb = "was" if number == 1 else "were"

		what = "Requested {} formatting argument for "\
			   "'{}' but only {} {} supplied!"

		what = what.format(requested, string, number, verb)

		raise errors.ArgumentError(what)
