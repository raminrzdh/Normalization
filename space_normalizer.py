import re
from src.settings.paths import NORMALIZER_DATA as PATH

connecting_characters = r'[ارزژدذو]'
non_connecting_characters = r'[بپتثجچحخسشصضطظعغفقکگلمنهی]'
suffixes = r'تری|ها|تر|ترین|هایم|هایش|هایت|هایمان|هایتان|های'
ha_suffixes = r'یمان|یشان|یتان|یم|یت|یش|ی'
verb_suffixes = r'ام|ای|است|ایم|اید|اند'
pronouns = r'ام|اش|ات'
verb_prefixes = r'(می|نمی|درمی|برمی)'
end_of_word = r'([.!؟:،؛«" ‌]|$)'
persian_characters = r'[آبپتثجچحخسشصضطظعغفقکگلمنهیارزژدذو]'
persian_words = r'[آبپتثجچحخسشصضطظعغفقکگلمنهیارزژدذو]+'


class SpaceNormalizer():

	def __init__(self):
		self.__add_patterns()
		self.__load_exceptions()

	def __load_exceptions(self):
		self.mi_exceptions = []
		self.ha_exceptions = []
		self.tar_exceptions = []

		with open(PATH + '/data/nonplurals.txt', 'r', encoding='utf-8') as nonplurals:
			for line in nonplurals:
				word = line[:-1]
				if word not in self.ha_exceptions:
					self.ha_exceptions.append(word)

		with open(PATH + '/data/noncomps.txt', 'r', encoding='utf-8') as noncomps:
			for line in noncomps:
				word = line[:-1]
				if word not in self.tar_exceptions:
					self.tar_exceptions.append(word)

		with open(PATH + '/data/nonverbs.txt', 'r', encoding='utf-8') as nonverbs:
			for line in nonverbs:
				word = line[:-1]
				if word not in self.mi_exceptions:
					self.mi_exceptions.append(word)

	def __add_patterns(self):

		self.patterns_and_replacements = []
		self.patterns_and_replacements.append((r'[ ]([.؟،!؛:])', r'\1'))
		self.patterns_and_replacements.append(( r'([«\[\(\{])' + r' ' , r'\1'))
		self.patterns_and_replacements.append((r' ' + r'([\»\]\)\}])', r'\1'))
		self.patterns_and_replacements.append((r'([.؛!،؟:])([آبپتثجچحخسشصضطظعغفقکگلمنهیارزژدذو])', r'\1 \2')) # put space between punctuations and words
		self.patterns_and_replacements.append(
			(r'(^| )' + verb_prefixes + r'( )', r'\1\2‌'))  # یک نیمفاصله بعد از ۲\ قایم شده.
		self.patterns_and_replacements.append(
			(r'(' + non_connecting_characters + r')( )(' + suffixes + r')' + end_of_word,
			 r'\1‌\3\4'))  # یک نیم فاصله اون وسط قایم شده
		self.patterns_and_replacements.append(
			(r'(' + connecting_characters + r')( )(' + suffixes + ')' + end_of_word, r'\1\3\4'))
		self.patterns_and_replacements.append(
			(r'(ه)( )(' + pronouns + '|' + verb_suffixes + '|' + 'ی)' + end_of_word, r'\1‌\3\4'))


	def normalize(self, text):

		text = re.sub(r'[ ]+', r' ', text)

		for pattern in self.patterns_and_replacements:
			while(re.findall(pattern[0], text)):
				text = re.sub(pattern[0], pattern[1], text)

		connected_ha = r'(^| )((' + persian_words + non_connecting_characters + r')' + r'(ها))(' + end_of_word  +'|(' + ha_suffixes +'))'
		for match in re.findall(connected_ha, text):
			full_word = match[1]
			if full_word not in self.ha_exceptions:
				without_ha = match[2]
				if len(match) > 3:
					text = text.replace(full_word + match[4], without_ha + '‌' + 'ها' + match[4])
				else:
					text = text.replace(full_word, without_ha + '‌' + 'ها')

		connected_mi = r'(^| )' + r'((برمی|می|نمی|درمی)(' + persian_words + r'))(' + end_of_word + ')'
		for match in re.findall(connected_mi, text):
			full_word = match[1]
			mi = match[2]
			without_mi = match[3]

			if full_word not in self.mi_exceptions:
				text = text.replace(full_word, mi + '‌' + without_mi)

		connected_tar = r'(^| )((' + persian_words + non_connecting_characters + r')' + r'(تر|ترین))(' + end_of_word + ')'
		for match in re.findall(connected_tar, text):
			full_word = match[1]
			if full_word not in self.tar_exceptions:
				without_tar = match[2]
				tar = match[3]
				text = text.replace(full_word, without_tar + '‌' + tar)

		text = re.sub(r'[ ]+', r' ', text)
		return text


