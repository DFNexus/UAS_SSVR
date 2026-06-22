from ninja import Router
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Progress
from apps.courses.models import Lesson, Course
from apps.enrollments.models import Enrollment
from .schemas import ProgressSchema, ProgressDetailSchema
from .services import calculate_progress
from apps.users.auth import StudentAuth

router = Router(tags=["Progress"])

@router.post("/lessons/{lesson_id}/complete", response={200: ProgressSchema}, auth=StudentAuth())
def complete_lesson(request, lesson_id: int):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Must be enrolled
    enrollment = get_object_or_404(Enrollment, student=request.user, course=lesson.section.course)
    
    progress, created = Progress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson,
        defaults={'completed': True, 'completed_at': timezone.now()}
    )
    
    if not created and not progress.completed:
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()
        
    from ninja.responses import Status
    return Status(200, progress)

@router.get("/courses/{course_id}/progress", response=ProgressDetailSchema, auth=StudentAuth())
def get_course_progress(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    
    return calculate_progress(enrollment)
