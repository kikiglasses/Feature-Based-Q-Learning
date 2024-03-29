## REFERENCES 
## Adapted source code from 
## Nitish Gupta (2022), GitHub Repository, (Source Code), Available at:
## https://github.com/nitesh4146/Treasure-Hunters-Inc

import time
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import simpledialog, messagebox
from PIL import Image
from PIL import ImageTk
import os
import re


master = Tk()
master.wm_title("Dynamic Hazard Grid World")

result = messagebox.askyesno(
    "Welcome to Grid World", "Do you want to create a new map?")

grid = []
item_grid = []
path = os.getcwd() + "/images/"
wall_pic = ImageTk.PhotoImage(image=Image.open(path+'brick1.png'))
goal_pic = ImageTk.PhotoImage(image=Image.open(path+'diamond1.png'))
hazard_pic = ImageTk.PhotoImage(image=Image.open(path+'zombie1.png'))
agent_pic = ImageTk.PhotoImage(image=Image.open(path+'steve1.png'))
activ_pic = ImageTk.PhotoImage(image=Image.open(path+'lever1.png'))
deactiv_pic = ImageTk.PhotoImage(image=Image.open(path+'trapdoor1.png'))

Width = 48
actions = ["up", "left", "down", "right", "wait"]

# Read map from file
if not result:
    filename = askopenfilename(title="Select map file")
    print(filename)
    if len(filename) == 0:
        messagebox.showwarning('Error', 'No map selected!')
        quit()
    ins = open(filename, "r")
    for line in ins:
        number_strings = line.split()
        grid.append(number_strings)
    (x, y) = (len(grid[0]), len(grid))
    board = Canvas(master, width=x*Width, height=y*Width)
    item_grid = [[0 for row in grid[0]] for col in grid]

# Create new map file
# Not completed
else:
    x_str = simpledialog.askstring('Size', 'Enter grid size')
    if x_str == None:
        messagebox.showwarning('Error', 'No size found!')
        quit()
    x = int(x_str)
    (x, y) = (x, x)

    board = Canvas(master, width=x*Width, height=y*Width)
    start_count = 0
    goal_count = 0

    for i in range(x):
        for j in range(y):
            board.create_rectangle(
                i*Width, j*Width, (i+1)*Width, (j+1)*Width, fill="white", width=1, outline="black")

    board.pack(side=LEFT)

    grid = [['0' for row in range(x)] for col in range(y)]
    item_grid = [[0 for row in grid[0]] for col in grid]

    var = StringVar(master)
    var.set("Select item")

    option = OptionMenu(master, var, "start", "walls", "goal", "hazard", "activator", "deactivatable")
    option.pack()

    robot = 0


    '''
    Key to grid representation:
    0 = empty
    1 = wall
    2 = start
    3 = goal
    4 = hazard
    5 = activator
    6 = deactivatable
    '''

    def create_item(event):
        global robot, start_count, goal_count
        x, y = int(event.x/Width), int(event.y/Width)
        if item_grid[y][x] == 0:
            if var.get() == "walls":
                item_grid[y][x] = board.create_image(
                    x*Width+Width/2, y*Width+Width/2, image=wall_pic)
                grid[y][x] = '1'
            elif var.get() == "start":
                item_grid[y][x] = board.create_image(
                    x*Width+Width/2, y*Width+Width/2, image=agent_pic)
                grid[y][x] = '2'
                start_count += 1
            elif var.get() == "goal":
                item_grid[y][x] = board.create_image(
                    x*Width+Width/2, y*Width+Width/2, image=goal_pic)
                grid[y][x] = '3'
                goal_count += 1
            elif var.get() == "hazard":
                item_grid[y][x] = board.create_image(
                    x*Width+Width/2, y*Width+Width/2, image=hazard_pic)
                grid[y][x] = '4(1,0)'
            elif var.get() == "activator":
                item_grid[y][x] = board.create_image(
                    x*Width+Width/2, y*Width+Width/2, image=activ_pic)
                grid[y][x] = '5(1)' #channel selection should be added to gui
            elif var.get() == "deactivatable":
                item_grid[y][x] = board.create_image(
                    x*Width+Width/2, y*Width+Width/2, image=deactiv_pic)
                grid[y][x] = '6(1)'

    board.bind('<Button-1>', create_item)

    def delete_item(event):
        global start_count, goal_count
        x, y = int(event.x/Width), int(event.y/Width)
        if item_grid[y][x] != 0:
            board.delete(item_grid[y][x])
            item_grid[y][x] = 0
            grid[y][x] = '0'
            if var.get == "start":
                start_count -= 1
            elif var.get() == "goal":
                goal_count -= 1

    board.bind('<Button-3>', delete_item)
    board.bind('<Control-1>', delete_item)
    Label(text="""Instructions:
    1. Select item from dropdown
    2.Left click on grid cell to add
    3. Right click on grid cell to remove

    Note: Please close 
    this window when finished.""",
    font="Verdana 12").pack(side=BOTTOM)

    master.mainloop()
    master = Tk()
    master.wm_title("Dynamic Hazard Grid World")
    board = Canvas(master, width=x*Width, height=y*Width)

    if start_count < 1:
        messagebox.showwarning('Error', 'No start found!')
        quit()
    elif goal_count < 1:
        messagebox.showwarning('Error', 'No goal found!')
        quit()

