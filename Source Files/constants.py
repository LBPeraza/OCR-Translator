# constants.py
# For OCR Translator
# Lukas Peraza
# lbp
# Section A
# 15-112 Fall 2013

###################################
# OCR
###################################

IMGS_PER_CHAR = 6

X_MARGIN = 15
Y_MARGIN = 15

MAX_HOVER_X_DIST = 5
MAX_HOVER_Y_DIST = 10
WORD_SEPARATION = 3.0

###################################
# Box extraction
###################################

MIN_BOX_DISTANCE = 40

THRESHOLD_LEVELS = 3
THRESHOLD_VALUES = [0]
THRESHOLD_MIDS = []
valuePerLevel = 255.0 / THRESHOLD_LEVELS
for level in xrange(1, THRESHOLD_LEVELS + 1):
	value = int(level * valuePerLevel)
	THRESHOLD_VALUES.append(value)
	THRESHOLD_MIDS.append(int(value - valuePerLevel / 2))

###################################
# Options menu
###################################

import copy

INITIAL_ALPHA = 1.0
ALPHA_RANGE = (0.5, 3.0)
INIT_ALPHA_PERCENT = 0.2
INITIAL_BETA = 0
BETA_RANGE = (-100, 100)
INIT_BETA_PERCENT = 0.5

OPTIONS_WIDTH = 450
OPTIONS_HEIGHT = 300

LANGUAGES_TO = {'English':'en', 'Spanish':'sp', 'French':'fr',
			 'German':'de', 'Italian':'it'}
LANGUAGES_FROM = copy.copy(LANGUAGES_TO)
LANGUAGES_FROM['Auto'] = None
INIT_FROM = 'Auto'
INIT_TO = "English"

CHARACTER_WIDTH = 10
CHARACTER_HEIGHT = 20

TITLE_COLOR = 'black'
TITLE_FONT = 'Arial 9'

DROPDOWN_COLOR = 'white'
DROPDOWN_FONT = 'Arial 10'
DROPDOWN_FONTCOLOR = 'black'
DROPDOWN_BUTTONCOLOR = '#8feceb'
DROPDOWN_BUTTONHOVER = '#3cb8ec'
DROPDOWN_SELECTCOLOR = '#446cff'
SLIDER_LINECOLOR = '#333333'
SLIDER_WIDTH = 2
SLIDER_RADIUS = 7
SLIDER_COLOR = 'blue'

RESET_COLOR = 'green'
RESET_WIDTH = 40
RESET_HEIGHT = CHARACTER_HEIGHT

###################################
# Help text
###################################

OPTIONS = "Press 'O' for options menu"
HIT_SPACE_TEXT = "Press [space] to translate"
CONTINUE_TEXT = "Press [space] to reset"
EXIT_TEXT = "Press [Esc] to quit"