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

	def run(self):
		print "Starting engine"
		while True:
			if len(self._messages_from_gui) > 0:
				message = self._messages_from_gui.pop(0)
				print message[0]

				if (message[0]) == "load_brain":
					ant_brain = brain.Brain.parse_brain(message[1])
					if (message[2]) == "red":
						self._red_brain = ant_brain
					elif  (message[2]) == "black":
						self._black_brain = ant_brain

				if (message[0]) == "load world":
					print "loading world"
					self._world = self._parse_world(message[1])

				if (message[0]) == "generate_world":
					pass #TODO
				if (message[0]) == "step_world":
					pass
			time.sleep(.001)


	def _make_cell(self, ant=None, rock=False, markers=[], foods=0):
		return {"ant":ant, "rock":rock, "markers":markers, "foods":foods}


	def _parse_row_perim(self, row):
		"""Returns a parsed row perimeter in grid."""
		parsed = []
		for col in row:
			if col == ROCK:
				parsed.append(self._make_cell(rock=True))
			else:
				self._gui.change_world_details("Expected only #")
				return None

		return parsed


	def _parse_row_cell(self, row, current_row):
		"""Returns a parsed row of cells in grid."""
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
						cell["ant"] = brain.Brain(self._num_of_ants,self._red_brain,(current_col-1,current_row-1), "red")
						self._num_of_ants += 1
						self._red_ants.append(cell.["ant"])
					elif col == BLACK:
						cell["ant"] = brain.Brain(self._num_of_ants,self._black_brain,(current_col-1,current_row-1), "black")
						self._num_of_ants += 1
						self._black_ants.append(cell.["ant"])
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


	def _parse_world(self, path):
		"""Returns a complete tokenized grid after parsing."""
		self._num_of_ants = 0
		self._black_ants = None
		self._red_ants = None
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

		top_row = self._parse_row_perim(rows[0])
		if top_row == None:
			return None
		final.append(top_row)
		# Parse anything between top and bottom of grid
		for i in xrange(1, len(rows) - 1):
			row = self._parse_row_cell(rows[i], i+1)
			if row == None:
				return None
			final.append(row)

		# Parse bottom of grid
		bottom_row = self._parse_row_perim(rows[-1])
		if bottom_row == None:
			return None
		final.append(bottom_row)


		self._gui.change_world_details("done")
		return final
