import os
import csv
from datetime import date, datetime
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

FILENAME = "Documents/arrow_volume.csv"

def check_for_jump(new_date, new_volume): #Checks for a steep jump in arrow volume, and if there is, prints a warning message on the entry.
    try:
        with open(FILENAME, mode="r") as file: #Opens the file in read mode.
            reader = csv.reader(file) #Creates a CSV reader object.
            rows = list(reader)[1:] #Skips the header row.
            
        history = [] #Creates an empty list to store the history.
        for row in rows:
            if row:
                try:
                    dt = datetime.strptime(row[0], "%Y-%m-%d").date() #Converts the date string to a date object.
                    vol = int(row[1]) #Converts the volume string to an integer.
                    history.append((dt, vol)) #Appends the date and volume to the history list.
                except ValueError:
                    pass
                    
        history.sort(key=lambda x: x[0]) #Sorts the history by date.
        
        prev_vol = None #Sets the previous volume to None.
        for dt, vol in reversed(history): #Reverses the history to check the most recent entries first.
            if dt < new_date: #Checks if the date of the entry is before the new date.
                prev_vol = vol #Sets the previous volume to the volume of the entry.
                break #Breaks the loop.
                
        if prev_vol is not None and (new_volume - prev_vol) > 80: #Checks if the new volume is more than 80 arrows greater than the previous volume.
            print("\n⚠️ Careful! That is a big jump!")
    except Exception:
        pass

def add_entry():
    volume = int(input("Enter the number of arrows shot today: "))
    scores = input("Enter scores for today (comma-separated, or leave blank): ").strip()

    # Check if the file already exists
    file_exists = os.path.isfile(FILENAME)

    with open(FILENAME, mode="a", newline="") as file:
        writer = csv.writer(file)

        # Write header only if the file is new
        if not file_exists:
            writer.writerow(["date", "arrows", "scores"])

        writer.writerow([date.today(), volume, scores])

    print(f"Recorded {volume} arrows and scores '{scores}' for {date.today()}" if scores else f"Recorded {volume} arrows for {date.today()}")
    check_for_jump(date.today(), volume)

def add_retroactive_entry(): #Adds a retroactive entry to the CSV file.
    date_str = input("Enter the date (YYYY-MM-DD): ") #Prompts the user to enter the date of the entry.
    try:
        # Validate date format
        entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    try:
        volume = int(input("Enter the number of arrows shot: ")) #Prompts the user to enter the volume of arrows shot.
    except ValueError:
        print("Invalid number. Please enter an integer.") #Prints an error message if the volume is not an integer.
        return

    scores = input("Enter scores (comma-separated, or leave blank): ").strip()

    # Check if the file already exists
    file_exists = os.path.isfile(FILENAME)

    with open(FILENAME, mode="a", newline="") as file:
        writer = csv.writer(file)

        # Write header only if the file is new
        if not file_exists:
            writer.writerow(["date", "arrows", "scores"])

        writer.writerow([entry_date, volume, scores]) #Writes the date and volume to the CSV file.

    print(f"Recorded {volume} arrows and scores '{scores}' for {entry_date}" if scores else f"Recorded {volume} arrows for {entry_date}")
    check_for_jump(entry_date, volume) #Checks for a steep jump in arrow volume.

def show_history(): #Shows the history of arrow volume.
    try:
        with open(FILENAME, mode="r") as file:
            reader = csv.reader(file)
            print("\nArrow Volume History:")
            for row in reader:
                if not row or row[0] == "date":
                    continue
                score_str = f" | Scores: {row[2]}" if len(row) > 2 and row[2] else ""
                print(f"Date: {row[0]} | Arrows: {row[1]}{score_str}")
    except FileNotFoundError:
        print("No history yet. Start logging your arrows!")

