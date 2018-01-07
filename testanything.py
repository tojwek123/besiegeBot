import winmanip as wm
import imanalys
import cv2
import sys
import time
import win32con
import win32api
import numpy as np

GreenBlockRange = ([31, 80, 0], [55, 255, 0])
BlueBlockRange = ([126, 0, 18], [255, 0, 65])
OrangeBlockRange = ([31, 26, 131], [38, 105, 255])
PurpleBlockRange = ([127, 0, 100], [255, 1, 151])


grabber = wm.WindowGrabber()
keyboard = wm.Keyboard()
myVehicleDetector = imanalys.VehicleDetector(GreenBlockRange, BlueBlockRange)
enemyDetector = imanalys.VehicleDetector(OrangeBlockRange, PurpleBlockRange)
											 
winName = r'Besiege'

try:
	grabber.attach(winName)
	keyboard.attach(winName)
except wm.WinManipException as exc:
	print(exc)
	sys.exit(-1)

wasPressed = False
	
while not (keyboard.isPressed(win32con.VK_CONTROL) and keyboard.isPressed(ord('Q'))):
	im = grabber.grab()
	
	if im is not None:
		im = cv2.pyrDown(im)
		(myFront, myBack) = myVehicleDetector.getPos(im)
		(enemyFront, enemyBack) = enemyDetector.getPos(im)
		
		if myBack is not None and myFront is not None:
			cv2.arrowedLine(im, myBack, myFront, (0, 0, 255), 2)
			
		if enemyBack is not None and enemyFront is not None:
			cv2.arrowedLine(im, enemyBack, enemyFront, (0, 255, 0), 2)
			
		if myBack is not None and myFront is not None and \
		   enemyBack is not None and enemyFront is not None:
			
			cv2.line(im, myBack, enemyFront, (255, 0, 0), 2)
			relocatedMyFront = np.subtract(myFront, myBack)
			relocatedMyBack = (0, 0)
			relocatedEnemyFront = np.subtract(enemyFront, myBack)
			relocatedEnemyBack = np.subtract(enemyBack, myBack)
			
			myAngle = 0
			
			if relocatedMyFront[0] > 0 and relocatedMyFront[1] >= 0:
				myAngle = np.degrees(np.arctan(relocatedMyFront[1] / relocatedMyFront[0]))
			elif relocatedMyFront[0] > 0 and relocatedMyFront[1] < 0:
				myAngle = np.degrees(np.arctan(relocatedMyFront[1] / relocatedMyFront[0])) + 360
			elif relocatedMyFront[0] < 0:
				myAngle = np.degrees(np.arctan(relocatedMyFront[1] / relocatedMyFront[0])) + 180
			elif relocatedMyFront[0] == 0 and relocatedMyFront[1] > 0:
				myAngle = 90
			elif relocatedMyFront[0] == 0 and relocatedMyFront[1] < 0:
				myAngle = 270
				
			enemyAngle = 0
			
			if relocatedEnemyFront[0] > 0 and relocatedEnemyFront[1] >= 0:
				enemyAngle = np.degrees(np.arctan(relocatedEnemyFront[1] / relocatedEnemyFront[0]))
			elif relocatedEnemyFront[0] > 0 and relocatedEnemyFront[1] < 0:
				enemyAngle = np.degrees(np.arctan(relocatedEnemyFront[1] / relocatedEnemyFront[0])) + 360
			elif relocatedEnemyFront[0] < 0:
				enemyAngle = np.degrees(np.arctan(relocatedEnemyFront[1] / relocatedEnemyFront[0])) + 180
			elif relocatedEnemyFront[0] == 0 and relocatedEnemyFront[1] > 0:
				enemyAngle = 90
			elif relocatedEnemyFront[0] == 0 and relocatedEnemyFront[1] < 0:
				enemyAngle = 270
			
			angleDiff = myAngle - enemyAngle
			print(myAngle, enemyAngle, angleDiff)
			
			if keyboard.isPressed(ord('T')):
				keyboard.down(win32con.VK_UP)
				wasPressed = True
				if angleDiff < 3:
					keyboard.up(win32con.VK_LEFT)
					keyboard.down(win32con.VK_RIGHT)
				elif angleDiff > 3:
					keyboard.up(win32con.VK_RIGHT)
					keyboard.down(win32con.VK_LEFT)
			elif wasPressed:
				wasPressed = False
				keyboard.up(win32con.VK_UP)
				keyboard.up(win32con.VK_RIGHT)
				keyboard.up(win32con.VK_LEFT)
				
			(height, width) = im.shape[:2]
			
			# if keyboard.isPressed(ord('T')):
				# wasPressed = True
				# if myFront[1] < myBack[1]:
					# keyboard.up(win32con.VK_LEFT)
					# keyboard.down(win32con.VK_RIGHT)
				# elif myFront[1] > myBack[1]:
					# keyboard.up(win32con.VK_RIGHT)
					# keyboard.down(win32con.VK_LEFT)
			# elif wasPressed:
				# wasPressed = False
				# keyboard.up(win32con.VK_RIGHT)
				# keyboard.up(win32con.VK_LEFT)
			
		cv2.imshow('Preview', im)
		cv2.waitKey(1)
	else:
		print('Cannot grab window - it might be minimized')
			
grabber.detach()
keyboard.detach()
cv2.destroyAllWindows()