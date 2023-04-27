import Tkinter as tk
import math
import random
from qset_lib import Rover
from time import sleep
import signal
import csv

window_width_scale = 0.33
window_height_scale = 0.5

rover = Rover()
rover.send_command(0, 0)


root = tk.Tk()
root.title("Testing Environment")

w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (window_width_scale*w, window_height_scale*h))
root.update_idletasks()

canvas_width = root.winfo_width()
canvas_height = root.winfo_height()
origin_x = canvas_width / 2
origin_y = canvas_height*9 / 10
RADIUS_METER = canvas_height/20
RADIUS = RADIUS_METER*15

NUM_LINES = 30
degree_sign = u'\N{DEGREE SIGN}'

canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
canvas.pack()

canvas.create_arc(origin_x - RADIUS, origin_y - RADIUS, origin_x + RADIUS, origin_y + RADIUS,
                  start=0, extent=180, style=tk.ARC, width=2)

canvas.create_arc(origin_x - RADIUS_METER*1, origin_y - RADIUS_METER*1, origin_x + RADIUS_METER*1, origin_y + RADIUS_METER*1,
                  start=0, extent=180, style=tk.ARC, width=2)

random_angle = random.uniform(math.pi/8, math.pi*7/8)
target_x = math.sin(random_angle) * 30
target_y = math.cos(random_angle) * 30
print('Target: ' + str(target_x) + ',' + str(target_y))

if target_y - rover.y == 0:
    target_y += 0.1
target_heading = -1*math.atan((target_x - rover.x)/(target_y - rover.y))*180/math.pi
if target_heading < 0:
    target_heading += 180
target_heading -= rover.heading
target_heading = target_heading*math.pi/180

def faceTarget():
    dx = target_x - rover.x
    dy = target_y - rover.y
    angle_to_target = math.atan2(dy, dx)
    
    heading_diff = angle_to_target - math.radians(rover.heading)
    if heading_diff > math.pi:
        heading_diff -= 2 * math.pi
    elif heading_diff < -math.pi:
        heading_diff += 2 * math.pi
    heading_diff = heading_diff*180/math.pi

line_dict = {}
lidar_data = []
while len(lidar_data) != 30:
    lidar_data = [max(min(x, 15), 0) for x in rover.laser_distances]
buttonFunction_dict = {}    
button_dict = {}
for i in range(NUM_LINES):
    line_length = lidar_data[i] * RADIUS_METER
    angle = (math.pi / (NUM_LINES-1)) * i
    x1 = origin_x
    y1 = origin_y
    x2 = origin_x + line_length * math.cos(angle)
    y2 = origin_y - line_length * math.sin(angle)
    line_dict.update({i:canvas.create_line(x1, y1, x2, y2, fill='blue', width=2)})

    def f(i=i):
        global target_x, target_y
        def updateTargetLine():
            global target_y
            if target_y - rover.y == 0:
                target_y += 0.1
            target_heading = -1*math.atan((target_x - rover.x)/(target_y - rover.y))*180/math.pi
            if target_heading < 0:
                target_heading += 180
            target_heading -= rover.heading
            target_heading = target_heading*math.pi/180
            canvas.coords(targetLine, origin_x, origin_y, origin_x + RADIUS_METER * 17 * math.cos(target_heading), origin_y - RADIUS_METER * 17 * math.sin(target_heading))
            return

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
        
        def saveData(row_list):
            with open('training_data.csv', 'a') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(row_list)
            return
        
        lidar_data = [max(min(x, 15), 0) for x in rover.laser_distances]
        if target_y - rover.y == 0:
            target_y += 0.1
        target_heading = -1*math.atan((target_x - rover.x)/(target_y - rover.y))*180/math.pi
        if target_heading < 0:
            target_heading += 180
        target_heading -= rover.heading
        input_heading = ((math.pi / (NUM_LINES-1)) * i)*180/math.pi
        saveData([target_heading] + lidar_data + [input_heading])
        print([target_heading] + lidar_data + [input_heading])
        sleep(0.1)
        random_angle = random.uniform(math.pi/8, math.pi*7/8)
        target_x = math.sin(random_angle) * 30
        target_y = math.cos(random_angle) * 30
        print('Target: ' + str(target_x) + ',' + str(target_y))
        updateLidarLines()
        updateTargetLine()
        canvas.update_idletasks()
    buttonFunction_dict.update({i:f})
    button_dict.update({i:tk.Button(root, text=str(int(angle*180/math.pi))+degree_sign, command=buttonFunction_dict[i])})
    canvas.create_window(origin_x + RADIUS_METER * 15.5 * math.cos(angle), origin_y - RADIUS_METER * 15.5 * math.sin(angle), window=button_dict[i])

targetLine = canvas.create_line(origin_x, origin_y, origin_x + RADIUS_METER * 17 * math.cos(target_heading), origin_y - RADIUS_METER * 17 * math.sin(target_heading), fill='green', width=2)

root.mainloop()

