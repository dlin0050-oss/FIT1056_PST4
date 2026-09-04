import json
import os
import datetime
from app.student import StudentUser
from app.teacher import TeacherUser, Course

class ScheduleManager:
    """The main controller for all business logic and data handling."""
    def __init__(self, data_path="data/msms.json"):
        self.data_path = data_path
        self.students = []
        self.teachers = []
        self.courses = []
        self.attendance_log = []    
        self._load_data()

    def _load_data(self):
        """Loads data from the JSON file and populates the object lists."""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                self.students = [StudentUser(**s) for s in data.get("students", [])]
                self.teachers = [TeacherUser(**t) for t in data.get("teachers", [])]
                self.courses = [Course(**c) for c in data.get("courses", [])]
                
                self.attendance_log = data.get("attendance", [])
        except FileNotFoundError:
            print("Data file not found. Starting with a clean state.")

    def _save_data(self):
        """Converts object lists back to dictionaries and saves to JSON."""
        data_to_save = {
            "students": [s.__dict__ for s in self.students],
            "teachers": [t.__dict__ for t in self.teachers],
            "courses": [c.__dict__ for c in self.courses],
            "attendance": self.attendance_log
        }
        dir_name = os.path.dirname(self.data_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=4)    

    def find_student_by_id(self, student_id):
        """Helper method to find a student by ID."""
        return next((s for s in self.students if str(s.id) == str(student_id)), None)

    def find_course_by_id(self, course_id):
        """Helper method to find a course by ID."""
        return next((c for c in self.courses if str(c.id) == str(course_id)), None)

    def check_in(self, student_id, course_id):
        """Records a student's attendance for a course after validation."""
        student = self.find_student_by_id(student_id)
        course = self.find_course_by_id(course_id)
        
        if not student or not course:
            print("Error: Check-in failed. Invalid Student or Course ID.")
            return False
            
        timestamp = datetime.datetime.now().isoformat()
        check_in_record = {
            "student_id": student_id, 
            "course_id": course_id, 
            "timestamp": timestamp
        }
        
        self.attendance_log.append(check_in_record)
        self._save_data()
        print(f"Success: Student {student.name} checked into {course.name}.")
        return True