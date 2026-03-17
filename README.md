# Timetable Solver

A constraint-based timetable scheduling system that generates weekly class schedules from structured input data. Features a fast CLI backend and a clean Flask-based web interface to view results.

## Features
- **Constraint Satisfaction Problem (CSP) Engine**: Recursive backtracking solver to search for valid combinations.
- **Hard Constraints**: Handles teacher availability, maximum sessions per day, room capacity limits, and no-overlapping rules.
- **Soft Constraints (Scoring Engine)**: Evaluates schedules penalizing uneven day loads, excessive gaps, and front-loaded periods.
- **Terminal CLI & Flask Web UI**: Run from terminal for direct export or view beautifully rendered tables in your browser.
- **Auto Data Validation**: Verifies dependencies in provided CSV files.
- **Multiple Output Formats**: Export valid schedules to `.csv` and structured text grids including specific teacher, student, and admin views.

## Project Structure
```
Timetable-Solver/
├── data/                    # Input CSV files
├── output/                  # Generated schedule outputs (CSV, TXT)
├── src/                     # Core backend engine
│   ├── config.py            # Solver configurations
│   ├── constraints.py       # Hard constraint validations
│   ├── evaluator.py         # Soft constraint scoring function
│   ├── exporter.py          # Formats and saves files
│   ├── loader.py            # Loads and maps CSV data to models
│   ├── models.py            # Entity dataclasses
│   ├── solver.py            # Recursive backtracking algorithm
│   └── validator.py         # Validates relations
├── static/                  # Web CSS (Forest Green & White theme)
├── templates/               # Web Jinja templates
├── app.py                   # Flask web interface
├── main.py                  # CLI backend runner
├── requirements.txt         # Dependencies
└── README.md                # Documentation
```

## How It Works
1. **Input Loading**: Reads `teachers`, `classes`, `subjects`, `rooms`, `requirements`, and `availability` from the `data/` folder.
2. **Expansion**: `Requirements` are broken into atomic `SessionTasks` that the solver needs to fulfill.
3. **Solver**: Attempts to place every `SessionTask` into a valid `Timeslot` and `Room`.
4. **Validation**: Each placement is run through `constraints.py`. If it fails, the solver explores the next alternative path.
5. **Scoring**: Because multiple schedules might be valid, `evaluator.py` ranks them.
6. **Outputting**: Export the highest scoring schedule in varying formats for different personas (Teacher limits, Class loads, Room allocations).

## Constraints Implemented
- Teacher cannot teach two places at once.
- Class cannot have two subjects simultaneously.
- Room cannot hold multiple classes at once.
- A subject won't appear twice on the same day for a class.
- Defined teacher availability slots are respected.
- Teacher must use their `preferred_room_id` if set.
- Maximum number of sessions per day per class.

## Scoring Overview
- Penalties for gaps between subjects in a day.
- Penalties if subjects are poorly distributed across the week.
- Penalties if teachers have too many consecutive teaching periods. 
- The lower the penalty subtractions (closer to base score), the better the schedule.

## Getting Started

### Prerequisites
- Python 3.8+
- Flask

### Installation

1. Prepare virtual environment & install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 1. Running the Terminal Version (CLI)

This will discover a schedule and save it inside the `output/` directory as `schedule.csv`, `report.txt`, and `student_view.txt`.

```bash
python main.py
```

### 2. Running the Flask Web App

Explore the schedules visually in your browser. Navigating to the homepage displays summary statistics before generating.

```bash
python app.py
```
Open `http://localhost:5000/` in your browser.

## Sample Outputs
`sample_output/` provides an example of what `report.txt` and `student_view.txt` generates so you can expect the layout structure. 
![Example App Layout](https://picsum.photos/seed/schedule/800/400)
