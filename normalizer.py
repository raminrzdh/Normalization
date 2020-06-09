import re

from src.utils.text.preprocess_tools.normalizer.normalize_character import CharacterNormalizer
from src.utils.text.preprocess_tools.normalizer.space_normalizer import SpaceNormalizer
from src.settings.paths import NORMALIZER_DATA as PATH

class Normalizer:

	def __init__(self, priority_mapping=None):
		self.character_normalizer = CharacterNormalizer(priority_mapping=priority_mapping)
		self.space_normalizer = SpaceNormalizer()
		self.words_with_repeated_chars = self._load_words(PATH + '/data/repeated_chars_2.txt')

	def _load_words(self, file_address):
		list_of_words = []
		with open(file_address, 'r', encoding='utf-8') as words:
			for line in words:
				list_of_words.append(line[:-1])

		return list_of_words

	def _get_ignorable_intervals(self, word):
		patterns = self.words_with_repeated_chars
		intervals = []
		for pattern in patterns:
			regex = re.compile(pattern)
			if regex.finditer(word):
				for matching in regex.finditer(word):
					intervals.append(matching.span())

		return intervals

	def _remove_repeats(self, word, begin, end, ignorable_intervals):
		def is_in_an_interval(number, intervals):
			for interval in intervals:
				if number >= interval[0] and number < interval[1]:
					return True
			return False

		result = ""
		includes_ignorables = False
		found_final = False
		final_character = 0
		for index in range(0, len(word)):
			if is_in_an_interval(index, ignorable_intervals):
				result += word[index]
				includes_ignorables = True
				continue
			if includes_ignorables and not found_final:
				found_final = True
				final_character = index
			if index < begin + 1:
				result += word[index]
			elif index < end:
				continue
			else:
				result += word[index]

		if includes_ignorables and not found_final:
			final_character = len(word)
		return result, includes_ignorables, final_character

	def remove_repeated_characters(self, expression):
		"""
		:param expression: A string that it's unnecessary repeated characters are to be deleted.
		:return: The input string without unnecessary repeated characters.
		"""
		result = ""
		for word in expression.split(' '):
			if word in self.words_with_repeated_chars:
				if result == '':
					result = result + word
				else:
					result = result + ' ' + word
				continue
			result_word = ""
			to_be_ignored = self._get_ignorable_intervals(word)
			pattern = r'(.)\1{1,}'
			regex = re.compile(pattern)
			matching = regex.search(word)
			while matching:
				new_word, includes_ignorables, final_character = self._remove_repeats(word, matching.span()[0],
				                                                                      matching.span()[1], to_be_ignored)
				if new_word == word:
					if includes_ignorables:
						result_word += word[0:final_character]
						word = word[final_character:]
						to_be_ignored = self._get_ignorable_intervals(word)
						matching = regex.search(word)
					else:
						return new_word
				else:
					if len(self._get_ignorable_intervals(word)) > len(self._get_ignorable_intervals(new_word)):
						result_word += word[matching.span()[0]: matching.span()[1]]
						word = word[matching.span()[1]:]
					else:
						word = new_word

					to_be_ignored = self._get_ignorable_intervals(word)
					matching = regex.search(word)
			result_word += word
			if result == '':
				result += result_word
			else:
				result += ' ' + result_word
		return result

	def normalize(self, text, remove_repeated_chars=True, normalize_spaces=True):
		character_level_normalized = ""
		for character in text:
			character_level_normalized += self.character_normalizer.normalize(character)

		normalized = character_level_normalized
		if normalize_spaces:
			normalized = self.space_normalizer.normalize(normalized)

		if remove_repeated_chars:
			normalized = self.remove_repeated_characters(normalized)
		normalized = ' '.join(normalized.split())

		return normalized


