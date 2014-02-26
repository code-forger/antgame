import threading
import pygame

pygame.init()

class renderer(threading.Thread):
	def __init__(self, window, messages_from_engine, current_engine):
		threading.Thread(self)
		self._window = window
		self._messages_from_engine = messages_from_engine
		self._current_engine = current_engine

	def run(self):
		if len(self, _messages_from_engine):
			message = _messages_from_engine.pop(0)
			if message[0] == "render world":
				world = message[1]
				engine = message[2]

				if engine == self._current_engine:
					pass
					#TODO render the world to the screen
		else:
			pass
