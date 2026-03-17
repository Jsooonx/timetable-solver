def calculate_score(schedule, data) -> int:
    score = 10000
    
    # Extract sessions by class and day
    class_day_sessions = {}
    teacher_day_sessions = {}
    
    for session in schedule.sessions:
        c_id = session.task.requirement.class_id
        t_id = session.task.requirement.teacher_id
        day = session.timeslot.day
        period = session.timeslot.period
        
        if c_id not in class_day_sessions:
            class_day_sessions[c_id] = {}
        if day not in class_day_sessions[c_id]:
            class_day_sessions[c_id][day] = []
        class_day_sessions[c_id][day].append(period)

        if t_id not in teacher_day_sessions:
            teacher_day_sessions[t_id] = {}
        if day not in teacher_day_sessions[t_id]:
            teacher_day_sessions[t_id][day] = []
        teacher_day_sessions[t_id][day].append(period)

    # 1. Penalize gaps within a class day
    for c_id, days in class_day_sessions.items():
        for day, periods in days.items():
            periods.sort()
            for i in range(1, len(periods)):
                diff = periods[i] - periods[i-1]
                if diff > 1:
                    score -= (diff - 1) * 10  # Penalize gap

    # 2. Too few used days in a week (unbalanced load)
    # 3. Penalize unbalanced daily load
    # Let's say ideal load is total / len(days)
    for c_id, days in class_day_sessions.items():
        if len(days) < 5:  # Assuming a 5-day week
            score -= (5 - len(days)) * 20
        
        counts = [len(p) for p in days.values()]
        if counts:
            max_c = max(counts)
            min_c = min(counts)
            score -= (max_c - min_c) * 5

    # 4. Penalize teachers teaching too many consecutive periods
    for t_id, days in teacher_day_sessions.items():
        for day, periods in days.items():
            periods.sort()
            consecutive = 1
            for i in range(1, len(periods)):
                if periods[i] - periods[i-1] == 1:
                    consecutive += 1
                    if consecutive > 3:  # More than 3 consecutive periods
                        score -= 15
                else:
                    consecutive = 1

    # 5. Penalize schedules too heavily front-loaded into early weekdays
    # (Assuming Monday=1... Friday=5)
    day_weights = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5}
    for c_id, days in class_day_sessions.items():
        front_loaded_score = 0
        for day, periods in days.items():
            weight = day_weights.get(day, 3)
            front_loaded_score += len(periods) * (5 - weight)  # early days give higher penalty component
        score -= front_loaded_score * 1  # slight penalty

    return score