def plot_volume(): #Plots the arrow volume over time.
    if plt is None:
        print("matplotlib is not installed. Please try running: py -m pip install matplotlib")
        return

    try:
        with open(FILENAME, mode="r") as file:
            reader = csv.reader(file)
            dates = []
            volumes = []
            
            for row in reader:
                if not row or row[0] == "date":
                    continue
                try:
                    date_obj = datetime.strptime(row[0], "%Y-%m-%d").date() #Converts the date string to a date object.
                    dates.append(date_obj) #Appends the date to the dates list.
                    volumes.append(int(row[1])) #Appends the volume to the volumes list.
                except (ValueError, IndexError):
                    pass
            
            if not dates:
                print("No valid data to plot yet.")
                return
            # Plotting Arrow volume over time 
            plt.figure(figsize=(10, 6))
            plt.plot(dates, volumes, marker='o', linestyle='-', color='b')
            plt.title("Arrow Volume Over Time")
            plt.xlabel("Date")
            plt.ylabel("Arrows Shot")
            plt.grid(True)
            plt.gcf().autofmt_xdate()
            plt.tight_layout()
            plt.show()

    except FileNotFoundError:
        print("No history yet. Start logging your arrows!")
    except Exception as e:
        print(f"An error occurred while plotting: {e}")

def plot_scores(): #Plots the archery scores over time.
    if plt is None:
        print("matplotlib is not installed. Please try running: py -m pip install matplotlib")
        return

    try:
        with open(FILENAME, mode="r") as file:
            reader = csv.reader(file)
            dates = []
            scores = []
            
            for row in reader:
                if not row or row[0] == "date":
                    continue
                if len(row) > 2 and row[2].strip():
                    try:
                        date_obj = datetime.strptime(row[0], "%Y-%m-%d").date()
                        # Parse comma-separated scores
                        day_scores = [float(s.strip()) for s in row[2].split(",") if s.strip()]
                        for s in day_scores:
                            dates.append(date_obj)
                            scores.append(s)
                    except ValueError:
                        pass
            
            if not dates:
                print("No valid score data to plot yet.")
                return
            
            # Plotting Scores over time 
            plt.figure(figsize=(10, 6))
            plt.scatter(dates, scores, color='g', marker='x', s=100)
            plt.title("Shooting Scores Over Time")
            plt.xlabel("Date")
            plt.ylabel("Score")
            plt.grid(True)
            plt.gcf().autofmt_xdate()
            plt.tight_layout()
            plt.show()

    except FileNotFoundError:
        print("No history yet. Start logging your arrows and scores!")
    except Exception as e:
        print(f"An error occurred while plotting: {e}")

def delete_entry():
    if not os.path.isfile(FILENAME):
        print("No history yet. Nothing to delete!")
        return

    with open(FILENAME, mode="r") as file:
        reader = csv.reader(file)
        rows = list(reader)

    if len(rows) <= 1:
        print("No history yet. Nothing to delete!")
        return

    header = rows[0]
    data = rows[1:]

    print("\nArrow Volume History:")
    for i, row in enumerate(data):
        if row:  # Ensure row is not empty
            score_str = f" | Scores: {row[2]}" if len(row) > 2 and row[2] else ""
            print(f"{i + 1}. Date: {row[0]} | Arrows: {row[1]}{score_str}")

    try:
        choice = int(input("\nEnter the number of the entry to delete (or 0 to cancel): "))
        if choice == 0:
            return
        if 1 <= choice <= len(data):
            deleted_row = data.pop(choice - 1)
            score_str = f", Scores {deleted_row[2]}" if len(deleted_row) > 2 and deleted_row[2] else ""
            print(f"Deleted entry: Date {deleted_row[0]}, Arrows {deleted_row[1]}{score_str}")

            with open(FILENAME, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(header)
                writer.writerows(data)
        else:
            print("Invalid entry number.")
    except ValueError:
        print("Invalid input. Please enter a number.")

def main():
    while True:
        print("\n--- Arrow Volume Tracker ---") # Prints the title of the program
        print("1. Add today's arrow volume") # Prints the option to add today's arrow volume
        print("2. Add retroactive arrow volume") # Prints the option to add retroactive arrow volume
        print("3. Show history") # Prints the option to show history
        print("4. Plot volume over time") # Prints the option to plot volume over time
        print("5. Plot scores over time") # Prints the option to plot scores over time
        print("6. Delete an entry") # Prints the option to delete an entry
        print("7. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            add_entry()
        elif choice == "2":
            add_retroactive_entry()
        elif choice == "3":
            show_history()
        elif choice == "4":
            plot_volume()
        elif choice == "5":
            plot_scores()
        elif choice == "6":
            delete_entry()
        elif choice == "7":
            print("Good shooting today.")
            break

if __name__ == "__main__":
    main()