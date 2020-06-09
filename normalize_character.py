import json
import re
from src.settings.paths import NORMALIZER_DATA as PATH

class CharacterNormalizer:
	def __init__(self, priority_mapping=None):
		"""
		:param priority_mapping: A dictionary mapping characters' unicode(in string format) to their normalized form, which will be prioritized over the default mapping.
		"""
		self.removable_characters = self._load_unicodes(PATH + '/data/removable_characters')
		self.spaceable_characters = self._load_unicodes(PATH + '/data/spaceable_characters')
		self.character_mapping = self._load_mapping()
		self.character_mapping.update([(character, '') for character in self.removable_characters])
		self.character_mapping.update([(character, ' ') for character in self.spaceable_characters])
		if priority_mapping is not None:
			self.priority_mapping = priority_mapping
		else:
			self.priority_mapping = {}

	def normalize(self, character):
		"""
		:param character: Any character
		:return: normalized form of the character. could be space, empty string, or a new character in normal Persian.
		"""
		if str(ord(character)) in self.priority_mapping.keys():
			return self.priority_mapping.get(str(ord(character)))
		return self.character_mapping.get(str(ord(character)), character)

	def _load_unicodes(self, file_address):
		unicodes = []
		with open(file_address, 'r') as unicodes_file:
			for line in unicodes_file:
				unicodes.append(line[:-1])

		return unicodes

	def _load_mapping(self):
		with open(PATH + '/data/persianable_chars.json', 'r') as character_mappings:
			mapping = json.load(character_mappings)

		return mapping