walls = []
goals = []
hazards = {}    # "Channel" : [line of ordered locations]
hazard_ind = {} # "Channel" : current index
hazard_dir = {} # "Channel" : current direction (forwards/backwards)
activs = {}     # "Channel" : [list of activators on this channel]
xactivs = {}    # Dictionary of activators that have been activated in the current run
deactivs = {}   # "Channel" : [list of deactivatables on this channel]
xdeactivs = {}  # Dictionary of deactivatables that have been deactivated in the current run

# Add each type from grid list to its own list
for i in range(y):
    for j in range(x):
        if grid[i][j] == "1":
            walls.append((j, i))
        elif grid[i][j] == "2":
            start = (j, i)
            last = start
        elif grid[i][j] == "3":
            goals.append((j, i))

        # regex check -- stores 'i' from '4(i,j)' into channel.group(1), 'j' into channel.group(2)
        # If matches the regex (begins with 4, contains a pair of brackets, can contain two comma seperated strings between the breackets)
        elif channel := re.search('4\((.*),(.*)\)', grid[i][j]):
            if channel.group(1) not in hazards.keys():
                hazards[channel.group(1)] = []
                hazard_dir[channel.group(1)] = 1
                hazard_ind[channel.group(1)] = 0
                hazards[channel.group(1)].append((j, i))
                grid[i][j] = '4'
            else :
                hazards[channel.group(1)].append((j, i))
                grid[i][j] = '0'

        # regex check -- stores 'x' from '5(x)' into channel.group(1)
        # If matches the regex (begins with 5, contains a pair of brackets, can contain a string between the breackets)
        elif channel := re.search('5\((.*)\)', grid[i][j]):
            if channel.group(1) not in activs.keys():
                activs[channel.group(1)] = []
            activs[channel.group(1)].append((j,i))
            grid[i][j] = '5'

        # regex check same as above but for 6
        elif channel := re.search('6\((.*)\)', grid[i][j]):
            if channel.group(1) not in deactivs.keys():
                deactivs[channel.group(1)] = []
            deactivs[channel.group(1)].append((j,i))
            grid[i][j] = '6'

player = start
flag = True
restart = False

# Displays grid and displays specials as images
def visualize_grid():
    global specials, walls, Width, x, y, player
    for i in range(x):
        for j in range(y):
            board.create_rectangle(
                i*Width, j*Width, (i+1)*Width, (j+1)*Width, fill="white", width=1)
    for k,v in hazards.items(): # Move to player update function
        (i,j) = v[0]
        item_grid[i][j] = board.create_image(i*Width+Width/2, j*Width+Width/2, image=hazard_pic)
    for (i,j) in goals:
        item_grid[i][j] = board.create_image(i*Width+Width/2, j*Width+Width/2, image=goal_pic)
    for (i, j) in walls:
        item_grid[i][j] = board.create_image(i*Width+Width/2, j*Width+Width/2, image=wall_pic)
    for a in list(activs.values()):
        for (i,j) in a :
            item_grid[i][j] = board.create_image(i*Width+Width/2, j*Width+Width/2, image=activ_pic)
    for d in list(deactivs.values()):
        for (i,j) in d:
            item_grid[i][j] = board.create_image(i*Width+Width/2, j*Width+Width/2, image=deactiv_pic)

def move_bot(new_x, new_y):
    global player, x, y, walk_reward, robot, restart, last
    if (new_x >= 0) and (new_x < x) and (new_y >= 0) and (new_y < y) and not ((new_x, new_y) in walls):
        board.coords(robot, new_x*Width+Width/2, new_y*Width+Width/2)
        player = (new_x, new_y)
    move_hazards()
    # Check for goal or hazard to restart
    if player in goals:
        restart = True
        print('\n******Success******')
    for k,v in hazards.items():
        if (player == v[hazard_ind[k]]) or ((player == v[hazard_ind[k] - hazard_dir[k]]) and (v[hazard_ind[k]] == last)):
            restart = True
            print('\n******Failure******')
    last = player

