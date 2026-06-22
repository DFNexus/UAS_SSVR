from ninja import ModelSchema, Schema
from typing import List

from apps.courses.schemas import LessonSchema
from .models import Progress

class ProgressSchema(ModelSchema):
    lesson: LessonSchema
    
    class Meta:
        model = Progress
        fields = ['id', 'completed', 'completed_at']

class SectionProgressSchema(Schema):
    section_id: int
    title: str
    total_lessons: int
    completed_lessons: int
    progress_percentage: float

class CourseProgressDetailSchema(Schema):
    course_id: int
    total_lessons: int
    completed_lessons: int
    progress_percentage: float
    sections: List[SectionProgressSchema] = []
