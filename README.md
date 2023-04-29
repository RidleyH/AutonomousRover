# AutonomousRover

AutonomousRover is a Python program that navigates a rover autonomously through a field of obstacles in a simulated environment using LiDAR and positioning data. This project is built on top of the Gazebo simulation environment and uses the qset_lib Python library to interact with it.

## Project Structure

The project consists of several files:

- `mobile_data_collection.py`: opens a GUI in which a human user only sees information available to the rover through the LiDAR sensors and heading data. The user can control the rover through the obstacles towards randomly assigned target coordinates. Each time the user inputs a new direction for the rover to travel in, the GUI saves all of the LiDAR and positioning data to the `training_data.csv` file.
- `stationary_data_collection.py`: opens a GUI in which a human user only sees information available to the rover through the LiDAR sensors and heading data. The user can decide the rover's next heading given a set of obstacles. Each time the user inputs a direction for the rover to travel in, the GUI saves all of the LiDAR and positioning data to the `training_data.csv` file and randomly assigns new target coordinates. The rover does not move and sees the exact same environment every iteration. This strategy is useful for addressing specific situations in which the existing neural network malfunctions and requires additional training.
- `train_network.py`: uses the human user data stored in the `training_data.csv` file to train a neural network using scikit-learn and saves it to the `model.joblib` file. The neural network takes an input of the difference from the rover's current heading to the heading towards the target as well as 30 inputs of all LiDAR values, and returns an output of the recommended next heading for the rover.
- `main.py`: generates random target coordinates, loads the `model.joblib` file as the neural network, and maneuvers the rover towards it moving 1 meter at a time, reevaluating the rover's heading using the neural network each time.

## Credits

This project was developed by Ridley Horton as part of a semester long engineering project. This project uses the qset_lib Python library developed by the Queens Space Engineering Team specifically for interacting with Gazebo using Python.

## License

This project is licensed under the MIT License.

