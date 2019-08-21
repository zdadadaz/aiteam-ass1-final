import sys
from sokoban_map import SokobanMap
from astar_solver import astar 
from queue import PriorityQueue
import time
from prioritize import Prioritize
from copy import deepcopy
import numpy as np


class UniformCost(astar):
    def __init__(self,state = None, parent = None,action = None,depth = 0,cost=0):
        super(UniformCost,self).__init__(state,parent,action,depth,cost)
        self.name = 'uc'

    def heuristic_func(self,nextNode, game_map):
        return 0
    
    def uc_run(self,game_map,outfile):
        return self.astar_run(game_map,outfile)

def main(arglist):
    # file = './testcases/deadlock1.txt'
    # file = './testcases/1box_m1.txt'
    # outfile = 'deadlock1_out.txt'
    file = arglist[0]
    outfile = arglist[1]
    game_map = SokobanMap(file)
    state = (game_map.player_position,game_map.box_positions)
    uc_sokoban= UniformCost(state=state)
    uc_sokoban.uc_run(game_map,outfile)


if __name__ == '__main__':
    main(sys.argv[1:])
    
    