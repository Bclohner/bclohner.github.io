import os
import csv
import json
import webbrowser
import http.server
import socketserver
from urllib.parse import parse_qs
from datetime import date, datetime, timedelta
from dataclasses import dataclass

FILENAME = "Documents/arrow_volume.csv"
BASE_VOLUME = 400
PORT = 8000

# ---------------------------------------------------------
# CYCLE GENERATOR 
# ---------------------------------------------------------
DEFAULT_MULTIPLIERS = {
    "Monday": 0.0,
    "Tuesday": 0.2,
    "Wednesday": 0.0,
    "Thursday": 0.2,
    "Friday": 0.0,
    "Saturday": 0.3,
    "Sunday": 0.3,
}

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

def generate_4w_cycle(start_date: str, base_volume: int, multipliers=None):
    if multipliers is None:
        multipliers = DEFAULT_MULTIPLIERS

    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    all_weeks = []

    for i, week_label in enumerate(WEEK_ORDER):
        week_start = start + timedelta(days=7 * i)
        factor = WEEK_FACTORS[week_label]
        target_volume = int(base_volume * factor)
        days = []
        weekly_total = 0

        for offset in range(7):
            dt = week_start + timedelta(days=offset)
            day_name = dt.strftime("%A")
            mult = multipliers.get(day_name, 0)
            arrows = int(target_volume * mult)
            weekly_total += arrows

            days.append(DayPlan(
                date=str(dt),
                day=day_name,
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

def get_base_cycle_start():
    earliest = None
    try:
        if os.path.isfile(FILENAME):
            with open(FILENAME, mode="r") as file:
                reader = csv.reader(file)
                rows = list(reader)[1:]
                for row in rows:
                    if row and row[0] != "date":
                        dt = datetime.strptime(row[0], "%Y-%m-%d").date()
                        if earliest is None or dt < earliest:
                            earliest = dt
    except Exception:
        pass
    
    if earliest is None:
        earliest = date.today()

    start_diff = earliest.weekday()
    return earliest - timedelta(days=start_diff)

def get_year_cycle():
    cycle = []
    base_start = get_base_cycle_start()
    current_start = base_start
    current_base_volume = float(BASE_VOLUME)
    for _ in range(13): 
        cycle.extend(generate_4w_cycle(
            start_date=str(current_start),
            base_volume=int(current_base_volume)
        ))
        current_start += timedelta(days=28)
        current_base_volume *= 1.10
    return cycle

def get_actual_logs():
    logs = {}
    if os.path.isfile(FILENAME):
        try:
            with open(FILENAME, mode="r") as file:
                reader = csv.reader(file)
                rows = list(reader)[1:]
                for row in rows:
                    if row and row[0] != "date":
                        date_str = row[0]
                        vol = int(row[1])
                        scores = row[2] if len(row) > 2 else ""
                        logs[date_str] = {"arrows": vol, "scores": scores}
        except Exception:
            pass
    return logs

def check_for_jump(new_date, new_volume):
    history = get_actual_logs()
    sorted_dates = sorted(history.keys())
    
    prev_vol = None
    for dt_str in reversed(sorted_dates):
        if datetime.strptime(dt_str, "%Y-%m-%d").date() < new_date:
            prev_vol = history[dt_str]["arrows"]
            break
            
    if prev_vol is not None and (new_volume - prev_vol) > 80:
        print(f"\\n+++ SYSTEM ALERT +++\\nCareful! Shot of {new_volume} arrows is a big jump greater than 80 from the previous entry!\\n++++++++++++++++++++")

# ---------------------------------------------------------
# INTERACTIVE HTML DASHBOARD BUILDER
# ---------------------------------------------------------

def generate_dashboard_html():
    cycle_data = get_year_cycle()
    logs = get_actual_logs()
    
    events = []
    color_map = {
        "Base Week": "#3788d8",
        "+10% Week": "#f39c12",
        "Max Week +20%": "#e74c3c",
        "Recovery Week -25%": "#2ecc71"
    }

    for week in cycle_data:
        color = color_map.get(week.label, "#3788d8")
        for d in week.days:
            has_actual = d.date in logs
            actual_info = logs.get(d.date)
            
            # Event 1: Expected Target
            if d.arrows > 0:
                events.append({
                    "title": f"Expected Arrow volume: {d.arrows}",
                    "start": d.date,
                    "color": color,
                    "allDay": True,
                    "extendedProps": {
                        "phase": week.label
                    }
                })
            
            # Event 2: Shot Arrows
            if has_actual:
                actual_vol = actual_info["arrows"]
                events.append({
                    "title": f"Shot Arrows: {actual_vol}",
                    "start": d.date,
                    "color": "#8e44ad", 
                    "allDay": True
                })

                # Event 3: Scores
                if actual_info.get("scores"):
                    events.append({
                        "title": f"Scores: {actual_info['scores']}",
                        "start": d.date,
                        "color": "#27ae60", 
                        "allDay": True
                    })

    all_dates_set = set()
    expected_dict = {}
    actual_dict = {}
    score_points = []
    
    for dt_str in logs:
        all_dates_set.add(dt_str)
        actual_dict[dt_str] = logs[dt_str]["arrows"]
        sc_str = logs[dt_str]["scores"]
        if sc_str:
            try:
                for s in sc_str.split(","):
                    if s.strip():
                        score_points.append({"x": dt_str, "y": float(s.strip())})
            except Exception:
                pass
                
    for week in cycle_data:
        for d in week.days:
            if d.arrows > 0:
                all_dates_set.add(d.date)
                expected_dict[d.date] = d.arrows
                
    volLabels = sorted(list(all_dates_set))
    expectedData = [expected_dict.get(dt, 'null') for dt in volLabels]
    actualData = [actual_dict.get(dt, 'null') for dt in volLabels]
    
    expectedDataStr = "[" + ",".join(str(e) for e in expectedData) + "]"
    actualDataStr = "[" + ",".join(str(e) for e in actualData) + "]"
    volLabelsStr = json.dumps(volLabels)
    scorePointsStr = json.dumps(score_points)
    
    first_date = volLabels[0] if volLabels else date.today().isoformat()
    last_date = volLabels[-1] if volLabels else date.today().isoformat()

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8' />
    <title>Archery Training Dashboard</title>
    <script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.10/index.global.min.js'></script>
    <script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
    <script src='https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js'></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
            background-color: #f7f9fc;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .fc-event-title {{
            font-weight: bold;
            font-size: 0.95em;
            padding: 4px;
            white-space: pre-wrap; 
        }}
        h2 {{
            border-bottom: 2px solid #efefef;
            padding-bottom: 10px;
            color: #2c3e50;
            margin-top: 0;
        }}
        .form-group {{ margin-bottom: 10px; }}
        input[type="date"], input[type="number"], input[type="text"] {{
            padding: 8px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;
        }}
        label {{ display: block; font-weight: bold; margin-bottom: 5px; font-size: 0.9em; }}
        button {{
            padding: 10px 20px; background: #3788d8; color: white; border: none; 
            border-radius: 4px; font-weight: bold; cursor: pointer; transition: background 0.2s;
        }}
        button:hover {{ background: #2980b9; }}
    </style>
</head>
<body>
    <div class="container">
        <h1 style="text-align:center; margin-bottom: 30px; color: #2c3e50;">Archery Training Dashboard</h1>
        
        <!-- NEW SECURE DATA ENTRY UI -->
        <div class="card" style="background: #eaf1f8; border-left: 5px solid #3788d8;">
            <h2>📝 Add Training Entry</h2>
            <form action="/add_entry" method="POST" style="display: flex; gap: 20px; align-items: flex-end; flex-wrap: wrap;">
                <div>
                    <label>Date</label>
                    <input type="date" name="date" required value="{date.today().isoformat()}">
                </div>
                <div>
                    <label>Shot Arrows</label>
                    <input type="number" name="volume" required placeholder="e.g. 100">
                </div>
                <div style="flex-grow: 1; min-width: 250px;">
                    <label>Scores (comma separated, optional)</label>
                    <input type="text" name="scores" style="width: 100%;" placeholder="e.g. 290, 292">
                </div>
                <div>
                    <button type="submit">Save Entry</button>
                </div>
            </form>
        </div>

        <div class="card">
            <h2>📅 Cycle Calendar</h2>
            <div id='calendar'></div>
        </div>

        <div class="card">
            <h2>📈 Expected Target vs Actual Volume</h2>
            <canvas id="volChart" width="400" height="150"></canvas>
        </div>

        <div class="card">
            <h2>🎯 Shooting Scores</h2>
            <canvas id="scoreChart" width="400" height="150"></canvas>
        </div>
    </div>

    <script>
      document.addEventListener('DOMContentLoaded', function() {{
        var calendarEl = document.getElementById('calendar');
        var calendar = new FullCalendar.Calendar(calendarEl, {{
          initialView: 'dayGridMonth',
          firstDay: 1,
          initialDate: '{date.today()}',
          headerToolbar: {{
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek'
          }},
          events: {json.dumps(events)},
          eventClick: function(info) {{
            if(info.event.extendedProps.phase) {{
                alert('Training Phase: ' + info.event.extendedProps.phase + '\\n' + info.event.title);
            }}
          }}
        }});
        calendar.render();

        var volCtx = document.getElementById('volChart').getContext('2d');
        var volChart = new Chart(volCtx, {{
            type: 'line',
            data: {{
                labels: {volLabelsStr},
                datasets: [
                    {{
                        label: 'Shot Arrows',
                        data: {actualDataStr},
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderWidth: 3,
                        tension: 0.1,
                        fill: false,
                        spanGaps: true,
                        pointRadius: 4
                    }},
                    {{
                        label: 'Expected Arrow volume',
                        data: {expectedDataStr},
                        borderColor: 'rgba(150, 150, 150, 0.8)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        tension: 0.1,
                        fill: false,
                        spanGaps: true,
                        pointRadius: 0
                    }}
                ]
            }},
            options: {{
                scales: {{ 
                    x: {{
                        type: 'time',
                        time: {{
                            unit: 'month',
                            displayFormats: {{ month: 'MMM yyyy' }}
                        }},
                        min: '{first_date}',
                        max: '{last_date}',
                        title: {{ display: true, text: 'Month' }}
                    }},
                    y: {{ beginAtZero: true }} 
                }}
            }}
        }});

        var scoreCtx = document.getElementById('scoreChart').getContext('2d');
        var scoreChart = new Chart(scoreCtx, {{
            type: 'scatter',
            data: {{
                datasets: [{{
                    label: 'Scores',
                    data: {scorePointsStr},
                    backgroundColor: 'rgba(46, 204, 113, 1)',
                    borderColor: 'rgba(46, 204, 113, 1)',
                    pointRadius: 6,
                }}]
            }},
            options: {{
                scales: {{
                    x: {{
                        type: 'time',
                        time: {{
                            unit: 'month',
                            displayFormats: {{ month: 'MMM yyyy' }}
                        }},
                        min: '{first_date}',
                        max: '{last_date}',
                        title: {{ display: true, text: 'Month' }}
                    }},
                    y: {{ beginAtZero: false }}
                }}
            }}
        }});
      }});
    </script>
</body>
</html>"""

# ---------------------------------------------------------
# BACKEND WEB SERVER
# ---------------------------------------------------------

class ArcheryAppHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/dashboard':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # Dynamically generate and stream the HTML exactly like a modern server
            html = generate_dashboard_html()
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/add_entry':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            fields = parse_qs(post_data)
            
            date_str = fields.get('date', [''])[0]
            volume_str = fields.get('volume', [''])[0]
            scores_str = fields.get('scores', [''])[0].strip()
            
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d").date()
                vol = int(volume_str)
            except ValueError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Invalid HTTP Form parameters. Action failed.")
                return
            
            # Secure appendage into CSV
            file_exists = os.path.isfile(FILENAME)
            with open(FILENAME, mode="a", newline="") as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["date", "arrows", "scores"])
                writer.writerow([dt, vol, scores_str])
            
            # Check terminal print logic
            print(f"\\nSERVER LOG: Logged {vol} arrows mapped to {dt}")
            check_for_jump(dt, vol)
            
            # Instantly redirect the browser back to the homepage so it naturally refreshes!
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
            
    def log_message(self, format, *args):
        # Override to suppress default HTTP spammy logs and keep terminal clean for jump checks
        pass

def main():
    print("\\n--- LOCAL SERVER BOOTING ---")
    print(f"Hosting Archery Tracking Application on PORT {PORT}...")
    print("WARNING: Press 'Ctrl+C' in this terminal at any time to shut the server down.\\n")
    
    # Auto-open browser
    webbrowser.open(f"http://localhost:{PORT}")
    
    # Hold server alive indefinitely
    with socketserver.TCPServer(("", PORT), ArcheryAppHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\\nServer shutting down safely... Goodbye!")

if __name__ == "__main__":
    main()