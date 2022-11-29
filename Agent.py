import numpy as np
import math as math
import Map
import threading
import time
import random
import keyboard

# grid = [[0, 0, 0, 0],
#         [0, -99, 0, 0],
#         [0, 0, 0, 0],
#         [0, 0, 0, 0]]
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
Q = {}
discount = Map.discount
print_states = Map.print_states

### Reward Function
alpha = 1
score = 1
move_reward = -0.04
goal_reward = 1
hazard_reward = -1
move_pass = 0.8
move_fail = 0.1
move_action = [-1, 0, 1]
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

w = np.array([1, #Weight vector
                1,
                1,
                1,
                1,
                1,
                1])

visited = np.zeros((Map.x, Map.y))

def get_num_adj(location):
    # return the number of passable adjacent tiles
    n = 0
    (loc_x, loc_y) = location
    if Map.grid[loc_x+1][loc_y] == "0":
        n += 1
    if Map.grid[loc_x-1][loc_y] == "0":
        n += 1
    if Map.grid[loc_x][loc_y+1] == "0":
        n += 1
    if Map.grid[loc_x][loc_y-1] == "0":
        n += 1
    return n

def goal_dist(location):
    # return the Manhattan distance from the closest goal
    (loc_x, loc_y) = location
    min_dist = -1
    for goal in goals:
        (goal_x, goal_y) = goal
        temp = abs(goal_x - loc_x) + abs(goal_y - loc_y)
        if (temp < min_dist or min_dist == -1):
            min_dist = temp
    return min_dist

# Removed goal_direction as it is captured by goal_dist()

def haz_two_away(location):
    # return the Manhattan distance from the nearest hazard
    (loc_x, loc_y) = location
    min_dist = -1
    for k,v in Map.hazards.items() :
        (hazard_x, hazard_y) = v.values()[Map.hazard_ind[k]]
        temp = abs(hazard_x - loc_x) + abs(hazard_y - loc_y)
        if (temp < min_dist or min_dist == -1):
            min_dist = temp
    if (min_dist > 2 or min_dist == -1):
        return 0
    return 1

# Maybe not a very useful feature
def num_haz():
    return len(Map.hazards)

def activ_dist(location):
    # return Manhattan distance of closest unactivated activator
    (loc_x, loc_y) = location
    min_dist = -1
    for k,v in Map.activs.items():
        for activ in v:
            (activ_x, activ_y) = activ
            temp = abs(activ_x - loc_x) + abs(activ_y - loc_y)
            if (temp < min_dist or min_dist == -1):
                min_dist = temp
    return min_dist

def num_unact_channels():      ### slight change from initial proposal
    # return number of channels yet to be activated
    return(len(Map.activs.keys()))



def init():
    for i in range(Map.x):
        for j in range(Map.y):
            if (i, j) in walls:
                continue
            states.append((i, j))


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

def random_action(act):
    random.seed(a=None)
    r = random.random()
    other_actions = []
    for a in actions:
        if a != act:
            other_actions.append(a)
    print(other_actions)
    if r >= 1 - epsilon:
        r2 = random.randint(0, 2)
        print("Random action:", other_actions[r2])
        return other_actions[r2]

    else:
        print("Best action")
        return act

def random_run() : #Random agent movements for testing
    global current
    iter = 1
    init()

    while iter <= episodes :
        if Map.flag is None:
            quit()
        if Map.flag is True:
            continue
        restart_check(iter)
        wait()

        random.seed(a=None)
        r = random.randint(0,4)
        move(actions[r])

def test_run() :
    init()
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

def restart_check(iter):
    global alpha, score
    if Map.restart is True:
        current = Map.start
        visited[current[0]][current[1]] += 1
        Map.move_bot(current[0], current[1])
        Map.restart = False
        Map.restart_game()
        alpha = pow(iter, -0.1)
        score = 1


def wait():
    time.sleep((1.9*Map.w1.get() - 19.9) / -18)


def q_learn() :
    global alpha, discount, current, score, epsilon, episodes, print_states

    iter = 1
    init()

    while iter <= episodes:
        # Agent reached a goal/hazard
        restart_check(iter)
        wait()
        epsilon = Map.w2.get()
        # epsilon = soft_max(current, iter)
        discount = Map.discount
        print_states = Map.print_states

        print("Epsilon: ", epsilon)
        print("Discount: ", discount)
    
# def wasd_run():
#     init()
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


#t = threading.Thread(target=q_learn)
#t = threading.Thread(target=test_run)
t = threading.Thread(target=random_run)
t.daemon = True
t.start()
Map.begin()