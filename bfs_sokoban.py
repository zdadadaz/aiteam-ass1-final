# -*- coding: utf-8 -*-

import sys
from sokoban_map import SokobanMap
from util_datastruct import Queue
from util_datastruct import Stack
import time

class BFS_sokoban():
    def __init__(self,state = None, parent = None,action = None,depth = 0):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = depth
        self.name = 'bfs'

    def get_successor(self,game_map,node,act):
#         LEFT = 'l'
#         RIGHT = 'r'
#         UP = 'u'
#         DOWN = 'd'
        curState = node.state
        if game_map.apply_move(act):
            curState = game_map.get_state()
        game_map.set_state(node.state)
        return curState
   
    def traverse(self,node,game_map):
        x = node
        statelist = []
        while x.parent:
            statelist.append((x.state,x.action,x.depth))
            x = x.parent
        statelist.append((x.state,x.action,x.depth))
        for i in reversed(statelist):
            game_map.set_state(i[0])
            # game_map.render()
        return reversed(statelist)
    
    def writeOut(self,filename,statelist,script):
        f = open(filename,'w')
        tmp=''
        for i in statelist:
            tmp = tmp + str(i[1])
            tmp = tmp + ','
        f.write(tmp[5:-1])
        f.close()

        # f = open(filename[:-4] +'_' +self.name + filename[-4:],'w')
        # for i in script:
        #     f.write(i + '\n')
        # f.close()

    
    def get_successor_pull(self,game_map,node,act):
#         LEFT = 'l'
#         RIGHT = 'r'
#         UP = 'u'
#         DOWN = 'd'
        curState = node
        if game_map.apply_pull(act):
            curState = game_map.get_state()
        game_map.set_state(node)
        return curState

    def initSimpleDeadlock(self,game_map):
        tg = game_map.get_target()
        curState = game_map.get_state()
        visited_all = []
        sizemap = game_map.get_size()
        for i in range(len(tg)):
            step_tg =[float("inf") for i in range(sizemap[0]*sizemap[1])]
            state = (tg[i],curState[1])
            queue = Queue()
            queue.enqueue((state,None))
            visited = set()
            while not queue.isEmpty():
                tmpNode = queue.dequeue()
                curNode = tmpNode[0]
                visited.add((curNode[0]))  
                if tmpNode[1] is not None:
                    step_tg[curNode[0][0]*sizemap[0] + curNode[0][1]] = step_tg[tmpNode[1][0]*sizemap[0] + tmpNode[1][1]] + 1
                else:
                    step_tg[curNode[0][0]*sizemap[0] + curNode[0][1]] = 0

                game_map.set_state(curNode)
                for action in ['l','r','u','d']:
                    new_state = self.get_successor_pull(game_map,curNode,action)
                    if (new_state[0]) not in visited:
                        queue.enqueue((new_state,curNode[0]))
            visited_all.append(visited)
            # visited_all=visited_all.union(visited) if i ==0 else visited_all.intersection(visited)     
            game_map.set_step(step_tg)

        game_map.set_state(curState)
        game_map.set_simpleDeadlock(list(visited_all))

    def findDiffbox(self,game_map,curState):
        orgState = game_map.get_state()
        diffidx = -1
        for i in range(len(curState[1])):
            if curState[1][i] != orgState[1][i]:
                diffidx = i
        return diffidx

    def freezeDeadlock(self,game_map,curState,diffidx):
        orgState = game_map.get_state()
        game_map.set_state(curState)
        count =[0]
        count_tg =[0]
        resultv =  game_map.check_freezeDeadlock_v(curState[1][diffidx],count,curState[1][diffidx],count_tg) 
        if resultv == True and count_tg[0] == count[0]:
            resultv = False
        game_map.set_state(curState)
        count = [0]
        count_tg =[0]
        resulth = game_map.check_freezeDeadlock_h(curState[1][diffidx],count,curState[1][diffidx],count_tg)
        if resulth == True and count_tg[0] == count[0]:
            resulth = False
        game_map.set_state(orgState)
        return resultv and resulth
        
    def bfs(self,game_map,outfile):
        start = time.time()
        queue = Queue()
        queue.enqueue(self)
        visited = set([])
        deadlockhist = set([])
        self.initSimpleDeadlock(game_map)
        node_count = 1
        q_count = 1
        while not queue.isEmpty():
            q_count -= 1
            curNode = queue.dequeue()
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
                    newNode = BFS_sokoban(state=new_state,parent=curNode,action=action,depth = curNode.depth+1)
                    queue.enqueue(newNode)
                    q_count +=1
        print('Failed to reach target goal. Number of states explored = ')
        return len(visited)


   
def main(arglist):
    # file = './smallSet/Mulholland_D/Mulholland_D-24.soko'
    # file = './testcases/1box_m2.txt'
    # file = './testcases/1box_m1.txt'
    # outfile = './output/1box_m2_out.txt'
    file = arglist[0]
    outfile = arglist[1]
    game_map = SokobanMap(file)
    state = tuple((game_map.player_position,game_map.box_positions))
    bfs_sokoban= BFS_sokoban(state)
    bfs_sokoban.bfs(game_map,outfile)

    # game_map.render()
    # state = game_map.get_state()
    # bfs_sokoban.initSimpleDeadlock(game_map)
    # game_map.set_state(state)
    # game_map.update_simpleDealock_status()
    # game_map.render_deadlock()
    # print(game_map.get_state())

    # deadlock1
    # newState =((2, 5), [(2, 3), (2, 4), (3, 2), (3, 3)])

    # deadlock2
    # newState =((2, 3), [(1, 2), (1, 3)])
    
    # deadlock3
    # newState =((4, 5), [(2, 2), (2, 3), (3, 2), (3, 4), (4, 3), (4, 4)])

    # print(bfs_sokoban.freezeDeadlock(game_map,newState,1))

if __name__ == '__main__':
    main(sys.argv[1:])
    