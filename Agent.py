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

# start = Map.start # (0, Map.y - 1)
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

### Reward Function
learning_rate = 0.5
score = 1
epsilon = 0.1
episodes = 10000
steps = 300


s = np.array([1, #State vector
                0,
                0,
                0,
                0,
                0,
                0])

w = np.zeros(np.shape(s))

visited = np.zeros((Map.x, Map.y))

def get_features(x,y) :
    feature_vector =  np.array([1,
        get_num_adj(x,y),
        goal_dist(x,y),
        haz_dist(x,y),
        num_haz(),
        activ_dist(x,y),
        num_unact_channels()])
    return feature_vector



def get_num_adj(x,y):
    # return the number of passable adjacent tiles from x,y
    n = 0
    if x + 1 < Map.x : #check right
        if (x + 1, y) not in walls :
            if (x + 1, y) not in list(Map.deactivs.values()) :
                n += 1
    if x - 1 >= 0 : #check left
        if (x - 1, y) not in walls :
            if (x - 1, y) not in list(Map.deactivs.values()) :
                n += 1
    if y - 1 >= 0 : #check up
        if (x, y - 1) not in walls :
            if (x, y - 1) not in list(Map.deactivs.values()) :
                n += 1
    if y + 1 < Map.y : #check left
        if (x, y + 1) not in walls :
            if (x, y + 1) not in list(Map.deactivs.values()) :
                n += 1
    return n

def goal_dist(x,y):
    # return the Manhattan distance from the closest goal
    min_dist = -1
    for goal in goals:
        (goal_x, goal_y) = goal
        temp = abs(goal_x - x) + abs(goal_y - y)
        if (temp < min_dist or min_dist == -1):
            min_dist = temp
    return min_dist

# Removed goal_direction as it is captured by goal_dist()

def haz_dist(x,y):
    # return the Manhattan distance from the nearest hazard
    min_dist = -1
    for k,v in Map.hazards.items() :
        (hazard_x, hazard_y) = v[Map.hazard_ind[k]]
        temp = abs(hazard_x - x) + abs(hazard_y - y)
        if (temp < min_dist or min_dist == -1):
            min_dist = temp
    return min_dist

# Maybe not a very useful feature
def num_haz():
    return len(list(Map.hazards.keys()))

def activ_dist(x,y):
    # return Manhattan distance of closest unactivated activator
    min_dist = -1
    for k,v in Map.activs.items():
        for activ in v:
            (activ_x, activ_y) = activ
            temp = abs(activ_x - x) + abs(activ_y - y)
            if (temp < min_dist or min_dist == -1):
                min_dist = temp
    return min_dist

def num_unact_channels():      ### slight change from initial proposal
    # return number of channels yet to be activated
    return(len(list(Map.activs.keys())))

def get_legal_moves(x,y):
    legal_moves = []
    if x + 1 < Map.x : #check right
        if (x + 1, y) not in walls :
            if (x + 1, y) not in list(Map.deactivs.values()) :
                legal_moves.append((x+1, y))
    if x - 1 >= 0 : #check left
        if (x - 1, y) not in walls :
            if (x - 1, y) not in list(Map.deactivs.values()) :
                legal_moves.append((x-1,y))
    if y - 1 >= 0 : #check up
        if (x, y - 1) not in walls :
            if (x, y - 1) not in list(Map.deactivs.values()) :
                legal_moves.append((x,y-1))
    if y + 1 < Map.y : #check left
        if (x, y + 1) not in walls :
            if (x, y + 1) not in list(Map.deactivs.values()) :
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
    # otherwise waits

    # check for goal or hazard
    if current in walls:
        current = s
    elif current in goals:
        Map.restart = True
        print("**********************  Success score = ", score)
        return
    for k,v in Map.hazards.items():
        if current == v[Map.hazard_ind[k]]:
            Map.restart = True
            print("**********************  Fail score = ", score)
            return
        
    else:
        for k,v in Map.activs.items() :# k = key (channel of activator), v = array of locations (x,y) for channel
            if current in v : #If current in activators
                for i in v: # Remove all activators with channel k
                    Map.grid[i[0]][i[1]] = '0'
                    Map.board.delete(Map.item_grid[i[0]][i[1]])
                Map.activs.pop(k)
                for i in Map.deactivs[k]: # Remove all deactivatables with channel k
                    Map.grid[i[0]][i[1]] = '0'
                    Map.board.delete(Map.item_grid[i[0]][i[1]])
                Map.deactivs.pop(k)
                break
        for k,v in Map.deactivs.items() :
            if current in v:
                current = s

    Map.move_bot(current[0], current[1])

    # Increments visited grid for new location
    visited[current[0]][current[1]] += 1

    s2 = current
    return s, action, s2

def random_run() : #Random agent movements for testing
    global current
    iter = 1

    while iter <= episodes :
        if Map.flag is None:
            quit()
        if Map.flag is True:
            continue
        if Map.restart is True:
            current = Map.start
            Map.move_bot(current[0], current[1])
            Map.restart = False
            Map.restart_game()
            alpha = pow(iter, -0.1)
            score = 1
        time.sleep((1.9*Map.w1.get() - 19.9) / -18)

        random.seed(a=None)
        r = random.randint(0,4)
        move(actions[r])

def test_run() :
    def time_move(action) :
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

def get_q(s,w) :
    return np.dot(w.T,s)

def q_learn() :
    global alpha, discount, current, score, epsilon, episodes, print_states, w

    iter = 1

    while iter <= episodes:
        # Agent reached a goal/hazard
        if Map.restart is True:
            current = Map.start
            visited[current[0]][current[1]] += 1
            Map.move_bot(current[0], current[1])
            Map.restart = False
            Map.restart_game()
            alpha = pow(iter, -0.1)
            score = 1

        time.sleep((1.9*Map.w1.get() - 19.9) / -9)
        epsilon = Map.w2.get()
        # epsilon = soft_max(current, iter)
        discount = Map.discount
        print_states = Map.print_states

        q =[]
        print(current)
        for move in get_legal_moves(current[0],current[1]):
            si = get_features(move[0], move[1])
            q.append((move[0], move[1], get_q(si,w)))
        
        r = random.random()

        movement_q = (0,0,0)
        if r < epsilon:
            r = random.randint(0, len(q)-1)
            movement_q = q[r]
            Map.move_bot(movement_q[0], movement_q[1])
            
        else:
            for i in q :
                if  i[2] > movement_q[2]:
                    movement_q = i
            Map.move_bot(movement_q[0], movement_q[1])
        print("Moved to: ", movement_q[0], movement_q[1])

        r =1

        w += (learning_rate * (r + discount * get_q(s, w) - movement_q[2])) * s 
        print(w)

        
    
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


t = threading.Thread(target=q_learn)
t.daemon = True
t.start()
Map.begin()