from app.user import User

class StudentUser(User):
    """Represents a student user in the system."""
    def __init__(self, id, name, enrolled_course_ids=None):
        super().__init__(id, name)
        self.enrolled_course_ids = enrolled_course_ids if enrolled_course_ids is not None else []