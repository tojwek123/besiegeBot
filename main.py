import winmanip as wm
import keyboard as kbd
import besiege
import trigutils as trig
import cv2
import sys
import time
import win32con
import win32api
import numpy as np

#Marker consists of color lower and upper bounds, values were chosen experimentally
GreenMarker =  {'lowerBound': [31, 80, 0],   'upperBound': [55, 255, 0]}
BlueMarker =   {'lowerBound': [126, 0, 18],  'upperBound': [255, 0, 65]}
OrangeMarker = {'lowerBound': [31, 26, 131], 'upperBound': [38, 105, 255]}
PurpleMarker = {'lowerBound': [127, 0, 100], 'upperBound': [255, 1, 151]}

ControlLayout = {'left':     win32con.VK_LEFT,
				 'right':    win32con.VK_RIGHT,
				 'forward':  win32con.VK_UP,
				 'backward': win32con.VK_DOWN,
				 'fire':	  ord('C')}
			
WinName = r'Besiege'

def main(argv):
	screen = wm.WindowGrabber()
	myVehicle = besiege.Vehicle(GreenMarker, BlueMarker)
	enemyVehicle = besiege.Vehicle(OrangeMarker, PurpleMarker)
	kbd.enableKeyPwm(WinName)
	
	try:
		screen.attach(WinName)
	except wm.WinManipException as exc:
		print(exc)
		sys.exit(-1)

	wasPressed = False
		
	while not (kbd.isKeyPressed(win32con.VK_CONTROL) and kbd.isKeyPressed(ord('Q'))):
		im = screen.grab()
		
		if kbd.isKeyPressed(win32con.VK_CONTROL) and kbd.isKeyPressed(ord('T')) and not wasPressed:
			wasPressed = True
			kbd.setKeyPwm(win32con.VK_UP, 10, WinName)
		elif not (kbd.isKeyPressed(win32con.VK_CONTROL) and kbd.isKeyPressed(ord('T'))) and wasPressed:
			wasPressed = False
			kbd.setKeyPwm(win32con.VK_UP, 0, WinName)
		
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
				
				trig.getAngleBetweenTwoLines(myPos['back'], myPos['front'], enemyPos['back'], enemyPos['front'])
				
				# relocatedMyFront = np.subtract(myFront, myBack)
				# relocatedMyBack = (0, 0)
				# relocatedEnemyFront = np.subtract(enemyFront, myBack)
				# relocatedEnemyBack = np.subtract(enemyBack, myBack)
				
				# myAngle = 0
				
				# if relocatedMyFront[0] > 0 and relocatedMyFront[1] >= 0:
					# myAngle = np.degrees(np.arctan(relocatedMyFront[1] / relocatedMyFront[0]))
				# elif relocatedMyFront[0] > 0 and relocatedMyFront[1] < 0:
					# myAngle = np.degrees(np.arctan(relocatedMyFront[1] / relocatedMyFront[0])) + 360
				# elif relocatedMyFront[0] < 0:
					# myAngle = np.degrees(np.arctan(relocatedMyFront[1] / relocatedMyFront[0])) + 180
				# elif relocatedMyFront[0] == 0 and relocatedMyFront[1] > 0:
					# myAngle = 90
				# elif relocatedMyFront[0] == 0 and relocatedMyFront[1] < 0:
					# myAngle = 270
					
				# enemyAngle = 0
				
				# if relocatedEnemyFront[0] > 0 and relocatedEnemyFront[1] >= 0:
					# enemyAngle = np.degrees(np.arctan(relocatedEnemyFront[1] / relocatedEnemyFront[0]))
				# elif relocatedEnemyFront[0] > 0 and relocatedEnemyFront[1] < 0:
					# enemyAngle = np.degrees(np.arctan(relocatedEnemyFront[1] / relocatedEnemyFront[0])) + 360
				# elif relocatedEnemyFront[0] < 0:
					# enemyAngle = np.degrees(np.arctan(relocatedEnemyFront[1] / relocatedEnemyFront[0])) + 180
				# elif relocatedEnemyFront[0] == 0 and relocatedEnemyFront[1] > 0:
					# enemyAngle = 90
				# elif relocatedEnemyFront[0] == 0 and relocatedEnemyFront[1] < 0:
					# enemyAngle = 270
				
				# angleDiff = myAngle - enemyAngle
				# print(myAngle, enemyAngle, angleDiff)
				
				# if keyboard.isPressed(ord('T')):
					# keyboard.down(win32con.VK_UP)
					# wasPressed = True
					# if angleDiff < 3:
						# keyboard.up(win32con.VK_LEFT)
						# keyboard.down(win32con.VK_RIGHT)
					# elif angleDiff > 3:
						# keyboard.up(win32con.VK_RIGHT)
						# keyboard.down(win32con.VK_LEFT)
				# elif wasPressed:
					# wasPressed = False
					# keyboard.up(win32con.VK_UP)
					# keyboard.up(win32con.VK_RIGHT)
					# keyboard.up(win32con.VK_LEFT)
					
				# (height, width) = im.shape[:2]
				
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
				
	kbd.disableKeyPwm()
	screen.detach()
	cv2.destroyAllWindows()

if __name__ == '__main__':
	main(sys.argv)