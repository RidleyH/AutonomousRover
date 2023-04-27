# AutonomousRover

This project consists of an autonomous rover controlled by a Python script called `main.py`. The rover is simulated in the Gazebo simulation environment, and it can be interacted with using Python 2.7.17.

## Installation

1. Clone this repository using `git clone https://github.com/RidleyH/AutonomousRover.git`
2. Install the required dependencies listed above.
3. Navigate to the project directory using `cd autonomousrover`.
4. Run the `main.py` script using `python main.py`.

## Project Overview

The rover is controlled by a neural network that was trained on human pathfinding data in the `training_final_data.csv` file. This CSV file was created using two other scripts: `mobileDataCollection.py` and `stationaryDataCollection.py`. These scripts open up a GUI for the user to control the rover, allowing them to collect data on the rover's movements.

The `trainNetwork.py` script uses scikit-learn to create, train, and save the neural network to a file called `model.joblib`.

The `main.py` script is the main control script for the rover. It loads the neural network from the `model.joblib` file and controls the rover's movements based on the output of the neural network.

## Usage

Once you have installed the required dependencies, cloned the repository and opened Gazebo, navigate to the project directory and run `python main.py`. The rover will begin to move based on the output of the neural network.

You can also modify the code in the `main.py` script to change the behavior of the rover. For example, you could modify the neural network or change the rover's movement parameters.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.
