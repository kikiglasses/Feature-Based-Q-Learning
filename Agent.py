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

current = Map.start
last = (-1,-1)
walls = Map.walls

goals = Map.goals


discount = Map.discount
learning_rate = 0.01
score = 1
epsilon = 0.25
episodes = 10000


s = np.array([1, #State vector
                0,
                0,
                0,
                0,
                0], dtype=float)

w = np.array([1, #Weight vector
                10,
                -2,
                5,
                1,
                -1], dtype=float)

visited = [[0 for row in range(Map.x)] for col in range(Map.y)]


def goal_dist(x,y):
    # return the Manhattan distance from the closest goal
    min_dist = pow(Map.x+Map.y,2)
    for goal in goals:
        (goal_x, goal_y) = goal
        dist = abs(goal_x - x) + abs(goal_y - y)
        if (dist < min_dist):
            min_dist = dist
    return inverse_square(min_dist)

def hazard_dist(x,y):
    # return Manhattan distance of closest unactivated activator
    min_dist = pow(Map.x+Map.y,2)
    for k,v in Map.hazards.items():
        (hazard_x, hazard_y) = v[Map.hazard_ind[k]]
        dist = abs(hazard_x - x) + abs(hazard_y - y)
        if (dist < min_dist) :
            min_dist = dist
    return inverse_square(min_dist)

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

def num_unact_channels():
    # return number of channels yet to be activated
    return(len(list(Map.activs.keys())))

def times_visited(x,y):
    return visited[y][x]

def get_features(x,y) :
    #haz_count = nearby_haz_count(x,y)
    feature_vector =  np.array([1,
        goal_dist(x,y),
        hazard_dist(x,y),
        activ_dist(x,y),
        num_unact_channels(),
        times_visited(x,y)])
    return feature_vector

def inverse_square(num) :
    # Maps Manhattan distance to a mectric more useful to the algorithm
    return 1/(pow(num + 1,2))

# def nearby_haz_count(x,y):
#     # return number of hazards within 1 and 2 tiles (Manhattan distance)
#     count1 = 0  # number of hazards 1 away
#     count2 = 0  # number of hazards 2 away
#     for k,v in Map.hazards.items() :
#         (hazard_x, hazard_y) = v[Map.hazard_ind[k]]
#         dist = abs(hazard_x - x) + abs(hazard_y - y)
#         if (dist <= 1):
#             count1 += 1
#             count2 += 1
#         elif (dist <= 2):
#             count2 += 1
#     return (0, count1, count2)

# def just_visited(x,y) :
#     global last
#     return 1 if (x,y) == last else 0

def get_legal_moves(x,y):
    legal_moves = [(x,y)]
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
    global current, score, last, visited
    last = current

    (curr_x, curr_y) = current

    # Checks move is valid for map
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
        current = last
    
    # Check for activators
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
                current = last

    Map.move_bot(current[0], current[1])

    # Increments visited grid for new location
    visited[current[1]][current[0]] += 1

    s2 = current
    return last, action, s2


def restart_check():
    global alpha, score, current, visited
    # Starts reset procedure
    if Map.restart is True:
        current = Map.start
        visited = [[0 for row in range(Map.x)] for col in range(Map.y)]
        visited[current[0]][current[1]] += 1
        Map.restart = False
        Map.restart_game()
        score = 1

def wait():
    time.sleep((1.9*Map.w1.get() - 19.9) / -18)

def get_q(s,w) :
    return np.dot(w.T,s)

def reward(x,y):
    global last, visited
    r = 0
    count = 0
    # Reward arriving at a goal
    if (x,y) in goals :
        r += 100
    # Punish being caught by a hazard
    for k,v in Map.hazards.items():
        if (x,y) == v[Map.hazard_ind[k]]:
            r += -20
    # Reward activating an activator
    for k,v in Map.activs.items():
        if (x,y) in v :
            r += 150
    
    (last_x,last_y) = last
    lm = get_legal_moves(last_x, last_y)
    # Calculate average number of visits of last move's options
    for (x1,y1) in lm :
        count += visited[y1][x1]
    # Punish having returned to tiles visited more than average
    if visited[y][x] > count/len(lm) :
        r += -visited[y][x] / count
    # Reward having returned to tiles visited less than average
    else:
        r += visited[y][x] / count
    # Return sum total of all above rewards
    return r


def q_learn() :
    global alpha, current, discount, score, epsilon, episodes, iter, w, s
    iter = 1

    while iter <= episodes:
        restart_check()
        if Map.flag is None:
            quit()
        if Map.flag is True:
            continue
        # Agent reached a goal/hazard
        wait()
        epsilon = Map.w2.get()
        discount = Map.discount
        (cx, cy) = current
        q =[]
        for m in get_legal_moves(cx, cy):
            si = get_features(m[0], m[1])
            q.append((m[0], m[1], get_q(si,w)))

        r = random.random()

        selected_q = (0,0,0)
        if r < epsilon:
            r = random.randint(1, len(q)-1)
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

        max_q = - math.inf
        for m in get_legal_moves(selected_q[0], selected_q[1]):
            si = get_features(m[0], m[1])
            if get_q(si,w) > max_q :
                max_q = get_q(si,w)
        w += (learning_rate * (reward(current[0], current[1]) + discount * max_q - selected_q[2])) * s
        print('Weight Vector :',w)
        print('Abstract State :',s)
        iter += 1

def random_run() :
    global current
    #Random agent movements for testing
    iter = 1
    while iter <= episodes :
        if Map.flag is None:
            quit()
        if Map.flag is True:
            continue
        restart_check()
        wait()
        random.seed(a=None)
        r = random.randint(0,3)
        move(actions[r])

t = threading.Thread(target=q_learn)
t.daemon = True
t.start()
Map.begin()