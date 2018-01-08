import cv2
import numpy as np
import winmanip as wm
import threading
import time

class Vehicle:
	
	def __init__(self, frontMarker, backMarker):
		self.frontMarker = (np.array(frontMarker['lowerBound'] + [255]), np.array(frontMarker['upperBound'] + [255]))
		self.backMarker = (np.array(backMarker['lowerBound'] + [255]), np.array(backMarker['upperBound'] + [255]))
		
	def getPos(self, im):
		(frontMask, front) = self._findAreaCenter(im, self.frontMarker)
		(backMask, back) = self._findAreaCenter(im, self.backMarker)
		
		result = {'frontMask': frontMask, 'backMask': backMask}
		
		if front is not None:
			result.update({'front': front})
		if back is not None:
			result.update({'back': back})
		
		return result
		
	def _findAreaCenter(self, im, colorRange):
		center = None
		#im = cv2.GaussianBlur(im, (5, 5), 0)
		mask = cv2.inRange(im, colorRange[0], colorRange[1])
		kernel = np.ones((3,3),np.uint8)
		mask = cv2.dilate(mask, kernel)
		#mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
		#mask = cv2.medianBlur(mask, 3)
		
		contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		
		for contour in contours[1]:
			M = cv2.moments(contour)
			try:
				center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))
			except:
				pass
		
		return (mask, center)
		
class ControllableVehicle(Vehicle):
	
	def __init__(self, frontMarker, backMarker, controlLayout):
		super().__init__(frontMarker, backMarker)
		self._controlLayout = controlLayout
		
	def setForwardSpeed(self, speed, keyboard):
		if speed >= 0:
			keyboard.setKeyPwm(self._controlLayout['forward'], speed)
			keyboard.setKeyPwm(self._controlLayout['backward'], 0)
		else:
			keyboard.setKeyPwm(self._controlLayout['forward'], 0)
			keyboard.setKeyPwm(self._controlLayout['backward'], -speed)
			
	def setRotationSpeed(self, speed, keyboard):
		if speed >= 0:
			keyboard.setKeyPwm(self._controlLayout['left'], speed)
			keyboard.setKeyPwm(self._controlLayout['right'], 0)
		else:
			keyboard.setKeyPwm(self._controlLayout['left'], 0)
			keyboard.setKeyPwm(self._controlLayout['right'], -speed)