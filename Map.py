import time
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import simpledialog, messagebox
from PIL import Image
from PIL import ImageTk
import os

master = Tk()
master.wm_title("Welcome to Treasure Hunters Inc.")

result = messagebox.askyesno(
    "Welcome to Grid World", "Do you want to create a new map?")

grid = []
path = os.getcwd() + "/images/"

triangle_size = 0.3
text_offset = 17
cell_score_min = -0.2
cell_score_max = 0.2
Width = 70
actions = ["up", "left", "down", "right", "wait"]
print_states = False

if not result:
    filename = askopenfilename(title="Select map file")
    print(filename)
    if len(filename) == 0:
        messagebox.showwarning('Error', 'No map selected!')
        quit()
    ins = open(filename, "r")
    for line in ins:
        number_strings = line.split()
        numbers = [int(n) for n in number_strings]
        grid.append(numbers)
    (x, y) = (len(grid[0]), len(grid))
    board = Canvas(master, width=x*Width, height=y*Width)
else:
    x_str = simpledialog.askstring('Size', 'Enter grid size')
    if x_str == None:
        messagebox.showwarning('Error', 'No size found!')
        quit()
    x = int(x_str)
    (x, y) = (x, x)
    path = os.getcwd() + "/images/"
    wall_pic = ImageTk.PhotoImage(image=Image.open(path+'brick.png'))
    goal_pic = ImageTk.PhotoImage(image=Image.open(path+'diamond.png'))
    hazard_pic = ImageTk.PhotoImage(image=Image.open(path+'zombie.png'))
    agent_pic = ImageTk.PhotoImage(image=Image.open(path+'steve.png'))
    activ_pic = ImageTk.PhotoImage(image=Image.open(path+'lever.jpg'))
    deact_pic = ImageTk.PhotoImage(image=Image.open(path+'piston.jpg'))

    board = Canvas(master, width=x*Width, height=y*Width)
    start_count = 0
    goal_count = 0

    for i in range(x):
        for j in range(y):
            board.create_rectangle(
                i*Width, j*Width, (i+1)*Width, (j+1)*Width, fill="white", width=1)

    board.pack(side=LEFT)
    grid = [[0 for row in range(x)] for col in range(y)]
    item_grid = [[0 for row in grid[0]] for col in grid]

    var = StringVar(master)
    var.set("Select item")

    option = OptionMenu(master, var, "start", "walls", "goal", "hazard", "activator", "deactivatable")
    option.pack()

    robot = 0


    '''
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
        x, y = int(event.x/75), int(event.y/75)
        if item_grid[y][x] == 0:
            if var.get() == "walls":
                item_grid[y][x] = board.create_image(
                    x*Width+35, y*Width+35, image=wall_pic)
                grid[y][x] = 1
            elif var.get() == "start":
                item_grid[y][x] = board.create_image(
                    x*Width+35, y*Width+35, image=agent_pic)
                grid[y][x] = 2
                start_count += 1
            elif var.get() == "goal":
                item_grid[y][x] = board.create_image(
                    x*Width+35, y*Width+35, image=goal_pic)
                grid[y][x] = 3
                goal_count += 1
            elif var.get() == "hazard":
                item_grid[y][x] = board.create_image(
                    x*Width+35, y*Width+35, image=hazard_pic)
                grid[y][x] = 4
            elif var.get() == "activator":
                item_grid[y][x] = board.create_image(
                    x*Width+35, y*Width+35, image=activ_pic)
                grid[y][x] = 5
            elif var.get() == "deactivatable":
                item_grid[y][x] = board.create_image(
                    x*Width+35, y*Width+35, image=deact_pic)
                grid[y][x] = 6

    board.bind('<Button-1>', create_item)

    def delete_item(event):
        global start_count, goal_count
        x, y = int(event.x/75), int(event.y/75)
        if item_grid[y][x] != 0:
            board.delete(item_grid[y][x])
            item_grid[y][x] = 0
            grid[y][x] = 0
            if var.get == "start":
                start_count -= 1
            elif var.get() == "goal":
                goal_count -= 1

    board.bind('<Button-3>', delete_item)
    Label(text="Instructions: \n1. Select item from dropdown\n2.Left click on grid cell to add\n3. Right click on grid cell to remove\n\n\n\nNote: Please close \nthis window after finished.", font="Verdana 12").pack(side=BOTTOM)
    master.mainloop()
    master = Tk()
    master.wm_title("Welcome to Treasure Hunters Inc.")
    board = Canvas(master, width=x*Width, height=y*Width)

    if start_count < 1:
        messagebox.showwarning('Error', 'No start found!')
        quit()
    elif goal_count < 1:
        messagebox.showwarning('Error', 'No goal found!')
        quit()

print(x, y)
walls = []
start = ()
specials = []
hazards = []
activs = []
deactivs = []

for i in range(y):
    for j in range(x):
        if grid[i][j] == 1:
            walls.append((j, i))
        if grid[i][j] == 2:
            start = (j, i)
        if grid[i][j] == 3:
            specials.append((j, i, "green", 1))
            goal = (j, i)
        if grid[i][j] == 4:
            specials.append((j, i, "red", -1))
            hazards.append((j, i))
            # Add activators and deactivators


player = start
tri_objects = {}
text_objects = {}
flag = True
restart = False

path = os.getcwd() + "/images/"
wall_pic = ImageTk.PhotoImage(image=Image.open(path+'wall.png'))
diamond_pic = ImageTk.PhotoImage(image=Image.open(path+'diamond.png'))
fire_pic = ImageTk.PhotoImage(image=Image.open(path+'monster.png'))
robot_pic = ImageTk.PhotoImage(image=Image.open(path+'robot.png'))

def visualize_grid():
    global specials, walls, Width, x, y, player
    for i in range(x):
        for j in range(y):
            board.create_rectangle(
                i*Width, j*Width, (i+1)*Width, (j+1)*Width, fill="white", width=1)
            # temp = {}
            # temp_val = {}
            # for action in actions:
            #     (temp[action], temp_val[action]
            #      ) = create_triangle(i, j, action)
            # tri_objects[(i, j)] = temp
            # text_objects[(i, j)] = temp_val
    for (i, j, c, w) in specials:
        # board.create_rectangle(i*Width, j*Width, (i+1)*Width, (j+1)*Width, fill=c, width=1)
        if w == -1:
            board.create_image(i*Width+35, j*Width+35, image=hazard_pic)
        else:
            board.create_image(i*Width+35, j*Width+35, image=goal_pic)
    for (i, j) in walls:
        # board.create_rectangle(i*Width, j*Width, (i+1)*Width, (j+1)*Width, fill="black", width=1)
        board.create_image(i*Width+35, j*Width+35, image=wall_pic)

def begin():
    global flag
    master.mainloop()
    flag = None
    time.sleep(0.1)
