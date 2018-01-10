import cv2
import numpy as np
import winmanip as wm
import trigutils
import threading
import time
import queue

class Vehicle:
	
	def __init__(self, frontMarker, backMarker):
		self.frontMarker = (np.array(frontMarker['lowerBound'] + [255]), np.array(frontMarker['upperBound'] + [255]))
		self.backMarker = (np.array(backMarker['lowerBound'] + [255]), np.array(backMarker['upperBound'] + [255]))
		
	def cleanup(self):
		pass
		
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
	
	def __init__(self, frontMarker, backMarker, controlLayout, keyboard):
		super().__init__(frontMarker, backMarker)
		self._controlLayout = controlLayout
		self._keyboard = keyboard
		self._shootingThread = threading.Thread(target=self._shootingHandler)
		self._shootingQueue = queue.Queue()
		
	def cleanup(self):
		self._shootingThread.stop()
		self._shootingQueue.put({'stop': True})
		
	def setForwardSpeed(self, speed):
		if speed >= 0:
			self._keyboard.setKeyPwm(self._controlLayout['forward'], speed)
			self._keyboard.setKeyPwm(self._controlLayout['backward'], 0)
		else:
			self._keyboard.setKeyPwm(self._controlLayout['forward'], 0)
			self._keyboard.setKeyPwm(self._controlLayout['backward'], -speed)
			
	def setRotationSpeed(self, speed):
		if speed >= 0:
			self._keyboard.setKeyPwm(self._controlLayout['left'], speed)
			self._keyboard.setKeyPwm(self._controlLayout['right'], 0)
		else:
			self._keyboard.setKeyPwm(self._controlLayout['left'], 0)
			self._keyboard.setKeyPwm(self._controlLayout['right'], -speed)
			
	def setShooting(self, rate):
		self._shootingRate = rate
		self._shootingQueue.put({'rate': rate})
		
	def _shootingHandler(self):
		sleepTime = None
	
		while True:
			try:
				queueItem = self._shootingQueue.get(timeout=sleepTime)
				
				if 'stop' in queueItem:
					if queueItem['stop'] == True:
						break
						
				if 'rate' in queueItem:
					rate = queueItem['rate']
					
					if rate is not None:
						sleepTime = 1 / rate
					else sleepTime = None
			except Queue.Empty:
				pass
		
			self._keyboard.keyClick(self._controlLayout['shoot'])
		
			
class AutoVehicle(ControllableVehicle):
	
	def __init__(self, frontMarker, backMarker, controlLayout, keyboard, enemyVehicle):
		super().__init__(frontMarker, backMarker, controlLayout, keyboard)
		self._enemyVehicle = enemyVehicle
		self._pos = None
		self._isFollowingEnemyAngle = False
		
		#Regulator params
		self._rotRegGain = 2
		
	def feedImage(self, im):
		self._pos = super().getPos(im)
		self._enemyPos = self._enemyVehicle.getPos(im)
		
		if self._isFollowingEnemyAngle:
			self._followEnemyAngle()
		
	def getPos(self):
		return self._pos
		
	def getEnemyPos(self):
		return self._enemyPos
		
	def getOffTheLineAngle(self):
		if 'front' in self._pos and 'back' in self._pos and 'front' in self._enemyPos:
			angle = 180 - trigutils.getAngleBetweenTwoLines(self._pos['back'], self._pos['front'], self._enemyPos['front'], self._pos['back'])
		else:
			angle = None
		return angle
		
	def setFollowEnemyAngle(self, choice):
		if choice == False:
			self.setRotationSpeed(0)
			
		self._isFollowingEnemyAngle = choice
		
	def _followEnemyAngle(self):
		angle = self.getOffTheLineAngle()
		
		if angle is not None:
			rotationControl = int((angle) * self._rotRegGain)
			self.setRotationSpeed(rotationControl)