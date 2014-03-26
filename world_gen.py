import engine as eg
import random as rand
import collections

from brain import adjacent_cell


ANTHILL_SIDES_LEN = 7
ANTHILL_TOTAL_NUM_LINES = ((ANTHILL_SIDES_LEN * 2) - 1)

FOODBLOB_SIDES_LEN = 5


def gen_world(dimensions):
    NUM_ROWS, NUM_COLS = dimensions

    world = collections.deque()

    # Generate top perimeter.
    world.append([eg.ROCK] * NUM_COLS)

    # In between top and bottom perimeters, generate a clean world.
    # (all non-perimeter cells are clear)
    for i in xrange(NUM_ROWS - 2):
        world.append([eg.ROCK] + ([eg.NONE] * (NUM_COLS - 2)) + [eg.ROCK])

    # Generate bottom perimeter.
    world.append([eg.ROCK] * NUM_COLS)

    # Apply red anthill in world.
    randomly_apply_anthill(world, eg.RED)

    # Apply black anthill in world.
    randomly_apply_anthill(world, eg.BLACK)

    # Apply food blocks in world.
    randomly_apply_foodblob(world)

    # Apply rocks in world.
    randomly_apply_rocks(world)

    world.appendleft([str(NUM_ROWS)])
    world.appendleft([str(NUM_COLS)])

    return world


def randomly_apply_anthill(world, color):
    anthill_insert_to_world_successful = False
    available_spaces = get_available_spaces(world)
    rand.shuffle(available_spaces)
    for space in available_spaces:
        if anthill_space_is_viable(world, space):
            apply_anthill(world, space, color)
            anthill_insert_to_world_successful = True

        if anthill_insert_to_world_successful:
            break


def anthill_space_is_viable(world, space):
    if not anthill_border_is_viable(world, space):
        return False

    # Get the very topmost leftmost of anthill
    x, y = space
    for i in xrange(ANTHILL_SIDES_LEN - 1):
        x, y = adjacent_cell((x, y), 4)

    LHS_Y = y >= 1
    RHS_Y = y + ANTHILL_TOTAL_NUM_LINES - 1 < len(world) - 1

    # Get left most middle corner of anthill
    mx, my = space
    for i in xrange(ANTHILL_SIDES_LEN - 1):
        mx, my = adjacent_cell((mx, my), 3)

    LHS_X = mx >= 1
    RHS_X = mx + ANTHILL_TOTAL_NUM_LINES - 1 < len(world[i]) - 1

    # Check if it hasn't gone outside the world.
    if not (LHS_Y and RHS_Y and LHS_X and RHS_X):
        return False

    # Keeps track of the current line in the anthill.
    hex_line = 0
    for i in xrange(y, y + ANTHILL_TOTAL_NUM_LINES):
        # Check if the current line is clean (all clear cells)
        for j in xrange(x, x + ANTHILL_SIDES_LEN + hex_line):
            if world[i][j] != eg.NONE:
                return False

        # True if the anthill lines should get bigger.
        # False if they should get smaller.
        if y < space[1]:
            x, y = adjacent_cell((x, y), 2)
            hex_line += 1
        else:
            x, y = adjacent_cell((x, y), 1)
            hex_line -= 1

    return True


def randomly_apply_foodblob(world):
    foodblob_insert_to_world_successful = 0
    available_spaces = get_available_spaces(world)
    rand.shuffle(available_spaces)
    for space in available_spaces:
        allowed_left = False
        allowed_right = False

        if foodblob_space_is_viable(world, space, (0, 5)):
            allowed_left = True

        if foodblob_space_is_viable(world, space, (3, 4)):
            allowed_right = True

        if allowed_left and allowed_right:
            if rand.randint(0, 1):
                apply_foodblob(world, space, (0, 5))
            else:
                apply_foodblob(world, space, (3, 4))
            foodblob_insert_to_world_successful += 1
        elif allowed_right:
            apply_foodblob(world, space, (3, 4))
            foodblob_insert_to_world_successful += 1
        elif allowed_left:
            apply_foodblob(world, space, (0, 5))
            foodblob_insert_to_world_successful += 1

        if foodblob_insert_to_world_successful == 11:
            break


def apply_foodblob(world, space, key):
    # Get the topmost of foodblob
    x, y = space
    for i in xrange(FOODBLOB_SIDES_LEN - 1):
        x, y = adjacent_cell((x, y), key[1])

    op = lambda x: (x - 3) % 6

    for i in xrange(FOODBLOB_SIDES_LEN):
        for j in xrange(x, x + FOODBLOB_SIDES_LEN):
            world[y][j] = "5"

        x, y = adjacent_cell((x, y), op(key[1]))

    return True


