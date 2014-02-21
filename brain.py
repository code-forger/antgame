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
	
	@classmethod
	def parse_brain(cls, filename):
		with open(filename) as brain_file:
			num_of_lines = len(brain_file.readlines())
			for i, line in enumerate(brain_file.readlines()):
				line = line.strip()
				words = line.split(" ")
				if words[0] == "Sense":
					if (words[1] not in ["Here", "Ahead", "LeftAhead", "RightAhead"]):
						Brain.gui.show_brain_checked("The second word on line: " + (i + 1) + " is " + words[1] + " and should be either 'Here', 'Ahead', 'LeftAhead' or 'RightAhead'.")
						return None
					if int(words[2]) < 0 or int(words[2]) > num_of_lines:
						Brain.gui.show_brain_checked("The third word on line: " + (i + 1) + " is " + words[2] + " and should be between 0 and the number of states.")
						return None
					if int(words[3]) < 0 and int(words[3]) > num_of_lines:
						Brain.gui.show_brain_checked("The third word on line: " + (i + 1) + " is " + words[3] + " and should be between 0 and the number of states.")
						return None
					if (words[4] not in ["Friend", "Foe", "FriendWithFood", "FoewithFood", "Food", "Rock", "Marker", "FoeMarker", "Home", "ForHome"]):
						Brain.gui.show_brain_checked("The fifth word on line: " + (i + 1) + " is " + words[4] + " and should be either 'Friend', 'Foe', 'FriendWithFood', 'FoewithFood', 'Food', 'Rock', 'Marker', 'FoeMarker', 'Home', 'ForHome'")
						return None
					if words[4] == "Marker" and int(words[5]) > 6 and int(words[5]) < 0:
						Brain.gui.show_brain_checked("The 6th word on line: " + (i + 1) + " is " + words[4] + " and should be between 1 and 6")
						return None
						
							