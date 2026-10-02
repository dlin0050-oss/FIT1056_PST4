"""Shared business logic for the cumulative PST1–4 application."""
import json
from datetime import datetime
from pathlib import Path
from app.student import StudentUser
from app.teacher import TeacherUser, Course


class ScheduleManager:
    def __init__(self, data_path=None):
        self.data_path = Path(data_path) if data_path else Path(__file__).resolve().parents[1] / 'data/msms.json'
        self.students, self.teachers, self.courses, self.attendance_log = [], [], [], []
        self._load_data()

    def _load_data(self):
        data = json.loads(self.data_path.read_text(encoding='utf-8')) if self.data_path.exists() else {}
        self.students = [StudentUser(**s) for s in data.get('students', [])]
        self.teachers = [TeacherUser(**t) for t in data.get('teachers', [])]
        self.courses = [Course(**c) for c in data.get('courses', [])]
        self.attendance_log = data.get('attendance', [])
        for label in ('student', 'teacher', 'course'):
            records = getattr(self, label + 's')
            next_id = max((int(x.id) for x in records), default=0) + 1
            setattr(self, 'next_' + label + '_id', max(next_id, int(data.get('next_' + label + '_id', 1))))
        self.next_lesson_id = max((int(l['lesson_id']) for c in self.courses for l in c.lessons), default=0) + 1
        # Student memberships are authoritative when legacy lists disagree.
        for c in self.courses:
            c.enrolled_student_ids = [s.id for s in self.students if c.id in s.enrolled_course_ids]

    def _save_data(self):
        data = {name: [x.__dict__ for x in getattr(self, name)] for name in ('students', 'teachers', 'courses')}
        data['attendance'] = self.attendance_log
        for label in ('student', 'teacher', 'course'):
            data['next_' + label + '_id'] = getattr(self, 'next_' + label + '_id')
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.data_path.with_suffix('.tmp')
        temp.write_text(json.dumps(data, indent=4), encoding='utf-8')
        temp.replace(self.data_path)

    @staticmethod
    def _text(value, field):
        value = value.strip()
        if not value:
            raise ValueError(f'{field} cannot be blank.')
        return value

    def _find(self, records, record_id, label):
        result = next((x for x in records if str(x.id) == str(record_id)), None)
        if result is None:
            raise ValueError(f'{label} not found.')
        return result

    def find_student_by_id(self, student_id):
        return next((s for s in self.students if str(s.id) == str(student_id)), None)

    def find_course_by_id(self, course_id):
        return next((c for c in self.courses if str(c.id) == str(course_id)), None)

    def find_students(self, term):
        return [s for s in self.students if term.strip().casefold() in s.name.casefold()]

    def find_teachers(self, term):
        term = term.strip().casefold()
        return [t for t in self.teachers if term in t.name.casefold() or term in (t.speciality or '').casefold()]

    def add_student(self, name):
        student = StudentUser(self.next_student_id, self._text(name, 'Name'))
        self.students.append(student)
        self.next_student_id += 1
        self._save_data()
        return student

    def add_teacher(self, name, speciality):
        teacher = TeacherUser(self.next_teacher_id, self._text(name, 'Name'), self._text(speciality, 'Speciality'))
        self.teachers.append(teacher)
        self.next_teacher_id += 1
        self._save_data()
        return teacher

    def add_course(self, name, instrument, teacher_id):
        name, instrument = self._text(name, 'Name'), self._text(instrument, 'Instrument')
        teacher = self._find(self.teachers, teacher_id, 'Teacher')
        if (teacher.speciality or '').casefold() != instrument.casefold():
            raise ValueError('The teacher speciality must match the instrument.')
        course = Course(self.next_course_id, name, instrument, teacher.id)
        self.courses.append(course)
        self.next_course_id += 1
        self._save_data()
        return course

    def register_new_student(self, name, instrument):
        name, instrument = self._text(name, 'Name'), self._text(instrument, 'Instrument')
        course = next((c for c in self.courses if c.instrument.casefold() == instrument.casefold()), None)
        if course is None:
            raise ValueError('No course is available for this instrument. Add a teacher and course first.')
        self._find(self.teachers, course.teacher_id, 'Course teacher')
        student = StudentUser(self.next_student_id, name, [course.id])
        self.students.append(student)
        course.enrolled_student_ids.append(student.id)
        self.next_student_id += 1
        self._save_data()
        return student

    def enrol_student(self, student_id, course_id):
        student = self._find(self.students, student_id, 'Student')
        course = self._find(self.courses, course_id, 'Course')
        if course.id in student.enrolled_course_ids:
            raise ValueError('Student is already enrolled in this course.')
        student.enrolled_course_ids.append(course.id)
        course.enrolled_student_ids.append(student.id)
        self._save_data()

    def switch_course(self, student_id, from_course_id, to_course_id):
        student = self._find(self.students, student_id, 'Student')
        old = self._find(self.courses, from_course_id, 'Original course')
        new = self._find(self.courses, to_course_id, 'New course')
        if old.id not in student.enrolled_course_ids:
            raise ValueError('Student is not enrolled in the original course.')
        if new.id in student.enrolled_course_ids:
            raise ValueError('Student is already enrolled in the destination course.')
        student.enrolled_course_ids.remove(old.id)
        student.enrolled_course_ids.append(new.id)
        old.enrolled_student_ids = [i for i in old.enrolled_student_ids if i != student.id]
        new.enrolled_student_ids.append(student.id)
        self._save_data()
        return True

    def update_student(self, student_id, name):
        student = self._find(self.students, student_id, 'Student')
        student.name = self._text(name, 'Name')
        self._save_data()

    def update_teacher(self, teacher_id, name, speciality):
        teacher = self._find(self.teachers, teacher_id, 'Teacher')
        name, speciality = self._text(name, 'Name'), self._text(speciality, 'Speciality')
        if any(c.teacher_id == teacher.id and c.instrument.casefold() != speciality.casefold() for c in self.courses):
            raise ValueError('Speciality must remain compatible with assigned courses.')
        teacher.name, teacher.speciality = name, speciality
        self._save_data()

    def remove_student(self, student_id):
        student = self._find(self.students, student_id, 'Student')
        self.students.remove(student)
        for c in self.courses:
            c.enrolled_student_ids = [i for i in c.enrolled_student_ids if i != student.id]
        self._save_data()

    def remove_teacher(self, teacher_id):
        teacher = self._find(self.teachers, teacher_id, 'Teacher')
        if any(c.teacher_id == teacher.id for c in self.courses):
            raise ValueError('Cannot remove a teacher assigned to a course.')
        self.teachers.remove(teacher)
        self._save_data()

    def check_in(self, student_id, course_id):
        student = self._find(self.students, student_id, 'Student')
        course = self._find(self.courses, course_id, 'Course')
        if course.id not in student.enrolled_course_ids:
            raise ValueError('Student is not enrolled in this course.')
        self.attendance_log.append({'student_id': student.id, 'course_id': course.id, 'timestamp': datetime.now().isoformat()})
        self._save_data()
        return True

    def student_card(self, student_id):
        student = self._find(self.students, student_id, 'Student')
        names = [c.name for c in self.courses if c.id in student.enrolled_course_ids]
        return f'MUSIC SCHOOL ID BADGE\nID: {student.id}\nName: {student.name}\nEnrolled in: {", ".join(names) or "None"}\n'

    def add_lesson(self, course_id, day, start_time, room):
        course = self._find(self.courses, course_id, 'Course')
        room = self._text(room, 'Room')
        if day not in ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'):
            raise ValueError('Choose a weekday.')
        datetime.strptime(start_time, '%H:%M')
        for c in self.courses:
            for lesson in c.lessons:
                if lesson['day'] == day and lesson['start_time'] == start_time and (lesson['room'].casefold() == room.casefold() or c.teacher_id == course.teacher_id):
                    raise ValueError('Room or teacher is already booked at this start time.')
        course.lessons.append({'lesson_id': self.next_lesson_id, 'day': day, 'start_time': start_time, 'room': room})
        self.next_lesson_id += 1
        self._save_data()

    def daily_roster(self, day):
        rows = []
        for course in self.courses:
            teacher = next((t for t in self.teachers if t.id == course.teacher_id), None)
            for lesson in course.lessons:
                if lesson['day'] == day:
                    rows.append({'Course ID': course.id, 'Course': course.name, 'Time': lesson['start_time'], 'Room': lesson['room'], 'Teacher': teacher.name if teacher else 'Unknown'})
        return sorted(rows, key=lambda row: row['Time'])
