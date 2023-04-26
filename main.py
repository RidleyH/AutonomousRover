import Tkinter as tk
import math
import random
from qset_lib import Rover
from time import sleep
import numpy as np
import joblib
import pandas as pd

def face_target(target_x, target_y):
    # Calculate the angle to the target in radians
    x_change = target_x - rover.x
    y_change = target_y - rover.y
    target_angle = math.atan2(y_change, x_change)

    # Calculate the change in heading to face the target
    heading_difference = target_angle - math.radians(rover.heading)
    heading_difference = (heading_difference + math.pi) % (2 * math.pi) - math.pi
    heading_difference_degrees = math.degrees(heading_difference)

    # Rotate the rover to face the target
    rotate_rover(heading_difference_degrees / 2)
    rotate_rover(heading_difference_degrees / 2)

def calculate_target_heading(target_x, target_y):
    # Calculate the angle to the target in degrees
    x_diff = target_x - rover.x
    y_diff = target_y - rover.y
    target_angle = math.degrees(math.atan2(y_diff, x_diff))

    # Calculate the change in heading to face the target
    target_heading_difference = target_angle - rover.heading

    # Normalize the target heading difference to be between -180 and 180 degrees
    if target_heading_difference > 180:
        target_heading_difference -= 360
    elif target_heading_difference <= -180:
        target_heading_difference += 360

    # Add 90 degrees to the target heading difference
    return target_heading_difference + 90

def rotate_rover(heading_change):
    # calculate the target heading in degrees from -180 to 180
    target_heading = ((rover.heading + heading_change) % 360)
    
    # calculate the angular difference between current and target headings
    angle_diff = target_heading - rover.heading
    if angle_diff > 180:
        angle_diff -= 360
    elif angle_diff < -180:
        angle_diff += 360
    
    # calculate the direction and speed of the turn
    direction = 1 if angle_diff < 0 else -1
    lidar_index = 1 if angle_diff < 0 else 28
    
    # set the differential steering speeds to rotate the rover
    while (abs(angle_diff) > 1) & ([max(min(x, 15), 0) for x in rover.laser_distances][lidar_index] > 0.6):  # adjust the threshold as needed
        rover.send_command(direction, -direction)
        angle_diff = target_heading - rover.heading
        if angle_diff > 180:
            angle_diff -= 360
        elif angle_diff < -180:
            angle_diff += 360
        # print([max(min(x, 15), 0) for x in rover.laser_distances][lidar_index])
        sleep(0.01)
    
    # stop the rover when the desired heading is reached
    rover.send_command(0, 0)

def moveRover(move_distance):
    x1, y1 = rover.x, rover.y
    while (math.sqrt((x1 - rover.x)**2 + (y1 - rover.y)**2) < move_distance):
        lidar_distances = [max(min(x, 15), 0) for x in rover.laser_distances]
        danger_distances = [x1_elem - x2_elem for (x1_elem, x2_elem) in zip(lidar_distances, safety_distances)]
        # print(danger_distances)
        if ((min(danger_distances)) < 0):
            # print("DANGER")
            if danger_distances.index(min(danger_distances)) < 14.5:
                while ((min([x1_elem - x2_elem for (x1_elem, x2_elem) in zip([max(min(x, 15), 0) for x in rover.laser_distances], safety_distances)])) < 0) & ([max(min(x, 15), 0) for x in rover.laser_distances][28] > 0.6):
                    rover.send_command(-1,1)
                    # print([max(min(x, 15), 0) for x in rover.laser_distances][28])
                    sleep(0.01)
            else:
                while ((min([x1_elem - x2_elem for (x1_elem, x2_elem) in zip([max(min(x, 15), 0) for x in rover.laser_distances], safety_distances)])) < 0) & ([max(min(x, 15), 0) for x in rover.laser_distances][1] > 0.6):
                    rover.send_command(1,-1)
                    # print([max(min(x, 15), 0) for x in rover.laser_distances][1])
                    sleep(0.01)
            rover.send_command(0,0)
            # print("safe")
            continue
        rover.send_command(5, 5)
        sleep(0.01)
    rover.send_command(0,0)
    return


rover = Rover()
rover.send_command(0, 0)

# Load the training data from the CSV file
train_data = pd.read_csv('training_data_final.csv',header=None)

lidar_data = [max(min(x, 15), 0) for x in rover.laser_distances]
while len(lidar_data) != 30:
    lidar_data = [max(min(x, 15), 0) for x in rover.laser_distances]

# target_x = random.randint(20, 25)
target_x = 15
target_y = random.randint(-10, 10)
print('Random Target: (' + str(target_x) + ', ' + str(target_y) + ')')

base = [abs(x*180/29 - 90)*math.pi/180 for x in list(range(0,30))]
front_distances = [0.6/math.cos(x) for x in base[7:23]]
right_distances = [(0.6)/math.sin(x) for x in base[0:7]]
left_distances = [(0.6)/math.sin(x) for x in base[23:30]]
safety_distances = right_distances + front_distances + left_distances

face_target(target_x, target_y)
model = joblib.load("model.joblib")
while math.sqrt((target_x - rover.x)**2 + (target_y - rover.y)**2) > 1:
    lidar_data = [max(min(x, 15), 0) for x in rover.laser_distances]
    target_heading = calculate_target_heading(target_x, target_y)
    all_data = [target_heading]+lidar_data
    model_heading = model.predict([all_data])[0]
    print('New Heading: ' + str(round(model_heading, 2)))
    rotate_rover(model_heading - 90)
    moveRover(1)


# time_total = 0
# while (time_total < 60):
#     lidar_distances = [max(min(x, 15), 0) for x in rover.laser_distances]
#     danger_distances = [x1_elem - x2_elem for (x1_elem, x2_elem) in zip(lidar_distances, safety_distances)]
#     # print(danger_distances)
#     if ((min(danger_distances)) < 0):
#         print("DANGER")
#         continue
#     print("safe")
#     sleep(0.01)
#     time_total += 0.01

# moveRover(5)