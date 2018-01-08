import win32gui
import win32api
import win32con
import threading
import queue
import time

class Keyboard():
	
	KeysLookup = {
		'CTRL': win32con.VK_CONTROL,
		'SHIFT': win32con.VK_SHIFT,
		'ALT': win32con.VK_MENU
		}
	
	def __init__(self):
		self._pwmThread = threading.Thread(target=self._pwmHandler)
		self._pwmQueue = queue.Queue()
		self._hwnd = None
	
	@classmethod
	def isKeyPressed(cls, key):
		if type(key) is str:
			key = ord(key)
		return win32api.GetAsyncKeyState(key) != 0
	
	@classmethod
	def isShortcutPressed(cls, shortcut):
		shortcut = shortcut.upper()
		keys = shortcut.split('+')
		pressed = True
		
		for key in keys:
			if key in cls.KeysLookup:
				if not cls.isKeyPressed(cls.KeysLookup[key]):
					pressed = False
					break
			elif not cls.isKeyPressed(ord(key)):
				pressed = False
				break
		
		return pressed
	
	def attach(self, winName):
		self._hwnd = win32gui.FindWindow(None, winName)
		
	def detach(self):
		self._hwnd = None
	
	def keyDown(self, key):
		self._setWindowFocus()
		win32api.keybd_event(key, 0, win32con.KEYEVENTF_EXTENDEDKEY, 0)
	
	def keyUp(self, key):
		self._setWindowFocus()
		win32api.keybd_event(key, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)
	
	def keyClick(self, key):
		self._setWindowFocus()
		win32api.keybd_event(key, 0, win32con.KEYEVENTF_EXTENDEDKEY, 0)
		win32api.keybd_event(key, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)
	
	def enableKeyPwm(self):
		self._pwmThread.start()
	
	def disableKeyPwm(self):
		self._pwmQueue.put(False)
		self._pwmThread.join()
	
	def setKeyPwm(self, key, duty):
		"""duty is from 0 to 100"""
		request = (key, duty)
		self._pwmQueue.put(request)
	
	def _pwmHandler(self):
		pwmKeys = {}
		pwmCnt = 0
		
		while True:
			while not self._pwmQueue.empty():
				request = self._pwmQueue.get()
				if type(request) is not tuple:
					#Key up for all pwm keys
					for key in pwmKeys:
						self.keyUp(key)
					return
				
				#Key up if 0 value appeared
				if request[1] == 0:
					self.keyUp(request[0])
					
				pwmKeys.update({request[0]: request[1]})
			
			for key in pwmKeys:
				if pwmKeys[key] > 0:
					if pwmKeys[key] == pwmCnt:
						self.keyUp(key)
					elif pwmCnt == 0:
						self.keyDown(key)
			
			pwmCnt = (pwmCnt + 1) % 100
			time.sleep(0.001)
			
	def _setWindowFocus(self):
		if self._hwnd is not None:
			win32gui.SetForegroundWindow(self._hwnd)
	