from ninja import ModelSchema, Schema

from apps.courses.schemas import CourseSchema
from apps.users.schemas import UserSchema
from .models import Enrollment

class EnrollmentSchema(ModelSchema):
    course: CourseSchema
    student: UserSchema
    
    class Meta:
        model = Enrollment
        fields = ['id', 'enrolled_at']

class EnrollmentCreateSchema(Schema):
    course_id: int
