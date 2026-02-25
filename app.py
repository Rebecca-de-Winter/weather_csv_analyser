import os
import csv
from datetime import datetime
from uuid import uuid4
from pathlib import Path

from flask import Flask, request, render_template_string
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

app = Flask(__name__)

DEGREE_SYMBOL = u"\N{DEGREE SIGN}C"
SAMPLE_CSV_PATH = Path("data") / "sample.csv"

os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
# ----------------------------
# SHECODES WEATHER APP MAIN FUNCTIONS
# ----------------------------

def format_temperature(temp):
    """Takes a temperature and returns it in string format with the degrees
        and Celcius symbols.

    Args:
        temp: A string representing a temperature.
    Returns:
        A string contain the temperature and "degrees Celcius."
    """
    return f"{temp}{DEGREE_SYMBOL}"


def convert_date(iso_string):
    """Converts and ISO formatted date into a human-readable format.

    Args:
        iso_string: An ISO date string.
    Returns:
        A date formatted like: Weekday Date Month Year e.g. Tuesday 06 July 2021
    """
    result = datetime.fromisoformat(iso_string)
    formatted_date = result.strftime("%A %d %B %Y")
    return(formatted_date)


def convert_f_to_c(temp_in_fahrenheit):
    """Converts a temperature from Fahrenheit to Celcius.

    Args:
        temp_in_fahrenheit: float representing a temperature.
    Returns:
        A float representing a temperature in degrees Celcius, rounded to 1 decimal place.
    """
    temp = float(temp_in_fahrenheit)
    celcius = (temp - 32) * 5/9
    rounded_number = round(celcius, 1)
    return(rounded_number)


def calculate_mean(weather_data):
    """Calculates the mean value from a list of numbers.

    Args:
        weather_data: a list of numbers.
    Returns:
        A float representing the mean value.
    """
    total = 0
    for temp in weather_data:
        total = total + float(temp)
    result = total/ len(weather_data)
    return result


