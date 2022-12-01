## REFERENCES 
## Adapted source code from 
## Nitish Gupta (2022), GitHub Repository, (Source Code), Available at:
## https://github.com/nitesh4146/Treasure-Hunters-Inc

import numpy as np
import math as math
import Map
import threading
import time
import random

grid = Map.grid
actions = Map.actions  # ["up", "left", "down", "right", "wait"]
policy_sign = ["^", "<", "v", ">"]
states = []

current = Map.start
walls = Map.walls

goals = Map.goals
'''
print("Goal: ", goals)
print("Walls: ", walls)
print("Deactivs: ", Map.deactivs)
print("Activs: ", Map.activs)
'''
discount = Map.discount
print_states = Map.print_states

learning_rate = 0.01
score = 1
epsilon = 0.5
episodes = 10000
steps = 300


s = np.array([1, #State vector
                0,
                0,
                0,
                0,
                0])

w = np.ones(np.shape(s))

visited = np.zeros((Map.x, Map.y))


def get_num_adj(x,y):
    # return the number of passable adjacent tiles from x,y
    return len(get_legal_moves(x,y))


def goal_dist(x,y):
    # return the Manhattan distance from the closest goal
    min_dist = pow(Map.x+Map.y,2)
    for goal in goals:
        (goal_x, goal_y) = goal
        dist = abs(goal_x - x) + abs(goal_y - y)
        if (dist < min_dist):
            min_dist = dist
    return inverse_square(min_dist)


    ### Feature changed - add to write-up
def nearby_haz_count(x,y):
    # return number of hazards within 1 and tiles (Manhattan distance)
    count1 = 0  # number of hazards 1 away
    count2 = 0  # number of hazards 2 away
    for k,v in Map.hazards.items() :
        (hazard_x, hazard_y) = v[Map.hazard_ind[k]]
        dist = abs(hazard_x - x) + abs(hazard_y - y)
        if (dist <= 1):
            count1 += 1
            count2 += 1
        elif (dist <= 2):
            count2 += 1
    return (0, count1, count2)


# Maybe not a very useful feature
def num_haz():
    return len(list(Map.hazards.keys()))

def inverse_square(num) :
    return 1/(pow(num + 0.1,2))

def activ_dist(x,y):
    # return Manhattan distance of closest unactivated activator
    min_dist = pow(Map.x+Map.y,2)
    for k,v in Map.activs.items():
        for activ in v:
            (activ_x, activ_y) = activ
            dist = abs(activ_x - x) + abs(activ_y - y)
            if (dist < min_dist):
                min_dist = dist
    return inverse_square(min_dist)


def num_unact_channels():      ### slight change from initial proposal
    # return number of channels yet to be activated
    return(len(list(Map.activs.keys())))


def get_features(x,y) :
    haz_count = nearby_haz_count(x,y)
    feature_vector =  np.array([1,
        goal_dist(x,y),
        haz_count[1],
        haz_count[2],
        activ_dist(x,y),
        num_unact_channels()])
    return feature_vector


def get_legal_moves(x,y):
    legal_moves = []
    # Add deactivatable walls to walls
    temp = walls.copy()
    for arr in Map.deactivs.values():
        temp.append(arr)
    # Check if move would take into a wall
    if x + 1 < Map.x : #check right
        if (x + 1, y) not in temp :
            legal_moves.append((x+1, y))
    if x - 1 >= 0 : #check left
        if (x - 1, y) not in temp :
            legal_moves.append((x-1,y))
    if y - 1 >= 0 : #check up
        if (x, y - 1) not in temp :
            legal_moves.append((x,y-1))
    if y + 1 < Map.y : #check left
        if (x, y + 1) not in temp :
            legal_moves.append((x,y+1))
    return legal_moves


def move(action):
    global current, score
    s = current
    (curr_x, curr_y) = current

    ### Checks move is valid for map
    if action == actions[0]: #up
        current = (curr_x, curr_y-1 if curr_y-1 >= 0 else curr_y)
    elif action == actions[2]: #down
        current = (curr_x, curr_y+1 if curr_y+1 < Map.y else curr_y)
    elif action == actions[3]: #right
        current = (curr_x+1 if curr_x+1 < Map.x else curr_x, curr_y)
    elif action == actions[1]: #left
        current = (curr_x-1 if curr_x-1 >= 0 else curr_x, curr_y)

    # Add deactivatable walls to walls
    temp = walls.copy()
    for arr in Map.deactivs.values():
        temp.append(arr)
    # Check if move would take into a wall
    if current in temp:
        current = s
    
    # Check for goal or hazard
    elif current in goals:
        Map.restart = True
        print("Success score = ", score)
        return
    for k,v in Map.hazards.items():
        print("current: ", current, ", hazard: ", v[Map.hazard_ind[k]])
        if current == v[Map.hazard_ind[k]]:
            Map.restart = True
            print("Fail score = ", score)
            return
    
    # check for activators
    else:
        for k,v in Map.activs.copy().items() :# k = key (channel of activator), v = array of locations (x,y) for channel
            if current in v : #If current in activators
                for x in v: # Remove all activators with channel k
                    (i,j) = x
                    Map.grid[i][j] = '0'
                    Map.board.delete(Map.item_grid[i][j])
                Map.xactivs[k] = Map.activs.pop(k)
                for x in Map.deactivs[k]: # Remove all deactivatables with channel k
                    (i,j) = x
                    Map.grid[i][j] = '0'
                    Map.board.delete(Map.item_grid[i][j])
                Map.xdeactivs[k] = Map.deactivs.pop(k)
        for k,v in Map.deactivs.copy().items() :
            if current in v:
                current = s

    Map.move_bot(current[0], current[1])

    # Increments visited grid for new location
    visited[current[0]][current[1]] += 1

    s2 = current
    return s, action, s2


