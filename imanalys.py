import cv2
import numpy as np

class VehicleDetector:
	
	def __init__(self, frontColorRange, backColorRange):
		self.frontColorRange = (np.array(frontColorRange[0] + [255]), np.array(frontColorRange[1] + [255]))
		self.backColorRange = (np.array(backColorRange[0] + [255]), np.array(backColorRange[1] + [255]))
		
	def getPos(self, im):
		#Detect front:
		
		(_, front) = self._findAreaCenter(im, self.frontColorRange)
		(mask, back) = self._findAreaCenter(im, self.backColorRange)
		
		cv2.imshow('mask', mask)
		
		return (front, back)
			
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