def move_hazards():
    global player, score, robot, restart, activs, deactivs, xactivs, xdeactivs, hazards, hazard_ind, hazard_dir
    for k,v in hazards.items():

        # If the hazard is at either end of its list of locations, change direction
        if hazard_ind[k] + 1  == len(hazards[k]) :
            hazard_dir[k] = -1
        elif hazard_ind[k] == 0 :
            hazard_dir[k] = 1
        
        # Gets current location and next location
        (curr_x, curr_y) = v[hazard_ind[k]]
        (new_x, new_y) = v[hazard_ind[k] + hazard_dir[k]]

        # Increments hazard index in correct direction
        hazard_ind[k] = hazard_ind[k] + hazard_dir[k]
        
        # Modify the grid to show changes
        item_grid[new_x][new_y] = board.create_image(new_x*Width+Width/2, new_y*Width+Width/2, image=hazard_pic)
        board.delete(item_grid[curr_x][curr_y])
        item_grid[curr_x][curr_y] = 0

        grid[curr_y][curr_x] = '0'
        grid[new_y][new_x] = '4'

def restart_game():
    global player, score, robot, restart, activs, deactivs, xactivs, xdeactivs, hazards, hazard_ind, hazard_dir, item_grid, grid
    player = start
    score = 1
    restart = False
    board.coords(robot, start[0]*Width+Width/2, start[1]*Width+Width/2)
    for k,v in xactivs.copy().items() :# k = key (channel of activator), v = array of locations (x,y) for channel
        for x in v:
            (i,j) = x
            grid[i][j] = '5'
            item_grid[i][j] = board.create_image(i*Width+Width/2, j*Width+Width/2, image=activ_pic)
        activs[k] = xactivs.pop(k)
        for x in xdeactivs[k]:
            (i,j) = x
            grid[i][j] = '6'
            item_grid[i][j] = board.create_image(i*Width+Width/2, j*Width+Width/2, image=deactiv_pic)
        deactivs[k] = xdeactivs.pop(k)
    # Hazards reset to position 1
    for k,v in hazards.items():
        # Gets current location and next location
        (curr_x, curr_y) = v[hazard_ind[k]]
        (new_x, new_y) = v[0]
        hazard_dir[k] = 1
        hazard_ind[k] = 0
        
        # Modify the grid to show changes
        item_grid[new_x][new_y] = board.create_image(new_x*Width+Width/2, new_y*Width+Width/2, image=hazard_pic)
        board.delete(item_grid[curr_x][curr_y])
        item_grid[curr_x][curr_y] = 0

        grid[curr_x][curr_y] = '0'
        grid[new_x][new_y] = '4'


visualize_grid()
robot = board.create_image(start[0]*Width+Width/2, start[1]*Width+Width/2, image=agent_pic)

board.pack(side=LEFT)

################# Control widgets ##################
panel = Frame(master)
panel.pack(side=RIGHT)
Label(text="Controls\n", font="Verdana 12 bold").pack()

# Play/Pause Toggle
q1frame = Frame(master)
q1frame.pack()
b1 = Button(text="Play / Pause")

rb = Button(text="Restart")

def printName(event):
    global flag
    flag = not flag

def restartButton(event) :
    global restart
    restart = True
    
b1.bind("<Button-1>", printName)
rb.bind("<Button-1>", restartButton)
b1.pack()
rb.pack()

#   Sliders for speed and Epsilon
q3frame = Frame(master)
q3frame.pack()
w1 = Scale(q3frame, from_=1, to=10, orient=HORIZONTAL)
w1.pack(side=LEFT)
Label(text="Speed").pack()

################# Q Learning widgets ##################

separator = Frame(height=2, bd=1, relief=SUNKEN)
separator.pack(fill=X, padx=2, pady=2)

Label(text="Q Learning Parameters\n", font="Verdana 12 bold").pack()

# Discount text entry and button
qframe = Frame(master)
qframe.pack()
e = Entry(qframe, width=5)
e.pack(side=LEFT)
e.insert(0, "0.5")

discount = 0.5

def getDiscount(event):
    global discount
    discount = float(e.get())


b3 = Button(qframe, text="Discount")
b3.bind("<Button-1>", getDiscount)
b3.pack(side=LEFT)


#  Change start panel
q2frame = Frame(master)
q2frame.pack()


def setStart(event):
    global start
    new_start = (int(x_entry.get()), int(y_entry.get()))
    if new_start not in walls:
        start = new_start

b4 = Button(q2frame, text="Change Start")
b4.bind("<Button-1>", setStart)

x_entry = Entry(q2frame, width=4)
x_entry.pack(side=LEFT)
x_entry.insert(0, str(start[0]))
y_entry = Entry(q2frame, width=4)
y_entry.pack(side=LEFT)
y_entry.insert(0, str(start[1]))

b4.pack(side=LEFT)
Label(text="").pack()


# Exploration bar
q4frame = Frame(master)
q4frame.pack()
w2 = Scale(q4frame, from_=0.0, to=0.8, orient=HORIZONTAL, resolution=0.05)
w2.set(0.25)
w2.pack()
Label(text="Epsilon").pack()
Label(text="").pack()

def begin():
    global flag
    master.mainloop()
    flag = None
    time.sleep(0.1)