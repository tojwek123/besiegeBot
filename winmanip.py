from PIL import ImageGrab
import win32api
import win32gui
import win32ui
import win32con
import cv2
import numpy as np

class WinManipException(Exception):
	pass
	
class WindowGrabber:
	
	_TopOffset = 30
	_LeftOffset = 9
	
	def __init__(self):
		pass
		
	def attach(self, winName):
		self.hwnd = win32gui.FindWindow(None, winName)
		if 0 == self.hwnd:
			raise WinManipException('Window with name "{}" does not exist'.format(winName))
		
		self.hdcWindow = win32gui.GetDC(self.hwnd)
		self.hdcMemDC = win32gui.CreateCompatibleDC(self.hdcWindow)
		self.hwndDC = win32gui.GetWindowDC(self.hwnd)
		self.mfcDC  = win32ui.CreateDCFromHandle(self.hwndDC)
		self.saveDC = self.mfcDC.CreateCompatibleDC()
	
	def detach(self):
		self.saveDC.DeleteDC()
		self.mfcDC.DeleteDC()
		win32gui.ReleaseDC(self.hwnd, self.hwndDC)
	
	def grab(self):
		left, top, right, bottom = win32gui.GetClientRect(self.hwnd)
		width = right - left
		height = bottom - top
		
		saveBitMap = win32ui.CreateBitmap()
		saveBitMap.CreateCompatibleBitmap(self.mfcDC, width, height)
		self.saveDC.SelectObject(saveBitMap)
		
		self.saveDC.BitBlt((0, 0), (width, height), self.mfcDC, (left + WindowGrabber._LeftOffset, top + WindowGrabber._TopOffset), win32con.SRCCOPY) 
		
		bmpinfo = saveBitMap.GetInfo()
		bmpstr = saveBitMap.GetBitmapBits(True)
		try:
			cvIm = np.fromstring(bmpstr, np.uint8).reshape(bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)
		except ValueError:
			cvIm = None
			
		win32gui.DeleteObject(saveBitMap.GetHandle())
		return cvIm
		
class Keyboard:
	
	def __init__(self):
		pass
	
	def attach(self, winName):
		self.hwnd = win32gui.FindWindow(None, winName)
		if 0 == self.hwnd:
			raise WinManipException('Window with name "{}" does not exist'.format(winName))
			
	def detach(self):
		pass
			
	def down(self, key):
		win32gui.SetForegroundWindow(self.hwnd)
		win32api.keybd_event(key, 0, win32con.KEYEVENTF_EXTENDEDKEY, 0)
		
	def up(self, key):
		win32gui.SetForegroundWindow(self.hwnd)
		win32api.keybd_event(key, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)
		
	def click(self, key):
		win32gui.SetForegroundWindow(self.hwnd)
		win32api.keybd_event(key, 0, win32con.KEYEVENTF_EXTENDEDKEY, 0)
		win32api.keybd_event(key, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)
		
	def isPressed(self, key):
		return win32api.GetAsyncKeyState(key) != 0