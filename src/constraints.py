def is_valid_assignment(
    schedule,
    task,
    timeslot,
    room,
    data,
    config
) -> bool:
    req = task.requirement
    ts_id = timeslot.timeslot_id
    r_id = room.room_id
    t_id = req.teacher_id
    c_id = req.class_id
    s_id = req.subject_id
    day = timeslot.day
    
    # 1. Teacher availability must be respected
    teacher_availability = data['teacher_availability']
    if ts_id not in teacher_availability[t_id]:
        return False
        
    # 2. Blocked periods must not be used
    blocked_periods = getattr(config, 'BLOCKED_PERIODS_BY_DAY', {})
    if timeslot.period in blocked_periods.get(day, []):
        return False

    # 3. Allowed room IDs must be respected if provided
    if req.allowed_room_ids and r_id not in req.allowed_room_ids:
        return False
        
    # 4. Preferred room must be respected if provided
    if req.preferred_room_id and r_id != req.preferred_room_id:
        return False

    # 5. A room cannot be used by more than one class at the same time
    if f"{r_id}_{ts_id}" in schedule.room_timeslot:
        return False
        
    # 6. A teacher cannot teach two classes at the same time
    if f"{t_id}_{ts_id}" in schedule.teacher_timeslot:
        return False
        
    # 7. A class cannot have two subjects at the same time
    if f"{c_id}_{ts_id}" in schedule.class_timeslot:
        return False
        
    # 8. A subject cannot appear twice in the same day for the same class
    if f"{c_id}_{day}_{s_id}" in schedule.class_day_subject:
        return False
        
    # 9. Maximum sessions per day per class must not be exceeded
    max_sessions = getattr(config, 'MAX_SESSIONS_PER_DAY_PER_CLASS', 999)
    if schedule.class_day_count.get(f"{c_id}_{day}", 0) >= max_sessions:
        return False
        
    return True
