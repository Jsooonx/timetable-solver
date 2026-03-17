from dataclasses import dataclass, field
from typing import List, Optional, Set

@dataclass
class Teacher:
    teacher_id: str
    teacher_name: str

@dataclass
class ClassGroup:
    class_id: str
    class_name: str

@dataclass
class Subject:
    subject_id: str
    subject_name: str

@dataclass
class Room:
    room_id: str
    room_name: str
    capacity: int

@dataclass
class Timeslot:
    timeslot_id: str
    day: str
    period: int

@dataclass
class Requirement:
    requirement_id: str
    class_id: str
    subject_id: str
    teacher_id: str
    sessions_per_week: int
    preferred_room_id: Optional[str] = None
    allowed_room_ids: Optional[List[str]] = None

@dataclass
class SessionTask:
    task_id: str
    requirement: Requirement
    
@dataclass
class ScheduledSession:
    task: SessionTask
    timeslot: Timeslot
    room: Room

@dataclass
class Schedule:
    sessions: List[ScheduledSession] = field(default_factory=list)
    room_timeslot: Set[str] = field(default_factory=set)
    teacher_timeslot: Set[str] = field(default_factory=set)
    class_timeslot: Set[str] = field(default_factory=set)
    class_day_subject: Set[str] = field(default_factory=set)
    class_day_count: dict = field(default_factory=dict)

    def add_session(self, session: ScheduledSession):
        self.sessions.append(session)
        ts_id = session.timeslot.timeslot_id
        r_id = session.room.room_id
        t_id = session.task.requirement.teacher_id
        c_id = session.task.requirement.class_id
        day = session.timeslot.day
        s_id = session.task.requirement.subject_id
        
        self.room_timeslot.add(f"{r_id}_{ts_id}")
        self.teacher_timeslot.add(f"{t_id}_{ts_id}")
        self.class_timeslot.add(f"{c_id}_{ts_id}")
        self.class_day_subject.add(f"{c_id}_{day}_{s_id}")
        
        key = f"{c_id}_{day}"
        self.class_day_count[key] = self.class_day_count.get(key, 0) + 1

    def remove_session(self, session: ScheduledSession):
        self.sessions.remove(session)
        ts_id = session.timeslot.timeslot_id
        r_id = session.room.room_id
        t_id = session.task.requirement.teacher_id
        c_id = session.task.requirement.class_id
        day = session.timeslot.day
        s_id = session.task.requirement.subject_id

        self.room_timeslot.remove(f"{r_id}_{ts_id}")
        self.teacher_timeslot.remove(f"{t_id}_{ts_id}")
        self.class_timeslot.remove(f"{c_id}_{ts_id}")
        self.class_day_subject.remove(f"{c_id}_{day}_{s_id}")
        
        key = f"{c_id}_{day}"
        self.class_day_count[key] -= 1

    def clone(self):
        new_sched = Schedule()
        new_sched.sessions = list(self.sessions)
        new_sched.room_timeslot = set(self.room_timeslot)
        new_sched.teacher_timeslot = set(self.teacher_timeslot)
        new_sched.class_timeslot = set(self.class_timeslot)
        new_sched.class_day_subject = set(self.class_day_subject)
        new_sched.class_day_count = dict(self.class_day_count)
        return new_sched
