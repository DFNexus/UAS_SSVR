from ninja import Schema
from typing import List, Optional

class DashboardCourseSchema(Schema):
    id: int
    title: str
    slug: str
    
class ActiveCourseSchema(Schema):
    course: DashboardCourseSchema
    progress_percentage: float

class RecentLessonSchema(Schema):
    lesson_title: str
    section_title: str
    course_title: str

class StudentDashboardSchema(Schema):
    course_active: List[ActiveCourseSchema]
    course_completed: List[DashboardCourseSchema]
    total_enrolled: int
    total_completed: int
    recent_lesson: Optional[RecentLessonSchema] = None
    recommended_courses: List[DashboardCourseSchema]
