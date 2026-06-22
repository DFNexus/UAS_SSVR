from ninja import Router
from django.shortcuts import get_object_or_404
from .models import Review
from .schemas import ReviewSchema, ReviewCreateSchema, ReviewUpdateSchema
from apps.courses.models import Course
from apps.enrollments.models import Enrollment
from apps.users.auth import StudentAuth, BaseAuth
from ninja.responses import Status
from ninja.errors import HttpError

router = Router(tags=["Reviews"])

@router.post("/courses/{course_id}/reviews", response={201: ReviewSchema, 400: dict, 403: dict}, auth=StudentAuth())
def create_review(request, course_id: int, data: ReviewCreateSchema):
    course = get_object_or_404(Course, id=course_id)
    
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        raise HttpError(403, "You must be enrolled to leave a review.")
        
    if Review.objects.filter(student=request.user, course=course).exists():
        raise HttpError(400, "You have already reviewed this course.")
        
    review = Review.objects.create(
        student=request.user,
        course=course,
        rating=data.rating,
        body=data.body
    )
    return Status(201, review)

@router.get("/courses/{course_id}/reviews", response=list[ReviewSchema])
def list_course_reviews(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)
    return Review.objects.filter(course=course).select_related('student')

@router.put("/reviews/{review_id}", response={200: ReviewSchema, 400: dict, 403: dict}, auth=StudentAuth())
def update_review(request, review_id: int, data: ReviewUpdateSchema):
    review = get_object_or_404(Review, id=review_id)
    
    if review.student != request.user:
        raise HttpError(403, "You can only update your own review.")
        
    review.rating = data.rating
    review.body = data.body
    review.save()
    return Status(200, review)

@router.delete("/reviews/{review_id}", response={204: None, 403: dict}, auth=BaseAuth())
def delete_review(request, review_id: int):
    review = get_object_or_404(Review, id=review_id)
    
    if review.student != request.user and request.user.role != 'admin':
        raise HttpError(403, "You don't have permission to delete this review.")
        
    review.delete()
    return Status(204, None)
