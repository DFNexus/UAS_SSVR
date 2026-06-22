from ninja import Schema, ModelSchema, FilterSchema
from typing import List, Optional
from datetime import datetime

from apps.categories.schemas import CategorySchema
from apps.users.schemas import UserSchema
from .models import Course, Section, Lesson

class CourseFilterSchema(FilterSchema):
    search: Optional[str] = None
    category: Optional[str] = None
    instructor: Optional[int] = None
    level: Optional[str] = None
    status: Optional[str] = None
    ordering: Optional[str] = None

class LessonSchema(ModelSchema):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'order']

class LessonCreateSchema(Schema):
    title: str
    content: str
    order: int

class SectionSchema(ModelSchema):
    lessons: List[LessonSchema] = []
    
    class Meta:
        model = Section
        fields = ['id', 'title', 'order']

class SectionCreateSchema(Schema):
    title: str
    order: int

class CourseSchema(ModelSchema):
    category: CategorySchema
    instructor: UserSchema
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'description', 'level', 'status', 'created_at', 'updated_at']

class CourseDetailSchema(CourseSchema):
    sections: List[SectionSchema] = []

class CourseCreateSchema(Schema):
    title: str
    description: str
    category_id: int
    level: str = 'beginner'
    status: str = 'draft'

class CourseUpdateSchema(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    level: Optional[str] = None
    status: Optional[str] = None
