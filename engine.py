import brain
from threading import Thread
import time

class Engine(Thread):

    BLACK = "-"
    ROCK = "#"
    FOOD = (1, 9)
    NONE = "."
    RED = "+"

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
            time.sleep(.001)


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

