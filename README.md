# 🌤 Weather CSV Analyser

A Python + Flask web application that analyses weather data from a CSV file and generates:

- Statistical summaries (min, max, averages)
- Daily breakdown reports
- A Matplotlib trend chart
- Data validation warnings
- Automatic demo dataset on load

Deployed live here:  
👉 https://weather-csv-analyser.onrender.com

---

## About This Project

This project was created as part of my SheCodes learning journey to demonstrate backend development skills using Python and Flask.

The goal was to build a small but production-ready data processing tool that:

- Accepts file uploads via POST
- Parses and validates structured CSV input
- Performs statistical calculations
- Generates dynamic visualisations
- Is deployed to a live environment

It is designed as portfolio material to showcase practical backend capabilities.

---

## 🛠 Tech Stack

- **Python 3**
- **Flask**
- **Matplotlib**
- **Gunicorn (production server)**
- **Render (deployment)**

---

## 📂 Expected CSV Format

The app expects a CSV file with the following columns: date,min,max

Where:

- `date` → ISO timestamp (e.g. `2021-07-02T07:00:00+08:00`)
- `min` → minimum temperature (Fahrenheit)
- `max` → maximum temperature (Fahrenheit)

---

## ⚙️ Features Demonstrated

- File uploads via Flask (multipart/form-data)
- GET vs POST request handling
- Custom data parsing and validation
- Temperature conversion (F → C)
- Statistical calculations (mean, min, max with index tracking)
- Dynamic Matplotlib chart generation
- Production deployment with Gunicorn
- Git-based CI deployment to Render

---

## 💻 Run Locally

```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python app.py

Then open:

http://127.0.0.1:5000/

🌱 Future Improvements

- Improved chart styling and theming
- Export analysis as downloadable report
- Support for Celsius input mode
- Enhanced validation and error handling

👋 Author
Becky Cole
SheCodes Developer Cohort
GitHub: https://github.com/Rebecca-de-Winter
