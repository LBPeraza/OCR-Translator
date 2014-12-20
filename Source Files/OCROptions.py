# OCROptions.py
# Lukas Peraza
# lbp
# Section A
# 15-112 Fall 2013

# Options menu class
# for OCR Translator

from Tkinter import *
from constants import *
from Animation import Animation

# Extends a slightly modified version of Animation class to display an options menu
# with dropdown menus, sliders, and integer selectors

class OptionsMenu(Animation):
	def __init__(self, width=OPTIONS_WIDTH, height=OPTIONS_HEIGHT):
		self.width = width
		self.height = height
		self.dropdowns = dict()
		self.sliders = dict()
		self.boxes = []

	def addDropdown(self, title, contents, x, y, initialValue):
		self.dropdowns[title] = Dropdown(title, contents, x, y, initialValue)

	def addSlider(self, title, x, y, length, initialPercent, (low, high),
					orientation="vertical"):
		self.sliders[title] = Slider(title, x, y, length, initialPercent,
					(low, high), orientation)

	def addBox(self, left, top, r, b, width):
		self.boxes.append([(left, top, r, b), width])

	def redrawAll(self):
		self.drawBoxes()
		self.drawDropdowns()
		self.drawSliders()

	def drawBoxes(self):
		for box in self.boxes:
			self.canvas.create_rectangle(box[0], width=box[1], outline='blue')

	def drawSliders(self):
		for slider in self.sliders:
			self.sliders[slider].draw(self.canvas)

	def drawDropdowns(self):
		selected = None
		for dropdown in self.dropdowns:
			dd = self.dropdowns[dropdown]
			if dd.selected:
				selected = dd
			else:
				dd.draw(self.canvas)
		if (selected != None): selected.draw(self.canvas)

	def mouseMotion(self, event):
		for dropdown in self.dropdowns:
			dd = self.dropdowns[dropdown]
			if (dd.selected):
				dd.selection = dd.getSelectionAt(event.x, event.y)

	def mousePressed(self, event):
		(x, y) = (event.x, event.y)
		for dropdown in self.dropdowns:
			dd = self.dropdowns[dropdown]
			if dd.intersects(x, y):
				dd.selected = True
			else:
				dd.selected = False
				if (dd.selection != None):
					dd.value = dd.selection
				dd.selection = None
		for slider in self.sliders:
			s = self.sliders[slider]
			if (s.intersects(x, y)):
				s.selected = True
			if (s.resetIntersects(x, y)):
				s.percent = s.initialPercent
				s.value = s.getValue()

	def mouseReleased(self, event):
		for slider in self.sliders:
			self.sliders[slider].selected = False

	def leftMouseMotion(self, event):
		for slider in self.sliders:
			s = self.sliders[slider]
			if s.selected:
				s.percent = s.getPercentAt(event.x, event.y)
				s.value = s.getValue()

	def run(self):
		super(OptionsMenu, self).run("Options", self.width, self.height)

class Dropdown(object):
	# Dropdown menu!
	def __init__(self, title, contents, x, y, initialValue):
		self.title = title
		self.contents = contents
		# contents is a dictionary of (on screen value):(in-app value)
		self.contentList = sorted([key for key in contents])
		self.x = x
		self.y = y
		self.value = initialValue
		longestValue, length = None, None
		for value in contents:
			if len(value) > length:
				longestValue = value
				length = len(value)
		self.textMargin = 10
		self.width = CHARACTER_WIDTH * len(longestValue) + 2 * self.textMargin
		self.height = CHARACTER_HEIGHT
		self.selected = False
		self.selection = None

	def draw(self, canvas):
		self.drawTitle(canvas)
		self.drawSelection(canvas)
		self.drawSelectionButton(canvas)
		if (self.selected):
			self.drawOptions(canvas)

	def drawOptions(self, canvas):
		(x, y0) = (self.x, self.y + self.height+1)
		i = 0
		for option in self.contentList:
			self.drawOption(canvas, option, x, y0 + i*self.height)
			i += 1

	def drawOption(self, canvas, option, x, y):
		if (self.selection == option):
			color = DROPDOWN_SELECTCOLOR
		else:
			color = DROPDOWN_COLOR
		canvas.create_rectangle(x, y, x+self.width, y+self.height,
								fill=color, width=0)
		canvas.create_text(x+self.textMargin, y, anchor='nw', text=option,
						   fill=DROPDOWN_FONTCOLOR, font=DROPDOWN_FONT)

	def drawSelectionButton(self, canvas):
		(x, y) = (self.x+self.width, self.y)
		canvas.create_rectangle(x, y, x+self.height, y+self.height,
				fill=DROPDOWN_BUTTONCOLOR, activefill=DROPDOWN_BUTTONHOVER)

	def drawTitle(self, canvas):
		(x, y) = (self.x, self.y)
		canvas.create_text(x, y, anchor='sw', text=self.title,
						   fill=TITLE_COLOR, font=TITLE_FONT)

	def drawSelection(self, canvas):
		(x, y) = (self.x, self.y)
		canvas.create_rectangle(x, y, x+self.width, y+self.height,
								fill=DROPDOWN_COLOR)
		canvas.create_text(x+self.textMargin, y, anchor='nw', text=self.value,
						   fill=DROPDOWN_FONTCOLOR, font=DROPDOWN_FONT)

	def bounds(self):
		(x0, x1) = (self.x, self.x+self.width+self.height)
		y0 = self.y
		if self.selected:
			y1 = y0 + self.height
		else:
			y1 = y0 + self.height
		return (x0, y0, x1, y1)

	def intersects(self, x, y):
		(x0, y0, x1, y1) = self.bounds()
		if (x0 <= x <= x1 and
			y0 <= y <= y1):
			return True
		else:
			return False

	def getSelectionAt(self, x, y):
		(localX, localY) = (x-self.x, y-self.y-self.height-1)
		if (0 <= localX <= self.width and
			0 <= localY < len(self.contents)*self.height):
			selectionIndex = localY / self.height
			selection = self.contentList[selectionIndex]
		else:
			selection = None
		return selection

	def __repr__(self):
		return self.title

