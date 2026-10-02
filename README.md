# Music School Management System — PST4

A cumulative FIT1056 application built from the student's PST1, PST2 and PST3 code. PST4 replaces the console interface with Streamlit while retaining earlier workflows.

## Setup and run (Windows)

Open the PST4 folder in VS Code, then use its terminal:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run main.py
```

Open the local address printed in the terminal. Stop the application with Ctrl+C. Run the final command again to restart. On macOS/Linux, use `python3 -m venv .venv` and `.venv/bin/python` in place of the Windows Python path.

## Cumulative features

| Stage | Features retained in PST4 |
| --- | --- |
| PST1 | Student registration, enrolment, student/teacher search and lists, teacher creation, automatic IDs |
| PST2 | JSON persistence, student and teacher updates/removal, attendance, downloadable text student cards |
| PST3 | User inheritance, StudentUser/TeacherUser/Course models, ScheduleManager, daily lesson roster and course transfers |
| PST4 | Streamlit sidebar navigation, forms, tables, feedback, session-state manager; teacher and course pages expose earlier functionality |

## Project structure

- `main.py`: launches the GUI only.
- `app/user.py`, `app/student.py`, `app/teacher.py`: retained PST3 models.
- `app/schedule.py`: business rules, lookups, registration, IDs, enrolment, transfers, attendance and JSON persistence.
- `gui/main_dashboard.py`: Fragment 4.1 dashboard and persistent session manager.
- `gui/student_pages.py`: Fragment 4.2 registration, search, lists, editing, removal, enrolment, transfers and ID cards.
- `gui/roster_pages.py`: Fragment 4.3 weekday roster and check-in.
- `gui/teacher_pages.py`, `gui/course_pages.py`: cumulative management features.
- `gui/common.py`: shared record selectors and action feedback.
- `data/msms.json`: original PST3 records, including historical attendance.

## Design choices and assumptions

The GUI calls ScheduleManager methods rather than implementing business rules. The manager persists across Streamlit reruns using session state. Changes save immediately to JSON; the data path is based on the project location. ID counters persist and are checked against the highest existing ID at load time. Deleted IDs are not reused.

Student enrolments are the source of truth when older course membership lists disagree. Loading rebuilds the course student lists; the next successful change saves the consistent lists. Existing historical attendance is retained, even when a student's current enrolments differ.

Instrument registration uses the first matching course with an existing teacher. When no matching course exists, registration fails without creating a student. Users can also add an unenrolled student and select a specific course using Enrol. Names need not be unique: selectors include IDs. Search is case-insensitive; an empty search lists all records.

Course transfers update both membership lists. Check-in requires an existing student, existing course and enrolment. Attendance is course-level with a current timestamp; it is not restricted to the displayed weekday or a specific lesson. Repeated check-ins are permitted.

Removing students removes their current enrolments but retains historical attendance. Teachers with assigned courses cannot be removed. Teacher speciality must match their courses. Lesson conflict validation checks identical start times for the same room or teacher; lesson duration and overlapping intervals are not modelled. Payments is a placeholder, as in the supplied PST4 template.

This prototype is intended for one receptionist using a local JSON file. Concurrent browser sessions do not coordinate edits. Invalid JSON is displayed as a load error and is not silently overwritten. Automated testing and further hardening are future PST5 work.

## Manual checks

Use a copy of the data file for testing, or restore a backup afterwards.

1. Open every sidebar page. Check students, teachers, courses and attendance display correctly.
2. Search `alice`, then search `PIANO` on Teacher Management. Clear the search to see all records.
3. Register a student with Piano. Verify the new student has ID 3 and is enrolled in Beginner Piano. A blank name or unavailable instrument should show an error without adding a student.
4. Add a Violin teacher (ID 3), then a Violin course (ID 104). Add a lesson and view its weekday roster.
5. Enrol the new student in Violin. Switch their Piano course from Beginner to Intermediate. Check both student and course tables.
6. Check in an enrolled student. Try checking Bob into a Piano course: reject it and leave attendance unchanged.
7. Edit names, download a student card, remove a test student and an unassigned teacher. Reject removing a teacher with assigned courses.
8. Stop and restart. Check saved changes remain. Create another record and verify its ID is higher, including after deletion.
9. Move between pages after creating a record; confirm the same manager and data remain available.
10. Verify empty student/teacher/course data produces helpful messages rather than empty-selector errors.

## Git workflow

Use your existing repository and the `individual` branch. Preserve existing history. Review and commit working increments; do not fabricate old commits.

Suggested commit sequence:

1. `fix(core): restore cumulative features and persistent IDs`
2. `feat(gui): add dashboard and session manager`
3. `feat(students): add student management interface`
4. `feat(roster): add daily schedule and check-in interface`
5. `feat(management): expose teacher and course workflows`
6. `docs: document cumulative features and manual checks`

After running and checking the application:

```powershell
git status
git branch --show-current
git add app gui main.py requirements.txt README.md .gitignore data/msms.json
git commit -m "feat(pst4): complete cumulative Streamlit application"
git push origin individual
```

The delivered ZIP contains source and data, without `.git`, virtual environments or caches. Copy its files into your existing working repository before committing. Pushing and Moodle submission must be completed separately.
