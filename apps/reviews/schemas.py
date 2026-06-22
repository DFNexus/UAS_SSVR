from ninja import Schema, ModelSchema
from .models import Review
from typing import Optional

class ReviewSchema(ModelSchema):
    student_name: str

    class Meta:
        model = Review
        fields = ['id', 'rating', 'body', 'created_at', 'updated_at']

    @staticmethod
    def resolve_student_name(obj):
        return obj.student.username

class ReviewCreateSchema(Schema):
    rating: int
    body: Optional[str] = ""

class ReviewUpdateSchema(Schema):
    rating: int
    body: Optional[str] = ""
