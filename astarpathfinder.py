import pygame
import math
from queue import PriorityQueue

# window setup
WIDTH = 800
screen = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption('A* Pathfinding Visualiser')

# colour constants
RED = (255, 0, 0)           # closed
GREEN = (0, 255, 0)         # open
WHITE = (255, 255, 255)     # available
BLACK = (0, 0, 0)           # barrier
PURPLE = (128, 0, 128)      # final path
ORANGE = (255, 165 ,0)      # start
GREY = (128, 128, 128)      # grid lines
TURQUOISE = (64, 224, 208)  # end

# node class
class Node:
    def __init__(self, row, col, size, total_rows):
        self.row = row
        self.col = col
        self.x = col * size
        self.y = row * size
        self.color = WHITE
        self.neighbours = []
        self.size = size
        self.total_rows = total_rows
    
    def get_pos(self):
        return self.row, self.col
    
    def is_closed(self):
        return self.color == RED
    
    def is_open(self):
        return self.color == GREEN
    
    def is_barrier(self):
        return self.color == BLACK
    
    def is_start(self):
        return self.color == ORANGE
    
    def is_end(self):
        return self.color == TURQUOISE
    
    def reset(self):
        self.color = WHITE
    
    def make_closed(self):
        self.color = RED
    
    def make_open(self):
        self.color = GREEN
    
    def make_barrier(self):
        self.color = BLACK
    
    def make_start(self):
        self.color = ORANGE
    
    def make_end(self):
        self.color = TURQUOISE
    
    def make_path(self):
        self.color = PURPLE

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

    def update_neighbours(self, grid):
        self.neighbours = []
        if self.row < self.total_rows - 1 and not grid[self.row+1][self.col].is_barrier(): # down
            self.neighbours.append(grid[self.row+1][self.col])
        
        if self.row > 0 and not grid[self.row-1][self.col].is_barrier(): # up
            self.neighbours.append(grid[self.row-1][self.col])
        
        if self.col > 0 and not grid[self.row][self.col-1].is_barrier(): # left
            self.neighbours.append(grid[self.row][self.col-1])
        
        if self.col < self.total_rows - 1 and not grid[self.row][self.col+1].is_barrier(): # right
            self.neighbours.append(grid[self.row][self.col+1])

    def __lt__(self, other):
        return False

# heuristic function
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

# draw path
def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

# a* pathfinder algorithm
def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float('inf') for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float('inf') for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, current, draw)
            end.make_end()
            start.make_start()
            return True
        
        for neighbour in current.neighbours:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + h(neighbour.get_pos(), end.get_pos())
                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.make_open()
        
        draw()

        if current != start:
            current.make_closed()
    
    return False

# initialise nodes
def create_grid(rows):
    grid = []
    tilesize = WIDTH//rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            grid[i].append(Node(i, j, tilesize, rows))
    return grid

# draw the grid
def draw_grid(rows):
    gap = WIDTH//rows
    for i in range(rows):
        pygame.draw.line(screen, GREY, (0, i*gap), (WIDTH, i*gap)) # horizontal lines
        pygame.draw.line(screen, GREY, (i*gap, 0), (i*gap, WIDTH)) # vertical lines

# main draw
def draw(grid, rows):
    screen.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw()
    draw_grid(rows)
    pygame.display.update()

# convert (x, y) position to (row, col)
def xy_to_rc(pos, rows):
    tilesize = WIDTH // rows
    x, y = pos
    row = y // tilesize
    col = x // tilesize
    return (row, col)


def main():
    rows = 50
    grid = create_grid(rows)
    
    start = None
    end = None

    run = True
    while run:
        draw(grid, rows)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if pygame.mouse.get_pressed()[0]: # left click
                pos = pygame.mouse.get_pos()
                row, col = xy_to_rc(pos, rows)
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    node.make_start()
                elif not end and node != start:
                    end = node
                    node.make_end()
                elif node != start and node != end:
                    node.make_barrier()
            
            elif pygame.mouse.get_pressed()[2]: # right click
                pos = pygame.mouse.get_pos()
                row, col = xy_to_rc(pos, rows)
                node = grid[row][col]
                if node == start:
                    start = None
                elif node == end:
                    end = None
                node.reset()
            
            if event.type == pygame.KEYDOWN and start and end:
                if event.key == pygame.K_SPACE:
                    for row in grid:
                        for node in row:
                            node.update_neighbours(grid)
                    algorithm(lambda: draw(grid, rows), grid, start, end)
                
                elif event.key == pygame.K_RETURN:
                    for row in grid:
                        for node in row:
                            node.reset()
                    start = None
                    end = None
    
    pygame.quit()


main()