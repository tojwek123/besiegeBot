import cv2
import sys
import time
import win32con
import win32api
import numpy as np

import besiege
import trigutils as trig
import winmanip as wm
from keyboard import Keyboard

#Marker consists of color lower and upper bounds, values were chosen experimentally
GreenMarker  = {'lowerBound': [31, 80, 0],   'upperBound': [55, 255, 0]}
BlueMarker =   {'lowerBound': [126, 0, 18],  'upperBound': [255, 0, 65]}
OrangeMarker = {'lowerBound': [31, 26, 131], 'upperBound': [38, 105, 255]}
PurpleMarker = {'lowerBound': [127, 0, 100], 'upperBound': [255, 1, 151]}

ControlLayout = {'left':     win32con.VK_LEFT,
				 'right':    win32con.VK_RIGHT,
				 'forward':  win32con.VK_UP,
				 'backward': win32con.VK_DOWN,
				 'fire':	 ord('C')}
			
WinName = r'Besiege'

def main(argv):
	screen = wm.WindowGrabber()
	myVehicle = besiege.ControllableVehicle(GreenMarker, BlueMarker, ControlLayout)
	enemyVehicle = besiege.Vehicle(OrangeMarker, PurpleMarker)
	kbd = Keyboard()
	kbd.attach(WinName)
	kbd.enableKeyPwm()
	
	try:
		screen.attach(WinName)
	except wm.WinManipException as exc:
		print(exc)
		sys.exit(-1)

	wasPressed = False
		
	while not Keyboard.isShortcutPressed('CTRL+Q'):
		im = screen.grab()
		
		if im is not None:
			im = cv2.pyrDown(im)
			myPos = myVehicle.getPos(im)
			enemyPos = enemyVehicle.getPos(im)
			
			if 'front' in myPos and 'back' in myPos:
				cv2.arrowedLine(im, myPos['back'], myPos['front'], (0, 0, 255), 2)
				
			if 'front' in enemyPos and 'back' in enemyPos:
				cv2.arrowedLine(im, enemyPos['back'], enemyPos['front'], (0, 255, 0), 2)
				
			if 'front' in myPos and 'back' in myPos and 'front' in enemyPos and 'back' in enemyPos:
				cv2.line(im, myPos['back'], enemyPos['front'], (255, 0, 0), 2)
				
				if Keyboard.isShortcutPressed('CTRL+T'):
					wasPressed = True
					angle = trig.getAngleBetweenTwoLines(myPos['back'], myPos['front'], enemyPos['front'], myPos['back'])
					rotationControl = int((180 - angle) * 1.5)
					print(angle, rotationControl)
					myVehicle.setRotationSpeed(rotationControl, kbd)
					myVehicle.setForwardSpeed(100, kbd)
				elif not Keyboard.isShortcutPressed('CTRL+T') and wasPressed:
					wasPressed = False
					myVehicle.setForwardSpeed(0, kbd)
					myVehicle.setRotationSpeed(0, kbd)
			elif wasPressed:
				wasPressed = False
				myVehicle.setForwardSpeed(0, kbd)
				myVehicle.setRotationSpeed(0, kbd)
				
			cv2.imshow('Preview', im)
			cv2.waitKey(1)
		else:
			print('Cannot grab window - it might be minimized')
				
	kbd.disableKeyPwm()
	kbd.detach()
	screen.detach()
	cv2.destroyAllWindows()

if __name__ == '__main__':
	main(sys.argv)