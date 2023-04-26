import Tkinter as tk
import math
import random
from qset_lib import Rover
from time import sleep
import signal
import csv


window_width_scale = 1
window_height_scale = 1

target_x = random.randint(50, 60)
target_y = random.randint(-20, 20)


rover = Rover()
rover.send_command(0, 0)


# Create the GUI window
root = tk.Tk()
root.title("Testing Environment")

# Maximize the window to fill the screen
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (window_width_scale*w, window_height_scale*h))
root.update_idletasks()

# Calculate canvas dimensions and origin
canvas_width = root.winfo_width()
canvas_height = root.winfo_height()
origin_x = canvas_width / 2
origin_y = canvas_height*9 / 10
RADIUS_METER = canvas_height/20
RADIUS = RADIUS_METER*15

NUM_LINES = 30
degree_sign = u'\N{DEGREE SIGN}'

# Create the canvas for drawing
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
canvas.pack()

# Draw the semicircle
canvas.create_arc(origin_x - RADIUS, origin_y - RADIUS, origin_x + RADIUS, origin_y + RADIUS,
                  start=0, extent=180, style=tk.ARC, width=2)

canvas.create_arc(origin_x - RADIUS_METER*1, origin_y - RADIUS_METER*1, origin_x + RADIUS_METER*1, origin_y + RADIUS_METER*1,
                  start=0, extent=180, style=tk.ARC, width=2)

target_heading = -1*math.atan((target_x - rover.x)/(target_y - rover.y))*180/math.pi
if target_heading < 0:
    target_heading += 180
target_heading -= rover.heading
# print(target_heading)
target_heading = target_heading*math.pi/180

print('Target: ' + str(target_x) + ',' + str(target_y))

def updateLidarLines():
    lidar_data = [max(min(x, 15), 0) for x in rover.laser_distances]
    for i in range(NUM_LINES):
        line_length = lidar_data[i] * RADIUS_METER
        angle = (math.pi / (NUM_LINES-1)) * i
        x1 = origin_x
        y1 = origin_y
        x2 = origin_x + line_length * math.cos(angle)
        y2 = origin_y - line_length * math.sin(angle)
        canvas.coords(line_dict[i], x1, y1, x2, y2)
    return

def rotateRover(heading_change):
    currentHeading = rover.heading
    if heading_change > 0:
        left_side_speed = -1
        right_side_speed = 1
        while rover.heading < currentHeading + heading_change:
            # print(rover.heading)
            rover.send_command(left_side_speed, right_side_speed)
            sleep(0.01)
    elif heading_change < 0:
        left_side_speed = 1
        right_side_speed = -1
        while rover.heading > currentHeading + heading_change:
            # print(rover.heading)
            rover.send_command(left_side_speed, right_side_speed)
            sleep(0.01)

    rover.send_command(0, 0)
    return

def moveRover(distance):
    x1, y1 = rover.x, rover.y
    while math.sqrt((x1 - rover.x)**2 + (y1 - rover.y)**2) < distance:
        rover.send_command(5, 5)
        sleep(0.01)
    rover.send_command(0,0)
    return
    
def updateTargetLine():
    target_heading = -1*math.atan((target_x - rover.x)/(target_y - rover.y))*180/math.pi
    if target_heading < 0:
        target_heading += 180
    # print(target_heading)
    target_heading -= rover.heading
    target_heading = target_heading*math.pi/180
    canvas.coords(targetLine, origin_x, origin_y, origin_x + RADIUS_METER * 17 * math.cos(target_heading), origin_y - RADIUS_METER * 17 * math.sin(target_heading))

def saveData(row_list):
    # open CSV file for appending
    with open('training_data.csv', 'a') as csvfile:
        # create CSV writer object
        writer = csv.writer(csvfile)
        # write new row to CSV file
        writer.writerow(row_list)

line_dict = {}
lidar_data = []
while len(lidar_data) != 30:
    lidar_data = [max(min(x, 15), 0) for x in rover.laser_distances]
buttonFunction_dict = {}    
button_dict = {}
# Draw the blue lines
for i in range(NUM_LINES):
    line_length = lidar_data[i] * RADIUS_METER
    angle = (math.pi / (NUM_LINES-1)) * i
    x1 = origin_x
    y1 = origin_y
    x2 = origin_x + line_length * math.cos(angle)
    y2 = origin_y - line_length * math.sin(angle)
    line_dict.update({i:canvas.create_line(x1, y1, x2, y2, fill='blue', width=2)})

    def f(i=i):
        lidar_data = [max(min(x, 15), 0) for x in rover.laser_distances]
        target_heading = -1*math.atan((target_x - rover.x)/(target_y - rover.y))*180/math.pi
        if target_heading < 0:
            target_heading += 180
        target_heading -= rover.heading
        input_heading = ((math.pi / (NUM_LINES-1)) * i)*180/math.pi
        saveData([target_heading] + lidar_data + [input_heading])
        # print(input_heading)
        # print(target_heading)
        # print(lidar_data)
        rotateRover(input_heading - 90)
        moveRover(1)
        updateLidarLines()
        updateTargetLine()
    buttonFunction_dict.update({i:f})
    button_dict.update({i:tk.Button(root, text=str(int(angle*180/math.pi))+degree_sign, command=buttonFunction_dict[i])})
    canvas.create_window(origin_x + RADIUS_METER * 15.5 * math.cos(angle), origin_y - RADIUS_METER * 15.5 * math.sin(angle), window=button_dict[i])

targetLine = canvas.create_line(origin_x, origin_y, origin_x + RADIUS_METER * 17 * math.cos(target_heading), origin_y - RADIUS_METER * 17 * math.sin(target_heading), fill='green', width=2)

# Start the GUI event loop
root.mainloop()

