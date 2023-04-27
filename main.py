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
    
    # calculate the direction  of the turn
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
        sleep(0.01)
    
    # stop the rover when the desired heading is reached
    rover.send_command(0, 0)

def move_rover(move_distance):
    # Get current position of the rover
    x1, y1 = rover.x, rover.y

    # Move rover while it is less than the target distance
    while (math.sqrt((x1 - rover.x)**2 + (y1 - rover.y)**2) < move_distance):
        lidar_distances = [max(min(x, 15), 0) for x in rover.laser_distances]
        danger_distances = [x1_elem - x2_elem for (x1_elem, x2_elem) in zip(lidar_distances, safety_distances)]
        
        # If the minimum danger distance is less than zero, avoid obstacle
        if ((min(danger_distances)) < 0):
            if danger_distances.index(min(danger_distances)) < 14.5:
                # Avoid obstacle to the right
                while ((min([x1_elem - x2_elem for (x1_elem, x2_elem) in zip([max(min(x, 15), 0) for x in rover.laser_distances], safety_distances)])) < 0) & ([max(min(x, 15), 0) for x in rover.laser_distances][28] > 0.6):
                    rover.send_command(-1,1)
                    sleep(0.01)
            else:
                # Avoid obstacle to the left
                while ((min([x1_elem - x2_elem for (x1_elem, x2_elem) in zip([max(min(x, 15), 0) for x in rover.laser_distances], safety_distances)])) < 0) & ([max(min(x, 15), 0) for x in rover.laser_distances][1] > 0.6):
                    rover.send_command(1,-1)
                    sleep(0.01)
            # Stop rover after avoiding obstacle
            rover.send_command(0,0)
            continue

        # Move the rover forward
        rover.send_command(5, 5)
        sleep(0.01)

    # Stop rover after reaching target distance
    rover.send_command(0,0)
    return


# Create new river object
rover = Rover()

# Initialize lidar data and wait until all 30 distances are received
lidar_data = [max(min(x, 15), 0) for x in rover.laser_distances]
while len(lidar_data) != 30:
    lidar_data = [max(min(x, 15), 0) for x in rover.laser_distances]

# Calculate safety distances 
base = [abs(x*180/29 - 90)*math.pi/180 for x in list(range(0,30))]
front_distances = [0.6/math.cos(x) for x in base[7:23]]
right_distances = [(0.6)/math.sin(x) for x in base[0:7]]
left_distances = [(0.6)/math.sin(x) for x in base[23:30]]
safety_distances = right_distances + front_distances + left_distances

# Load the neural network model
model = joblib.load("model.joblib")

# Repeat 10 times
for i in range(10):
    coefficient = (-1)**i

    # Set a new random target
    # target_x = random.randint(20, 25)
    target_x = 13 * coefficient
    target_y = random.randint(-8, 8)
    print('New Random Target: (' + str(target_x) + ', ' + str(target_y) + ')')

    # Face the new target
    face_target(target_x, target_y)

    # Move towards the target while adjusting heading based on the neural network model
    while math.sqrt((target_x - rover.x)**2 + (target_y - rover.y)**2) > 1:
        # Update lidar data and calculate the target heading
        lidar_data = [max(min(x, 15), 0) for x in rover.laser_distances]
        target_heading = calculate_target_heading(target_x, target_y)

        # Combine the target heading and lidar data and decide the new heading with the model
        all_data = [target_heading]+lidar_data
        model_heading = model.predict([all_data])[0]
        print('New Heading: ' + str(round(model_heading, 2)))

        # rotate and move the rover based on the new heading
        rotate_rover(model_heading - 90)
        move_rover(1)