class Slider(object):
	def __init__(self, title, x, y, length, initialPercent, (low, high), orientation="vertical"):
		self.title = title
		self.x = x
		self.y = y
		self.length = length
		self.percent = initialPercent
		self.initialPercent = initialPercent
		self.low = low
		self.high = high
		self.value = self.getValue()
		self.orientation = orientation
		(self.sx, self.sy) = self.getSliderPosition()
		self.selected = False

	def getSliderPosition(self):
		if (self.orientation == "vertical"):
			maxPoint = (self.x, self.y + SLIDER_RADIUS)
			minPoint = (self.x, self.y + self.length + SLIDER_RADIUS)
		elif (self.orientation == "horizontal"):
			maxPoint = (self.x + self.length, self.y + SLIDER_RADIUS)
			minPoint = (self.x, self.y + SLIDER_RADIUS)
		x = (maxPoint[0] - minPoint[0]) * self.percent + minPoint[0]
		y = (maxPoint[1] - minPoint[1]) * self.percent + minPoint[1]
		return (x, y)

	def getPercentAt(self, x, y):
		if (self.orientation == "vertical"):
			maxPos = self.y + SLIDER_RADIUS
			minPos = self.y + self.length + SLIDER_RADIUS
			value = y
		elif (self.orientation == "horizontal"):
			maxPos = self.x + self.length
			minPos = self.x
			value = x
		diff = maxPos - minPos
		percent = float(value - minPos) / diff
		percent = max(0.0, percent)
		percent = min(1.0, percent)
		return percent

	def getValue(self):
		percent = self.percent
		(low, high) = self.low, self.high
		aboveLow = (high - low) * percent
		if (type(low) == int):
			return int(aboveLow + low)
		else:
			return "%0.2f" % (aboveLow + low)

	def intersects(self, x, y):
		(sx, sy) = self.getSliderPosition()
		(dx, dy) = (x - sx, y - sy)
		distance = (dx**2 + dy**2) ** 0.5
		return (distance < SLIDER_RADIUS)

	def resetIntersects(self, x, y):
		left = self.x + 25
		right = left + RESET_WIDTH
		if (self.orientation == 'vertical'):
			top = self.y+self.length+10+SLIDER_RADIUS
		elif(self.orientation == 'horizontal'):
			top  = self.y+10+SLIDER_RADIUS
		bottom = top+CHARACTER_HEIGHT
		return (left < x < right and
				top < y < bottom)

	def draw(self, canvas):
		self.drawTitle(canvas)
		self.drawLine(canvas)
		self.drawSlider(canvas)
		self.drawValue(canvas)
		self.drawReset(canvas)

	def drawTitle(self, canvas):
		(x, y) = (self.x, self.y)
		canvas.create_text(x, y, anchor='s', text=self.title,
						   font=TITLE_FONT, fill=TITLE_COLOR)

	def drawLine(self, canvas):
		point1 = (self.x, self.y + SLIDER_RADIUS)
		if (self.orientation == "vertical"):
			point2 = (self.x, self.y + self.length + SLIDER_RADIUS)
		elif (self.orientation == "horizontal"):
			point2 = (self.x + self.length, self.y + SLIDER_RADIUS)
		canvas.create_line(point1, point2, fill=SLIDER_LINECOLOR, width=SLIDER_WIDTH)

	def drawSlider(self, canvas):
		(x, y) = self.getSliderPosition()
		r = SLIDER_RADIUS
		canvas.create_oval(x-r, y-r, x+r, y+r, fill=SLIDER_COLOR)

	def drawValue(self, canvas):
		x = self.x
		if (self.orientation == "vertical"):
			y = self.y + self.length + 10 + SLIDER_RADIUS
		elif (self.orientation == 'horizontal'):
			y = self.y + 10 + SLIDER_RADIUS
		canvas.create_rectangle(x-20, y, x+20, y+CHARACTER_HEIGHT, fill="white")
		canvas.create_text(x, y, anchor='n', font=TITLE_FONT, fill=TITLE_COLOR,
						   text=self.value)

	def drawReset(self, canvas):
		x = self.x + 25
		if (self.orientation == "vertical"):
			y = self.y + self.length + 10 + SLIDER_RADIUS
		elif (self.orientation == "horizontal"):
			y = self.y + 10 + SLIDER_RADIUS
		canvas.create_rectangle(x, y, x+RESET_WIDTH, y+RESET_HEIGHT,
								fill=RESET_COLOR)
		canvas.create_text(x+RESET_WIDTH/2, y, anchor='n', font=TITLE_FONT,
							fill=TITLE_COLOR, text="reset")

	def __repr__(self):
		return self.title