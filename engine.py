import brain
from threading import Thread
import time

import world_gen

BLACK = "-"
ROCK = "#"
FOOD = (1, 9)
NONE = "."
RED = "+"

class Engine(Thread):
	def __init__(self, id, messages_from_gui, messages_to_renderer, gui):
		Thread.__init__(self)
		self._messages_from_gui = messages_from_gui
		self._messages_to_renderer = messages_to_renderer

		self.daemon = True
		self._gui = gui

		self._black_brain = None
		self._red_brain = None
		self._black_ants = None
		self._red_ants = None
		self._world = None
		self._current_step = "-1"
		brain.Brain.attach_gui(gui)
		self._all_ants = []
		self._ordered = []

		self._game_stats = {"current_step_of_game":0,
						   "red_alive":0,
						   "black_alive":0,
						   "red_dead_redemption":0,
						   "black_dead":0,
						   "red_carrying":0,
						   "black_carrying":0,
						   "red_stored":0,
						   "black_stored":0}
		self.id = str(id)

	def do(self):
		for a in self._ordered:
			#x,y = a._position
			#if self._is_alive(a,x,y):
			if a.alive:
				self._update_ant(a)

		#for x in self._world:
		#	for cell in x:
		#		if cell["ant"] != None:
		#			self._update_ant(cell["ant"])


	def run(self):
		while True:
			if len(self._messages_from_gui) > 0:
				message = self._messages_from_gui.pop(0)

				if (message[0]) == "load brain":
					self._current_step = -1
					ant_brain = brain.Brain.parse_brain(message[1], message[2])
					if (message[2]) == "red":
						#print "engine ", self.id, " has received its red brain"
						self._red_brain = ant_brain
					elif  (message[2]) == "black":
						#print "engine ", self.id, " has received its black brain"
						self._black_brain = ant_brain
					print "DONE BRAIN"

				elif (message[0]) == "load world":
					#try:
					self._current_step = -1
					self._world = self._parse_world(message[1])
					self._messages_to_renderer.append(["draw_world", self._world, self.id])
					self._game_stats["red_alive"] = len(self._red_ants)
					self._game_stats["black_alive"] = len(self._black_ants)
					self._all_ants = self._red_ants[:]
					self._all_ants.extend(self._black_ants)
					try:
						self._gui.change_game_stats(self._game_stats)
					except Exception as e:
						print "DEFFO THIS"
					#except Exception as e:
						#self._world = None
					print "DONE WORLD", self._world is None


				elif (message[0]) == "generate world":
					try:
						self._current_step = -1
						world = world_gen.gen_world(150, 150)
						world_gen.save_world(world, "generated.world")
						self._world = self._parse_world("generated.world")
						self._messages_to_renderer.append(["draw_world", self._world, self.id])
						self._game_stats["red_alive"] = len(self._red_ants)
						self._game_stats["black_alive"] = len(self._black_ants)
						self._all_ants = self._red_ants[:]
						self._all_ants.extend(self._black_ants)
						try:
							self._gui.change_game_stats(self._game_stats)
						except Exception as e:
							pass
					except Exception as e:
						self._world = None
				elif (message[0]) == "step world":
					self.step_world(message)	

			time.sleep(.001)

	def step_world(self, message):
		self._messages_from_gui[:] = [m for m in self._messages_from_gui if m != "step world"]
		old_stats = dict(self._game_stats)
		if self._current_step == -1:
			for ant in self._red_ants:
				ant._states = self._red_brain
			for ant in self._black_ants:
				ant._states = self._black_brain
			skipper = 0
			for i in range(len(self._all_ants)):
				steped = False
				while (True):
					for a in self._all_ants:
						if a.brain_id == i+skipper:
							self._ordered.append(a)
							steped = True
							break
					if steped == True:
						break
					else:
						skipper+=1
			self._current_step = 0
		elif self._current_step == 30000:
			self._gui.change_game_stats(self._game_stats)
		else:
			self.do()
			if old_stats == self._game_stats:
				self._current_step += 1
				self._game_stats["current_step_of_game"] = self._current_step
				self._messages_to_renderer.append(["draw_world", self._world, self.id])
				try:
					self._gui.change_game_stats(self._current_step)
				except Exception as e:
						pass	
			else:
				self._current_step += 1
				self._game_stats["current_step_of_game"] = self._current_step
				self._messages_to_renderer.append(["draw_world", self._world, self.id])
				try:	
					self._gui.change_game_stats(self._game_stats)
				except Exception as e:
						pass


	def _make_cell(self, ant=None, rock=False, markers=[], foods=0, hill=None):
		return {"ant":ant, "rock":rock, "markers":[], "foods":foods, "hill":None}


	def _parse_row_perim(self, row):
		"""Returns a parsed row perimeter in world."""
		parsed = []
		for col in row:
			if col == ROCK:
				parsed.append(self._make_cell(rock=True))
			else:
				try:
					self._gui.change_world_details("Expected only #")
				finally:
					return None

		return parsed


	def _parse_row_cell(self, row, current_row):
		"""Returns a parsed row of cells in world."""
		parsed = []

		if row[0] == ROCK:
			parsed.append(self._make_cell(rock=True))
		else:
			try:
				self._gui.change_world_details("Expected perimeter at beginning.")
			finally:
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
						self._foods += int(col)
					else:
						try:
							self._gui.change_world_details(col_count + "Expected +|-|.|#|1-9")
						finally:
							return None

				except ValueError as err:
					try:
						self._gui.change_world_details(col_count + "Expected a number")
					finally:
						return None


				parsed.append(cell)

			current_col += 1

		if row[-1] == ROCK:
			parsed.append(self._make_cell(rock=True))
		else:
			try:
				self._gui.change_world_details("Expected perimeter at end.")
			finally:
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
			if (response[1], ant.color) not in self._world[x][y]["markers"]:
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
				self._game_stats[ant.color + "_carrying"] += 1

		elif response[0] == "drop":
			if ant._has_food == True:
				ant._has_food = False

				self._world[x][y]["foods"] += 1
				self._game_stats[ant.color + "_carrying"] -= 1
				if self._world[x][y]["hill"]:
					self._game_stats[self._world[x][y]["hill"] + "_stored"] += 1


		elif response[0] == "move":
			new_x, new_y = self._apply_move(ant._direction, x, y)
			self._world[x][y]["ant"] = None
			self._world[new_x][new_y]["ant"] = ant
			ant._position = new_x, new_y

			for a in self._get_adj(ant, new_x, new_y):
				x,y = a._position
				if not self._is_alive(a,x,y):
					a.alive = False
					self._world[x][y]["foods"] += 3
					self._world[x][y]["ant"] = None
					if (a._color == "red"):
						self._game_stats["red_dead_redemption"] += 1
						self._game_stats["red_alive"] -= 1
					else:
						self._game_stats["black_dead"] += 1
						self._game_stats["black_alive"] -= 1

			x,y = ant._position
			if not self._is_alive(ant,x,y):
				ant.alive = False
				self._world[x][y]["foods"] += 3
				self._world[x][y]["ant"] = None
				if (ant._color == "red"):
					self._game_stats["red_dead_redemption"] += 1
					self._game_stats["red_alive"] -= 1
				else:
					self._game_stats["black_dead"] += 1
					self._game_stats["black_alive"] -= 1

		elif response[0] == "turn-right":
			if ant._direction < 5:
				ant._direction += 1
			else:
				ant._direction = 0

		elif response[0] == "turn-left":
			if ant._direction > 0:
				ant._direction -= 1
			else:
				ant._direction = 5

	def _get_adj(self, ant, x,y):
		ants = []
		if y % 2 == 0:
			for xx, yy in ((x+1,y), (x-1,y), (x-1,y+1),(x,y+1),(x-1,y-1),(x,y-1)):
				if self._world[xx][yy]["ant"] != None:
					ants.append(self._world[xx][yy]["ant"])
		else:
			for xx, yy in ((x+1,y), (x-1,y), (x+1,y+1),(x,y+1),(x+1,y-1),(x,y-1)):
				if self._world[xx][yy]["ant"] != None:
					ants.append(self._world[xx][yy]["ant"])
		return ants


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
		count = 0
		if y % 2 == 0:
			for xx, yy in ((x+1,y), (x-1,y), (x-1,y+1),(x,y+1),(x-1,y-1),(x,y-1)):
				if self._world[xx][yy]["ant"] == None:
					count += 1
				elif self._world[xx][yy]["ant"].color == ant.color:
					count += 1
				if count >= 2:
					return True
		else:
			for xx, yy in ((x+1,y), (x-1,y), (x+1,y+1),(x,y+1),(x+1,y-1),(x,y-1)):
				if self._world[xx][yy]["ant"] == None:
					count += 1
				elif self._world[xx][yy]["ant"].color == ant.color:
					count += 1
				if count >= 2:
					return True
		return False

	def _parse_world(self, path):
		"""Returns a complete tokenized world after parsing."""
		self._foods = 0
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

		try:
			self._gui.change_world_details("File: " + path + "\n" + 
										   "Size: 150 * 150\n" + 
										   "Ants: " + str(len(self._red_ants) + len(self._black_ants)) + "\n"
										   "Food: " + str(self._foods))
		finally:

			return zip(*final)


