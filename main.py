import os
import sys

# Ensure src is in path if running from root
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.loader import load_data
from src.validator import validate_data
from src.solver import TimetableSolver
from src.evaluator import calculate_score
from src.exporter import print_terminal_output, export_csv, export_txt

def main():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    
    print("Loading data...")
    data = load_data(data_dir)
    
    print("Validating data...")
    errors = validate_data(data)
    if errors:
        print("Validation errors found:")
        for err in errors:
            print(f" - {err}")
        return
    print("Data validation successful.")
    
    print("Initializing solver...")
    solver = TimetableSolver(data)
    print(f"Total Session Tasks to schedule: {len(solver.tasks)}")
    
    print("Searching for valid schedules...")
    best_schedule = solver.solve()
    
    if not best_schedule:
        print("No valid schedule could be found that satisfies all constraints.")
        return
        
    score = calculate_score(best_schedule, data)
    
    print_terminal_output(best_schedule, data, score)
    export_csv(best_schedule, data, output_dir)
    export_txt(best_schedule, data, output_dir, score)

if __name__ == "__main__":
    main()
