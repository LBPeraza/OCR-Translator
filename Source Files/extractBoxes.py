# extractBoxes.py
# Lukas Peraza
# lbp
# Section A
# 15-112 Fall 2013

import cv2
import numpy as np
from constants import *

def midThreshold(img, minValue, maxValue, value):
	# anything above minValue and below maxValue becomes value
	# anything outside of min/maxValue maintains its value
	gt = cv2.compare(img, minValue, cv2.CMP_GE)
	lt = cv2.compare(img, maxValue, cv2.CMP_LE)
	between = cv2.bitwise_and(gt, lt)
	newImg = np.zeros(img.shape, dtype=np.uint8)
	newImg += img
	newImg -= img*(between/255)
	newImg += value*(between/255)
	return newImg

cam = cv2.VideoCapture(0)

def posterize(img):
	img = cv2.bilateralFilter(img, 5, 75, 75)
	for level in xrange(THRESHOLD_LEVELS):
		minimum = THRESHOLD_VALUES[level]
		maximum = THRESHOLD_VALUES[level+1]
		average = (minimum + maximum) / 2
		img = midThreshold(img, minimum, maximum, minimum)
	return img

def getBoxes(img):
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	post = posterize(gray)
	contours = []
	for level in THRESHOLD_MIDS:
		contours.extend(getContoursAtLevel(post, level))
	uniqueContours = removeSimilarContours(contours)
	return uniqueContours

def removeSimilarContours(contours):
	uniqueContours = []
	for cont in contours:
		similar = False
		for otherCont in uniqueContours:
			if (areSimilar(cont, otherCont)):
				similar = True
				break
		if (not similar):
			uniqueContours.append(cont)
	return uniqueContours

def areSimilar(cont1, cont2):
	(x1, y1), (w1, h1), angle1 = cv2.minAreaRect(cont1)
	(x2, y2), (w2, h2), angle2 = cv2.minAreaRect(cont2)
	(area1, area2) = (w1*h1, w2*h2)
	distance = ((x1-x2)**2 + (y1-y2)**2)**0.5
	areaDifference = area1 / area2 - 1
	angleDifference = angle1 - angle2
	if (distance < MIN_BOX_DISTANCE and
		abs(areaDifference) < 0.2 and
		abs(angleDifference) < 20):
		return True
	else:
		return False

def getContoursAtLevel(post, level):
	r, bin = cv2.threshold(post, level, 255, cv2.THRESH_BINARY)
	contours, h = cv2.findContours(bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	contours = boxContours(contours, post)
	return contours

def boxContours(contours, img):
	(rows, cols) = img.shape
	imgArea = rows*cols
	boxes = []
	for contour in contours:
		approx = cv2.approxPolyDP(contour, 0.1*cv2.arcLength(contour, True), True)
		cntArea = cv2.contourArea(approx)
		if (1000 < cntArea < 0.8*imgArea):
			rect = cv2.minAreaRect(contour)
			box = np.int0(cv2.cv.BoxPoints(rect))
			boxArea = cv2.contourArea(box)
			percent = boxArea / cntArea
			if (abs(percent - 1) < 0.1):
				boxes.append(box)
	return boxes