if __name__ == "__main__":

	class RANDOM():
	    def __init__(self, seed):
	        RANDOM.S = []
	        RANDOM.S.append(seed)

	        for i in xrange(0, 4):
	            RANDOM.S.append(RANDOM.S[-1] * 22695477 + 1)

	def get_random(cls, n):
	    if n > 0:
	        x = (RANDOM.S[-1] / 65536) % 16384
	        RANDOM.S[-1] = RANDOM.S[-1] * 22695477 + 1

	        return int(x % n)
	RANDOM(12345)
	brain.Brain._rand_gen = get_random
	def get_state(world, expected):
		for i, x in enumerate(world):
			for j, c in enumerate(x):
				cell = world[j][i]
				string = ""
				string += "cell ("+str(j)+", "+str(i)+"): "
				if cell["rock"]:
					string += "rock"
				if cell["foods"] > 0:
					string += str(cell["foods"])+" food; "
				if cell["hill"] is not None:
					string += cell["hill"]+" hill; "
				red = []
				black = []
				for m in cell["markers"]:
					if m[1] == "red":
						red.append(m[0])
					else:
						black.append(m[0])
				if len(red) > 0:
					string += "red marks: "
					red.sort()
					for x in red:
						string += str(x)
					string += "; "

				if len(black) > 0:
					string += "black marks: "
					black.sort()
					for x in black:
						string += str(x)
					string += "; "

				if cell["ant"] is not None:
					a = cell["ant"]
					h = "0"
					if a._has_food:
						h = "1"
					string += a._color+" ant of id "+str(a.brain_id)+", dir "+str(a._direction)+", food "+h+", state "+str(a._state)+", resting "+str(a._rest_time)+""
				string += "\n"
				string == expected[j + i*len(world)]
				#if j == 5 and i == 2:
				#	print "!"
				#	print "exp:",expected[j + i*len(world)]
				#	print "got:",string
				#	print "x"
				if not string.strip() == expected[j + i*len(world)].strip():
					print "NOOOOOOOOO"
					print ""
					print "exp:",expected[j + i*len(world)]
					print "got:",string
					print ""
					sys.exit()
	print "this"
	messages_to_engine = []
	_messages_to_runner = messages_to_runner = []
	messages_between_engine_and_renderer = []
	game_engine = Engine(-1,messages_to_engine, messages_between_engine_and_renderer, None)
	game_engine.start()

	world_renderer = renderer.Renderer(messages_between_engine_and_renderer)
	world_renderer.start()

	messages_to_engine.append(["load world", "tester.world"])
	messages_to_engine.append(["load brain", "tester.brain", "red"])
	messages_to_engine.append(["load brain", "tester.brain", "black"])
	print "this"
	time.sleep(1)	

	expected = []

	with open("dump.all") as f:
		while (True):
			step = []
			while (True):
				l = f.readline()
				#print l[:3], l[:3] == "..."
				if l == "" or l[:3] == "...":
					break
				step.append(l.strip())
			if len(step) == 0:
				break
			expected.append(step)


	print game_engine._current_step < 100
	game_engine.step_world([""])
	time.sleep(.1)	

	while game_engine._current_step < 10000:
		print game_engine._current_step
		game_engine.step_world([""])
		get_state(game_engine._world,expected[game_engine._current_step])
	
	time.sleep(1000)	