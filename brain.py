class Brain:
	def __init__(self, brain_id, states, position):
		self.brain_id = brain_id
		self._state = 0
		self._states = states
		self._has_food = False
		self._direction = 0
		self._position = position
		self._rest_time = 0

	def update_brain(self, world):
		pass
	
	def attach_gui(gui):
		Brain._gui = gui
		
	def parse_brain(filename):
		pass