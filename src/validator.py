def validate_data(data: dict) -> list:
    errors = []
    teachers = data['teachers']
    classes = data['classes']
    subjects = data['subjects']
    rooms = data['rooms']
    requirements = data['requirements']

    for req in requirements:
        if req.teacher_id not in teachers:
            errors.append(f"Requirement {req.requirement_id}: Teacher {req.teacher_id} not found.")
        if req.class_id not in classes:
            errors.append(f"Requirement {req.requirement_id}: Class {req.class_id} not found.")
        if req.subject_id not in subjects:
            errors.append(f"Requirement {req.requirement_id}: Subject {req.subject_id} not found.")
        if req.preferred_room_id and req.preferred_room_id not in rooms:
            errors.append(f"Requirement {req.requirement_id}: Preferred room {req.preferred_room_id} not found.")
        if req.allowed_room_ids:
            for r_id in req.allowed_room_ids:
                if r_id not in rooms:
                    errors.append(f"Requirement {req.requirement_id}: Allowed room {r_id} not found.")

    return errors
