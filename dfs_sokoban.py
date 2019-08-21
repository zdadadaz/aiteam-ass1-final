# -*- coding: utf-8 -*-

import sys
from sokoban_map_modified import SokobanMap
from bfs_sokoban import BFS_sokoban 
from util_datastruct import Stack
import time


class DFS_sokoban(BFS_sokoban):
    def __init__(self,state = None, parent = None,action = None,depth = 0,cost=0):
        super(DFS_sokoban,self).__init__(state,parent,action,depth)
        self.name = 'dfs'

    def dfs(self,game_map,outfile):
        start = time.time()
        queue = Stack()
        queue.push(self)
        visited = set([])
        deadlockhist = set([])
        count = 0
        self.initSimpleDeadlock(game_map)
        node_count = 1
        while not queue.isEmpty():
            count = count +1
            curNode = queue.pop()
            
            hashvalue= hash(str(curNode.state))
            visited.add(hashvalue)            
            game_map.set_state(curNode.state)
            game_map.update_simpleDealock_status()
#            check success or not
            if game_map.is_finished():
                script = []
                timescript = 'Time required = ' + str( time.time()- start)
                exploredscript = 'Explored number = '+ str(len(visited))
                frontierscript = 'Frontier number = '+ str(queue.size())
                nodescript = 'Generated node number = '+ str(node_count)
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
                return True
            
            for action in ['l','r','u','d']:
                new_state = self.get_successor(game_map,curNode,action)
                hashvalue= hash(str(new_state))
                if hashvalue not in visited:
                    if new_state[1] != curNode.state[1]:
                        diffidx = self.findDiffbox(game_map,new_state)
                        if  str(new_state[1]) in deadlockhist:
                            continue
                        
                        if  game_map.check_simpleDeadlock(curNode.state[1][diffidx],new_state[1][diffidx]) or self.freezeDeadlock(game_map,new_state,diffidx):
                            deadlockhist.add(str(new_state[1]))
                            continue
                    node_count += 1
                    newNode = DFS_sokoban(state=new_state,parent=curNode,action=action,depth = curNode.depth+1)
                    queue.push(newNode)
        print('Failed to reach target goal. Number of states explored = ')
        return len(visited)        

def main(arglist):
    # file = './testcases/deadlock1.txt'
    # file = './testcases/1box_m1.txt'
    # outfile = 'deadlock1_out.txt'
    file = arglist[0]
    outfile = arglist[1]
    game_map = SokobanMap(file)
    state = (game_map.player_position,game_map.box_positions)
    dfs_sokoban= DFS_sokoban(state=state)
    dfs_sokoban.dfs(game_map,outfile)


if __name__ == '__main__':
    main(sys.argv[1:])
    
    
