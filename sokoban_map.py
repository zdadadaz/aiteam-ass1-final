import sys
from copy import deepcopy
import numpy as np

class SokobanMap:
    """
    Instance of a Sokoban game map. You may use this class and its functions
    directly or duplicate and modify it in your solution. You should avoid
    modifying this file directly.

    COMP3702 2019 Assignment 1 Support Code

    Last updated by njc 11/08/19
    """

    # input file symbols
    # BOX_SYMBOL = '$'
    # TGT_SYMBOL = '.'
    # PLAYER_SYMBOL = '@'
    # BOX_ON_TGT_SYMBOL = '*'
    # PLAYER_ON_TGT_SYMBOL = '+'
    
    BOX_SYMBOL = 'B'
    TGT_SYMBOL = 'T'
    PLAYER_SYMBOL = 'P'
    OBSTACLE_SYMBOL = '#'
    FREE_SPACE_SYMBOL = ' '
    BOX_ON_TGT_SYMBOL = 'b'
    PLAYER_ON_TGT_SYMBOL = 'p'
    
    # move symbols (i.e. output file symbols)
    LEFT = 'l'
    RIGHT = 'r'
    UP = 'u'
    DOWN = 'd'

    # render characters
    FREE_GLYPH = '   '
    OBST_GLYPH = 'XXX'
    BOX_GLYPH = '[B]'
    TGT_GLYPH = '(T)'
    PLAYER_GLYPH = '<P>'
    DL_GLYPH = '{d}'

    def __init__(self, filename):
        """
        Build a Sokoban map instance from the given file name
        :param filename:
        """
        f = open(filename, 'r')

        rows = []
        for line in f:
            if len(line.strip()) > 0:
                rows.append(list(line.strip()))

        f.close()

        row_len = len(rows[0])
        for row in rows:
            assert len(row) == row_len, "Mismatch in row length"

        num_rows = len(rows)

        box_positions = []
        tgt_positions = []
        player_position = None
        for i in range(num_rows):
            for j in range(row_len):
                if rows[i][j] == self.BOX_SYMBOL:
                    box_positions.append((i, j))
                    rows[i][j] = self.FREE_SPACE_SYMBOL
                elif rows[i][j] == self.TGT_SYMBOL:
                    tgt_positions.append((i, j))
                    rows[i][j] = self.FREE_SPACE_SYMBOL
                elif rows[i][j] == self.PLAYER_SYMBOL:
                    player_position = (i, j)
                    rows[i][j] = self.FREE_SPACE_SYMBOL
                elif rows[i][j] == self.BOX_ON_TGT_SYMBOL:
                    box_positions.append((i, j))
                    tgt_positions.append((i, j))
                    rows[i][j] = self.FREE_SPACE_SYMBOL
                elif rows[i][j] == self.PLAYER_ON_TGT_SYMBOL:
                    player_position = (i, j)
                    tgt_positions.append((i, j))
                    rows[i][j] = self.FREE_SPACE_SYMBOL

        assert len(box_positions) == len(tgt_positions), "Number of boxes does not match number of targets"

        self.x_size = row_len
        self.y_size = num_rows
        self.box_positions = box_positions
        self.tgt_positions = tgt_positions
        self.player_position = player_position
        self.player_x = player_position[1]
        self.player_y = player_position[0]
        self.obstacle_map = rows
        self.simpledealock = None
        self.simpledealock_status = None
        self.step_all = []

    def set_state(self,state):
        self.box_positions = deepcopy(state[1])        
        self.player_position = deepcopy(state[0])
        self.player_x = self.player_position[1]
        self.player_y = self.player_position[0]

    def get_target_num(self):
        return len(self.box_positions)

    def get_size(self):
        return [self.x_size, self.y_size]

    def get_state(self):
        return tuple((self.player_position,self.box_positions))

    def get_target(self):
        return deepcopy(self.tgt_positions)
    
    def set_step(self, map):
        self.step_all.append(map)
        # print(np.array(map).reshape(self.y_size,self.x_size))

    def get_step(self, tg,xy):
        return self.step_all[tg][xy[0]*self.x_size + xy[1]]

    def set_simpleDeadlock(self,visited):
        deadlist = [[0 for x in range(self.x_size)] for y in range(self.y_size)] 
        for i in range(self.y_size):
            for j in range(self.x_size):
                count = 0
                for k in range(len(visited)):
                    if ((i,j) in visited[k]):
                        count += 1
                deadlist[i][j] = count
                if (i,j) in self.tgt_positions:
                    deadlist[i][j] = -1

                # if ((i,j) in self.tgt_positions):
                #     deadlist[i][j] = 10000
        self.simpledealock = deadlist

    def update_simpleDealock_status(self):
        sd_status = {}
        sd_status[-1] = set()
        for i in range(len(self.tgt_positions)+1):
            sd_status[i] = set()
        for i in self.box_positions:
            # tmp =self.simpledealock[i[0]][i[1]]
            sd_status[self.simpledealock[i[0]][i[1]]].add(i)

        self.simpledealock_status = sd_status
        
    def check_simpleDeadlock(self,boxOrgState,boxNewState):
        # check if in new box in the same area or new box in the target
        if self.simpledealock[boxNewState[0]][boxNewState[1]] == self.simpledealock[boxOrgState[0]][boxOrgState[1]] or boxNewState in self.tgt_positions:
            return False
        # change one area to the other, so number + 1
        elif self.simpledealock[boxNewState[0]][boxNewState[1]]< (len(self.simpledealock_status[self.simpledealock[boxNewState[0]][boxNewState[1]]])+1):
            return True
        else:
            return False

    def check_freezeDeadlock_v(self, boxPos,count,orgboxPos,count_tg):
        if boxPos in self.tgt_positions:
            count_tg[0] += 1
        count[0] +=1 
        if count[0] >len(self.tgt_positions)+1:
            return True
        if count[0] >2 and orgboxPos == boxPos:
            return True
        if self.obstacle_map[boxPos[0] -1][boxPos[1]] == self.OBSTACLE_SYMBOL or self.obstacle_map[boxPos[0] + 1][boxPos[1]] == self.OBSTACLE_SYMBOL:
            return True
        elif self.simpledealock[boxPos[0] - 1][boxPos[1]] == 0 and self.simpledealock[boxPos[0] + 1][boxPos[1]] == 0:
        # elif (boxPos[0] - 1,boxPos[1]) in self.simpledealock and (boxPos[0] + 1,boxPos[1]) in self.simpledealock:
            return True
        elif (boxPos[0] - 1,boxPos[1]) in self.box_positions:
            return self.check_freezeDeadlock_h((boxPos[0] - 1,boxPos[1]) ,count,orgboxPos,count_tg)
        elif (boxPos[0] + 1,boxPos[1]) in self.box_positions:
            return self.check_freezeDeadlock_h((boxPos[0] + 1,boxPos[1]) ,count,orgboxPos,count_tg)
        else:
            return False

    def check_freezeDeadlock_h(self, boxPos,count,orgboxPos,count_tg):
        if boxPos in self.tgt_positions:
            count_tg[0] += 1
        count[0] +=1
        if count[0] >len(self.tgt_positions)+1:
            return True
        if count[0] >2 and orgboxPos == boxPos:
            return True
        if self.obstacle_map[boxPos[0]][boxPos[1]-1] == self.OBSTACLE_SYMBOL or self.obstacle_map[boxPos[0]][boxPos[1] + 1] == self.OBSTACLE_SYMBOL:
            return True
        elif self.simpledealock[boxPos[0]][boxPos[1] - 1] == 0 and self.simpledealock[boxPos[0]][boxPos[1] + 1] == 0:        
        # elif (boxPos[0],boxPos[1] - 1) in self.simpledealock and (boxPos[0],boxPos[1] + 1) in self.simpledealock:
            return True
        elif (boxPos[0],boxPos[1] - 1) in self.box_positions:
            return self.check_freezeDeadlock_v((boxPos[0],boxPos[1] - 1) ,count,orgboxPos,count_tg)
        elif (boxPos[0],boxPos[1] + 1) in self.box_positions:
            return self.check_freezeDeadlock_v((boxPos[0],boxPos[1] + 1) ,count,orgboxPos,count_tg)
        else:
            return False

    def apply_pull(self,move):
        """
        Apply a player pull to the map.
        :param move: 'L', 'R', 'U' or 'D'
        :return: True if move was successful, false if move could not be completed
        """
        # basic obstacle check
        if move == self.LEFT:
            if self.player_x - 2 < 0 or self.obstacle_map[self.player_y][self.player_x - 2] == self.OBSTACLE_SYMBOL or self.obstacle_map[self.player_y][self.player_x - 1] == self.OBSTACLE_SYMBOL:
                return False
            else:
                new_x = self.player_x - 1
                new_y = self.player_y

        elif move == self.RIGHT:
            if self.player_x + 2 >= self.x_size or self.obstacle_map[self.player_y][self.player_x + 2] == self.OBSTACLE_SYMBOL or self.obstacle_map[self.player_y][self.player_x + 1] == self.OBSTACLE_SYMBOL:
                return False
            else:
                new_x = self.player_x + 1
                new_y = self.player_y

        elif move == self.UP:
            if self.player_y - 2 < 0 or self.obstacle_map[self.player_y - 2][self.player_x] == self.OBSTACLE_SYMBOL or self.obstacle_map[self.player_y - 1][self.player_x] == self.OBSTACLE_SYMBOL:
                return False
            else:
                new_x = self.player_x
                new_y = self.player_y - 1

        else:
            if self.player_y + 2 >= self.y_size or self.obstacle_map[self.player_y + 2][self.player_x] == self.OBSTACLE_SYMBOL or self.obstacle_map[self.player_y + 1][self.player_x] == self.OBSTACLE_SYMBOL:
                return False
            else:
                new_x = self.player_x
                new_y = self.player_y + 1

        # update player position
        self.player_position = (new_y, new_x)
        self.player_x = new_x
        self.player_y = new_y
        
        return True


    def apply_move(self, move):
        """
        Apply a player move to the map.
        :param move: 'L', 'R', 'U' or 'D'
        :return: True if move was successful, false if move could not be completed
        """
        # basic obstacle check
        if move == self.LEFT:
            if self.obstacle_map[self.player_y][self.player_x - 1] == self.OBSTACLE_SYMBOL:
                return False
            else:
                new_x = self.player_x - 1
                new_y = self.player_y

        elif move == self.RIGHT:
            if self.obstacle_map[self.player_y][self.player_x + 1] == self.OBSTACLE_SYMBOL:
                return False
            else:
                new_x = self.player_x + 1
                new_y = self.player_y

        elif move == self.UP:
            if self.obstacle_map[self.player_y - 1][self.player_x] == self.OBSTACLE_SYMBOL:
                return False
            else:
                new_x = self.player_x
                new_y = self.player_y - 1

        else:
            if self.obstacle_map[self.player_y + 1][self.player_x] == self.OBSTACLE_SYMBOL:
                return False
            else:
                new_x = self.player_x
                new_y = self.player_y + 1

        # pushed box collision check
        if (new_y, new_x) in self.box_positions:
            if move == self.LEFT:
                if self.obstacle_map[new_y][new_x - 1] == self.OBSTACLE_SYMBOL or (new_y, new_x - 1) in self.box_positions:
                    return False
                else:
                    new_box_x = new_x - 1
                    new_box_y = new_y

            elif move == self.RIGHT:
                if self.obstacle_map[new_y][new_x + 1] == self.OBSTACLE_SYMBOL or (new_y, new_x + 1) in self.box_positions:
                    return False
                else:
                    new_box_x = new_x + 1
                    new_box_y = new_y

            elif move == self.UP:
                if self.obstacle_map[new_y - 1][new_x] == self.OBSTACLE_SYMBOL  or (new_y - 1, new_x) in self.box_positions:
                    return False
                else:
                    new_box_x = new_x
                    new_box_y = new_y - 1

            else:
                if self.obstacle_map[new_y + 1][new_x] == self.OBSTACLE_SYMBOL or (new_y + 1, new_x) in self.box_positions:
                    return False
                else:
                    new_box_x = new_x
                    new_box_y = new_y + 1

            # update box position
            # using this way, visited id might be repeated since it will treat it as diff path for different order
            # self.box_positions.remove((new_y, new_x))
            # self.box_positions.append((new_box_y, new_box_x))
            self.box_positions[ self.box_positions.index((new_y, new_x))] = (new_box_y, new_box_x)

        # update player position
        self.player_position = (new_y, new_x)
        self.player_x = new_x
        self.player_y = new_y
        
        return True

    def render_deadlock(self):
        """
        Render the map's current state to terminal
        """
        for r in range(self.y_size):
            line = ''
            for c in range(self.x_size):
                symbol = self.FREE_GLYPH

                # for j in range(len(self.simpledealock_status)):
                #     aa = self.simpledealock_status[j]
                #     if (r,c) in aa:
                #         symbol = '('+str(j)+')'
                #         break
                #     else:
                #         symbol ='('+str(0)+')'

                # if self.simpledealock[r][c] == 0:
                #     symbol = self.DL_GLYPH
                symbol = '('+str(self.simpledealock[r][c])+')'

                if self.obstacle_map[r][c] == self.OBSTACLE_SYMBOL:
                    symbol = self.OBST_GLYPH
                # if (r, c) in self.tgt_positions:
                #     symbol = self.TGT_GLYPH
                # box or deadlock overwrites tgt
                if (r, c) in self.box_positions:
                    symbol = self.BOX_GLYPH
                line += symbol
            print(line)

        print('\n\n')

    def render(self):
        """
        Render the map's current state to terminal
        """
        for r in range(self.y_size):
            line = ''
            for c in range(self.x_size):
                symbol = self.FREE_GLYPH
                if self.obstacle_map[r][c] == self.OBSTACLE_SYMBOL:
                    symbol = self.OBST_GLYPH
                if (r, c) in self.tgt_positions:
                    symbol = self.TGT_GLYPH
                # box or player overwrites tgt
                if (r, c) in self.box_positions:
                    symbol = self.BOX_GLYPH
                if self.player_x == c and self.player_y == r:
                    symbol = self.PLAYER_GLYPH
                line += symbol
            print(line)

        print('\n\n')

    def is_finished(self):
        finished = True
        for i in self.box_positions:
            if i not in self.tgt_positions:
                finished = False
        return finished


