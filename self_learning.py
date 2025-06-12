import time
import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os

class SelfLearningBot:
    def __init__(self):
        self.model = LogisticRegression()  # Logistic regression for classification
        self.data_file = "trade_data.json"  # File to store trade data for training
        self.trade_data = self.load_trade_data()  # Load previous trade data
        self.train_model()  # Train the model on the current data

    def load_trade_data(self):
        """Load trade data from the file."""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                return json.load(f)
        else:
            return []

    def save_trade_data(self):
        """Save trade data to the file for later retraining."""
        with open(self.data_file, "w") as f:
            json.dump(self.trade_data, f, indent=2)

    def collect_trade_features(self, trade):
        """Extract features from a trade. Example: confidence, wallet success rate, etc."""
        return [
            trade['confidence'],
            trade['wallet_success_rate'],
            trade['price_change']
        ]

    def train_model(self):
        """Train the model based on existing trade data."""
        if len(self.trade_data) > 1:
            features = [self.collect_trade_features(t) for t in self.trade_data]
            labels = [t['success'] for t in self.trade_data]  # 1 for success, 0 for failure

            X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

            self.model.fit(X_train, y_train)  # Train the model

            # Evaluate the model
            predictions = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)
            print(f"Model accuracy: {accuracy * 100:.2f}%")

    def predict_trade_success(self, trade):
        """Predict the success of a new trade."""
        features = np.array(self.collect_trade_features(trade)).reshape(1, -1)
        prediction = self.model.predict(features)

        return prediction[0]  # 1 for success, 0 for failure

    def update_with_new_data(self, trade):
        """Update the model with new trade data."""
        self.trade_data.append(trade)
        self.save_trade_data()  # Save the updated data
        self.train_model()  # Retrain the model periodically

    def run_self_learning_loop(self):
        """Run the self-learning loop."""
        while True:
            print("Running self-learning loop...")

            # Example: Collect new trade data (you can customize this logic)
            new_trade = {
                "confidence": 90,  # Example confidence
                "wallet_success_rate": 80,  # Example wallet success rate
                "price_change": 2.0,  # Example price change
                "success": 1  # 1 for success, 0 for failure (based on past data)
            }

            # Update the model with new data
            self.update_with_new_data(new_trade)

            time.sleep(300)  # Wait for 5 minutes before the next cycle

# Create a singleton instance
bot = SelfLearningBot()

# Export the run_self_learning_loop function at module level
def run_self_learning_loop():
    bot.run_self_learning_loop()