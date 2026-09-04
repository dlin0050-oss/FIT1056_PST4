# main.py - The View Layer
from app.schedule import ScheduleManager

def front_desk_daily_roster(manager, day):
    """Displays a pretty table of all lessons on a given day."""
    print(f"\n--- Daily Roster for {day} ---")

    matching_courses = []
    for course in manager.courses:
        for lesson in course.lessons:
            if lesson.get("day", "").lower() == day.lower():
                matching_courses.append((course, lesson))
                break

    if not matching_courses:
        print(f"No lessons scheduled for {day}.")
        return

    for course, lesson in matching_courses:
        teacher = next((t for t in manager.teachers if str(t.id) == str(course.teacher_id)), None)
        teacher_name = teacher.name if teacher else "Unknown"
        print(f"Course: {course.name} (ID: {course.id}) | Time: {lesson.get('start_time')} | Room: {lesson.get('room')} | Teacher: {teacher_name}")
    
def switch_course(manager, student_id, from_course_id, to_course_id):
    """Handles student course enrollment transfers."""
    student = manager.find_student_by_id(student_id)
    from_course = manager.find_course_by_id(from_course_id)
    to_course = manager.find_course_by_id(to_course_id)

    if not student or not from_course or not to_course:
        print("Error: Switch failed. Invalid Student or Course ID.")
        return False

    if any(str(c_id) == str(from_course_id) for c_id in student.enrolled_course_ids):
        student.enrolled_course_ids = [c_id for c_id in student.enrolled_course_ids if str(c_id) != str(from_course_id)]
        
        new_c_id = int(to_course_id) if str(to_course_id).isdigit() else to_course_id
        student.enrolled_course_ids.append(new_c_id)

        manager._save_data()
        print(f"Success: Switched {student.name} from {from_course.name} to {to_course.name}.")
        return True
    else:
        print(f"Error: Student {student.name} is not enrolled in course {from_course.name}.")
        return False

def main():
    """Main function to run the MSMS application."""
    manager = ScheduleManager()
    
    while True:
        print("\n===== MSMS v3 (Object-Oriented) =====")
        print("1. View Daily Roster")
        print("2. Check-in Student")
        print("3. Switch Student Course")
        print("Q. Quit")

        choice = input("Enter choice: ").strip()

        if choice == '1':
            day = input("Enter day (e.g., Monday): ")
            front_desk_daily_roster(manager, day)
        elif choice == '2':
            s_id = input("Enter Student ID: ").strip()
            c_id = input("Enter Course ID: ").strip()
            manager.check_in(s_id, c_id)
        elif choice == '3':
            s_id = input("Enter Student ID: ").strip()
            from_c = input("Enter From Course ID: ").strip()
            to_c = input("Enter To Course ID: ").strip()
            switch_course(manager, s_id, from_c, to_c)
        elif choice.lower() == 'q': 
            print("Goodbye!")
            break
        
if __name__ == "__main__": 
    main()