from ninja import Router
from typing import List
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

from .models import Enrollment
from apps.courses.models import Course
from .schemas import EnrollmentSchema, EnrollmentCreateSchema
from apps.users.auth import StudentAuth, InstructorAuth

router = Router(tags=["Enrollments"])

@router.post("/enrollments/", response={201: EnrollmentSchema}, auth=StudentAuth())
def create_enrollment(request, payload: EnrollmentCreateSchema):
    course = get_object_or_404(Course, id=payload.course_id)
    
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        raise HttpError(400, "You are already enrolled in this course")
        
    enrollment = Enrollment.objects.create(
        student=request.user,
        course=course
    )
    return 201, enrollment

@router.get("/enrollments/me", response=List[EnrollmentSchema], auth=StudentAuth())
def my_enrollments(request):
    return Enrollment.objects.filter(student=request.user).select_related(
        'course', 'student', 'course__category', 'course__instructor'
    )

@router.get("/courses/{course_id}/enrollments", response=List[EnrollmentSchema], auth=InstructorAuth())
def course_enrollments(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)
    if course.instructor != request.user and request.user.role != 'admin':
        raise HttpError(403, "You can only view enrollments for your own courses.")
        
    return Enrollment.objects.filter(course=course).select_related(
        'course', 'student', 'course__category', 'course__instructor'
    )
