# -*- coding: utf-8 -*-

import sys
from sokoban_map_modified import SokobanMap
from bfs_sokoban import BFS_sokoban 
from queue import PriorityQueue
import time
from prioritize import Prioritize
from copy import deepcopy
import numpy as np


class astar(BFS_sokoban):
    def __init__(self,state = None, parent = None,action = None,depth = 0,cost=0):
        super(astar,self).__init__(state,parent,action,depth)
        self.sofar_cost = cost
        self.actioncost = 1
        self.name = 'astar'

    def heuristic_func(self,nextNode, game_map):
        target = game_map.tgt_positions
        person = deepcopy(nextNode.state[0])
        box = deepcopy(nextNode.state[1])
        boxdist = []
        dist = 0
        for bx in box:
            target_dist = []
            tg_count = 0
            for tg in target:
                target_dist.append(self.get_dist_from_target(game_map,bx,tg_count))
                tg_count += 1
                # target_dist.append(self.manhattan_dist(bx,tg))
            tg_min_index = np.argmin(target_dist)
            dist += target_dist[tg_min_index]
            # tg_min_index
        return dist

    def manhattan_dist(self,x,y):
        dx = abs(x[0]-y[0])
        dy = abs(x[1]-y[1])
        D=1
        return D*(dx+dy)

    def get_dist_from_target(self,game_map,bx,tg):
        return game_map.get_step(tg,bx)
    
    def astar_run(self,game_map,outfile):
        start = time.time()
        queue = PriorityQueue()
        self.sofar_cost = 0
        queue.put(Prioritize(0,self))
#        visited = set([])
        visited = {}
        visitedBox = set()
        deadlockhist = set([])
        self.initSimpleDeadlock(game_map)
        # game_map.update_simpleDealock_status()  
        # game_map.render_deadlock()
        node_count = 1
        q_count = 1
        while queue:
            curItem = queue.get()   
            q_count -= 1
            curNode = curItem.item
            visited[str(curNode.state)] = curNode         
            game_map.set_state(curNode.state)
            game_map.update_simpleDealock_status()  
            # game_map.render_deadlock()
            # game_map.render()
            # if (time.time()- start > len(game_map.get_target())*30):
            #     printout = []
            #     printout.append(100000)
            #     printout.append(100000)
            #     printout.append(100000)
            #     printout.append(100000)
            #     printout.append(100000)
            #     print('Run out of time')
            #     return printout

#            check success or not
            if game_map.is_finished():
                script = []
                timescript = 'Time required = ' + str( time.time()- start)
                exploredscript = 'Explored number = '+ str(len(visited))
                frontierscript = 'Frontier number = '+ str(queue.qsize())
                nodescript = 'Generated node number = '+ str(node_count)
                
                ts = str( time.time()- start)
                es = str(len(visited))
                fs = str(queue.qsize())
                ns = str(node_count)
                
                printout = []
                printout.append(ns)
                printout.append(fs)
                printout.append(es)
                printout.append(ts)

                script.append(timescript)
                script.append(exploredscript)
                script.append(frontierscript)
                script.append(nodescript)

                print(timescript)
                print(exploredscript)
                print(frontierscript)
                print(nodescript)
                shortestpath = self.traverse(curNode,game_map)
                self.writeOut(outfile,shortestpath,script)
                return printout
            
            for action in ['l','r','u','d']:
                new_state = self.get_successor(game_map,curNode,action)
                new_cost = curNode.sofar_cost + self.actioncost
                if (str(new_state) not in visited) or (new_cost < visited[str(new_state)].sofar_cost) :
                    if (str(new_state) not in visited):
                        # if box moved
                        if new_state[1] != curNode.state[1]:
                            # if box postion visited
                            if tuple(new_state[1]) in visitedBox:
                                continue
                            else:
                                visitedBox.add(tuple(new_state[1]))
                            diffidx = self.findDiffbox(game_map,new_state)
                            # new box position in the deadlock list
                            if  str(new_state[1]) in deadlockhist:
                                continue
                            # if new_state[1][diffidx] == (1,2):
                            #     aa=1
                            # game_map.render()
                            # game_map.set_state(new_state)
                            # print('moved box:',new_state[1][diffidx])
                            # print('org: ', curNode.state)
                            # print('new: ', new_state)
                            # game_map.render()
                            # game_map.set_state(curNode.state)
                            # simple = game_map.check_simpleDeadlock(curNode.state[1][diffidx],new_state[1][diffidx])
                            # freeze = self.freezeDeadlock(game_map,new_state,diffidx)
                            # if simple == False and  freeze == True:
                            #     game_map.render_deadlock()
                            #     aa=1
                            # print('simple:',simple)
                            # print('freeze:',freeze)
                            if  game_map.check_simpleDeadlock(curNode.state[1][diffidx],new_state[1][diffidx]) or self.freezeDeadlock(game_map,new_state,diffidx):
                                deadlockhist.add(str(new_state[1]))
                                continue
                        newNode = astar(state=new_state,parent=curNode,action=action,depth = curNode.depth+1,cost =new_cost)
                        visited[str(new_state)] =newNode
                        node_count += 1
                    visited[str(new_state)].sofar_cost = int(new_cost)
                    priority_cost = new_cost + self.heuristic_func(newNode,game_map)
                    queue.put(Prioritize(int(priority_cost),newNode))
                    q_count +=1
        print('Failed to reach target goal. Number of states explored = ')
        return len(visited)        
    
def main(arglist):
    # file = './smallSet/Mulholland_D/Mulholland_D-24.soko'
    # file = './testcases1/1box_m3.txt'
    # file = './testcases/deadlock1.txt'
    # file = './testcases/2box_m1.txt'
    # outfile = 'deadlock1_out.txt'
    file = arglist[0]
    outfile = arglist[1]
    game_map = SokobanMap(file)
    state = (game_map.player_position,game_map.box_positions)
    astar_sokoban= astar(state)
    # astar_sokoban.initSimpleDeadlock(game_map)
    # game_map.set_state(state)
    # game_map.update_simpleDealock_status()
    # game_map.render_deadlock()
    astar_sokoban.astar_run(game_map,outfile)


if __name__ == '__main__':
    main(sys.argv[1:])
    
    