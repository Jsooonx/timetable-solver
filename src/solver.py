import time
from typing import List, Optional
from .models import SessionTask, Schedule, ScheduledSession
from .constraints import is_valid_assignment
from .evaluator import calculate_score
from . import config

def expand_requirements(requirements) -> List[SessionTask]:
    tasks = []
    task_counter = 1
    for req in requirements:
        for _ in range(req.sessions_per_week):
            tasks.append(SessionTask(f"TASK_{task_counter}", req))
            task_counter += 1
    # Heuristic: sort tasks by most constrained (e.g. preferred room, allowed rooms, teacher availability)
    tasks.sort(key=lambda t: (
        0 if t.requirement.preferred_room_id else 1,
        len(t.requirement.allowed_room_ids) if t.requirement.allowed_room_ids else 999
    ))
    return tasks

class TimetableSolver:
    def __init__(self, data):
        self.data = data
        self.tasks = expand_requirements(data['requirements'])
        self.timeslots = list(data['timeslots'].values())
        self.rooms = list(data['rooms'].values())
        
        # Sort timeslots by day/period
        day_order = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5}
        self.timeslots.sort(key=lambda x: (day_order.get(x.day, 99), x.period))

        self.valid_schedules = []
        self.start_time = 0

    def solve(self) -> Optional[Schedule]:
        self.start_time = time.time()
        self.valid_schedules = []
        
        initial_schedule = Schedule()
        self._backtrack(initial_schedule, 0)
        
        if not self.valid_schedules:
            return None
            
        print(f"Found {len(self.valid_schedules)} valid schedules.")
        
        # Evaluate and find the best
        best_schedule = None
        best_score = float('-inf')
        
        for sched in self.valid_schedules:
            score = calculate_score(sched, self.data)
            if score > best_score:
                best_score = score
                best_schedule = sched
                
        print(f"Best score found: {best_score}")
        return best_schedule

    def _backtrack(self, schedule: Schedule, task_idx: int):
        if task_idx == len(self.tasks):
            # Found a valid schedule
            self.valid_schedules.append(schedule.clone())
            return
            
        if len(self.valid_schedules) >= getattr(config, 'MAX_SOLUTIONS_TO_FIND', 10):
            return
            
        if time.time() - self.start_time > getattr(config, 'MAX_SEARCH_TIME_SECONDS', 10):
            return

        task = self.tasks[task_idx]
        
        # Room filtering heuristic
        applicable_rooms = self.rooms
        if task.requirement.preferred_room_id:
            applicable_rooms = [r for r in applicable_rooms if r.room_id == task.requirement.preferred_room_id]
        elif task.requirement.allowed_room_ids:
            applicable_rooms = [r for r in applicable_rooms if r.room_id in task.requirement.allowed_room_ids]

        for ts in self.timeslots:
            for room in applicable_rooms:
                if is_valid_assignment(schedule, task, ts, room, self.data, config):
                    session = ScheduledSession(task, ts, room)
                    schedule.add_session(session)
                    
                    self._backtrack(schedule, task_idx + 1)
                    
                    schedule.remove_session(session)
                    
                    if len(self.valid_schedules) >= getattr(config, 'MAX_SOLUTIONS_TO_FIND', 10):
                        return
                    if time.time() - self.start_time > getattr(config, 'MAX_SEARCH_TIME_SECONDS', 10):
                        return
