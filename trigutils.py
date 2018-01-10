import numpy as np

def getAngleBetweenTwoLines(a1, a2, b1, b2):
	"""Returns angle (0 - 360 degrees) between line which goes through points a1, a2
	   and line which goes through points b1, b2"""
	tf_a1 = (0, 0)
	tf_a2 = np.subtract(a2, a1)
	tf_b1 = (0, 0)
	tf_b2 = np.subtract(b2, b1)
	
	a_angle = getPtAngle(tf_a2)
	b_angle = getPtAngle(tf_b2)
	
	if a_angle > b_angle:
		diff = 360 - a_angle + b_angle
	else:
		diff = b_angle - a_angle
	
	return float(diff)
	
		
def getPtAngle(pt):
	"""Returns angle (0 - 360 degrees) between x-axis and line which goes through points (0, 0) and pt"""
	angle = 0
	
	if pt[0] > 0 and pt[1] >= 0:
		angle = np.degrees(np.arctan(pt[1] / pt[0]))
	elif pt[0] > 0 and pt[1] < 0:
		angle = np.degrees(np.arctan(pt[1] / pt[0])) + 360
	elif pt[0] < 0:
		angle = np.degrees(np.arctan(pt[1] / pt[0])) + 180
	elif pt[0] == 0 and pt[1] > 0:
		angle = 90
	elif pt[0] == 0 and pt[1] < 0:
		angle = 270
		
	return angle