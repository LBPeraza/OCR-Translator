# BoxHandling.py
# Lukas Peraza
# lbp
# Section A
# 15-112 Fall 2013

import cv2
import numpy as np

class Box(object):
	def __init__(self, rect):
		(x, y), (w, h), angle = rect
		(self.x, self.y, self.w, self.h, self.angle) = (
			x, y, w, h, angle)
		self.contour = np.int0(cv2.cv.BoxPoints(rect))
		self.area = cv2.contourArea(self.contour)

	def __eq__(self, other):
		x1, y1, w1, h1, angle1 = self.x, self.y, self.w, self.h, self.angle
		o = other
		x2, y2, w2, h2, angle2 = o.x, o,y, o.w, o.h, o.angle
		distance = ((x1-x2)**2 + (y1-y2)**2)**0.5
		areaOffset = 1.0 * (self.area / o.area) - 1.0
		angleDifference = angle1 - angle2
		return (distance < 20 and
				abs(areaDifference) < 0.2 and
				abs(angleDifference) < 20)

	def rotatedBounds(self):
		(left, right) = (self.x - self.w/2, self.x + self.w/2)
		(top, bottom) = (self.y - self.h/2, self.y + self.h/2)
		(left, top) = (max(0, left), max(0, top))
		return (int(left), int(top), int(right), int(bottom))

	def imgPart(self, img):
		# The part of img which is contained in the box
		M = cv2.getRotationMatrix2D((self.x, self.y), self.angle, 1)
		(rows, cols, ch) = img.shape
		rotatedImg = cv2.warpAffine(img, M, (cols, rows))
		(left, top, right, bottom) = self.rotatedBounds()
		return rotatedImg[top:bottom+1, left:right+1]

	def avgColor(self, img):
		part = self.imgPart(img)
		mean = cv2.mean(part)
		return mean

	def replaceText(self, img, text, rotation):
		# first, eliminates text that is in img contained by the box
		color = self.avgColor(img)
		M = cv2.getRotationMatrix2D((self.x, self.y), self.angle, 1)
		(rows, cols, ch) = img.shape
		rotatedImg = np.zeros(img.shape, dtype=np.uint8)
		(left, top, right, bottom) = self.rotatedBounds()
		cv2.rectangle(rotatedImg, (left, top), (right-5, bottom-5), color, -1)
		# adds the text we want to display
		rotatedImg = addText(rotatedImg, self.rotatedBounds(), text, (10, 10, 10), rotation)
		M2 = cv2.getRotationMatrix2D((self.x, self.y), -self.angle, 1)
		unrotatedImg = cv2.warpAffine(rotatedImg, M2, (cols, rows))
		newImg = np.zeros(img.shape, dtype=np.uint8)
		# replaces the box on the image with the updated box
		isntBlack = cv2.compare(unrotatedImg, newImg, cv2.CMP_NE) / 255
		#isBlack = cv2.compare(unrotatedImg, newImg, cv2.CMP_EQ) / 255
		newImg += img
		newImg -= img*isntBlack
		newImg += unrotatedImg*isntBlack
		return newImg

def shrink(bounds, amount):
	# shrinks bounds by amount on each side
	(left, top, right, bottom) = bounds
	return (left+amount, top+amount, right-amount, bottom-amount)

def addText(img, bounds, text, color, rotation):
	# adds text to img
	(l, t, r, b) = bounds
	ext = img[t:b, l:r]
	for x in xrange((rotation + 1) % 4):
		ext = rotate90(ext)
	(w, h, ch) = ext.shape
	extBounds = (0, 0, w, h)
	lines = text.split('\n')
	lengths = [len(line) for line in lines]
	longest = lengths.index(max(lengths))
	longLine = lines[longest]
	font = cv2.FONT_HERSHEY_SIMPLEX
	textSize = findTextSize(w, longLine, font)
	origins = []
	for li in xrange(len(lines)):
		line = lines[li]
		origin = findOrigin(extBounds, line, li, len(lines), textSize, font)
		cv2.putText(ext, line, origin, font, textSize, color, 2)
	for x in xrange(3 - rotation):
		ext = rotate90(ext)
	img[t:b, l:r] = ext
	return img

def rotate90(img):
	(height, width, c) = img.shape
	larger = max(height, width)
	big = np.zeros((larger, larger, c), dtype=np.uint8)
	big[:height,:width] = img
	pts1 = np.float32([[0, 0], [width, 0], [0, height]])
	pts2 = np.float32([[height, 0], [height, width], [0,0]])
	M = cv2.getAffineTransform(pts1, pts2)
	dst = cv2.warpAffine(big, M, (larger, larger))[:width,:height]
	return dst

def boxFromContour(contour):
	return Box(cv2.minAreaRect(contour))

def findTextSize(width, text, font):
	lines = text.split('\n')
	textSize = 0.1
	size, b = cv2.getTextSize(text, font, textSize, 2)
	while (size[0] < width):
		textSize += 0.01
		size, b = cv2.getTextSize(text, font, textSize, 2)
	return textSize

def findOrigin(bounds, text, line, numLines, textSize, font):
	size, b = cv2.getTextSize(text, font, textSize, 2)
	(w, h) = size
	cx = (bounds[0] + bounds[2]) / 2
	cy = (bounds[1] + bounds[3]) / 2
	allTextHeight = numLines * h * 1.5
	top = cy - allTextHeight/2
	oy = top + (line) * h*1.5
	ox = cx - w/2
	return (int(ox), int(oy))

def invert(color):
	inverted = []
	for channel in color:
		inverted.append(255 - channel)
	return tuple(inverted)

def run():
	cam = cv2.VideoCapture(0)
	rect = (300, 300), (100, 70), 24
	while True:
		ret, img = cam.read()
		box = Box(rect)
		box.replaceText(img, "text")
		#cv2.putText(img, "Long text with\nnew lines and such", (0, 200), cv2.FONT_HERSHEY_SIMPLEX,
		#	2, (255, 255, 255), 1)
		addText(img, (0, 0, 640, 480), "Long text which\nshould be split!", (255, 255, 255))
		cv2.imshow("img", img)
		if (cv2.waitKey(5) & 0xFF == 27):
			break