def restart_check(iter):
    global alpha, score, current
    if Map.restart is True:
        current = Map.start
        visited[current[0]][current[1]] += 1
        Map.move_bot(current[0], current[1])
        Map.restart = False
        Map.restart_game()
        score = 1


def wait():
    time.sleep((1.9*Map.w1.get() - 19.9) / -18)


def get_q(s,w) :
    return np.dot(w.T,s)


def reward(x,y):
    r = 0
    if str(grid[y][x]) == '3':
        r += 100
    elif str(grid[y][x]) == '4':
        r += -100
    elif str(grid[y][x]) == '5':
        r += 150
    #r += -5 * visited[x][y]
    return r


def q_learn() :
    global alpha, current, discount, score, epsilon, episodes, print_states, iter, w, s
    
    iter = 1
    moves = 0

    Map.restart_game()
    while iter <= episodes:
        if Map.flag is None:
            quit()
        if Map.flag is True:
            continue
        # Agent reached a goal/hazard
        restart_check(iter)
        wait()
        epsilon = Map.w2.get()
        print("epsilon:", epsilon)
        # epsilon = soft_max(current, iter)
        discount = Map.discount
        print_states = Map.print_states
        (cx, cy) = current
        q =[]
        # print(get_legal_moves(cx, cy))
        for m in get_legal_moves(cx, cy):
            si = get_features(m[0], m[1])
            q.append((m[0], m[1], get_q(si,w)))

        r = random.random()
        #print(r)
        selected_q = (0,0,0)
        if r < epsilon:
            r = random.randint(0, len(q)-1)
            selected_q = q[r]

        else:
            for i in q :
                if (i[2] > selected_q[2] or selected_q == (0,0,0)):
                    selected_q = i

        (mx, my, mq) = selected_q
        if (mx, my) == (cx + 1, cy) : # move right
            move(actions[3])
        elif (mx, my) == (cx - 1, cy) : # move left
            move(actions[1])
        elif (mx, my) == (cx, cy + 1) : # move down
            move(actions[2])
        elif (mx, my) == (cx, cy - 1) : # move up
            move(actions[0])
        else :
            move(actions[4])
        
        s = get_features(selected_q[0], selected_q[1])
        # print(s)
        # print("Moved to: ", current)

       # print(reward(current[0], current[1]))
        w += (learning_rate * (reward(current[0], current[1]) + discount * get_q(s, w) - selected_q[2])) * s 
        print(np.around(w))
        print(s)
        iter += 1
        moves +=1

def random_run() : #Random agent movements for testing
    global current
    iter = 1
    while iter <= episodes :
        if Map.flag is None:
            quit()
        if Map.flag is True:
            continue
        restart_check(iter)
        wait()

        random.seed(a=None)
        r = random.randint(0,3)
        move(actions[r])

# def wasd_run():
#     def key_pressed(event):
#         if event.char == "W" :
#             move(actions[0])
#         elif event.char == "A" :
#             move(actions[1])
#         elif event.char == "S" :
#             move(actions[2])
#         elif event.char == "D" :
#             move(actions[3])
#         elif event.char == " " :
#             move(actions[4])
#         else :
#             return
#         iter = iter + 1
#         return
 

    # Map.board.bind('<Key>', key_pressed)


        # if key_press == "A" :
        #     move(actions[1])
        # if key_press == "S" :
        #     move(actions[2])
        # if key_press == "D" :
        #     move(actions[3])
        # if key_press == "Space" :
        #     move(actions[4])


def test_run() :
    global current
    def time_move(action) :
        restart_check(1)
        move(action)
        time.sleep(0.3)
    time_move(actions[3])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[2])
    time_move(actions[2])
    time_move(actions[2])
    time_move(actions[3])
    time_move(actions[3])
    time_move(actions[3])
    time_move(actions[3])
    time_move(actions[1])
    time_move(actions[1])
    time_move(actions[1])
    time_move(actions[1])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[1])
    
    time_move(actions[3])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[2])
    time_move(actions[2])
    time_move(actions[2])
    time_move(actions[3])
    time_move(actions[3])
    time_move(actions[3])
    time_move(actions[3])
    time_move(actions[1])
    time_move(actions[1])
    time_move(actions[1])
    time_move(actions[1])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[0])
    time_move(actions[1])
    time_move(actions[3])


t = threading.Thread(target=q_learn)
t.daemon = True
t.start()
Map.begin()