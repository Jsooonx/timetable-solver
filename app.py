import os
from flask import Flask, render_template, request, redirect, url_for
from src.loader import load_data
from src.solver import TimetableSolver
from src.evaluator import calculate_score
from src.validator import validate_data

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def get_grid_data(schedule, data, entity_type):
    # entity_type in ['class', 'teacher', 'room']
    day_order = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5}
    unique_days = sorted(list(set(ts.day for ts in data['timeslots'].values())), key=lambda x: day_order.get(x, 99))
    unique_periods = sorted(list(set(ts.period for ts in data['timeslots'].values())))
    
    entities = {}
    if entity_type == 'class':
        entities = {c_id: c.class_name for c_id, c in data['classes'].items()}
    elif entity_type == 'teacher':
        entities = {t_id: t.teacher_name for t_id, t in data['teachers'].items()}
    elif entity_type == 'room':
        entities = {r_id: r.room_name for r_id, r in data['rooms'].items()}
        
    grids = []
    
    for ent_id, ent_name in entities.items():
        grid = {d: {p: "" for p in unique_periods} for d in unique_days}
        
        for session in schedule.sessions:
            match = False
            if entity_type == 'class' and session.task.requirement.class_id == ent_id:
                match = True
            elif entity_type == 'teacher' and session.task.requirement.teacher_id == ent_id:
                match = True
            elif entity_type == 'room' and session.room.room_id == ent_id:
                match = True
                
            if match:
                c_name = data['classes'][session.task.requirement.class_id].class_name
                s_name = data['subjects'][session.task.requirement.subject_id].subject_name
                t_name = data['teachers'][session.task.requirement.teacher_id].teacher_name
                r_name = session.room.room_name
                
                day = session.timeslot.day
                period = session.timeslot.period
                
                if entity_type == 'class':
                    info = f"<b>{s_name}</b><br><small>{t_name}, {r_name}</small>"
                elif entity_type == 'teacher':
                    info = f"<b>{c_name} - {s_name}</b><br><small>{r_name}</small>"
                elif entity_type == 'room':
                    info = f"<b>{c_name} - {s_name}</b><br><small>{t_name}</small>"
                
                grid[day][period] = info
                
        grids.append({
            'name': ent_name,
            'grid': grid
        })
        
    return {
        'days': unique_days,
        'periods': unique_periods,
        'grids': grids
    }

@app.route('/')
def index():
    try:
        data = load_data(DATA_DIR)
        errors = validate_data(data)
        context = {
            'teachers_count': len(data['teachers']),
            'classes_count': len(data['classes']),
            'subjects_count': len(data['subjects']),
            'rooms_count': len(data['rooms']),
            'requirements_count': len(data['requirements']),
            'errors': errors
        }
    except Exception as e:
        context = {'error': str(e)}
        
    return render_template('index.html', **context)

@app.route('/generate')
def generate():
    data = load_data(DATA_DIR)
    solver = TimetableSolver(data)
    best_schedule = solver.solve()
    
    if not best_schedule:
        return render_template('error.html', message="Failed to generate a valid schedule.")
        
    score = calculate_score(best_schedule, data)
    
    class_data = get_grid_data(best_schedule, data, 'class')
    teacher_data = get_grid_data(best_schedule, data, 'teacher')
    room_data = get_grid_data(best_schedule, data, 'room')
    
    return render_template('results.html', 
                          score=score,
                          total_sessions=len(best_schedule.sessions),
                          class_data=class_data,
                          teacher_data=teacher_data,
                          room_data=room_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
