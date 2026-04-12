import datetime
from dataclasses import dataclass, asdict
import json

# ---------------------------------------------------------
# DEFAULT DAILY MULTIPLIERS (from your 4W Cycle spreadsheet)
# ---------------------------------------------------------
DEFAULT_MULTIPLIERS = {
    "Monday": 0,
    "Tuesday": 1/3,
    "Wednesday": 0,
    "Thursday": 1/3,
    "Friday": 0,
    "Saturday": 0,
    "Sunday": 1/3,
}

# ---------------------------------------------------------
# WEEKLY LOAD FACTORS
# ---------------------------------------------------------
WEEK_FACTORS = {
    "Base Week": 1.00,
    "+10% Week": 1.10,
    "Max Week +20%": 1.20,
    "Recovery Week -25%": 0.75,
}

WEEK_ORDER = [
    "Base Week",
    "+10% Week",
    "Max Week +20%",
    "Recovery Week -25%",
]

# ---------------------------------------------------------
# DATA STRUCTURES
# ---------------------------------------------------------

@dataclass
class DayPlan:
    date: str
    day: str
    multiplier: float
    arrows: int

@dataclass
class WeekPlan:
    label: str
    week_of: str
    total_volume: int
    days: list

# ---------------------------------------------------------
# MAIN GENERATION FUNCTION
# ---------------------------------------------------------

def generate_4w_cycle(start_date: str, base_volume: int, multipliers=None):
    """
    Generates a full 4-week archery training cycle.

    Parameters:
        start_date (str): YYYY-MM-DD
        base_volume (int): Base week arrow volume
        multipliers (dict): Optional custom daily multipliers

    Returns:
        list[WeekPlan]
    """
    if multipliers is None:
        multipliers = DEFAULT_MULTIPLIERS

    start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    all_weeks = []

    for i, week_label in enumerate(WEEK_ORDER):
        week_start = start + datetime.timedelta(days=7 * i)
        factor = WEEK_FACTORS[week_label]

        # Everything scales from the base volume
        target_volume = int(base_volume * factor)

        days = []
        weekly_total = 0

        for offset, (day, mult) in enumerate(multipliers.items()):
            date = week_start + datetime.timedelta(days=offset)
            arrows = int(target_volume * mult)
            weekly_total += arrows

            days.append(DayPlan(
                date=str(date),
                day=day,
                multiplier=mult,
                arrows=arrows
            ))

        all_weeks.append(WeekPlan(
            label=week_label,
            week_of=str(week_start),
            total_volume=weekly_total,
            days=days
        ))

    return all_weeks

# ---------------------------------------------------------
# EXAMPLE USAGE
# ---------------------------------------------------------

if __name__ == "__main__":
    # Change this number to scale the entire cycle
    BASE_VOLUME = 90

    # Optional: override multipliers
    # custom_multipliers = {
    #     "Monday": 0.10,
    #     "Tuesday": 0.25,
    #     "Wednesday": 0.10,
    #     "Thursday": 0.25,
    #     "Friday": 0,
    #     "Saturday": 0.15,
    #     "Sunday": 0.15,
    # }

    cycle = generate_4w_cycle(
        start_date="2025-10-07",
        base_volume=BASE_VOLUME,
        # multipliers=custom_multipliers
    )

    # Pretty-print JSON output
    print(json.dumps([asdict(w) for w in cycle], indent=4))