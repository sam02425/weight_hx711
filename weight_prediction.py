import numpy as np
from scipy.optimize import curve_fit

class WeightPredictor:
    def __init__(self):
        self.model = None

    def train(self, sensor_readings, actual_weights):
        def model_func(x, a, b, c, d):
            return a * x[0] + b * x[1] + c * x[2] + d * x[3]

        popt, _ = curve_fit(model_func, sensor_readings.T, actual_weights)
        self.model = lambda x: model_func(x, *popt)

    def predict(self, sensor_readings):
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        return self.model(sensor_readings)

    def save_model(self, filename):
        if self.model is None:
            raise ValueError("Model not trained. Nothing to save.")
        np.save(filename, self.model)

    def load_model(self, filename):
        self.model = np.load(filename, allow_pickle=True).item()

def main():
    # Example usage
    predictor = WeightPredictor()

    # Generate some example data
    sensor_readings = np.random.rand(100, 4) * 1000  # 100 samples, 4 sensors
    actual_weights = np.sum(sensor_readings, axis=1) + np.random.randn(100) * 10  # Add some noise

    # Train the model
    predictor.train(sensor_readings, actual_weights)

    # Make a prediction
    new_reading = np.array([250, 300, 275, 225])
    predicted_weight = predictor.predict(new_reading)
    print(f"Predicted weight: {predicted_weight:.2f} grams")

    # Save and load the model
    predictor.save_model('weight_model.npy')
    predictor.load_model('weight_model.npy')

if __name__ == "__main__":
    main()