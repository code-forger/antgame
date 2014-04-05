from threading import Thread
import time

class Runner(Thread):
	def __init__(self, messages_from_gui, messages_to_engine):
		Thread.__init__(self)
		self._messages_from_gui = messages_from_gui
		self._messages_to_engine = messages_to_engine
		self.daemon = True
		
		self._running = False
		self._speed = 1
		
		self._timeout = False


	def run(self):
		print "Starting runner"
		while True:
			if len(self._messages_from_gui):
				message = self._messages_from_gui.pop(0)
				if message[0] == "run":
					print "RUN"
					self._running = True
				if message[0] == "stop":
					self._running = False
				if message[0] == "speed":
					#print message
					self._speed = int(message[1])
				for x in self._messages_from_gui:
					if x[0] == message[0]:
						self._messages_from_gui.remove(x)
						message = x
			time.sleep(.001)
			if self._running:
				self._timeout -= 1
				if self._timeout < 0:
					self._timeout = 1000/self._speed
					self._messages_to_engine.append(["step world"])