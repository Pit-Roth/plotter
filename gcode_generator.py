# imports
import pygame
from pygame.locals import *
from datetime import datetime
from tree import tree_func

# initialize pygame
pygame.init()

# set the "gcode-dimensions" of the drawing area
gcode_width = 160
gcode_height = 180


# "center" all lines according to the first point of the first line
# lines is a list of lines (lists), each line is a list of two points (tuples)
def center_lines(lines: list):
    start = lines[0][0]
    new_lines = []
    for line in lines:
        p1, p2 = line[0], line[1]
        new_lines.append([(p1[0] - start[0], p1[1] - start[1]), (p2[0] - start[0], p2[1] - start[1])])
    return new_lines


# stack class
class Stack:
    def __init__(self):
        self.items = []

    def is_empty(self):
        return len(self.items) == 0

    def push(self, x):
        self.items.append(x)

    def pop(self):
        if len(self.items) > 0:
            return self.items.pop()

    def top(self):
        if len(self.items) > 0:
            return self.items[-1]

    def size(self):
        return len(self.items)

    def __str__(self):
        s = "Stack (from top to bottom): [ "
        for x in reversed(self.items):
            s += f"{x} "
        s += "]"
        return s


# gcode class
class GCode:
    # initialize gcode instance
    def __init__(self, name: str, speed: int, custom_type=None):
        self.name = name
        self.type = custom_type
        self.lines = []
        self.lines.append("G21")  # set units to mm
        self.lines.append("G90")  # absolute mode
        # self.lines.append("G91")  # relative mode
        self.lines.append("G28.1 X0 Y0 Z0")  # set home position
        self.feed_rate = speed
        # set the initial z coordinate to 1
        self.z = 1

    # used for rapid movements
    # in order for those to be useful, the pen needs to be able to be lifted
    def fly_to(self, point: tuple):
        self.go_up()
        self.lines.append(f"G0 X{point[0]} Y{point[1]} F{self.feed_rate}")
        self.go_down()

    # draw a certain line (from current position to point)
    def move_to(self, point: tuple):
        self.lines.append(f"G01 X{point[0]} Y{point[1]} F{self.feed_rate}")

    # lift the pen up
    def go_up(self):
        self.lines.append(f"G01 Z{1} F{self.feed_rate}")

    # lower the pen down
    def go_down(self):
        self.lines.append(f"G01 Z{0} F{self.feed_rate}")

    # save the gcode to a file
    # the filename is adapted according to the name of the gcode and the time the gcode is generated
    def save(self):
        file_name = f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gcode"
        file_path = r"/Users/proth/PycharmProjects/micro_projects/O1RAS/gcodes/" + file_name
        with open(file_path, "w") as file:
            file.writelines([line + "\n" for line in self.lines])
        print(f"The gcode was saved: {file_name}")

    # print the gcode to the terminal
    def print(self):
        for line in self.lines:
            print(line)

    # reset the gcode (reinitialize the class)
    def reset(self):
        self.__init__(self.name, self.feed_rate, self.type)

    # draw a certain sketch that is the converted to gcode
    # pygame is used to get this functionality
    def draw(self, w=500, h=500):
        screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption(self.name)
        screen.fill('white')
        pygame.display.update()

        fps = 30
        clock = pygame.time.Clock()

        pixels = []
        done = False
        pressed = False
        # was_pressed = False
        while not done:
            for event in pygame.event.get():
                if event.type == QUIT:
                    done = True
                if event.type == MOUSEBUTTONDOWN:
                    pressed = True
                if event.type == MOUSEBUTTONUP:
                    pressed = False
                if event.type == KEYDOWN:
                    if event.key == K_s:
                        self.reset()
                        for pixel_x, pixel_y in pixels:
                            self.move_to(
                                (round(pixel_y * (gcode_width / h), 4), round(pixel_x * (gcode_height / w), 4)))
                        self.save()

            if len(pixels) > 2:
                pygame.draw.lines(screen, 'black', False, [(0, 0)] + pixels)

            if pressed:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if 0 <= mouse_x < w and 0 <= mouse_y < h:
                    pixels.append((mouse_x, mouse_y))

            pygame.display.update()
            clock.tick(fps)

        pygame.quit()

    #
    def lines_to_gcode(self, lines: list):
        # overwrite any existing gcode
        self.reset()
        lines = center_lines(lines)
        for line in lines:
            self.fly_to(line[0])
            self.move_to(line[1])
        self.fly_to((0, 0))

    # optimizing the tree lines so that the pen doesn't need to be lifted up
    def optimize_tree_lines(self, lines: list):
        # overwrite any existing gcode
        self.reset()
        # n_nodes = len(lines) + 1
        # generate adjacency list (in this case dictionary)

        # let the beginning of the tree be "(0, 0)"
        lines = center_lines(lines)

        # generate the adjacency list for the tree
        adj = {}
        for p1, p2 in lines:
            adj_p1 = adj.get(p1, [])
            adj_p1.append(p2)
            adj[p1] = adj_p1
            adj_p2 = adj.get(p2, [])
            adj_p2.append(p1)
            adj[p2] = adj_p2

        # initialize the stack and start at the first point of the first line aka "(0, 0)"
        s = Stack()
        s.push(lines[0][0])
        # keep track of the visited nodes
        visited = set()

        # use DFS to traverse the tree in a manner that allows for the pen to be "held down" at all moments
        # for further information on "depth-first search": https://en.wikipedia.org/wiki/Depth-first_search
        while not s.is_empty():
            v = s.pop()
            if v not in visited:
                self.move_to(v)
                visited.add(v)
                for branch in adj[v]:
                    s.push(branch)
            else:
                self.move_to(v)


# this code is used to randomly generate beautiful looking "trees"
width, height = 500, 500


# convert coordinates on a width * height map to coordinates on a gcode_width * gcode_height map
def convert_to_coordinates(p: tuple):
    return round(p[1] * (gcode_width / height), 4), round(p[0] * (gcode_height / width), 4)


# randomly generate a tree and return it in the form of tree lines
tree_lines = tree_func(width, height, 100, 100, 0.05, 0.5, [[0, -2], [2, -1], [-2, -1], [2, 1], [-2, 1], [0, 2]],
                       [50, 50], 8, 0.30, 1000)

# draw tree as it was generated
gcode1 = GCode("tree", 1000)
gcode1.lines_to_gcode(tree_lines)
gcode1.save()

# draw tree using depth-first search
gcode2 = GCode("tree_optimized", 1000)
gcode2.optimize_tree_lines(tree_lines)
gcode2.save()

