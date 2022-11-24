import numpy as np
import math as math
import Map
import threading
import time
import random

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
goal = Map.goal  # (Map.specials[1][0], Map.specials[1][1])
hazards = Map.hazards  # [(Map.specials[0][0], Map.specials[0][1])]
print("Goal: ", goal)
print("Hazard: ", hazards)
print("Walls: ", walls)

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


state_vector = [0,
                0,
                0,
                0,
                0,
                0]

def get_num_adj():
    # return the number of passable adjacent tiles
    n = 0
    (curr_x, curr_y) = current
    if Map.grid[curr_x+1][curr_y] == 0:
        n += 1
    if Map.grid[curr_x-1][curr_y] == 0:
        n += 1
    if Map.grid[curr_x][curr_y+1] == 0:
        n += 1
    if Map.grid[curr_x][curr_y-1] == 0:
        n += 1
    return n


def goal_dist():
    # return the Manhattan distance from the goal
    # make global goal location variable
    (curr_x, curr_y) = current
    (goal_x, goal_y) = goal
    return goal_x - curr_x + goal_y - curr_y

#Removed goal_direction

def haz_dist():
    (curr_x, curr_y) = current
    min_dist = -1
    for hazard in hazards :
        (hazard_x, hazard_y) = hazard
        temp = hazard_x - curr_x + hazard_y - curr_y
        if (temp < min_dist or min_dist == -1):
            min_dist = temp
    return min_dist
    


def num_haz():
    return len(hazards)

def activ_dist():
    # return Manhattan distance of closest unactivated activator
    # will have to check current location of activators
    pass

def num_unvis_activ():
    # return number of activators yet to be visited
    # global number of activators yet to be visited variable
    pass


def init():
    for i in range(Map.x):
        for j in range(Map.y):
            if (i, j) in walls:
                continue
            states.append((i, j))

    # for state in states:
    #     temp = {}
    #     for action in actions:
    #         if state == goal:
    #             temp[action] = goal_reward
    #         elif state in pit:
    #             temp[action] = pit_reward
    #         else:
    #             temp[action] = 0.1
    #             Map.set_color(state, action, temp[action])
    #     Q[state] = temp


# def print_q():
#     for state in states:
#         if state == goal:
#             print("Goal ", state, " : ", Q[state])
#         elif state in pit:
#             print("Monster ", state, " : ", Q[state])
#         else:
#             print(state, " : ", Q[state])


# def print_policy():
#     global grid
#     policy = [[" " for col in grid[0]] for row in grid]

#     for s in Q:
#         (a, b) = s
#         (act, val) = max_q(s)
#         if s == goal:
#             policy[a][b] = str(goal_reward)
#             grid[a][b] = goal_reward
#         elif s == pit:
#             policy[a][b] = str(pit_reward)
#             grid[a][b] = pit_reward
#         else:
#             policy[a][b] = policy_sign[actions.index(act)]
#             grid[a][b] = format(val, '.2f')
#     print(np.array(grid))
#     print(np.array(policy))


def move(action):
    global current, score
    s = current
    (curr_x, curr_y) = current

    if action == actions[0]: #up
        current = (curr_x, curr_y+1 if curr_y+1 < Map.y else curr_y)
    elif action == actions[3]: #down
        current = (curr_x, curr_y-1 if curr_y-1 >= 0 else curr_y)
    elif action == actions[0]: #right
        current = (curr_x+1 if curr_x+1 < Map.x else curr_x, curr_y)
    elif action == actions[2]: #left
        current = (curr_x-1 if curr_x-1 >= 0 else curr_x, curr_y)
    # otherwise waits

    # check for goal or pit
    if current in walls:
        current = s
    elif current == goal:
        Map.restart = True
        print("**********************  Success score = ", score)
    elif current in hazards:
        Map.restart = True
        print("**********************  Fail score = ", score)

    Map.move_bot(current[0], current[1])
    # r = move_reward

    # score += r
    s2 = current
    return s, action, s2


# def max_q(state):
#     q_val = None
#     act = None
#     for a, q in Q[state].items():
#         if q_val is None or q > q_val:
#             q_val = q
#             act = a
#     return act, q_val


# def update_q(s, a, alpha, new_q):
#     Q[s][a] *= (1 - alpha)
#     Q[s][a] += (alpha * new_q)
#     Map.set_color(s, a, Q[s][a])
#     print("Q(s) = (1-lr) * Q(s) + lr * Q'(s) = ", Q[s][a])


# def soft_max(state, tou):
#     (a, v) = max_q(state)
#     exp_q = math.exp(v/tou)

#     sum_exp_q = 0
#     for (act, val) in Q[state].items():
#         sum_exp_q += math.exp(val/tou)

#     soft_value = (exp_q / sum_exp_q)
#     return soft_value


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

# # The Q value iteration function
# def q_learn():
#     global alpha, discount, current, score, epsilon, episodes, print_states

#     iter = 1
#     init()

#     while iter <= episodes:
#         if Map.flag is None:
#             quit()
#         if Map.flag is True:
#             continue

#         # Get action and value corresponding to maximum q value
#         (max_act, max_val) = max_q(current)
#         print("*************************** %d ***************************"%(iter))
#         print("Current: ", current, max_q(current))

#         # Take optimal action
#         (s, a, reward, s2) = move(random_action(max_act))
#         print("Move: ", (s, a, reward, s2))

#         (max_act2, max_val2) = max_q(s2)
#         print("Next: ", s2, max_q(s2))

#         # Final Reward with discount
#         print("Q'(s) = {} + {}*{}".format(reward, discount, max_val2))

#         # Update q values
#         update_q(s, a, alpha, reward + discount*max_val2)

#         if print_states:
#             print_q()

#         # print_policy()
#         print("learning rate: ", alpha)
#         # raw_input()

#         iter += 1

#         if Map.restart is True:
#             current = Map.start
#             Map.move_bot(current[0], current[1])
#             Map.restart = False
#             Map.restart_game()
#             alpha = pow(iter, -0.1)
#             score = 1

#         time.sleep((Map.w1.get() + 0.1) / 100)
#         epsilon = Map.w2.get()
#         # epsilon = soft_max(current, iter)
#         discount = Map.discount
#         print_states = Map.print_states

#         print("Epsilon: ", epsilon)
#         print("Discount: ", discount)


t = threading.Thread(target=q_learn)
t.daemon = True
t.start()
Map.begin()