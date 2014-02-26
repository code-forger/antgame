import random

'''
Sense sensedir st1 st2 cond     Go to state st1 if cond holds in sensedir;
        and to state st2 otherwise.
Mark i st       Set mark i in current cell and go to st.
Unmark i st     Clear mark i in current cell and go to st.
PickUp st1 st2      Pick up food from current cell and go to st1;
        go to st2 if there is no food in the current cell.
Drop st     Drop food in current cell and go to st.
Turn lr st      Turn left or right and go to st.
Move st1 st2        Move forward and go to st1;
        go to st2 if the cell ahead is blocked.
Flip p st1 st2      Choose a random number x from 0 to p-1;
        go to st1 if x=0 and st2 otherwise.
        '''


class Brain:
    def __init__(self, brain_id, states, position, color):
        self.brain_id = brain_id
        self._state = 0
        self._states = states
        self._has_food = False
        self._direction = 0
        self._position = position
        self._rest_time = 0
        self._color = color
        self._rand_gen = make_rand_gen(random.randint(0, 10000))

    @property
    def color(self):
        return self._color

    @property
    def rest_time(self):
        return self._rest_time

    @property
    def has_food(self):
        return self._has_food

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    def update_brain(self, world):
        """
        Changes the state (excluding position) of brain, according to
        current instruction.
        """
        instruction = self._states[self._state]

        if self._rest_time > 0:
            self._rest_time -= 1
            return ["None"]

        move = []

        if instruction[0] == "Sense":
            pos = self._position
            dir = self._direction
            color = self._color

            sensed_pos = sensed_cell(pos, dir, instruction)

            if cell_matches(sensed_pos, instruction[3:], color):
                self._state = instruction[1]
            else:
                self._state = instruction[2]

            move = ["None"]
        elif instruction[0] == "Mark":
            move = instruction
            self._state = instruction[1]
        elif instruction[0] == "Unmark":
            move = instruction
            self._state = instruction[1]
        elif instruction[0] == "PickUp":
            x, y = self.position

            if self.has_food or world[x][y]["foods"] == 0:
                self._state = instruction[2]
            else:
                move = [instruction[0]]
                self._state = instruction[1]
        elif instruction[0] == "Drop":
            move = [instruction[0]]
            self._state = instruction[1]
        elif instruction[0] == "Turn":
            move = [instruction[0]+"-"+instruction[1]]
            self._state = instruction[1]
        elif instruction[0] == "Move":
            new_pos = adjacent_cell(self.position, self._direction)
            nx, ny = new_pos
            if rocky(new_pos) or world[nx][ny]["ant"] is not None:
                self._state = instruction[2]
            else:
                self._state = instruction[1]
                self._rest_time = 14
        elif instruction[0] == "Flip":
            rand_n = self._rand_gen(instruction[1])
            rand_state = instruction[2] if rand_n == 0 else instruction[3]
            self._state = rand_state
            move = ["None"]

        return move

    def attach_gui(gui):
        Brain._gui = gui

    @classmethod
    def parse_brain(cls, filename):
        instructions = []
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
                    instructions.append([words[0], int(words[1]), int(words[2])])
                elif words[0] == "Unmark":
                    if int(words[1]) < 0 or int(words[1]) > num_of_lines:
                        Brain.gui.show_brain_checked("The second word on line: " + (i + 1) + " is " + words[1] + " and should be between 0 and the number of states.")
                        return None
                    if int(words[2]) < 0 or int(words[2]) > num_of_lines:
                        Brain.gui.show_brain_checked("The third word on line: " + (i + 1) + " is " + words[2] + " and should be between 0 and the number of states.")
                        return None
                    instructions.append([words[0], int(words[1]), int(words[2])])
                elif words[0] == "PickUp":
                    if int(words[1]) < 0 or int(words[1]) > num_of_lines:
                        Brain.gui.show_brain_checked("The second word on line: " + (i + 1) + " is " + words[1] + " and should be between 0 and the number of states.")
                        return None
                    if int(words[2]) < 0 or int(words[2]) > num_of_lines:
                        Brain.gui.show_brain_checked("The third word on line: " + (i + 1) + " is " + words[2] + " and should be between 0 and the number of states.")
                        return None
                    instructions.append([words[0], int(words[1]), int(words[2])])
                elif words[0] == "Drop":
                    if int(words[1]) < 0 or int(words[1]) > num_of_lines:
                        Brain.gui.show_brain_checked("The second word on line: " + (i + 1) + " is " + words[1] + " and should be between 0 and the number of states.")
                        return None
                    instructions.append([words[0], int(words[1])])
                elif words[0] == "Turn":
                    if (words[1] not in ["Left", "Right"]):
                        Brain.gui.show_brain_checked("The second word on line: " + (i + 1) + " is " + words[1] + " and should be either 'Left' or 'Right'.")
                        return None
                    instructions.append([words[0], words[1]])
                elif words[0] == "Move":
                    if int(words[1]) < 0 or int(words[1]) > num_of_lines:
                        Brain.gui.show_brain_checked("The second word on line: " + (i + 1) + " is " + words[1] + " and should be between 0 and the number of states.")
                        return None
                    if int(words[2]) < 0 or int(words[2]) > num_of_lines:
                        Brain.gui.show_brain_checked("The third word on line: " + (i + 1) + " is " + words[2] + " and should be between 0 and the number of states.")
                        return None
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
                    instructions.append([words[0], int(words[1]), int(words[2]), int(words[3])])
                else:
                    Brain.gui.show_brain_checked("The first word on line: " + (i + 1) + " is " + words[0] + " and should be  either 'Sense', 'Mark', 'Unmark', 'PickUp', 'Drop', 'Turn', 'Move', 'Flip'")
        Brain.gui.show_brain_checked("The file is correct.")
        return instrucions


