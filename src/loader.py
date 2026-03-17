import csv
import os
from typing import Dict, List, Tuple
from .models import Teacher, ClassGroup, Subject, Room, Timeslot, Requirement

def _read_csv(file_path: str) -> List[Dict[str, str]]:
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def load_data(data_dir: str):
    teachers_data = _read_csv(os.path.join(data_dir, "teachers.csv"))
    classes_data = _read_csv(os.path.join(data_dir, "classes.csv"))
    subjects_data = _read_csv(os.path.join(data_dir, "subjects.csv"))
    rooms_data = _read_csv(os.path.join(data_dir, "rooms.csv"))
    timeslots_data = _read_csv(os.path.join(data_dir, "timeslots.csv"))
    requirements_data = _read_csv(os.path.join(data_dir, "requirements.csv"))
    availability_data = _read_csv(os.path.join(data_dir, "teacher_availability.csv"))

    teachers = {row['teacher_id']: Teacher(row['teacher_id'], row['teacher_name']) for row in teachers_data}
    classes = {row['class_id']: ClassGroup(row['class_id'], row['class_name']) for row in classes_data}
    subjects = {row['subject_id']: Subject(row['subject_id'], row['subject_name']) for row in subjects_data}
    rooms = {row['room_id']: Room(row['room_id'], row['room_name'], int(row['capacity'])) for row in rooms_data}
    
    timeslots = {}
    for row in timeslots_data:
        ts = Timeslot(row['timeslot_id'], row['day'], int(row['period']))
        timeslots[ts.timeslot_id] = ts

    requirements = []
    for row in requirements_data:
        allowed = None
        if row.get('allowed_room_ids'):
            allowed = [r.strip() for r in row['allowed_room_ids'].split(';') if r.strip()]
        
        req = Requirement(
            requirement_id=row['requirement_id'],
            class_id=row['class_id'],
            subject_id=row['subject_id'],
            teacher_id=row['teacher_id'],
            sessions_per_week=int(row['sessions_per_week']),
            preferred_room_id=row.get('preferred_room_id') or None,
            allowed_room_ids=allowed
        )
        requirements.append(req)

    # teacher_id -> set of timeslot_ids where they are AVAILABLE
    teacher_availability = {t_id: set(timeslots.keys()) for t_id in teachers.keys()}
    for row in availability_data:
        t_id = row['teacher_id']
        ts_id = row['timeslot_id']
        is_avail = row['is_available'].strip().lower() in ['true', '1', 'yes']
        if t_id in teacher_availability:
            if not is_avail:
                teacher_availability[t_id].discard(ts_id)

    return {
        'teachers': teachers,
        'classes': classes,
        'subjects': subjects,
        'rooms': rooms,
        'timeslots': timeslots,
        'requirements': requirements,
        'teacher_availability': teacher_availability
    }
