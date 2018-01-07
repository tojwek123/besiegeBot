import win32gui
import win32api
import win32con
import threading
import queue
import time

def keyDown(key, winName=None):
	if winName is not None:
		win32gui.SetForegroundWindow(win32gui.FindWindow(None, winName))
	win32api.keybd_event(key, 0, win32con.KEYEVENTF_EXTENDEDKEY, 0)
	
def keyUp(key, winName=None):
	if winName is not None:
		win32gui.SetForegroundWindow(win32gui.FindWindow(None, winName))
	win32api.keybd_event(key, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)
	
def keyClick(key, winName=None):
	if winName is not None:
		win32gui.SetForegroundWindow(win32gui.FindWindow(None, winName))
	win32api.keybd_event(key, 0, win32con.KEYEVENTF_EXTENDEDKEY, 0)
	win32api.keybd_event(key, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)
	
def isKeyPressed(key):
	return win32api.GetAsyncKeyState(key) != 0
	
def enableKeyPwm(winName=None):
	_pwmThread.start()
	
def disableKeyPwm():
	_pwmQueue.put(False)
	_pwmThread.join()
	
def setKeyPwm(key, duty, winName=None):
	"""duty is from 0 to 100"""
	request = {key: {'duty': duty, 'winName': winName}}
	_pwmQueue.put(request)
	
def _pwmHandler():
	global _pwmHwnd
	pwmKeys = {}
	pwmCnt = 0
	
	while True:
		while not _pwmQueue.empty():
			request = _pwmQueue.get()
			if type(request) is not dict:
				for key in pwmKeys:
					keyUp(key, pwmKeys[key]['winName'])
				return
			
			#Key up if 0 value appeared
			if list(request.values())[0]['duty'] == 0:
				keyUp(list(request.keys())[0], list(request.values())[0]['winName'])
				
			pwmKeys.update(request)
		
		for key in pwmKeys:
			if pwmKeys[key]['duty'] > 0:
				if pwmKeys[key]['duty'] == pwmCnt:
					keyUp(key, pwmKeys[key]['winName'])
				elif pwmCnt == 0:
					keyDown(key, pwmKeys[key]['winName'])
		
		pwmCnt = (pwmCnt + 1) % 100
		time.sleep(0.001)
		
_pwmThread = threading.Thread(target=_pwmHandler)
_pwmQueue = queue.Queue()
_pwmHwnd = None