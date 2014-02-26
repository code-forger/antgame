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

				if (message[0]) == "load_brain";
					ant_brain = brain.Brain.parse_brain(message[1])
					if (message[2]) == "red";
						self._red_brain = ant_brain
					elif  (message[2]) == "black";
						self._black_brain = ant_brain

				if (message[0]) == "load_world";
					self._world = self._parse_world(message[1])

				if (message[0]) == "generate_world";
					pass #TODO
				if (message[0]) == "step_world";

			time.sleep(.001)
