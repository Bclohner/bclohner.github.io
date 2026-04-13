import numpy as np
import matplotlib.pyplot as plt
import csv
import os
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

# ---------------------------------------------------------
# PEAK BONUS (Recovery Week)
# ---------------------------------------------------------
PEAK_BONUS = 2

# ---------------------------------------------------------
# PATH TO CSV IN Documents/Website/Documents
# ---------------------------------------------------------
CSV_PATH = r"C:\Users\bcloh\Documents\Website\Documents\arrow_volume.csv"

# ---------------------------------------------------------
# LOAD CSV (arrow_volume.csv)
# ---------------------------------------------------------
def load_arrow_volume_csv(csv_path): #loads the CSV file
    data = []
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f) #reads the CSV file
        for row in reader:
            arrows = int(row["arrows"]) #gets the arrow volume
            score_list = row["scores"].split(",") #splits the scores into a list
            for s in score_list:
                score = float(s.strip()) #converts the scores to floats
                data.append((arrows, score)) #appends the scores to the data
    return data

# ---------------------------------------------------------
# TRAIN MODEL
#Because this is based on previous performances, it may not reflect true scores, as other factors may be involved. It may also be less accurate several months in advance, as arrow volume increases, but the model has not learned yet.
# ---------------------------------------------------------
def train_model(past_data): #trains the model
    X = np.array([[arrows] for arrows, score in past_data]) #gets the arrow volume
    y = np.array([score for arrows, score in past_data]) #gets the scores
    model = LinearRegression() #creates a linear regression model
    model.fit(X, y) #fits the model to the data
    return model

# ---------------------------------------------------------
# PREDICT SCORE (with 0–300 clamp)
# ---------------------------------------------------------
def predict_score(model, arrow_volume, week_type="Base"): #predicts the score
    pred = model.predict([[arrow_volume]])[0] #predicts the score
    if week_type == "Recovery": #if the week type is recovery
        pred += PEAK_BONUS #adds the peak bonus
    pred = max(0, min(pred, 300)) #clamps the score between 0 and 300
    return round(pred, 1) #rounds the score to the nearest tenth

# ---------------------------------------------------------
# GENERATE CURRENT 4-WEEK CYCLE
# ---------------------------------------------------------
def generate_current_cycle(base_volume): #generates the current cycle
    return [
        (base_volume, "Base"),
        (round(base_volume * 1.10), "+10"),
        (round(base_volume * 1.20), "Max"),
        (round(base_volume * 0.75), "Recovery"),
    ]

# ---------------------------------------------------------
# GENERATE NEXT 4-WEEK CYCLE (+10% progression)
# ---------------------------------------------------------
def generate_next_cycle(base_volume):
    next_base = round(base_volume * 1.10)
    cycle = [
        (next_base, "Base"),
        (round(next_base * 1.10), "+10"),
        (round(next_base * 1.20), "Max"),
        (round(next_base * 0.75), "Recovery"),
    ]
    return cycle, next_base

# ---------------------------------------------------------
# FIND WHICH CYCLE A DATE BELONGS TO
# ---------------------------------------------------------
def get_cycle_for_date(start_date, target_date, base_volume): #finds which cycle a date belongs to
    start = datetime.strptime(start_date, "%Y-%m-%d") #converts the start date to a datetime object
    target = datetime.strptime(target_date, "%Y-%m-%d") #converts the target date to a datetime object

    delta_days = (target - start).days #calculates the difference in days between the target date and the start date
    if delta_days < 0: #if the difference in days is negative
        return None, None, None

    cycle_number = delta_days // 28
    week_index = (delta_days % 28) // 7

    cycle_base = round(base_volume * (1.10 ** cycle_number))
    cycle, _ = generate_next_cycle(cycle_base)

    return cycle_number + 1, week_index, cycle[week_index]

# ---------------------------------------------------------
# VISUALIZATION
# ---------------------------------------------------------
def visualize_predictions(past_data, future_weeks, predictions): #visualizes the predictions
    past_volumes = [d[0] for d in past_data] #gets the past volumes
    past_scores = [d[1] for d in past_data] #gets the past scores
    future_volumes = [fw[0] for fw in future_weeks] #gets the future volumes
    future_scores = predictions #gets the future scores

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

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__": 
    print("Running score predictor...") #prints that the score predictor is running

    if not os.path.exists(CSV_PATH): #checks if the CSV file exists
        print("ERROR: CSV file not found at:", CSV_PATH)
        exit()

    past_data = load_arrow_volume_csv(CSV_PATH) #loads the CSV file
    print("Loaded data:", past_data)

    model = train_model(past_data) #trains the model

    current_base = int(np.mean([d[0] for d in past_data])) #calculates the current base volume
    print(f"Current base volume: {current_base}") #prints the current base volume

    # ---------------------------------------------------------
    # SHOW CURRENT CYCLE PREDICTIONS
    # ---------------------------------------------------------
    future_weeks = generate_current_cycle(current_base) #generates the next 4 weeks of training
    print("\nPredictions for the CURRENT cycle:") #prints the current cycle predictions

    predictions = [predict_score(model, vol, week) for vol, week in future_weeks] #predicts the scores for the current cycle

    for (vol, week), pred in zip(future_weeks, predictions):
        print(f"  {week} week at {vol} arrows → predicted score: {pred}") #prints the predicted scores for the current cycle

    # ---------------------------------------------------------
    # MANUAL DATE INPUT
    # ---------------------------------------------------------
    training_start_date = "2026-04-14" #sets the training start date
    target_date = input("\nEnter a date to check (YYYY-MM-DD): ").strip() #gets the target date

    try:
        cycle_num, week_idx, (vol, week_type) = get_cycle_for_date(
            training_start_date,
            target_date,
            current_base
        )

        if cycle_num is None:
            print(f"{target_date} is before training started.") #prints that the date is before training started
        else:
            print(f"\nDate {target_date} is in:") #prints that the date is in the current cycle
            print(f"  Cycle {cycle_num}") #prints the current cycle number
            print(f"  Week {week_idx + 1} ({week_type})") #prints the current week number and type
            print(f"  Arrow volume: {vol}") #prints the current arrow volume

            predicted = predict_score(model, vol, week_type) #predicts the score
            print(f"  Predicted score: {predicted}") #prints the predicted score

    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.") #prints that the date format is invalid

    visualize_predictions(past_data, future_weeks, predictions) #visualizes the predictions