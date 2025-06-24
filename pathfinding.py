from collections import deque
from functools import lru_cache


class PathFinding:
    def __init__(self, game):
        self.game = game
        self.map = game.map.mini_map
        self.ways = [
            (-1, 0), (0, -1), (1, 0), (0, 1),
            (-1, -1), (1, -1), (1, 1), (-1, 1)
        ]
        self.graph = {}
        self.get_graph()

    @lru_cache
    def get_path(self, start, goal):
        self.visited = self.bfs(start, goal, self.graph)
        path = [goal]
        step = self.visited.get(goal, start)

        while step and step != start:
            path.append(step)
            step = self.visited[step]
        return path[-1]

    def bfs(self, start, goal, graph):
        queue = deque([start])
        visited = {start: None}

        while queue:
            current_node = queue.popleft()
            if current_node == goal:
                break
            next_nodes = graph[current_node]

            for next_node in next_nodes:
                if next_node not in visited and next_node not in self.game.object_handler.npc_positions:
                    queue.append(next_node)
                    visited[next_node] = current_node
        return visited

    def get_next_nodes(self, tile_x, tile_y):
        return [
            (tile_x + delta_x, tile_y + delta_y)
            for delta_x, delta_y in self.ways
            if (tile_x + delta_x, tile_y + delta_y) not in self.game.map.world_map
        ]

    def get_graph(self):
        for tile_y, row in enumerate(self.map):
            for tile_x, col in enumerate(row):
                if not col:
                    self.graph[(tile_x, tile_y)] = self.graph.get(
                        (tile_x, tile_y), []
                    ) + self.get_next_nodes(tile_x, tile_y)
