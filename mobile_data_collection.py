import Tkinter as tk
import math
import random
from qset_lib import Rover
from time import sleep
import signal
import csv

# Define function to update lidar lines on canvas
def update_lidar_lines():
    # Convert raw lidar data to line lengths in meters and set minimum and maximum range
    lidar_data = [max(min(x, 15), 0) for x in rover.laser_distances]

    # Iterate through each lidar line and update its position on the canvas
    for i in range(NUM_LINES):
        line_length = lidar_data[i] * RADIUS_METER
        angle = (math.pi / (NUM_LINES-1)) * i
        x1 = origin_x
        y1 = origin_y
        x2 = origin_x + line_length * math.cos(angle)
        y2 = origin_y - line_length * math.sin(angle)
        canvas.coords(line_dict[i], x1, y1, x2, y2)
    return

# Define function to rotate the rover by a given heading_change angle
def rotate_rover(heading_change):
    currentHeading = rover.heading

    # If need to rotate left
    if heading_change > 0:
        left_side_speed = -1
        right_side_speed = 1
        # Rotate the rover by sending commands to the motors and waiting until the desired heading is reached
        while rover.heading < currentHeading + heading_change:
            rover.send_command(left_side_speed, right_side_speed)
            sleep(0.01)

    # If need to rotate right
    elif heading_change < 0:
        left_side_speed = 1
        right_side_speed = -1
        # Rotate the rover by sending commands to the motors and waiting until the desired heading is reached
        while rover.heading > currentHeading + heading_change:
            rover.send_command(left_side_speed, right_side_speed)
            sleep(0.01)

    # Stop the rover
    rover.send_command(0, 0)
    return

# Define function to move the rover forward by a given distance in meters
def move_rover(distance):
    # Get initial position of the rover
    x1, y1 = rover.x, rover.y

    # Move the rover forward by sending commands to the motors and waiting until the desired distance is reached
    while math.sqrt((x1 - rover.x)**2 + (y1 - rover.y)**2) < distance:
        rover.send_command(5, 5)
        sleep(0.01)

    # Stop the rover
    rover.send_command(0,0)
    return

# Define function to update the target line on the canvas based on the position of the rover and the target
def update_target_line():
    # Calculate the heading to the target in radians and adjust for rover heading
    target_heading = -1*math.atan((target_x - rover.x)/(target_y - rover.y))*180/math.pi
    if target_heading < 0:
        target_heading += 180
    target_heading -= rover.heading
    target_heading = target_heading*math.pi/180
    # Update the position of the target line on the canvas
    canvas.coords(targetLine, origin_x, origin_y, origin_x + RADIUS_METER * 17 * math.cos(target_heading), origin_y - RADIUS_METER * 17 * math.sin(target_heading))

# Define function to save a row of data to a CSV file
def save_data(row_list):
    with open('training_data.csv', 'a') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(row_list)

# Create a Tkinter root object and set its title
root = tk.Tk()
root.title("Training Environment")
# Define the scale factors for the window dimensions and retrieve the screen width and height
window_width_scale = 1
window_height_scale = 1
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
# Set the window dimensions to be the width and height of the screen multiplied by the scale factors
root.geometry("%dx%d+0+0" % (window_width_scale*w, window_height_scale*h))
# Update the window idletasks to ensure that the window size is correctly set
root.update_idletasks()

# Set the canvas dimensions based on the window dimensions
canvas_width = root.winfo_width()
canvas_height = root.winfo_height()
# Define the origin point of the canvas (center bottom)
origin_x = canvas_width / 2
origin_y = canvas_height*9 / 10
# Define the radius of the circle that will represent the LiDAR lines on the canvas
RADIUS_METER = canvas_height/20
RADIUS = RADIUS_METER*15
NUM_LINES = 30

# Create a canvas object and set its dimensions to the size of the root window
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
# Pack the canvas object into the root window
canvas.pack()

# Create two arcs on the canvas representing the field of view of the LiDAR and the distance the rover moves in each step
canvas.create_arc(origin_x - RADIUS, origin_y - RADIUS, origin_x + RADIUS, origin_y + RADIUS,
                  start=0, extent=180, style=tk.ARC, width=2)
canvas.create_arc(origin_x - RADIUS_METER*1, origin_y - RADIUS_METER*1, origin_x + RADIUS_METER*1, origin_y + RADIUS_METER*1,
                  start=0, extent=180, style=tk.ARC, width=2)

# Initialize a new Rover object
rover = Rover()

# Generate random target coordinates
target_x = random.randint(50, 60)
target_y = random.randint(-20, 20)
# Print the target coordinates to the console
print('Target: ' + str(target_x) + ',' + str(target_y))

# Initialize an empty list to store the lidar data
lidar_data = []
# Loop until the lidar data contains 30 values
while len(lidar_data) != 30:
    # Get the latest lidar data from the rover and trim values to a maximum of 30 meters
    lidar_data = [max(min(x, 15), 0) for x in rover.laser_distances]

# Create empty dictionaries for lines, buttons, and button functions
line_dict = {}
button_dict = {}
buttonFunction_dict = {}
# Loop through each lidar reading to draw a line representing it on the canvas
for i in range(NUM_LINES):
    # Calculate the start and end locations of the line based on the lidar reading
    line_length = lidar_data[i] * RADIUS_METER
    angle = (math.pi / (NUM_LINES-1)) * i
    x1 = origin_x
    y1 = origin_y
    x2 = origin_x + line_length * math.cos(angle)
    y2 = origin_y - line_length * math.sin(angle)
    # Add the line to the line dictionary with its corresponding index
    line_dict.update({i:canvas.create_line(x1, y1, x2, y2, fill='blue', width=2)})

    # Create a button function for each line that saves the user input, moves the rover, and updates the canvas
    def f(i=i):
        lidar_data = [max(min(x, 15), 0) for x in rover.laser_distances]
        target_heading = -1*math.atan((target_x - rover.x)/(target_y - rover.y))*180/math.pi
        if target_heading < 0:
            target_heading += 180
        target_heading -= rover.heading
        input_heading = ((math.pi / (NUM_LINES-1)) * i)*180/math.pi
        save_data([target_heading] + lidar_data + [input_heading])
        rotate_rover(input_heading - 90)
        move_rover(1)
        update_lidar_lines()
        update_target_line()
        canvas.update_idletasks()

    # Add the button function to the button function dictionary with its corresponding index
    buttonFunction_dict.update({i:f})

    # Create a button for each line with its corresponding angle as the text
    degree_sign = u'\N{DEGREE SIGN}'
    button_dict.update({i:tk.Button(root, text=str(int(angle*180/math.pi))+degree_sign, command=buttonFunction_dict[i])})

    # Add the button to the canvas at the end of the line
    canvas.create_window(origin_x + RADIUS_METER * 15.5 * math.cos(angle), origin_y - RADIUS_METER * 15.5 * math.sin(angle), window=button_dict[i])

# Calculate the target heading angle in degrees
target_heading = -1*math.atan((target_x - rover.x)/(target_y - rover.y))*180/math.pi
# Normalize the target heading angle to be between 0 and 180 degrees
if target_heading < 0:
    target_heading += 180
# Adjust the target heading angle based on the current heading of the rover
target_heading -= rover.heading
target_heading = target_heading*math.pi/180
# Draw the target line on the canvas
targetLine = canvas.create_line(origin_x, origin_y, origin_x + RADIUS_METER * 17 * math.cos(target_heading), origin_y - RADIUS_METER * 17 * math.sin(target_heading), fill='green', width=2)

# Start the mainloop for the tkinter window
root.mainloop()

