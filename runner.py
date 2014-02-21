from threading import Thread

class runner(Thread):
	def __init__(self, messages_from_gui, messages_to_engine):
		Thread.__init__(self)
		self._messages_from_gui = self.messages_from_gui
		self._messages_to_engine = self.messages_to_engine
		
		self._running = False
		self._speed = False
		
		self._timeout = False

	def run():
		while true:
			if not len(self._messages_from_gui):
				message = self._messages_from_gui.pop(0)
				if message[0] == "run":
					self._running = true
				if message[0] == "stop":
					self._running = False
				if message[0] == "speed":
					self._speed = int(message[1])
			thread.sleep(100)
			if self_running:
				self._timeout -= 100
				if self._timeout < 0:
					self._timeout = self._speed
					self._messages_to_engine.append(["step world"])