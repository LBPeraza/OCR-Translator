# OCRTranslator.py
# Lukas Peraza
# lbp
# Section A
# 15-112 Fall 2013

from AsciiTranslator import AsciiTranslator as translator
from OCROptions import OptionsMenu
from BoxHandling import boxFromContour
from extractBoxes import getBoxes
from OCR import OCRApp
import cv2
import numpy as np
from constants import *
import copy
from Tkinter import *
import tkSimpleDialog

def initOptions():
	opts = OptionsMenu()
	alpha = INITIAL_ALPHA
	beta = INITIAL_BETA
	opts.addBox(20, 20, 200, 280, 3)
	opts.addDropdown("Translate from:", LANGUAGES_FROM, 50, 75, INIT_FROM)
	opts.addDropdown("Translate to:", LANGUAGES_TO, 50, 150, INIT_TO)
	opts.addSlider("Contrast", 250, 50, 200, INIT_ALPHA_PERCENT, ALPHA_RANGE)
	opts.addSlider("Brightness", 350, 50, 200, INIT_BETA_PERCENT, BETA_RANGE)
	options = [alpha, beta, INIT_FROM, INIT_TO]
	return opts, options

def runOCRTranslator():
	tr = translator()
	ocr = OCRApp()
	cam = cv2.VideoCapture(0)
	opts, options = initOptions()
	doNextThing('webcam', opts, cam, options, ocr, tr)

def doNextThing(next, opts, cam, options, ocr, tr):
	if (next == 'options'):
		options = runOptions(opts)
		doNextThing('webcam', opts, cam, options, ocr, tr)
	elif (next == 'webcam'):
		next = runWebcam(cam, options, ocr, tr)
		doNextThing(next, opts, cam, options, ocr, tr)
	else:
		cv2.destroyAllWindows()
		return None

def runOptions(menu):
	menu.run()
	alpha = menu.sliders['Contrast'].value
	beta = menu.sliders['Brightness'].value
	langFrom = menu.dropdowns['Translate from:'].value
	langTo = menu.dropdowns['Translate to:'].value
	langFrom = LANGUAGES_FROM[langFrom]
	langTo = LANGUAGES_TO[langTo]
	return [alpha, beta, langFrom, langTo]

def runWebcam(cam, options, ocr, tr):
	r, img = cam.read()
	(alpha, beta, langFrom, langTo) = options
	(rows, cols, ch) = img.shape
	while True:
		r, img = cam.read()
		img = cv2.multiply(img, np.array([alpha], dtype=float))
 		transImg = copy.deepcopy(img)
		boxes = getBoxes(img)
		cv2.drawContours(img, boxes, -1, (0, 0, 255), 2)
		img = addHelpText(img, rows, cols)
		cv2.imshow("OCR Translator", img)
		key = (cv2.waitKey(5) & 0xFF)
		if (chr(key) == 'o' or chr(key) == 'O'):
			return 'options'
		elif (key == 32):
			return doTranslation(transImg, boxes, ocr, tr, langFrom, langTo)
		elif (key == 27):
			return 'exit'

def doTranslation(img, boxes, ocr, tr, langFrom, langTo):
	if (len(boxes) == 0):
		return 'webcam'
	else:
		for textBox in boxes:
			box = boxFromContour(textBox)
			extraction = box.imgPart(img)
			read = ocr.readText(extraction)
			if (read == (None, None)): continue
			text, rotation = read
			title = "Confirm OCR"
			message = """Confirm that the detected text matches \
the text in the image.
Input a new line as two spaces."""
			init = text
			root = Tk()
			root.withdraw()
			fixText = tkSimpleDialog.askstring(title, message,
												initialvalue=init)
			root.destroy()
			if (fixText == None): continue
			translated = tr.translate(fixText, langTo, langFrom)
			img = box.replaceText(img, translated, rotation)
		(rows, cols, ch) = img.shape
		img = addContinueText(img, rows, cols)
		cv2.imshow("OCR Translator", img)
		while True:
			key = cv2.waitKey(10) & 0xFF
			if (key == 32): return 'webcam'
			elif (key == 27): return 'exit'

def addHelpText(img, rows, cols):
	font = cv2.FONT_HERSHEY_SIMPLEX
	cv2.rectangle(img, (0, 0), (cols, 40), (255, 255, 255), -1)
	cv2.putText(img, OPTIONS, (15, 30), font, 1, (0, 0, 0), 2)
	cv2.rectangle(img, (0, rows-40), (cols, rows), (255, 255, 255), -1)
	cv2.putText(img, HIT_SPACE_TEXT, (15, rows-10), font, 1, (0, 0, 0), 2)
	return img

def addContinueText(img, rows, cols):
	font = cv2.FONT_HERSHEY_SIMPLEX
	cv2.rectangle(img, (0, 0), (cols, 40), (255, 255, 255), -1)
	cv2.putText(img, CONTINUE_TEXT, (15, 30), font, 1, (0, 0, 0), 2)
	cv2.rectangle(img, (0, rows-40), (cols, rows), (255, 255, 255), -1)
	cv2.putText(img, EXIT_TEXT, (15, rows-10), font, 1, (0, 0, 0), 2)
	return img

import random
runOCRTranslator()