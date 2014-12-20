# AsciiTranslator.py
# Lukas Peraza
# lbp
# Section A
# 15-112 Fall 2013


# For OCR Translator Term Project

# Translates a string and returns ascii version
# Goslate uses UTF-8, which cannot be displayed by opencv
# using AsciiTranslator().translate() instead of
# Goslate().translate() allows translated text to be displayed


from goslate import Goslate
import unicodedata
import math

class AsciiTranslator(object):
	def __init__(self):
		self.t = Goslate()

	def translate(self, s, lang_to, lang_from=None):
		lineBreaks = s.count('  ')
		s = s.replace('  ', ' ')
		try:
			s = self.t.translate(s, lang_to, lang_from)
		except:
			# usually a socket timeout
			return self.addNewLines(s, lineBreaks)
		# utf-8 encoded string
		s = self.replaceUTFchars(s)
		s = self.addNewLines(s, lineBreaks)
		# now ascii encoded
		return s

	def addNewLines(self, s, lineBreaks):
		if (lineBreaks == 0):
			return s
		else:
			words = s.split(' ')
			numWords = len(words)
			wordsPerLine = int(math.ceil(1.0 * numWords / (lineBreaks + 1)))
			s = ""
			for i in xrange(numWords):
				s += words[i]
				if ((i+1) % wordsPerLine == 0):
					s += '\n'
				else:
					s += ' '
			return s.strip('\n')

	def replaceUTFchars(self, s):
		ascii = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
		# replaces UTF characters with closed ascii representation
		# e.g. characters with accents -> no accents
		return ascii