def main(arglist):
    """
    Run a playable game of Sokoban using the given filename as the map file.
    :param arglist: map file name
    """
    try:
        import msvcrt
        getchar = msvcrt.getch
    except ImportError:
        getchar = sys.stdin.read(1)

    if len(arglist) != 1:
        print("Running this file directly launches a playable game of Sokoban based on the given map file.")
        print("Usage: sokoban_map.py [map_file_name]")
        return

    print("Use the arrow keys to move. Press 'q' to quit. Press 'r' to restart the map.")

    map_inst = SokobanMap(arglist[0])
    map_inst.render()

    steps = 0

    while True:
        char = getchar()

        if char == b'q':
            break

        if char == b'r':
            map_inst = SokobanMap(arglist[0])
            map_inst.render()

            steps = 0

        if char == b'\xe0':
            # got arrow - read direction
            dir = getchar()
            if dir == b'H':
                a = SokobanMap.UP
            elif dir == b'P':
                a = SokobanMap.DOWN
            elif dir == b'K':
                a = SokobanMap.LEFT
            elif dir == b'M':
                a = SokobanMap.RIGHT
            else:
                print("!!!error")
                a = SokobanMap.UP

            map_inst.apply_move(a)
            map_inst.render()

            steps += 1

            if map_inst.is_finished():
                print("Puzzle solved in " + str(steps) + " steps!")
                return


if __name__ == '__main__':
    main(sys.argv[1:])







