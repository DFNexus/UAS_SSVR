from ninja import Router
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError
from django.utils import timezone

from .models import Progress
from apps.courses.models import Lesson, Course
from apps.enrollments.models import Enrollment
from .schemas import ProgressSchema, CourseProgressDetailSchema
from apps.users.auth import StudentAuth

router = Router(tags=["Progress"])

@router.post("/lessons/{lesson_id}/complete", response={200: ProgressSchema}, auth=StudentAuth())
def complete_lesson(request, lesson_id: int):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.section.course
    
    # Check enrollment
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    if not enrollment:
        raise HttpError(403, "You must be enrolled in the course to complete its lessons.")
        
    progress, created = Progress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson,
        defaults={'completed': True, 'completed_at': timezone.now()}
    )
    
    if not created and not progress.completed:
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()
        
    return 200, progress

from .services import ProgressService

@router.get("/courses/{course_id}/progress", response=CourseProgressDetailSchema, auth=StudentAuth())
def course_progress(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    
    if not enrollment:
        raise HttpError(403, "You are not enrolled in this course.")
        
    return ProgressService.calculate_course_progress(enrollment)
