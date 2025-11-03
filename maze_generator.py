# maze_generator.py
# DFS-based maze generator, with optional room carving to look like interior spaces.
# Returns a 2D list maze[y][x] where 0=open, 1=wall

import random

def generate_maze(width, height):
    """
    Generate a maze (width x height). Best if width/height are odd.
    Returns list of lists: maze[y][x] with 0 free, 1 wall.
    """
    # base grid of walls
    maze = [[1 for _ in range(width)] for _ in range(height)]

    # recursive DFS carve: step by 2 to leave walls between corridors
    def carve(x, y):
        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < width and 0 < ny < height and maze[ny][nx] == 1:
                # remove intermediate wall and the new cell
                maze[y + dy // 2][x + dx // 2] = 0
                maze[ny][nx] = 0
                carve(nx, ny)

    # pick a starting odd cell
    sx = random.randrange(1, width, 2)
    sy = random.randrange(1, height, 2)
    maze[sy][sx] = 0
    carve(sx, sy)

    # optionally carve a few rooms (to simulate mansion rooms / open areas)
    def add_room(x, y, rw, rh):
        for iy in range(y, min(y+rh, height-1)):
            for ix in range(x, min(x+rw, width-1)):
                if 0 < ix < width-1 and 0 < iy < height-1:
                    maze[iy][ix] = 0

    # add 0-3 rooms of varied sizes
    for _ in range(random.randint(0, 3)):
        rw = random.randrange(4, min(12, max(4, width-4)))
        rh = random.randrange(4, min(10, max(4, height-4)))
        rx = random.randrange(1, width - rw - 1)
        ry = random.randrange(1, height - rh - 1)
        add_room(rx, ry, rw, rh)
        # optional small furniture (blocking cells) inside room
        if random.random() < 0.6:
            fx = rx + random.randrange(1, max(2, rw-1))
            fy = ry + random.randrange(1, max(2, rh-1))
            fw = random.randrange(1, max(1, min(3, rw-2)))
            fh = random.randrange(1, max(1, min(3, rh-2)))
            for iy in range(fy, min(fy+fh, ry+rh-1)):
                for ix in range(fx, min(fx+fw, rx+rw-1)):
                    maze[iy][ix] = 1

    # ensure start and goal are open
    if height > 2 and width > 2:
        maze[1][1] = 0
        maze[height-2][width-2] = 0

    return maze
