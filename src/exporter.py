import csv
import os
from .evaluator import calculate_score

def print_terminal_output(schedule, data, score):
    print("\n" + "="*50)
    print("TIMETABLE SOLVER - BEST SCHEDULE")
    print("="*50)
    print(f"Total Session Tasks: {len(schedule.sessions)}")
    print(f"Best Schedule Score: {score}")
    print("\nReadable Schedule List:")
    for session in schedule.sessions:
        c_name = data['classes'][session.task.requirement.class_id].class_name
        s_name = data['subjects'][session.task.requirement.subject_id].subject_name
        t_name = data['teachers'][session.task.requirement.teacher_id].teacher_name
        r_name = session.room.room_name
        day = session.timeslot.day
        period = session.timeslot.period
        print(f"[{day} P{period}] {c_name} - {s_name} (Teacher: {t_name}, Room: {r_name})")

def export_csv(schedule, data, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "schedule.csv")
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Day', 'Period', 'Class', 'Subject', 'Teacher', 'Room'])
        for session in schedule.sessions:
            c_name = data['classes'][session.task.requirement.class_id].class_name
            s_name = data['subjects'][session.task.requirement.subject_id].subject_name
            t_name = data['teachers'][session.task.requirement.teacher_id].teacher_name
            r_name = session.room.room_name
            day = session.timeslot.day
            period = session.timeslot.period
            writer.writerow([day, period, c_name, s_name, t_name, r_name])
    print(f"Exported schedule to {file_path}")

def generate_grid_text(schedule, data, entity_type):
    # entity_type in ['class', 'teacher', 'room']
    
    # Sort timeslots for grid
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

    output = []
    
    for ent_id, ent_name in entities.items():
        output.append(f"\n--- {ent_name.upper()} TIMETABLE ---")
        
        # Build grid
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
                
                info = ""
                if entity_type == 'class':
                    info = f"{s_name}\n({t_name}, {r_name})"
                elif entity_type == 'teacher':
                    info = f"{c_name} - {s_name}\n({r_name})"
                elif entity_type == 'room':
                    info = f"{c_name} - {s_name}\n({t_name})"
                
                grid[day][period] = info.replace('\n', ' ')

        # Determine dynamic column widths
        col_widths = {p: len(f"Period {p}") for p in unique_periods}
        for d in unique_days:
            for p in unique_periods:
                if len(grid[d][p]) > col_widths[p]:
                    col_widths[p] = len(grid[d][p])
        
        # Add some padding to each column
        for p in unique_periods:
            col_widths[p] += 1

        # Format grid
        header = f"{'Day/Period':<12}"
        for p in unique_periods:
            p_str = f"Period {p}"
            header += f"| {p_str:<{col_widths[p]}}"
            
        output.append(header)
        output.append("-" * len(header))
        
        for day in unique_days:
            row_str = f"{day:<12}"
            for p in unique_periods:
                cell = grid[day][p]
                row_str += f"| {cell:<{col_widths[p]}}"
            output.append(row_str)
            
    return "\n".join(output)

def export_txt(schedule, data, output_dir, score):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. student_view.txt
    student_file = os.path.join(output_dir, "student_view.txt")
    with open(student_file, 'w', encoding='utf-8') as f:
        f.write("STUDENT TIMETABLE VIEW\n======================\n")
        f.write(generate_grid_text(schedule, data, 'class'))
        
    # 2. report.txt
    report_file = os.path.join(output_dir, "report.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("ADMIN TIMETABLE REPORT\n======================\n")
        f.write(f"Total Session Tasks: {len(schedule.sessions)}\n")
        f.write(f"Best Score: {score}\n\n")
        
        f.write("Readable Schedule List:\n")
        for session in schedule.sessions:
            c_name = data['classes'][session.task.requirement.class_id].class_name
            s_name = data['subjects'][session.task.requirement.subject_id].subject_name
            t_name = data['teachers'][session.task.requirement.teacher_id].teacher_name
            r_name = session.room.room_name
            day = session.timeslot.day
            period = session.timeslot.period
            f.write(f"[{day} P{period}] {c_name} - {s_name} (Teacher: {t_name}, Room: {r_name})\n")
            
        f.write("\n\nCLASS GRIDS:\n")
        f.write(generate_grid_text(schedule, data, 'class'))
        
        f.write("\n\nTEACHER GRIDS:\n")
        f.write(generate_grid_text(schedule, data, 'teacher'))
        
        f.write("\n\nROOM GRIDS:\n")
        f.write(generate_grid_text(schedule, data, 'room'))
        
    print(f"Exported text reports to {output_dir}")
