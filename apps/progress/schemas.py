from ninja import ModelSchema, Schema
from typing import Dict

from apps.courses.schemas import LessonSchema
from .models import Progress

class ProgressSchema(ModelSchema):
    lesson: LessonSchema
    
    class Meta:
        model = Progress
        fields = ['id', 'completed', 'completed_at']


class ProgressDetailSchema(Schema):
    lesson_progress: Dict[int, bool]
    section_progress: Dict[int, float]
    course_progress: float
