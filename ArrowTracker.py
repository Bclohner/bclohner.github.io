import os
import csv
from datetime import date

FILENAME = "arrow_volume.csv"

def add_entry():
    volume = int(input("Enter the number of arrows shot today: "))

    # Check if the file already exists
    file_exists = os.path.isfile(FILENAME)

    with open(FILENAME, mode="a", newline="") as file:
        writer = csv.writer(file)

        # Write header only if the file is new
        if not file_exists:
            writer.writerow(["date", "arrows"])

        writer.writerow([date.today(), volume])

    print(f"Recorded {volume} arrows for {date.today()}")

def show_history():
    try:
        with open(FILENAME, mode="r") as file:
            reader = csv.reader(file)
            print("\nArrow Volume History:")
            for row in reader:
                print(f"Date: {row[0]} | Arrows: {row[1]}")
    except FileNotFoundError:
        print("No history yet. Start logging your arrows!")

def main():
    while True:
        print("\n--- Arrow Volume Tracker ---")
        print("1. Add today's arrow volume")
        print("2. Show history")
        print("3. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            add_entry()
        elif choice == "2":
            show_history()
        elif choice == "3":
            print("Good shooting today.")
            break

if __name__ == "__main__":
    main()