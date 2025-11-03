# search_algorithms.py
# A* pathfinder used by guards or other pathing logic.

import heapq
import math

def get_neighbors(maze, node):
    x, y = node
    directions = [(0,1), (1,0), (0,-1), (-1,0)]
    neighbors = []
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= ny < len(maze) and 0 <= nx < len(maze[0]) and maze[ny][nx] == 0:
            neighbors.append((nx, ny))
    return neighbors

def heuristic(a, b):
    # Manhattan distance (good for grid with 4-neighborhood)
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(maze, start, goal):
    """
    Returns a path list from start to goal inclusive, or None if unreachable.
    Path is a list of (x,y) coordinates. start and goal are (x,y).
    """
    if start == goal:
        return [start]
    open_heap = []
    heapq.heappush(open_heap, (0, start))
    g_score = {start: 0}
    parent = {}
    closed = set()

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current in closed:
            continue
        if current == goal:
            # reconstruct
            path = []
            node = goal
            while node != start:
                path.append(node)
                node = parent[node]
            path.append(start)
            path.reverse()
            return path

        closed.add(current)
        for nb in get_neighbors(maze, current):
            tentative_g = g_score[current] + 1
            if nb not in g_score or tentative_g < g_score[nb]:
                g_score[nb] = tentative_g
                f = tentative_g + heuristic(nb, goal)
                heapq.heappush(open_heap, (f, nb))
                parent[nb] = current

    return None
