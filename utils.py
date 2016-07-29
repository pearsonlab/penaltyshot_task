from psychopy import core, visual
import numpy as np

def flicker(win, value):
	"""
	Send a binary signal (value) to the photodiode by flickering a white
    circle in the bottom right hand corner.
    """
	timer = core.Clock()
	circle = visual.Circle(win, units='height', radius=0.05,
    						fillColorSpace='rgb255',
    						lineColorSpace='rgb255',
    						fillColor=(0, 0, 0), pos=(0.75, -0.45),
    						lineColor=(0, 0, 0))
	value = np.binary_repr(value)
	# zero pad to 8 bits and add stop and start bits
	value = '1' + (8 - len(value)) * '0' + value + '1'
	# draw bits
	for bit in value:
		if bit == '1':
			circle.fillColor = (255, 255, 255)
			circle.draw()
		if bit == '0':
			circle.fillColor = (0, 0, 0)
			circle.draw()
		win.flip(clearBuffer=False)
	# clear circle on both buffers
	circle.fillColor = (0, 0, 0)
	circle.draw()
	win.flip(clearBuffer=False)
	circle.draw()
	return timer.getTime()

