from random import random, randint
from math import sqrt, e


# this is a program written by Nick that can randomly generate beautiful looking trees

# function to use in main program
def tree_func(S_WIDTH, S_HEIGHT, WIDTH, HEIGHT, GROWTH_RATE, SPREAD_STATE, lpos, postree, radius, unlikelyhood, maxframe):  # needed variables
    def create_kernel(form, r):  # creates a kernel of the surrounding
        kernel = []
        if form == "s":  # square shape
            for j in range(-r, r + 1):
                for i in range(-r, r + 1):
                    kernel.append([i, j])
        elif form == "c":  # circle shape

            for j in range(-r, r + 1):
                for i in range(-r, r + 1):
                    if r ** 2 >= j ** 2 + i ** 2:  # add every position inside circle
                        kernel.append([i, j])

        return kernel

    # colors
    white = (255, 255, 255)
    black = (0, 0, 0)

    SIZE = S_WIDTH // WIDTH  # proportion board/screen

    ROT_SPEED = 50  # Speed at wich generated leafs disappear

    # positions (where it can grow to)
    # pos = [[0,-1],[-1,0],[1,0],[0,1]]
    # pos1 = [[0,-1],[-1,0],[1,0],[0,1],[-1,-1],[-1,1],[1,-1],[1,1]]
    # pos1 = [[-1,-1],[-1,1],[1,-1],[1,1]]
    # pos = [[-2,-1],[1,-2],[-1,2],[2,1]]
    # pos = [[-1,-2],[2,-1],[-2,1],[1,2]]
    # pos1 = [[0,-2],[2,-1],[-2,-1],[2,1],[-2,1],[0,2]] #hex
    # pos= [[-1,-1],[0,1],[0,-1],[1,1]]
    # pos= [[0,-1],[0,1],[-2,3],[-1,-3],[3,2],[1,-2]]
    # pos= [[1,1],[0,-1],[-1,1]]
    # pos1 = [[-2,-1],[-1,-2],[-1,2],[1,-2],[1,2],[2,1],[-1,2],[-2,1]]#octa?
    # pos = [[0,-1],[-1,0],[1,0],[0,1],[-2,-2],[-2,2],[2,-2],[2,2]]
    # pos= [[0,-2],[2,-1],[-2,-1],[1,2],[-1,2]] #penta
    # pos = [[1,0],[1,-1]]
    # pos = [[-1,1],[-1,-1]]
    # pos2 = [[0,-2],[2,-1],[-2,-1],[2,1],[-2,1],[0,2],[0,-4],[4,-2],[-4,-2],[4,2],[-4,2],[0,4]]
    pos = lpos

    # initiation
    board = [[0 for x in range(WIDTH)] for y in range(HEIGHT)]  # generating a board with 0 everywhere

    probability_dis = "sig"  # currently used distribution, to find probability of spreading

    # frame number
    frame = 1

    # functions
    def dist(x1, y1, x2, y2):  # distance function
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def chancef(x, unlikelyh):  # function that calculates if the tree spreads or not
        if probability_dis == "sig":  # using a sigmoid function
            return random() > 2 * unlikelyh - 1 + 2 * (1 - unlikelyh) / (
                    1 + (1 + unlikelyh) ** (-x))  # sigmoid for chance of spreading
        elif probability_dis == "exp":  # other exponential function
            return random() > e ** (-(1 - unlikelyh) / abs(x))

    def grow():  # grow all points by growth_rate
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if GROWTH_RATE <= board[y][x] < 1 - GROWTH_RATE:  # every branch grows by GROWTH_RATE
                    board[y][x] = round(GROWTH_RATE + board[y][x], 2)

    def check_sur(x, y, kernel):  # with kernel, adds all surrounding points using the kernel
        count = 0
        for p in range(len(kernel)):  # for every position in the kernel
            dx = kernel[p][0]
            dy = kernel[p][1]
            if 0 <= y + dy < HEIGHT and 0 <= x + dx < WIDTH:
                count += abs(board[y + dy][x + dx])  # add every value around (x,y)
        return count

    class Tree:  # main class
        def __init__(self, pos, x, y, r, u=0.1) -> None:
            # initialize
            self.pos = pos
            self.x = x
            self.y = y
            self.points = [[x, y, 0]]  # current branches
            self.kernel = create_kernel("c", r)  # create a circular kernel with radius r
            self.unlikelyhood = u  # base probability of spreading

            board[y][x] = GROWTH_RATE  # set value at tree position

            self.lines = []  # connections between different points
            self.leafs = []  # list of leafs

        def add_roots(self):  # used for calculating new branches of the tree

            for point in self.points:  # for every point of the tree
                x, y, a = point
                if board[y][x] > SPREAD_STATE:  # if the point has a value high enough to spread
                    poss = self.pos[:]  # get kernel
                    # check neighbors in a random order
                    while True:
                        if len(poss) == 0:  # stop when every position of the kernel has been tried
                            break
                        r = randint(0, len(poss) - 1)  # else choose a random position of the kernel
                        if 0 <= x + poss[r][0] < WIDTH and 0 <= y + poss[r][
                            1] < HEIGHT:  # check if the position is inside the board
                            self.root(x + poss[r][0], y + poss[r][1], x,
                                      y)  # if position valid check surroundings and porbabbility

                        poss.remove(poss[r])  # remove this position from the list to check

        def root(self, i, j, x, y):  # function to add the branch or leaf or nothing to the tree
            if board[j][i] == 0:  # check if this position is still empty
                count = check_sur(i, j, self.kernel)  # check_sur_weighted(i,j)
                if chancef(count, self.unlikelyhood):  # if the random function is true add the branch to the tree
                    board[j][i] = GROWTH_RATE  # set the value of the board at (i,j)
                    self.points.append([i, j, 0])  # add the branch
                    self.lines.append([(x * SIZE, y * SIZE), (i * SIZE, j * SIZE)])  # add the connection
                elif chancef(count, self.unlikelyhood):  # if the random function is true add a leaf to the tree
                    board[j][i] = -1  # set value to -1 (leaf value)
                    self.leafs.append([(i, j), frame])  # add leaf to list

        def rot_leafs(self):  # lets disappear every leafs that is older than rot_speed
            for leaf in self.leafs:  # for every leaf

                if frame - leaf[1] >= ROT_SPEED:  # if the age of the leaf is more than rot_speed
                    self.leafs.remove(leaf)  # remove the leaf from list
                    board[leaf[0][1]][leaf[0][0]] = 0  # set board value again to 0

    Trees = [Tree(pos, postree[0], postree[1], radius, unlikelyhood)]  # create one tree

    for _ in range(maxframe):  # loop for maxframe frames

        grow()  # grow every point of the board if there is a branch

        for tree in Trees:
            tree.add_roots()  # check for every tree if there are new branches

        for tree in Trees:
            tree.rot_leafs()  # remove all the rotten leafs

        frame += 1

    return Trees[0].lines  # return every connection for visualization

