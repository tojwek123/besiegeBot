import cv2
import mss
import numpy as np

areaToGrab = {'top': 40, 'left': 0, 'width': 1366, 'height': 768}
scaleFactor = 0.25
sct = mss.mss()

while cv2.waitKey(25) & 0xFF != ord('q'):
	img = np.array(sct.grab(areaToGrab))
	img = cv2.resize(img, (int(areaToGrab['width'] * scaleFactor), int(areaToGrab['height'] * scaleFactor)))
	
	#Dunno why
	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
	
	lower = np.array([25, 220, 0])
	upper = np.array([35, 255, 0])
	
	mask = cv2.inRange(img, lower, upper)
	mask = cv2.medianBlur(mask,3)
	
	cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[1]
	
	lastPt = None
	
	for c in cnts:
		M = cv2.moments(c)
		cX = int(M["m10"] / M["m00"])
		cY = int(M["m01"] / M["m00"])
		
		if lastPt is not None:
			cv2.arrowedLine(img, lastPt, (cX, cY), (0, 0, 255), thickness=2)
		
		lastPt = (cX, cY)
		
	
	cv2.imshow('img', img)
	cv2.imshow('mask', mask)

cv2.destroyAllWindows()