def foodblob_space_is_viable(world, space, key):
    if not foodblob_border_is_viable(world, space, key):
        return False

    # Get the topmost of foodblob
    x, y = space
    for i in xrange(FOODBLOB_SIDES_LEN - 1):
        x, y = adjacent_cell((x, y), key[1])

    LHS_Y = y >= 1
    RHS_Y = y + FOODBLOB_SIDES_LEN - 1 < len(world) - 1

    # Get most horizontally corner of foodblob
    mx, my = space
    for i in xrange(FOODBLOB_SIDES_LEN - 1):
        mx, my = adjacent_cell((mx, my), key[0])

    LHS_X = mx >= 1
    RHS_X = mx + FOODBLOB_SIDES_LEN - 1 < len(world[i]) - 1

    # Check if it hasn't gone outside the world.
    if not (LHS_Y and RHS_Y and LHS_X and RHS_X):
        return False

    op = lambda x: (x - 3) % 6

    # Keeps track of the current line in the foodblob.
    for i in xrange(FOODBLOB_SIDES_LEN):
        # Check if the current line is clean (all clear cells)
        for j in xrange(x, x + FOODBLOB_SIDES_LEN):
            if world[y][j] != eg.NONE:
                return False

        x, y = adjacent_cell((x, y), op(key[1]))

    return True


def foodblob_border_is_viable(world, space, key):
    op = lambda x: (x - 3) % 6

    top = foodblob_side_is_viable(world, space, key[1], key[0])
    left = foodblob_side_is_viable(world, space, key[0], key[1])
    right = foodblob_side_is_viable(world, space, key[1], op(key[1]))
    bottom = foodblob_side_is_viable(world, space, key[0], op(key[0]))

    return top and left and right and bottom


def foodblob_side_is_viable(world, center, lhs, rhs):
    # Go to lhs corner of the side
    x, y = center
    for i in xrange(FOODBLOB_SIDES_LEN):
        x, y = adjacent_cell((x, y), lhs)

    # Checks if corners are outside the world.
    LHS_Y = y >= 0
    RHS_Y = y < len(world)

    if not (LHS_Y and RHS_Y):
        return False

    LHS_X = x >= 0
    RHS_X = x < len(world[y])

    if not (LHS_X and RHS_X):
        return False

    # From lhs to rhs, check for any obstacles
    for i in xrange(FOODBLOB_SIDES_LEN + 1):
        x, y = adjacent_cell((x, y), rhs)

        try:
            if world[y][x] != eg.NONE:
                return False
        except IndexError:
            return False

    return True


def apply_anthill(world, space, color):
    x, y = space
    for i in xrange(ANTHILL_SIDES_LEN - 1):
        x, y = adjacent_cell((x, y), 4)

    hex_line = 0
    for i in xrange(y, y + ANTHILL_TOTAL_NUM_LINES):
        for j in xrange(x, x + ANTHILL_SIDES_LEN + hex_line):
            world[i][j] = color

        if y < space[1]:
            x, y = adjacent_cell((x, y), 2)
            hex_line += 1
        else:
            x, y = adjacent_cell((x, y), 1)
            hex_line -= 1


def randomly_apply_rocks(world):
    for space in rand.sample(get_available_spaces(world), 14):
        current_space_occupied = False
        for i in xrange(5):
            tx, ty = adjacent_cell(space, i)
            if world[ty][tx] != eg.NONE:
                current_space_occupied = True
        if not current_space_occupied:
            x, y = space
            world[y][x] = eg.ROCK


def get_available_spaces(world):
    """Return all current available space in world."""
    spaces = []
    for y, row in enumerate(world):
        for x, column in enumerate(row):
            if column == eg.NONE:
                spaces.append((x, y))

    return spaces


def save_world(world, filename):
    with open(filename, "w") as f:
        for i, row in enumerate(world):
            if i % 2 != 0 and i not in [0, 1]:
                f.write(" ")

            for column in row:
                f.write(str(column))
                f.write(" ")

            f.write("\n")


def anthill_border_is_viable(world, space):
    top = anthill_side_is_viable(world, space, 4, 0)
    top_r = anthill_side_is_viable(world, space, 5, 1)
    top_l = anthill_side_is_viable(world, space, 4, 2)
    bottom = anthill_side_is_viable(world, space, 2, 0)
    bottom_r = anthill_side_is_viable(world, space, 0, 2)
    bottom_l = anthill_side_is_viable(world, space, 3, 1)

    return top and top_r and top_l and bottom and bottom_r and bottom_l


def anthill_side_is_viable(world, center, lhs, rhs):
    # Go to lhs corner of the side
    x, y = center
    for i in xrange(ANTHILL_SIDES_LEN):
        x, y = adjacent_cell((x, y), lhs)

    # Checks if corners are outside the world.
    LHS_Y = y >= 0
    RHS_Y = y < len(world)

    if not (LHS_Y and RHS_Y):
        return False

    LHS_X = x >= 0
    RHS_X = x < len(world[y])

    if not (LHS_X and RHS_X):
        return False

    # From lhs to rhs, check for any obstacles
    for i in xrange(ANTHILL_SIDES_LEN):
        x, y = adjacent_cell((x, y), rhs)

        if world[y][x] != eg.NONE:
            return False

    return True


def main():
    world = gen_world((150, 150))
    save_world(world, "new_world.world")


if __name__ == "__main__":
    main()
