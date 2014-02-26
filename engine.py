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

				if (message[0]) == "load brain":
					ant_brain = brain.Brain.parse_brain(message[1])
					if (message[2]) == "red":
						self._red_brain = ant_brain
					elif  (message[2]) == "black":
						self._black_brain = ant_brain

				if (message[0]) == "load world":
					self._world = self._parse_world(message[1])

				if (message[0]) == "generate world":
					pass #TODO
				if (message[0]) == "step world":
					for ant in self._red_ants:
						self._update_ant(ant)
					for ant in self._black_ants:
						self._update_ant(ant)
			time.sleep(.001)

	BLACK = "-"
	ROCK = "#"
	FOOD = (1, 9)
	NONE = "."
	RED = "+"


	def make_cell(ant=None, rock=False, markers=[], foods=0):
		return {"ant":ant, "rock":rock, "markers":markers, "foods":foods}


	def _parse_row_perim(self, row):
		"""Returns a parsed row perimeter in grid."""
		parsed = []
		for col in row:
			if col == ROCK:
				parsed.append(make_cell(rock=True))
			else:
				self._gui.change_world_details("Expected only #")

		return parsed


	def _parse_row_cell(self, row):
		"""Returns a parsed row of cells in grid."""
		parsed = []

		if row[0] == ROCK:
			parsed.append(make_cell(rock=True))
		else:
			self._gui.change_world_details("Expected perimeter at beginning.")

		current_col = 2

		for col in row[1:-1]:
			col_count = "col (" + str(current_col) + ") "

			if col == ROCK:
				parsed.append(make_cell(rock=True))
			else:
				cell = make_cell()

				try:
					if col == RED:
						cell["ant"] = brain.Brain(self._red_brain)
					elif col == BLACK:
						cell["ant"] = brain.Brain(self._black_brain)
					elif col == NONE:
						pass
					elif FOOD[0] <= int(col) <= FOOD[1]:
						cell["foods"] = int(col)
					else:
						self._gui.change_world_details(col_count + "Expected +|-|.|#|1-9")
				except ValueError as err:
					self._gui.change_world_details(col_count + "Expected a number")

				parsed.append(cell)

			current_col += 1

		if row[-1] == ROCK:
			parsed.append(make_cell(rock=True))
		else:
			self._gui.change_world_details("Expected perimeter at end.")

		return parsed


	def _update_ant(self, ant):
		"""Returns updated world after each intruction"""

		response[0] = ant.update_brain(self._world)
		x, y = ant._position

		if response[0] == "Mark":
			grid[x][y].markers.append(response[1])

		elif response[0] == "Unmark":
			if response[1] in grid[x][y].markers:
				grid[x][y].markers.remove(response[1])

		elif response[0] == "Pickup":
			if grid[x][y].foods > 0:
				ant._has_food = True
				grid[x][y].foods -= 1

		elif response[0] == "Drop":
			if ant._has_food == True:
				ant._has_food = False
				grid[x][y].foods += 1

		elif response[0] == "Move":
			new_x, new_y = self._apply_move(ant, ant._direction, x, y)

			if grid[new_x][new_y].rock == False && grid[new_x][new_y].ant == None:
				grid[x][y].ant = None
				grid[new_x][new_y].ant = ant
				ant._position = new_x, new_y
				if self._is_alive(ant, new_x, new_y) == False:
					grid[new_x][new_y].ant = None
					# remove ant
	
		elif response[0] == "Turn-Left":
			if ant._direction < 5:
				ant._direction += 1
			else:
				ant._direction = 0

		elif response[0] == "Turn-Right":
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
			if sum([0 if grid[xx][yy].ant == None else 1 for xx, yy in ((x+1,y), (x-1,y), (x-1,y+1),(x,y+1),(x-1,y-1),(x,y-1))]) >= 5:
				return False
		else:
			if sum([0 if grid[xx][yy].ant == None else 1 for xx, yy in ((x+1,y), (x-1,y), (x+1,y+1),(x,y+1),(x+1,y-1),(x,y-1))]) >= 5:
				return False

		return True


	def parse_grid(self, path):
		"""Returns a complete tokenized grid after parsing."""

		# Load file in path
		with open(path, "r") as f:
			grid = f.readlines()

		# Parse dimensions at the very top
		try:
			num_of_cols = int(grid[0])
			num_of_rows = int(grid[1])
		except ValueError as err:
			self._gui.change_world_details("Expected a number as dimension.")

		# Remove unnecessary white space.
		rows = [r.split() for r in grid[2:]]

		# Check if number of rows are correct.
		if len(rows) != num_of_rows:
			self._gui.change_world_details("line (2) Wrong number of rows.")

		# Check if number of columns in each row are correct.
		for i in xrange(0, len(rows)):
			if len(rows[i]) != num_of_cols:
				msg = "line (" + str(i + 3) + ") " + "Wrong number of columns."
				self._gui.change_world_details(msg)

		final = []

		final.append(_parse_row_perim(rows[0]))

		# Parse anything between top and bottom of grid
		for i in xrange(1, len(rows) - 1):
			final.append(_parse_row_cell(rows[i]))

		# Parse bottom of grid
		final.append(_parse_row_perim(rows[-1]))

		return final
