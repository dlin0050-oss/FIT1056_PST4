# Music School Management System (MSMS v3)

An OOP redesign of MSMS built with Python following the Model-View-Controller (MVC) architecture.

---

## 1. System Structure

#app/user.py`**: Base `User` class (`id`, `name`).
#app/student.py`**: `StudentUser` subclass managing `enrolled_course_ids`.
#app/teacher.py`**: `TeacherUser` and `Course` classes (handles nested `lessons`).
#app/schedule.py`**: `ScheduleManager` controller for logic, JSON persistence, and check-ins.
#main.py`**: CLI view layer driving the interactive terminal menu.
#data/msms.json`**: Persistent JSON data storage.

Design Choices & Assumptions
#Serialization via .__dict__ and **kwargs: To maintain a conservative, lightweight footprint without external dependencies, object-to-JSON serialization relies on .__dict__, and JSON-to-object loading utilizes standard dictionary unpacking (**kwargs). Model constructor parameter names strictly mirror the keys in data/msms.json.

#String-Casted ID Comparison: User input from terminal interfaces returns strings, whereas JSON stores numerical identifiers as integers. All lookup helper routines convert both operands to strings (str(s.id) == str(target_id)) to prevent type-mismatch bugs.

#Nested Schedule Model Parsing: Course schedules contain an array of lessons dictionaries containing day, start_time, and room. The view layer navigates this nested structure directly to isolate lesson daily schedules accurately.

---

*app/user.py: Base User class holding core attributes (id, name).
*app/teacher.py: TeacherUser model and Course model (stores teacher assignments and nested lessons).
*app/schedule.py: ScheduleManager controller handling business logic, JSON load/save via .__dict__, lookups, and check-ins.
*main.py: CLI View layer displaying the interactive menu and executing user workflows (roster, check-in, switch).
*data/msms.json: Persistent storage for students, teachers, courses, lessons, and attendance logs.
*app/__init__.py: Empty package marker allowing app/ to be imported as a module.

*check_in method: 
Validation: Calls find_student_by_id and find_course_by_id to verify both entities exist. If either ID is invalid, it prints an error message and returns False.
Timestamp Generation: Uses datetime.datetime.now().isoformat() to record the exact check-in date and time in standard ISO format.
Type Alignment: Converts numeric string inputs into int types so saved attendance records remain consistent with the existing JSON schema.
State Persistence: Appends the record dictionary (student_id, course_id, timestamp) to self.attendance_log, executes self._save_data() to update the JSON file, and prints a success message before returning True. 

---

## 2. How to Run & Test

Run the application:
python main.py