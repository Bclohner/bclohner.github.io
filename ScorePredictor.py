import numpy as np
import matplotlib.pyplot as plt
import csv
import os
from sklearn.linear_model import LinearRegression

# ---------------------------------------------------------
# PEAK BONUS (Recovery Week)
# ---------------------------------------------------------
PEAK_BONUS = 3

# ---------------------------------------------------------
# PATH TO YOUR CSV IN Documents/Website/Documents
# ---------------------------------------------------------
CSV_PATH = r"C:\Users\bcloh\Documents\Website\Documents\arrow_volume.csv"

# ---------------------------------------------------------
# LOAD YOUR CSV (arrow_volume.csv)
# ---------------------------------------------------------
def load_arrow_volume_csv(csv_path):
    """
    Loads your arrow_volume.csv file.
    Expands score pairs like "290,292" into two samples.
    """
    data = []

    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            arrows = int(row["arrows"])
            score_list = row["scores"].split(",")

            # Convert each score into its own training sample
            for s in score_list:
                score = float(s.strip())
                data.append((arrows, score))

    return data

# ---------------------------------------------------------
# TRAIN MODEL
# ---------------------------------------------------------
def train_model(past_data):
    X = np.array([[arrows] for arrows, score in past_data])
    y = np.array([score for arrows, score in past_data])

    model = LinearRegression()
    model.fit(X, y)
    return model

# ---------------------------------------------------------
# PREDICT SCORE
# ---------------------------------------------------------
def predict_score(model, arrow_volume, week_type="Base"):
    pred = model.predict([[arrow_volume]])[0]

    # Add peak bonus during Recovery Week
    if week_type == "Recovery":
        pred += PEAK_BONUS

    # Clamp to valid archery score range
    pred = max(0, min(pred, 300))

    return round(pred, 1)

# ---------------------------------------------------------
# VISUALIZATION
# ---------------------------------------------------------
def visualize_predictions(past_data, future_weeks, predictions):
    past_volumes = [d[0] for d in past_data]
    past_scores = [d[1] for d in past_data]

    future_volumes = [fw[0] for fw in future_weeks]
    future_scores = predictions

    plt.figure(figsize=(10, 6))

    plt.scatter(past_volumes, past_scores, color="blue", label="Past Scores", s=80)
    plt.scatter(future_volumes, future_scores, color="red", label="Predicted Scores", s=100)
    plt.plot(future_volumes, future_scores, color="red", linestyle="--", alpha=0.7)

    for (vol, week), score in zip(future_weeks, future_scores):
        if week == "Recovery":
            plt.scatter([vol], [score], color="gold", edgecolor="black", s=200)
            plt.annotate("Peak Week", (vol, score), textcoords="offset points", xytext=(10, 10))

    plt.title("Archery Score Prediction Based on Arrow Volume")
    plt.xlabel("Arrow Volume")
    plt.ylabel("Score")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def generate_next_cycle(base_volume): # Generates a 4-week cycle with +10% progression.
    """
    Generates a 4-week cycle with +10% progression.
    Returns a list of (arrow_volume, week_type).
    """
    next_base = round(base_volume * 1.10)

    cycle = [
        (next_base, "Base"),
        (round(next_base * 1.10), "+10"),
        (round(next_base * 1.20), "Max"),
        (round(next_base * 0.75), "Recovery"),
    ]

    return cycle, next_base
# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    print("Running score predictor...")

    # Check if CSV exists
    if not os.path.exists(CSV_PATH):
        print("ERROR: CSV file not found at:", CSV_PATH)
        print("Fix the path in the script and try again.")
        exit()

    # Load data
    past_data = load_arrow_volume_csv(CSV_PATH)
    print("Loaded data:", past_data)

    # Train model
    model = train_model(past_data)

    # Predict future weeks
    future_weeks = [
        (80, "Base"),
        (82, "+10"),
        (90, "Max"),
        (70, "Recovery"),
    ]

    predictions = [predict_score(model, vol, week) for vol, week in future_weeks]

    for (vol, week), pred in zip(future_weeks, predictions):
        print(f"Predicted score for {week} week at {vol} arrows: {pred}")

    # Visualize
    visualize_predictions(past_data, future_weeks, predictions)