#################################################
# Convenient functions for ant brain simulation #
#################################################


def adjacent_cell(pos, dir):
    """Returns the adjacent cell of position, depending on the direction."""
    x, y = pos

    even = (y % 2 == 0)

    next_dir = {}
    next_dir[0] = (x+1, y)
    next_dir[1] = (x, y+1) if even else (x+1, y+1)
    next_dir[2] = (x-1, y+1) if even else (x, y+1)
    next_dir[3] = (x-1, y)
    next_dir[4] = (x-1, y-1) if even else (x, y-1)
    next_dir[5] = (x, y-1) if even else (x+1, y-1)

    return next_dir[dir]


def sensed_cell(pos, dir, sense_dir):
    """Returns the coordinates of the cell being sensed."""
    cell = {}
    cell["Here"] = pos
    cell["Ahead"] = adjacent_cell(pos, dir)
    cell["LeftAhead"] = adjacent_cell(pos, turn("Left", dir))
    cell["RightAhead"] = adjacent_cell(pos, turn("Right", dir))

    return cell[sense_dir]


def turn(dir):
    """Returns the new turned direction."""
    next_dir = {}
    next_dir["Left"] = (d+5) % 6
    next_dir["Right"] = (d+1) % 6

    return next_dir[dir]


def other_color(color):
    """Returns the opposite color of the ant."""
    opposite_color = {}
    opposite_color["Red"] = "Black"
    opposite_color["Black"] = "Red"

    return opposite_color[color]


def rocky(world, pos):
    """Returns True if pos is rocky."""
    x, y = pos
    return world[x][y]['rock']


def check_marker_at(world, pos, color, marker):
    """Returns True if marker of color c is set in pos."""
    x, y = pos
    return any(m == marker and c == color for m, c in world[x][y]["markers"])


def any_marker_at(world, pos, color):
    """Returns True if ANY marker of color c is set in pos."""
    x, y = pos
    return any(c == color for m, c in world[x][y]["markers"])


def cell_matches(world, pos, cond, color):
    """
    Takes a position p, a condition cond, and a color c
    (the color of the ant that is doing the sensing), and
    checks whether cond holds at p.
    """
    if rocky(world, pos):
        return True if cond == "Rock" else False

    x, y = pos
    ant = world[x][y]["ant"]

    if ant is not None:
        ant_type = {}
        ant_type["Friend"] = (ant.color == color)
        ant_type["Foe"] = not ant_type["Friend"]
        ant_type["FriendWithFood"] = ant_type["Friend"] and ant.has_food
        ant_type["FoeWithFood"] = ant_type["Foe"] and ant.has_food

        return ant_type[cond[0]]

    other_type = {}
    other_type["Food"] = world[x][y]["foods"] > 0
    other_type["Rock"] = False
    other_type["Marker"] = check_marker_at(world, pos, color, cond[1])
    other_type["FoeMarker"] = any_marker_at(world, pos, other_color(color))
    other_type["Home"] = (world[x][y]["anthill"] == color)
    other_type["FoeHome"] = (world[x][y]["anthill"] == other_color(color))

    return other_type[cond[0]]


def make_rand_gen(seed):
    """Returns a predetermined pseudo rand gen based on seed."""
    S = []
    S.append(seed)

    for i in xrange(0, 4):
        S.append(S[-1] * 22695477 + 1)

    def randomint(n):
        if n > 0:
            x = (S[-1] / 65536) % n
            S.append(S[-1] * 22695477 + 1)

            return int(x % n)

    return randomint
