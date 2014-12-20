# compareImg.py
# Lukas Peraza
# lbp
# Section A
# 15-112 Fall 2013

# For OCR Translator

# Very primitive image comparisons
# only does strict black/white comparisons
# all that we need for OCR

import cv2
import numpy as np

def bwCompare(img, src):
	# compares a strictly black/white image
	# to a strictly black/white source
	# returns a percentage of match
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

	# we want to compare black areas
	# black - off, white - on
	# so it's easier to invert, then invert again at end
	img = invert(img)
	src = invert(src)

	(imgRows, imgCols) = img.shape
	(srcRows, srcCols) = src.shape

	# resize the images
	cmpHeight = min(imgRows, srcRows)
	cmpWidth = min(imgCols, srcCols)

	cmpImg = cv2.resize(img, (cmpWidth, cmpHeight))
	cmpSrc = cv2.resize(src, (cmpWidth, cmpHeight))
	#cmpImg = np.resize(cmpImg, (cmpHeight, cmpWidth))
	#cmpSrc = np.resize(cmpSrc, (cmpHeight, cmpWidth))

	comparison = cv2.bitwise_and(cmpImg, cmpSrc)
	similar1 = cv2.bitwise_xor(invert(comparison), cmpSrc)
	similar2 = cv2.bitwise_xor(invert(comparison), cmpImg)
	similar = (np.mean(similar1) + np.mean(similar2)) / 2
	return similar / 255, cmpImg, cmpSrc, comparison

def invert(img):
	return np.array([255], dtype=np.uint8) - img