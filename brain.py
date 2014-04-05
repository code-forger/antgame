import random
from memory_profiler import memory_usage
'''
sense sensedir st1 st2 cond     Go to state st1 if cond holds in sensedir;
        and to state st2 otherwise.
mark i st       Set mark i in current cell and go to st.
unmark i st     Clear mark i in current cell and go to st.
pickup st1 st2      Pick up food from current cell and go to st1;
        go to st2 if there is no food in the current cell.
drop st     drop food in current cell and go to st.
turn lr st      turn left or right and go to st.
move st1 st2        move forward and go to st1;
        go to st2 if the cell ahead is blocked.
flip p st1 st2      Choose a random number x from 0 to p-1;
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
        self.alive = True
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
        #mem_usage = memory_usage(-1, interval=.01, timeout=.01)
        #print mem_usage
        instruction = self._states[self._state]

        move = ["none"]

        if self._rest_time > 0:
            self._rest_time -= 1
            move = ["none"]      
        elif instruction[0] == "sense":
            pos = self._position
            dir = self._direction
            color = self._color

            sensed_pos = sensed_cell(pos, dir, instruction[1])

            if cell_matches(world, sensed_pos, instruction[4:], color):
                self._state = instruction[2]
            else:
                self._state = instruction[3]

            move = ["none"]

        elif instruction[0] in ["mark", "unmark"]:
            move = instruction[:-1]
            self._state = instruction[2]
        elif instruction[0] == "pickup":
            x, y = self.position

            if self.has_food or world[x][y]["foods"] == 0:
                move = ["none"]
                self._state = instruction[2]
            else:
                move = [instruction[0]]
                self._state = instruction[1]
        elif instruction[0] == "drop":
            move = [instruction[0]] if self.has_food else ["none"]
            self._state = instruction[1]
        elif instruction[0] == "turn":
            move = [instruction[0]+"-"+instruction[1]]
            self._state = instruction[2]
        elif instruction[0] == "move":
            new_pos = adjacent_cell(self.position, self._direction)
            nx, ny = new_pos
            if rocky(world, new_pos) or world[nx][ny]["ant"] is not None:
                move = ["none"]
                self._state = instruction[2]
            else:
                self._state = instruction[1]
                self._rest_time = 14
                move = [instruction[0]]
        elif instruction[0] == "flip":
            rand_n = self._rand_gen(instruction[1])
            rand_state = instruction[2] if rand_n == 0 else instruction[3]
            self._state = rand_state
            move = ["none"]
        return move

    @classmethod
    def attach_gui(cls, gui):
        cls.gui = gui

    @classmethod
    def parse_brain(cls, filename, color):
        instructions = []

        with open(filename) as brain_file:

            file_content = brain_file.readlines()
            num_of_lines = len(file_content)
            for i, line in enumerate(file_content):
                line = line.strip()

                # Split instructions into strings and remove their case sensitivity.
                words = [w.lower() for w in line.split(" ")]

                if words[0] == "sense":
                    if (words[1] not in ["here", "ahead", "leftahead", "rightahead"]):
                        Brain.gui.change_brain_details("The second word on line: " + str(i + 1) + " is " + words[1] + " and should be either 'Here', 'Ahead', 'LeftAhead' or 'RightAhead'.",color)
                        return None
                    if int(words[2]) < 0 or int(words[2]) > num_of_lines:
                        Brain.gui.change_brain_details("The third word on line: " + str(i + 1) + " is " + str(words[2]) + " and should be between 0 and the number of states.",color)
                        return None
                    if int(words[3]) < 0 and int(words[3]) > num_of_lines:
                        Brain.gui.change_brain_details("The third word on line: " + str(i + 1) + " is " + str(words[3]) + " and should be between 0 and the number of states.",color)
                        return None
                    if (words[4] not in ["friend", "foe", "friendwithfood", "foewithfood", "food", "rock", "marker", "foemarker", "home", "foehome"]):
                        Brain.gui.change_brain_details("The fifth word on line: " + str(i + 1) + " is " + words[4] + " and should be either 'Friend', 'Foe', 'FriendWithFood', 'FoewithFood', 'Food', 'Rock', 'marker', 'Foemarker', 'Home', 'ForHome'",color)
                        return None
                    if words[4] == "marker" and int(words[5]) > 6 and int(words[5]) < 0:
                        Brain.gui.change_brain_details("The 6th word on line: " + str(i + 1) + " is " + str(words[4]) + " and should be between 1 and 6",color)
                        return None
                    if words[4] == "marker":
                        instructions.append([words[0], words[1], int(words[2]), int(words[3]), words[4], int(words[5])])
                    else:
                        instructions.append([words[0], words[1], int(words[2]), int(words[3]), words[4]])
                elif words[0] == "mark":
                    if int(words[1]) < 0 or int(words[1]) > num_of_lines:
                        Brain.gui.change_brain_details("The second word on line: " + str(i + 1) + " is " + str(words[1]) + " and should be between 0 and the number of states.",color)
                        return None
                    if int(words[2]) < 0 or int(words[2]) > num_of_lines:
                        Brain.gui.change_brain_details("The third word on line: " + str(i + 1) + " is " + str(words[2]) + " and should be between 0 and the number of states.",color)
                        return None
                    instructions.append([words[0], int(words[1]), int(words[2])])
                elif words[0] == "unmark":
                    if int(words[1]) < 0 or int(words[1]) > num_of_lines:
                        Brain.gui.change_brain_details("The second word on line: " + str(i + 1) + " is " + str(words[1]) + " and should be between 0 and the number of states.",color)
                        return None
                    if int(words[2]) < 0 or int(words[2]) > num_of_lines:
                        Brain.gui.change_brain_details("The third word on line: " + str(i + 1) + " is " + str(words[2]) + " and should be between 0 and the number of states.",color)
                        return None
                    instructions.append([words[0], int(words[1]), int(words[2])])
                elif words[0] == "pickup":
                    if int(words[1]) < 0 or int(words[1]) > num_of_lines:
                        Brain.gui.change_brain_details("The second word on line: " + str(i + 1) + " is " + str(words[1]) + " and should be between 0 and the number of states.",color)
                        return None
                    if int(words[2]) < 0 or int(words[2]) > num_of_lines:
                        Brain.gui.change_brain_details("The third word on line: " + str(i + 1) + " is " + str(words[2]) + " and should be between 0 and the number of states.",color)
                        return None
                    instructions.append([words[0], int(words[1]), int(words[2])])
                elif words[0] == "drop":
                    if int(words[1]) < 0 or int(words[1]) > num_of_lines:
                        Brain.gui.change_brain_details("The second word on line: " + str(i + 1) + " is " + str(words[1]) + " and should be between 0 and the number of states.",color)
                        return None
                    instructions.append([words[0], int(words[1])])
                elif words[0] == "turn":
                    if (words[1] not in ["left", "right"]):
                        Brain.gui.change_brain_details("The second word on line: " + str(i + 1) + " is " + str(words[1]) + " and should be either 'Left' or 'Right'.",color)
                        return None

                    if int(words[2]) < 0 or int(words[2]) > num_of_lines:
                        Brain.gui.change_brain_details("The second word on line: " + str(i + 1) + " is " + words[2] + " and should be between 0 and the number of states.",color)
                        return None

                    instructions.append([words[0], words[1], int(words[2])])
                elif words[0] == "move":
                    if int(words[1]) < 0 or int(words[1]) > num_of_lines:
                        Brain.gui.change_brain_details("The second word on line: " + str(i + 1) + " is " + words[1] + " and should be between 0 and the number of states.",color)
                        return None
                    if int(words[2]) < 0 or int(words[2]) > num_of_lines:
                        Brain.gui.change_brain_details("The third word on line: " + str(i + 1) + " is " + words[2] + " and should be between 0 and the number of states.",color)
                        return None
                    instructions.append([words[0], int(words[1]), int(words[2])])
                elif words[0] == "flip":
                    if int(words[1]) < 0:
                        Brain.gui.change_brain_details("The second number on line: " + str(i + 1) + " is " + words[1] + " and should be a number no less than 0.",color)
                        return None
                    if int(words[2]) < 0 or int(words[2]) > num_of_lines:
                        Brain.gui.change_brain_details("The third word on line: " + str(i + 1) + " is " + words[2] + " and should be between 0 and the number of states.",color)
                        return None
                    if int(words[3]) < 0 or int(words[3]) > num_of_lines:
                        Brain.gui.change_brain_details("The fourth word on line: " + str(i + 1) + " is " + words[3] + " and should be between 0 and the number of states.",color)
                        return None
                    instructions.append([words[0], int(words[1]), int(words[2]), int(words[3])])
                else:
                    Brain.gui.change_brain_details("The first word on line: " + str(i + 1) + " is " + words[0] + " and should be  either 'sense', 'mark', 'unmark', 'pickup', 'drop', 'turn', 'move', 'flip'",color)
                    return None
        Brain.gui.change_brain_details("File: " + filename + "\n" +
                                       "States: " + str(len(instructions)), brain=color)
        return instructions


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
    cell["here"] = pos
    cell["ahead"] = adjacent_cell(pos, dir)
    cell["leftahead"] = adjacent_cell(pos, turn("left", dir))
    cell["rightahead"] = adjacent_cell(pos, turn("right", dir))

    return cell[sense_dir]

   
def turn(lr, dir):
    """Returns the new turned direction."""
    next_dir = {}
    next_dir["left"] = (dir+5) % 6
    next_dir["right"] = (dir+1) % 6
    return next_dir[lr]

 
def other_color(color):
    """Returns the opposite color of the ant."""
    opposite_color = {}
    opposite_color["red"] = "black"
    opposite_color["black"] = "red"

    return opposite_color[color]

   
def rocky(world, pos):
    """Returns True if pos is rocky."""
    x, y = pos
    return world[x][y]["rock"]
   
def check_marker_at(world, pos, color, marker):
    """Returns True if marker of color c is set in pos."""
    x, y = pos
    return any(m[0] == marker and m[1] == color for m in world[x][y]["markers"])

   
def any_marker_at(world, pos, color):
    """Returns True if ANY marker of color c is set in pos."""
    x, y = pos
    return any(m[1] == color for m in world[x][y]["markers"])

 
def cell_matches(world, pos, cond, color):
    """
    Takes a position p, a condition cond, and a color c
    (the color of the ant that is doing the sensing), and
    checks whether cond holds at p.
    """
    if rocky(world, pos):
        return True if cond[0] == "rock" else False

    x, y = pos
    ant = world[x][y]["ant"]

    if cond[0] == "marker":
        return check_marker_at(world, pos, color, cond[1])

    other_type = {}
    other_type["food"] = world[x][y]["foods"] > 0
    other_type["rock"] = False
    other_type["foemarker"] = any_marker_at(world, pos, other_color(color))
    other_type["home"] = (world[x][y]["hill"] == color)
    other_type["foehome"] = (world[x][y]["hill"] == other_color(color))

    other_type["friend"] = False
    other_type["foe"] = False
    other_type["friendwithfood"] = False
    other_type["foewithfood"] = False

    if ant is not None and cond[0] not in other_type:
        ant_type = {}
        ant_type["friend"] = (ant.color == color)
        ant_type["foe"] = not ant_type["friend"]
        ant_type["friendwithfood"] = ant_type["friend"] and ant.has_food
        ant_type["foewithfood"] = ant_type["foe"] and ant.has_food

        return ant_type[cond[0]]

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
            S[-1] = S[-1] * 22695477 + 1

            return int(x % n)

    return randomint
