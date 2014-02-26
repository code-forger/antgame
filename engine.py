import brain
from threading import Thread
import time

class Engine(Thread):
	def __init__(self, id, messages_from_gui, gui):
		Thread.__init__(self)
		self._messages_from_gui = messages_from_gui
		
		self.daemon = True
		self._gui = gui

	def run(self):
		print "Starting engine"
		while True:
			if len(self._messages_from_gui) > 0:
				message = self._messages_from_gui.pop(0)
				print message[0]
			time.sleep(.001)
