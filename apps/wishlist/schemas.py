from ninja import Schema, ModelSchema
from .models import Wishlist
from apps.courses.schemas import CourseSchema

class WishlistSchema(ModelSchema):
    course: CourseSchema

    class Meta:
        model = Wishlist
        fields = ['id', 'added_at']

class WishlistCreateSchema(Schema):
    course_id: int
