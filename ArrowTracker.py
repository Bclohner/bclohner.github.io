import os
import csv
from datetime import date, datetime
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

FILENAME = "arrow_volume.csv"

def check_for_jump(new_date, new_volume):
    try:
        with open(FILENAME, mode="r") as file:
            reader = csv.reader(file)
            rows = list(reader)[1:]
            
        history = []
        for row in rows:
            if row:
                try:
                    dt = datetime.strptime(row[0], "%Y-%m-%d").date()
                    vol = int(row[1])
                    history.append((dt, vol))
                except ValueError:
                    pass
                    
        history.sort(key=lambda x: x[0])
        
        prev_vol = None
        for dt, vol in reversed(history):
            if dt < new_date:
                prev_vol = vol
                break
                
        if prev_vol is not None and (new_volume - prev_vol) > 80:
            print("\n⚠️ Careful! That is a big jump!")
    except Exception:
        pass

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
    check_for_jump(date.today(), volume)

def add_retroactive_entry():
    date_str = input("Enter the date (YYYY-MM-DD): ")
    try:
        # Validate date format
        entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    try:
        volume = int(input("Enter the number of arrows shot: "))
    except ValueError:
        print("Invalid number. Please enter an integer.")
        return

    # Check if the file already exists
    file_exists = os.path.isfile(FILENAME)

    with open(FILENAME, mode="a", newline="") as file:
        writer = csv.writer(file)

        # Write header only if the file is new
        if not file_exists:
            writer.writerow(["date", "arrows"])

        writer.writerow([entry_date, volume])

    print(f"Recorded {volume} arrows for {entry_date}")
    check_for_jump(entry_date, volume)

def show_history():
    try:
        with open(FILENAME, mode="r") as file:
            reader = csv.reader(file)
            print("\nArrow Volume History:")
            for row in reader:
                print(f"Date: {row[0]} | Arrows: {row[1]}")
    except FileNotFoundError:
        print("No history yet. Start logging your arrows!")

def plot_volume():
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
                    date_obj = datetime.strptime(row[0], "%Y-%m-%d").date()
                    dates.append(date_obj)
                    volumes.append(int(row[1]))
                except (ValueError, IndexError):
                    pass
            
            if not dates:
                print("No valid data to plot yet.")
                return

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
            print(f"{i + 1}. Date: {row[0]} | Arrows: {row[1]}")

    try:
        choice = int(input("\nEnter the number of the entry to delete (or 0 to cancel): "))
        if choice == 0:
            return
        if 1 <= choice <= len(data):
            deleted_row = data.pop(choice - 1)
            print(f"Deleted entry: Date {deleted_row[0]}, Arrows {deleted_row[1]}")

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
        print("\n--- Arrow Volume Tracker ---")
        print("1. Add today's arrow volume")
        print("2. Add retroactive arrow volume")
        print("3. Show history")
        print("4. Plot volume over time")
        print("5. Delete an entry")
        print("6. Exit")

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
            delete_entry()
        elif choice == "6":
            print("Good shooting today.")
            break

if __name__ == "__main__":
    main()