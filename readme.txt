readme.txt
Lukas Peraza
lbp
Section A
15-112 Fall 2013



OCR Translator
	readme

3rd Party Libraries Required:
	goslate (packaged in project .zip)
	opencv/cv2
	numpy


-INSTALLING OPENCV/NUMPY on WINDOWS
download numpy from
	http://sourceforge.net/projects/numpy/files/NumPy/1.6.1/numpy-1.6.1-win32-superpack-python2.7.exe/download
run the numpy .exe file to install it, leaving everything default
download opencv from
	http://sourceforge.net/projects/opencvlibrary/riles/opencv-win/2.4.1/OpenCV-2.4.1.exe/download
run this .exe file and remember the extraction folder you specified
wait for everything to be extracted
now navigate to the directory you extracted opencv to
navigate to opencv\build\python\x86\2.7\ and copy cv2.pyd
paste this file in the folder
	C:\Python27\Lib\site-packages
open Python IDLE and type
	import cv2
if there is no error message, installation has succeeded


-RUNNING OCRTranslator
open
	Source Files\OCRTranslator.py in your python IDE of choice
	run from the IDE


-USING OCRTranslator
The webcam should be pointed at a sign which has text on it
When the sign is aligned correctly, a red box should appear around the sign
When the red box is steady around the sign you want to translate, press the space bar
The video stream will stop
Before completing the translation, a dialog will appear to confirm the recognized characters
Any line breaks (return/new line) are represented by two spaces in the dialog
After the OCR is confirmed, the translated text will be displayed on the sign on screen

-OPTIONS
While the video stream is active, press the o key to open the options menu
From within the options menu, Translate From language and Translate To language can be changed
Also, brightness and contrast sliders are present in case lighting is not optimal

-EXITING
Any time the video stream is active, pressing [esc] will close the program