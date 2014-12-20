# OCR.py
# Lukas Peraza
# lbp
# Section A
# 15-112 Fall 2013


# Optical Character Recognition
# use OCRApp().readText to read the text on an image

import cv2
import numpy as np
from compareImg import bwCompare
import time
import string
from constants import *
import os
import copy

class OCRApp(object):

	def readLetter(self, img, letterBox, avgHeight):
		ret, img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
		(top, left, bottom, right) = letterBox
		letterImg = img[top:bottom, left:right]
		letter = None
		maxSim = 0.5
		pathSpec = 'Letter Images/%s/%s/%d.bmp'
		# We're really just comparing the letter to a database of
		# known letters - it's that easy
		for char in string.ascii_letters:
			case = "Capital" if char.isupper() else "Lowercase"
			for imNum in xrange(1, IMGS_PER_CHAR + 1):
				srcPath = pathSpec % (case, char, imNum)
				if os.path.exists(srcPath):
					src = cv2.imread(srcPath)
					sim, a, b, c = bwCompare(letterImg, src)
					if (sim > maxSim):
						# if it's more similar than the previously
						# most similar character, replace it
						maxSim = sim
						letter = char
		if (letter != None and height(letterBox) < 0.9*avgHeight):
			# some letters look the same capital and lower case
			# so the shorter letters are just going to be set
			# to lower case
			letter = letter.lower()
		return letter, maxSim

	def getLetters(self, img):
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		(rows, cols) = img.shape
		img = img[Y_MARGIN:rows-Y_MARGIN, X_MARGIN:cols-X_MARGIN]
		allRegions = cv2.adaptiveThreshold(img, 255,
										   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
										   cv2.THRESH_BINARY, 11, 2)
		regionLabels = np.zeros(allRegions.shape, dtype=int)
		(height, width) = allRegions.shape
		imgArea = height*width
		regionNumber = 1
		inRegion = False
		letterBoxes = []
		# we're just floodFilling each letter to find its boundaries
		for row in xrange(height):
			for col in xrange(width):
				if (allRegions[row, col] == 0 and
					regionLabels[row, col] == 0):
					# black, unlabeled pixel
					regionLabels, bounds = self.fillLabels(allRegions,
														   regionLabels,
												   row, col,
												   (row, col, row, col))
					if (self.area(bounds) > 50 and
						bounds[3] - bounds[1] < 0.5*width and
						bounds[2] - bounds[0] < 0.5*height and
						bounds[3] - bounds[1] > 3 and
						bounds[2] - bounds[0] > 3):
						# if it's not too small, we're
						# gonna assume it's a letter
						letterBoxes.append(adjust(bounds, X_MARGIN, Y_MARGIN))
		letterBoxes = removeNestedBoxes(letterBoxes)
		letterBoxes = self.mergeHoverers(letterBoxes)
		letterBoxes = self.sortLetterBoxes(letterBoxes)
		return allRegions, letterBoxes

	def mergeHoverers(self, boxes):
		# the 'hoverers' over i's and j's (the dot things)
		# need to be merged with the main part of the letter
		mergePairs = []
		for b in xrange(1, len(boxes)):
			box1 = boxes[b]
			cx1 = (box1[1] + box1[3]) / 2
			area1 = self.area(box1)
			top = box1[0]
			for b2 in xrange(b):
				box2 = boxes[b2]
				cx2 = (box2[1] + box2[3]) / 2
				area2 = self.area(box2)
				bottom = box2[2]
				if (abs(cx1 - cx2) < MAX_HOVER_X_DIST and
					top - bottom < MAX_HOVER_Y_DIST and
					area2 < area1):
					mergePairs.extend([b, b2])
		mergedBoxes = []
		for b in xrange(len(boxes)):
			if b not in mergePairs:
				mergedBoxes.append(boxes[b])
		for m in xrange(0, len(mergePairs), 2):
			merged = mergeBoxes(boxes[mergePairs[m]], boxes[mergePairs[m+1]])
			mergedBoxes.append(merged)
		return mergedBoxes

	def getWords(self, line):
		# split a line into multiple words
		avgSeparation = 0.0
		for l in xrange(1, len(line)):
			left = line[l][1]  # left of current letter
			right = line[l-1][3] # right of previous letter
			sep = left - right  # distance between letters
			avgSeparation += sep
		avgSeparation /= (len(line) + 1)
		words = []
		currentWord = [line[0]]
		for l in xrange(1, len(line)):
			left = line[l][1]
			right = line[l-1][3]
			sep = left - right
			if (sep > WORD_SEPARATION*avgSeparation):
				words.append(copy.deepcopy(currentWord))
				currentWord = []
			currentWord.append(line[l])
		words.append(currentWord)
		return words

	def splitLines(self, letters):
		# split a set of letters into lines
		currentLine = [letters[0]]
		lines = []
		for l in xrange(1, len(letters)):
			letter = letters[l]
			previousLetter = letters[l-1]
			if (letter[1] < previousLetter[1]):
				# letter is to the left of previousLetter
				lines.append(copy.deepcopy(currentLine))
				currentLine = []
			currentLine.append(letter)
		lines.append(copy.deepcopy(currentLine))
		return lines

	def area(self, bounds):
		(top, left, bottom, right) = bounds
		w = right - left
		h = bottom - top
		return abs(w*h)

	def sortLetterBoxes(self, boxes):
		sortedBoxes = sorted(boxes, boxCmp)
		return sortedBoxes

	def getLetterContours(self, img):
		r, boxes = self.getLetters(img)
		contours = []
		for box in boxes:
			contours.append(self.getContour(box))
		return contours

	def getContour(self, box):
		(top, left, bottom, right) = box
		contour = np.zeros((4, 2), dtype=int)
		contour[0] = np.array([left, top])
		contour[1] = np.array([right, top])
		contour[2] = np.array([right, bottom])
		contour[3] = np.array([left, bottom])
		return contour

	def fillLabels(self, src, dest, srow, scol, bounds):
		# modified form of floodFill from class
		(rows, cols) = src.shape
		if (srow < 0 or scol < 0 or
			srow >= rows or scol >= cols):
			return dest, bounds
		if (dest[srow, scol] == 0 and
			src[srow, scol] == 0):
			dest[srow, scol] = 1
			dest, bounds = self.fillLabels(src, dest, srow-1, scol, bounds)
			dest, bounds = self.fillLabels(src, dest, srow, scol+1, bounds)
			dest, bounds = self.fillLabels(src, dest, srow+1, scol, bounds)
			dest, bounds = self.fillLabels(src, dest, srow, scol-1, bounds)
		(top, left, bottom, right) = bounds
		(top, bottom) = (min(srow, top), max(srow, bottom))
		(left, right) = (min(scol, left), max(scol, right))
		return dest, [top, left, bottom, right]

	def avgHeight(self, letters):
		# somewhat deceptive name:
		# returns the average height if there is a large height range
		# otherwise returns None
		# if None, letters are all similar size, so we assume
		# they are all capital
		avgHeight = 0.0
		maxHeight = None
		minHeight = None
		for letter in letters:
			letterHeight = height(letter)
			if (maxHeight == None or letterHeight > maxHeight):
				maxHeight = letterHeight
			if (minHeight == None or letterHeight < minHeight):
				minHeight = letterHeight
			avgHeight += height(letter)
		avgHeight /= len(letters)
		heightRange = maxHeight - minHeight
		return avgHeight if heightRange > 10 else None

	def readText(self, img):
		# reads the text in 4 orientations, and
		# returns the 
		img = cv2.bilateralFilter(img, 5, 75, 75)
		maxSim = None
		goodRotation = None
		finalText = None
		for x in xrange(4):
			img = rotate90(img)
			read = self.readTextRotation(img)
			if (read == None): continue
			text, allSim = self.readTextRotation(img)
			if allSim > maxSim:
				finalText = text.strip(' ')
				maxSim = allSim
				goodRotation = x
		return finalText, goodRotation

	def readTextRotation(self, img):
		# reads a single orientation of the text
		r, letters = self.getLetters(img)
		if (len (letters) == 0): return None
		lines = self.splitLines(letters)
		letterHeight = self.avgHeight(letters)
		letters = 0
		allSim = 0
		text = ""
		for line in lines:
			words = self.getWords(line)
			for word in words:
				for letter in word:
					l, sim = self.readLetter(img, letter, letterHeight)
					text += l if (l!=None) else ""
					allSim += sim
					letters += 1
				text += " "
			text = text.strip(" ") + "  "
		allSim /= letters
		return text, allSim

