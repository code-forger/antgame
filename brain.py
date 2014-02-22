'''
Sense sensedir st1 st2 cond	 	Go to state st1 if cond holds in sensedir;
 	 	and to state st2 otherwise.
Mark i st	 	Set mark i in current cell and go to st.
Unmark i st	 	Clear mark i in current cell and go to st.
PickUp st1 st2	 	Pick up food from current cell and go to st1;
 	 	go to st2 if there is no food in the current cell.
Drop st	 	Drop food in current cell and go to st.
Turn lr st	 	Turn left or right and go to st.
Move st1 st2	 	Move forward and go to st1;
 	 	go to st2 if the cell ahead is blocked.
Flip p st1 st2	 	Choose a random number x from 0 to p-1;
 	 	go to st1 if x=0 and st2 otherwise.
		'''

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
		instructions = []
		success = "The file is correct!"
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
					if words[4] == "Marker":
						instructions.append([words[0], words[1], int(words[2]), int(words[3]), words[4], int(words[5])])
					else:
						instructions.append([words[0], words[1], int(words[2]), int(words[3]), words[4]])
				elif words[0] == "Mark":
					if int(words[1]) < 0 or int(words[1]) > num_of_lines:
						Brain.gui.show_brain_checked("The second word on line: " + (i + 1) + " is " + words[1] + " and should be between 0 and the number of states.")
							return None
					if int(words[2]) < 0 or int(words[2]) > num_of_lines:
						Brain.gui.show_brain_checked("The third word on line: " + (i + 1) + " is " + words[2] + " and should be between 0 and the number of states.")
							return None
					else:
						instructions.append([words[0], int(words[1]), int(words[2])]) 
				elif words[0] == "Unmark":
					if int(words[1]) < 0 or int(words[1]) > num_of_lines:
						Brain.gui.show_brain_checked("The second word on line: " + (i + 1) + " is " + words[1] + " and should be between 0 and the number of states.")
							return None
					if int(words[2]) < 0 or int(words[2]) > num_of_lines:
						Brain.gui.show_brain_checked("The third word on line: " + (i + 1) + " is " + words[2] + " and should be between 0 and the number of states.")
							return None
					else:
						instructions.append([words[0], int(words[1]), int(words[2])]) 
				elif words[0] == "PickUp":
					if int(words[1]) < 0 or int(words[1]) > num_of_lines:
						Brain.gui.show_brain_checked("The second word on line: " + (i + 1) + " is " + words[1] + " and should be between 0 and the number of states.")
							return None
					if int(words[2]) < 0 or int(words[2]) > num_of_lines:
						Brain.gui.show_brain_checked("The third word on line: " + (i + 1) + " is " + words[2] + " and should be between 0 and the number of states.")
							return None
					else:
						instructions.append([words[0], int(words[1]), int(words[2])]) 
				elif words[0] == "Drop":
					if int(words[1]) < 0 or int(words[1]) > num_of_lines:
						Brain.gui.show_brain_checked("The second word on line: " + (i + 1) + " is " + words[1] + " and should be between 0 and the number of states.")
							return None
					else:
						instructions.append([words[0], int(words[1])]) 
				elif words[0] == "Turn":
					if (words[1] not in ["Left", "Right"]):
						Brain.gui.show_brain_checked("The second word on line: " + (i + 1) + " is " + words[1] + " and should be either 'Left' or 'Right'.")
						return None
				elif words[0] == "Move":
					if int(words[1]) < 0 or int(words[1]) > num_of_lines:
						Brain.gui.show_brain_checked("The second word on line: " + (i + 1) + " is " + words[1] + " and should be between 0 and the number of states.")
							return None
					if int(words[2]) < 0 or int(words[2]) > num_of_lines:
						Brain.gui.show_brain_checked("The third word on line: " + (i + 1) + " is " + words[2] + " and should be between 0 and the number of states.")
							return None
					else:
						instructions.append([words[0], int(words[1]), int(words[2])]) 
				elif words[0] == "Flip":
					if int(words[1]) < 0:
						Brain.gui.show_brain_checked("The second number on line: " + (i + 1) + " is " + words[1] + " and should be a number no less than 0.")
							return None
					if int(words[2]) < 0 or int(words[2]) > num_of_lines:
						Brain.gui.show_brain_checked("The third word on line: " + (i + 1) + " is " + words[2] + " and should be between 0 and the number of states.")
							return None
					if int(words[3]) < 0 or int(words[3]) > num_of_lines:
						Brain.gui.show_brain_checked("The fourth word on line: " + (i + 1) + " is " + words[3] + " and should be between 0 and the number of states.")
							return None
					else:
						instructions.append([words[0], int(words[1]), int(words[2]), int(words[3])]) 
				else:
					Brain.gui.show_brain_checked("The first word on line: " + (i + 1) + " is " + words[0] + " and should be  either 'Sense', 'Mark', 'Unmark', 'PickUp', 'Drop', 'Turn', 'Move', 'Flip'")
			print success
		return instrucions
						
							