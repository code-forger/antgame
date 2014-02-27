import brain
from threading import Thread
import time

BLACK = "-"
ROCK = "#"
FOOD = (1, 9)
NONE = "."
RED = "+"

class Engine(Thread):
	def __init__(self, id, messages_from_gui, gui):
		Thread.__init__(self)
		self._messages_from_gui = messages_from_gui

		self.daemon = True
		self._gui = gui

		self._black_brain = None
		self._red_brain = None
		self._black_ants = None
		self._red_ants = None
		self._world = None
		self._current_step = -1
		brain.Brain.attach_gui(gui)

	def run(self):
		print "Starting engine"
		while True:
			if len(self._messages_from_gui) > 0:
				message = self._messages_from_gui.pop(0)
				print message[0]

				if (message[0]) == "load brain":
					ant_brain = brain.Brain.parse_brain(message[1])
					if (message[2]) == "red":
						self._red_brain = ant_brain
					elif  (message[2]) == "black":
						self._black_brain = ant_brain

				elif (message[0]) == "load world":
					self._world = self._parse_world(message[1])
					self._gui.draw_world(self._world)

				elif (message[0]) == "generate world":
					pass #TODO
				elif (message[0]) == "step world":
					print "STEPPING VORLD"
					if self._current_step == -1:
						for ant in self._red_ants:
							print len(self._red_brain)
							ant._states = self._red_brain
						for ant in self._black_ants:
							print len(self._black_brain)
							ant._states = self._black_brain
						self._current_step = 0
					for ant in self._red_ants:
						self._update_ant(ant)
					for ant in self._black_ants:
						self._update_ant(ant)
					self._current_step += 1
			time.sleep(.001)


	def _make_cell(self, ant=None, rock=False, markers=[], foods=0, hill=None):
		return {"ant":ant, "rock":rock, "markers":markers, "foods":foods, "hill":None}


	def _parse_row_perim(self, row):
		"""Returns a parsed row perimeter in world."""
		parsed = []
		for col in row:
			if col == ROCK:
				parsed.append(self._make_cell(rock=True))
			else:
				self._gui.change_world_details("Expected only #")
				return None

		return parsed


	def _parse_row_cell(self, row, current_row):
		"""Returns a parsed row of cells in world."""
		parsed = []

		if row[0] == ROCK:
			parsed.append(self._make_cell(rock=True))
		else:
			self._gui.change_world_details("Expected perimeter at beginning.")
			return None


		current_col = 2

		for col in row[1:-1]:
			col_count = "col (" + str(current_col) + ") "

			if col == ROCK:
				parsed.append(self._make_cell(rock=True))
			else:
				cell = self._make_cell()

				try:
					if col == RED:
						cell["hill"] = "red"
						cell["ant"] = brain.Brain(self._num_of_ants,self._red_brain,(current_col-1,current_row-1), "red")
						self._num_of_ants += 1
						self._red_ants.append(cell["ant"])
					elif col == BLACK:
						cell["hill"] = "black"
						cell["ant"] = brain.Brain(self._num_of_ants,self._black_brain,(current_col-1,current_row-1), "black")
						self._num_of_ants += 1
						self._black_ants.append(cell["ant"])
					elif col == NONE:
						pass
					elif FOOD[0] <= int(col) <= FOOD[1]:
						cell["foods"] = int(col)
					else:
						self._gui.change_world_details(col_count + "Expected +|-|.|#|1-9")
						return None

				except ValueError as err:
					self._gui.change_world_details(col_count + "Expected a number")
					return None


				parsed.append(cell)

			current_col += 1

		if row[-1] == ROCK:
			parsed.append(self._make_cell(rock=True))
		else:
			self._gui.change_world_details("Expected perimeter at end.")
			return None


		return parsed


	def _update_ant(self, ant):
		"""Returns updated world after each intruction"""

		response = ant.update_brain(self._world)
		x, y = ant._position

		# NOTE: Markers also have a color associated to them
		# e.g. a marker would look like:
		# (1, "red")
		# (4, "black")

		if response[0] == "mark":
			# TODO: Please revise as it was just a quick fix
			# Delete TODO comment if it seems fine
			self._world[x][y]["markers"].append((response[1], ant.color))

		elif response[0] == "unmark":
			# TODO: Please revise as it was just a quick fix
			# Delete TODO comment if it seems fine
			if (response[1], ant.color) in self._world[x][y]["markers"]:
				self._world[x][y]["markers"].remove((response[1], ant.color))

		elif response[0] == "pickup":
			if self._world[x][y]["foods"] > 0:
				ant._has_food = True
				self._world[x][y]["foods"] -= 1

		elif response[0] == "drop":
			if ant._has_food == True:
				ant._has_food = False
				self._world[x][y]["foods"] += 1

		elif response[0] == "move":
			new_x, new_y = self._apply_move(ant._direction, x, y)

			if self._world[new_x][new_y]["rock"] == False and self._world[new_x][new_y]["ant"] == None:
				self._world[x][y]["ant"] = None
				self._world[new_x][new_y]["ant"] = ant
				ant._position = new_x, new_y
				if self._is_alive(ant, new_x, new_y) == False:
					self._world[new_x][new_y]["ant"] = None
					exec("self._" + ant._color + "_ants.remove(ant)")

		elif response[0] == "turn-left":
			if ant._direction < 5:
				ant._direction += 1
			else:
				ant._direction = 0

		elif response[0] == "turn-right":
			if ant._direction > 0:
				ant._direction -= 1
			else:
				ant._direction = 5


	def _apply_move(self, d, x, y):
		"""Returns the correct move"""

		if y % 2 == 0:
			if d == 0:
				x += 1

			elif d == 1:
				y += 1

			elif d == 2:
				x -= 1
				y += 1

			elif d == 3:
				x -= 1

			elif d == 4:
				x -= 1
				y -= 1

			elif d == 5:
				y -= 1

		else:
			if d == 0:
				x += 1

			elif d == 1:
				x += 1
				y += 1

			elif d == 2:
				y += 1

			elif d == 3:
				x -= 1

			elif d == 4:
				y -= 1

			elif d == 5:
				x += 1
				y -= 1

		return x, y


	def _is_alive(self, ant, x, y):
		"""Checks if ant is still alive after move"""

		if y % 2 == 0:
			if sum([0 if self._world[xx][yy]["ant"] == None else 1 for xx, yy in ((x+1,y), (x-1,y), (x-1,y+1),(x,y+1),(x-1,y-1),(x,y-1))]) >= 5:
				return False
		else:
			if sum([0 if self._world[xx][yy]["ant"] == None else 1 for xx, yy in ((x+1,y), (x-1,y), (x+1,y+1),(x,y+1),(x+1,y-1),(x,y-1))]) >= 5:
				return False

		return True


	def parse_grid(self, path):
		"""Returns a complete tokenized grid after parsing."""

	def _parse_world(self, path):
		"""Returns a complete tokenized world after parsing."""
		self._num_of_ants = 0
		self._black_ants = []
		self._red_ants = []

		# Load file in path
		with open(path, "r") as f:
			world = f.readlines()

		# Parse dimensions at the very top
		try:
			num_of_cols = int(world[0])
			num_of_rows = int(world[1])
		except ValueError as err:
			self._gui.change_world_details("Expected a number as dimension.")



		# Remove unnecessary white space.
		rows = [r.split() for r in world[2:]]

		# Check if number of rows are correct.
		if len(rows) != num_of_rows:
			self._gui.change_world_details("line (2) Wrong number of rows.")

		# Check if number of columns in each row are correct.
		for i in xrange(0, len(rows)):
			if len(rows[i]) != num_of_cols:
				msg = "line (" + str(i + 3) + ") " + "Wrong number of columns."
				self._gui.change_world_details(msg)

		final = []

		top_row = self._parse_row_perim(rows[0])
		if top_row == None:
			return None
		final.append(top_row)
		# Parse anything between top and bottom of world
		for i in xrange(1, len(rows) - 1):
			row = self._parse_row_cell(rows[i], i+1)
			if row == None:
				return None
			final.append(row)

		# Parse bottom of world
		bottom_row = self._parse_row_perim(rows[-1])
		if bottom_row == None:
			return None
		final.append(bottom_row)


		self._gui.change_world_details("done")
		return final