def load_data_from_csv(csv_file):
    """Reads a csv file and stores the data in a list.

    Args:
        csv_file: a string representing the file path to a csv file.
    Returns:
        A list of lists, where each sublist is a (non-empty) line in the csv file.
    """
    data_list = []
    with open(csv_file, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for row in csv_reader:
            if not row:
                continue
            
            if len(row) == 1 and row[0].strip() == "":
                continue

            date = row[0].strip()
            min = int(row[1])
            max = int(row[2])
            data_list.append([date, min, max])
    return data_list


def find_min(weather_data):
    """Calculates the minimum value in a list of numbers.

    Args:
        weather_data: A list of numbers.
    Returns:
        The minimum value and it's position in the list. (In case of multiple matches, return the index of the *last* example in the list.)
    """
    if not weather_data:
        return()
    min_value = float(weather_data[0])
    min_position = 0

    for i in range(1, len(weather_data)):
        value = float(weather_data[i])
        if value <= min_value:
            min_value = value
            min_position = i

    return (min_value, min_position)


def find_max(weather_data):
    """Calculates the maximum value in a list of numbers.

    Args:
        weather_data: A list of numbers.
    Returns:
        The maximum value and it's position in the list. (In case of multiple matches, return the index of the *last* example in the list.)
    """
    if not weather_data:
        return()
    max_value = float(weather_data[0])
    max_position = 0

    for i in range(1, len(weather_data)):
        value = float(weather_data[i])
        if value >= max_value:
            max_value = value
            max_position = i
    return (max_value, max_position)


def generate_summary(weather_data):
    """Outputs a summary for the given weather data.

    Args:
        weather_data: A list of lists, where each sublist represents a day of weather data.
    Returns:
        A string containing the summary information.
    """
    min_list = []
    max_list = []
    for day in weather_data:
        min_list.append(day[1])
        max_list.append(day[2])

    min_value, min_position = find_min(min_list)
    min_timestamp = weather_data[min_position][0]
    min_value = convert_f_to_c(min_value)
    min_date = convert_date(min_timestamp)

    overview = f"{len(weather_data)} Day Overview\n"
    line_low = f"  The lowest temperature will be {format_temperature(min_value)}, and will occur on {min_date}.\n"

    max_value, max_position = find_max(max_list)
    max_timestamp = weather_data[max_position][0]
    max_value = convert_f_to_c(max_value)
    max_date = convert_date(max_timestamp)
    line_high = f"  The highest temperature will be {format_temperature(max_value)}, and will occur on {max_date}.\n"

    lows = []
    for day in weather_data:
        lows.append(day[1])

    average_low = calculate_mean(lows)
    average_low = convert_f_to_c(average_low)
    line_avg_low = f"  The average low this week is {format_temperature(average_low)}.\n"

    highs = []
    for day in weather_data:
        highs.append(day[2])

    average_high = calculate_mean(highs)
    average_high = convert_f_to_c(average_high)
    line_avg_high = f"  The average high this week is {format_temperature(average_high)}.\n"

    summary = overview + line_low + line_high + line_avg_low + line_avg_high
    return summary


def generate_daily_summary(weather_data):
    """Outputs a daily summary for the given weather data.

    Args:
        weather_data: A list of lists, where each sublist represents a day of weather data.
    Returns:
        A string containing the summary information.
    """
    summary = ""
    for day in weather_data:
        current_date = convert_date(day[0])
        summary += f"---- {current_date} ----\n"

        min_temp = day[1]
        converted_min_temp = format_temperature(convert_f_to_c(min_temp))
        summary += f"  Minimum Temperature: {converted_min_temp}\n"

        max_temp = day[2]
        converted_max_temp = format_temperature(convert_f_to_c(max_temp))
        summary += f"  Maximum Temperature: {converted_max_temp}\n\n"

    return summary


# ----------------------------
# Chart + warnings + analyzing helper
# ----------------------------

def build_warnings(weather_data):
    warnings = []
    for day in weather_data:
        date_str = day[0]
        min_f = day[1]
        max_f = day[2]
        if min_f > max_f:
            warnings.append(f"{date_str}: min ({min_f}F) is greater than max ({max_f}F).")
    return warnings


def make_chart(weather_data, out_path):
    # x axis: dates
    dates = [datetime.fromisoformat(day[0]) for day in weather_data]

    # y axis: Celsius values
    mins_c = [convert_f_to_c(day[1]) for day in weather_data]
    maxs_c = [convert_f_to_c(day[2]) for day in weather_data]

    plt.figure()
    plt.plot(dates, mins_c, marker="o", label="Min (°C)")
    plt.plot(dates, maxs_c, marker="o", label="Max (°C)")
    plt.title("Temperature Trend")
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def analyze_csv_path(csv_path):
    weather_data = load_data_from_csv(csv_path)
    if not weather_data:
        return "CSV contained no data rows.", "", [], None

    summary = generate_summary(weather_data)
    daily = generate_daily_summary(weather_data)
    warnings = build_warnings(weather_data)

    os.makedirs("static", exist_ok=True)
    chart_filename = f"weather_trend_{uuid4().hex}.png"
    chart_path = os.path.join("static", chart_filename)
    make_chart(weather_data, chart_path)
    chart_url = f"/static/{chart_filename}"

    return summary, daily, warnings, chart_url


# ----------------------------
# Simple UI
# ----------------------------

HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Weather CSV Analyser</title>
  <style>
    :root {
      --bg: #f7f9ff;
      --card: #ffffff;
      --border: #e6eaf5;

      --text: #1f2937;
      --muted: #6b7280;

      --accent: #4f46e5;
      --accent-hover: #4338ca;
      --accent-soft: rgba(79, 70, 229, 0.12);

      --good: #10b981;
      --good-soft: rgba(16, 185, 129, 0.12);

      --warning-bg: #fff4e5;
      --warning-border: #ffd28a;

      --shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
      --radius: 16px;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: "Segoe UI", system-ui, -apple-system, Arial, sans-serif;
      background:
        radial-gradient(900px 380px at 20% -10%, rgba(79,70,229,0.14), transparent 60%),
        radial-gradient(800px 320px at 90% 0%, rgba(16,185,129,0.10), transparent 55%),
        var(--bg);
      color: var(--text);
    }

    .container {
      max-width: 980px;
      margin: 42px auto;
      padding: 0 20px 70px;
    }

    .header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 18px;
      flex-wrap: wrap;
      margin-bottom: 18px;
    }

    h1 {
      font-size: 38px;
      margin: 0 0 10px;
      letter-spacing: -0.02em;
    }

    .subtitle {
      margin: 0;
      color: var(--muted);
      max-width: 70ch;
      line-height: 1.5;
    }

    .badge-row {
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
      margin-top: 10px;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      padding: 7px 12px;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: #fff;
      color: var(--muted);
    }

    .badge--demo {
      border-color: rgba(16,185,129,0.25);
      background: var(--good-soft);
      color: #065f46;
      font-weight: 600;
    }

    .badge-dot {
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: var(--good);
      display: inline-block;
    }

    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 22px 22px;
      margin-top: 18px;
      box-shadow: var(--shadow);
    }

    .card h2 {
      margin: 0 0 12px;
      font-size: 20px;
      letter-spacing: -0.01em;
    }

    .helper {
      margin: 0 0 14px;
      color: var(--muted);
      line-height: 1.55;
      font-size: 14px;
    }

    .example {
      display: inline-block;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      background: #f1f5ff;
      border: 1px solid rgba(79,70,229,0.18);
      padding: 2px 8px;
      border-radius: 10px;
      color: #2b2a7a;
      font-size: 12px;
      vertical-align: middle;
    }

    .form-row {
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
      margin-top: 10px;
    }

    .btn {
      appearance: none;
      border: none;
      cursor: pointer;
      border-radius: 12px;
      padding: 10px 14px;
      font-weight: 700;
      letter-spacing: 0.01em;
      transition: 0.18s ease;
      display: inline-flex;
      align-items: center;
      gap: 10px;
      text-decoration: none;
      user-select: none;
    }

    .btn-primary {
      background: linear-gradient(135deg, var(--accent), #6d28d9);
      color: #fff;
      box-shadow: 0 8px 18px rgba(79,70,229,0.25);
    }

    .btn-primary:hover {
      transform: translateY(-1px);
      filter: brightness(1.02);
    }

    .btn-ghost {
      background: rgba(255,255,255,0.75);
      color: var(--accent);
      border: 1px solid rgba(79,70,229,0.18);
    }

    .btn-ghost:hover {
      background: rgba(79,70,229,0.08);
    }

    /* Custom file upload UI */
    input[type="file"] {
      display: none;
    }

    .file-wrap {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      padding: 10px 12px;
      border: 1px dashed rgba(79,70,229,0.28);
      border-radius: 14px;
      background: rgba(79,70,229,0.05);
    }

    .file-name {
      font-size: 13px;
      color: var(--muted);
      min-width: 170px;
    }

    .file-name strong {
      color: var(--text);
      font-weight: 700;
    }

    .mini {
      font-size: 12px;
      color: var(--muted);
    }

    pre {
      background: #f5f7ff;
      border: 1px solid rgba(79,70,229,0.12);
      padding: 14px;
      border-radius: 14px;
      overflow-x: auto;
      font-size: 14px;
      line-height: 1.5;
      margin: 0;
    }

    img {
      max-width: 100%;
      border-radius: 14px;
      border: 1px solid var(--border);
    }

    .warn {
      background: var(--warning-bg);
      border: 1px solid var(--warning-border);
      padding: 12px;
      border-radius: 14px;
    }

    ul { margin: 8px 0 0 18px; }

    .footer-note {
      margin-top: 30px;
      font-size: 13px;
      color: var(--muted);
      text-align: center;
    }

    @media (max-width: 600px) {
      h1 { font-size: 32px; }
      .file-name { min-width: 0; }
      .btn { width: 100%; justify-content: center; }
      .file-wrap { width: 100%; }
    }
  </style>
</head>

<body>
  <div class="container">

    <div class="header">
      <div>
        <h1>Weather CSV Analyser</h1>
        <p class="subtitle">
          A tiny tool that turns a CSV into insights and a trend chart.
          Demo data loads automatically, and you can upload your own file any time.
        </p>

        <div class="badge-row">
          <span class="badge badge--demo"><span class="badge-dot"></span> Demo loaded</span>
          <span class="badge">Python</span>
          <span class="badge">Flask</span>
          <span class="badge">Matplotlib</span>
        </div>
      </div>
    </div>

    <div class="card">
      <h2>Upload CSV</h2>

      <p class="helper">
        Your CSV needs <strong>three columns</strong> in this order:
        <strong>date, min, max</strong>.
        The <strong>date</strong> should be an ISO timestamp (it’s basically a very strict date format computers love),
        like <span class="example">2021-07-02T07:00:00+08:00</span>.
        The <strong>min</strong> and <strong>max</strong> are temperatures in Fahrenheit (numbers).
      </p>

      <form method="POST" enctype="multipart/form-data">

        <div class="form-row">

          <label class="file-wrap">
            <input id="csv_file" type="file" name="csv_file" accept=".csv" required>
            <span class="btn btn-ghost" role="button">📎 Choose CSV</span>
            <span class="file-name" id="fileName">No file chosen</span>
          </label>

          <button class="btn btn-primary" type="submit">🚀 Analyse Upload</button>
          <a class="btn btn-ghost" href="/">↻ Reload Demo</a>

        </div>

        <p class="mini" style="margin-top:10px;">
          Tip: if you don’t have a file handy, just scroll down and check out the demo output.
        </p>

      </form>
    </div>

    {% if warnings %}
      <div class="card">
        <h2>Data Warnings</h2>
        <div class="warn">
          <ul>
            {% for w in warnings %}
              <li>{{ w }}</li>
            {% endfor %}
          </ul>
        </div>
      </div>
    {% endif %}

    {% if summary %}
      <div class="card">
        <h2>Summary</h2>
        <pre>{{ summary }}</pre>
      </div>
    {% endif %}

    {% if daily %}
      <div class="card">
        <h2>Daily Breakdown</h2>
        <pre>{{ daily }}</pre>
      </div>
    {% endif %}

    {% if chart_url %}
      <div class="card">
        <h2>Temperature Trend</h2>
        <img src="{{ chart_url }}" alt="Temperature trend chart">
      </div>
    {% endif %}

    <div class="footer-note">
      Built by Becky, powered by CSVs and curiosity. 📊
    </div>

  </div>

  <script>
    // Show chosen file name nicely
    const input = document.getElementById("csv_file");
    const nameEl = document.getElementById("fileName");

    if (input && nameEl) {
      input.addEventListener("change", () => {
        if (input.files && input.files.length > 0) {
          nameEl.innerHTML = "<strong>" + input.files[0].name + "</strong>";
        } else {
          nameEl.textContent = "No file chosen";
        }
      });
    }
  </script>

</body>
</html>
"""


# ----------------------------
# Route: GET loads demo, POST analyzes upload
# ----------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        # Demo mode: load sample CSV if it exists
        if SAMPLE_CSV_PATH.exists():
            summary, daily, warnings, chart_url = analyze_csv_path(str(SAMPLE_CSV_PATH))
        else:
            summary = "Demo file not found. Create data/sample.csv"
            daily = ""
            warnings = []
            chart_url = None

        return render_template_string(HTML, summary=summary, daily=daily, warnings=warnings, chart_url=chart_url)

    # POST: uploaded file
    file = request.files.get("csv_file")
    if not file or not file.filename.lower().endswith(".csv"):
        return render_template_string(HTML, summary="Please upload a .csv file.", daily="", warnings=[], chart_url=None)

    os.makedirs("uploads", exist_ok=True)
    upload_path = os.path.join("uploads", file.filename)
    file.save(upload_path)

    summary, daily, warnings, chart_url = analyze_csv_path(upload_path)
    return render_template_string(HTML, summary=summary, daily=daily, warnings=warnings, chart_url=chart_url)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)