def rotate90(img):
	# rotates img 90 degrees
	# maintains all image data
	(height, width, c) = img.shape
	larger = max(height, width)
	big = np.zeros((larger, larger, c), dtype=np.uint8)
	big[:height,:width] = img
	pts1 = np.float32([[0, 0], [width, 0], [0, height]])
	pts2 = np.float32([[height, 0], [height, width], [0,0]])
	M = cv2.getAffineTransform(pts1, pts2)
	dst = cv2.warpAffine(big, M, (larger, larger))[:width,:height]
	return dst

def adjust(bounds, xMargin, yMargin):
	(top, left, bottom, right) = bounds
	(left, right) = (left + xMargin, right + xMargin)
	(top, bottom) = (top + yMargin, bottom + yMargin)
	return (top, left, bottom, right)

def mergeBoxes(box1, box2):
	# combine 2 boxes into 1
	(t1, l1, b1, r1) = box1
	(t2, l2, b2, r2) = box2
	(top, left) = (min(t1, t2), min(l1, l2))
	(bottom, right) = (max(b1, b2), max(r1, r2))
	return (top, left, bottom, right)

def removeNestedBoxes(boxes):
	# removes any nested boxes from a list of sorted boxes
	#return boxes
	noNested = []
	merged = set()
	for b0 in xrange(len(boxes)):
		if (b0 not in merged):
			box0 = boxes[b0]
			for b1 in xrange(b0, len(boxes)):
				if (b1 not in merged):
					box1 = boxes[b1]
					if (intersect(box0, box1)):
						box0 = mergeBoxes(box0, box1)
						merged.add(b1)
			noNested.append(box0)
	return noNested

def intersect(box0, box1):
	(t0, l0, b0, r0) = box0
	(t1, l1, b1, r1) = box1
	top = (t0 < t1 < b0)
	bottom = (t0 < b1 < b0)
	left = (l0 < l1 < r0)
	right = (l0 < r1 < r0)
	return ((left and (top or bottom)) or 
		    (right and (top or bottom)))

def boxCmp(box1, box2):
	# compare 2 boxes to sort them in order
	(t1, l1, b1, r1) = box1
	(t2, l2, b2, r2) = box2
	# sort first by y position, then by x position
	if (t1 >= b2):
		# 1 lower than 2
		return 1
	elif (t2 >= b1):
		# 2 lower than 1
		return -1
	elif (l2 >= l1):
		# 2 to the right of 1
		return -1
	elif (l1 >= l2):
		# 1 to the right of 2
		return 1
	else:
		# shouldn't happen
		return 0

def height(letter):
	bottom = letter[2]
	top = letter[0]
	return bottom - top

def contourBounds(contour):
	xPoints = [point[0] for point in contour]
	yPoints = [point[1] for point in contour]
	(left, top) = (min(xPoints), min(yPoints))
	(right, bottom) = (max(xPoints), max(yPoints))
	return (top, left, bottom, right)