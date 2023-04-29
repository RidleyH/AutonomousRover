import pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
import joblib

# Load the training data from the CSV file
train_data = pd.read_csv('training_data_final.csv',header=None)

# Split the data into input features (X) and output target (y)
X_train = train_data.iloc[:, :31].values
y_train = train_data.iloc[:, 31].values

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.2)

# Initialize a multilayer perceptron regressor model with 16 neurons in the hidden layer, using the lbfgs solver for optimization, alpha regularization parameter of 10^-4, a maximum of 10,000 iterations and a fixed random state for reproducibility.
model = MLPRegressor(hidden_layer_sizes=(16), max_iter=10000, solver='lbfgs', alpha=10**(-4), random_state=42)

# Train the neural network on the training data
model.fit(X_train, y_train)

# Evaluate the performance of the neural network on the testing data
score = model.score(X_test, y_test)
print("Test score: {:.2f}".format(score))

# Save the trained model to a file
joblib.dump(model, "model.joblib")
