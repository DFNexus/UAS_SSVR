from apps.enrollments.models import Enrollment
from .models import Progress

def calculate_progress(enrollment: Enrollment) -> dict:
    course = enrollment.course
    sections = course.sections.all().prefetch_related('lessons')
    
    completed_lesson_ids = set(Progress.objects.filter(
        enrollment=enrollment, 
        completed=True
    ).values_list('lesson_id', flat=True))
    
    course_total_lessons = 0
    course_completed_lessons = 0
    
    lesson_progress = {}
    section_progress = {}
    
    for section in sections:
        section_lessons = section.lessons.all()
        section_total = len(section_lessons)
        section_completed = sum(1 for lesson in section_lessons if lesson.id in completed_lesson_ids)
        
        for lesson in section_lessons:
            lesson_progress[lesson.id] = (lesson.id in completed_lesson_ids)
            
        section_percentage = 0.0
        if section_total > 0:
            section_percentage = round((section_completed / section_total) * 100, 2)
            
        section_progress[section.id] = section_percentage
        
        course_total_lessons += section_total
        course_completed_lessons += section_completed
        
    course_percentage = 0.0
    if course_total_lessons > 0:
        course_percentage = round((course_completed_lessons / course_total_lessons) * 100, 2)
        
    return {
        "lesson_progress": lesson_progress,
        "section_progress": section_progress,
        "course_progress": course_percentage
    }
