from apps.courses.models import Course, Section, Lesson
from apps.enrollments.models import Enrollment
from .models import Progress

class ProgressService:
    @staticmethod
    def calculate_course_progress(enrollment: Enrollment) -> dict:
        course = enrollment.course
        sections = course.sections.all().prefetch_related('lessons')
        
        # Get all completed lesson IDs for this enrollment
        completed_lesson_ids = set(Progress.objects.filter(
            enrollment=enrollment, 
            completed=True
        ).values_list('lesson_id', flat=True))
        
        course_total_lessons = 0
        course_completed_lessons = 0
        section_progress_list = []
        
        for section in sections:
            section_lessons = section.lessons.all()
            section_total = len(section_lessons)
            section_completed = sum(1 for lesson in section_lessons if lesson.id in completed_lesson_ids)
            
            section_percentage = 0.0
            if section_total > 0:
                section_percentage = round((section_completed / section_total) * 100, 2)
                
            section_progress_list.append({
                "section_id": section.id,
                "title": section.title,
                "total_lessons": section_total,
                "completed_lessons": section_completed,
                "progress_percentage": section_percentage
            })
            
            course_total_lessons += section_total
            course_completed_lessons += section_completed
            
        course_percentage = 0.0
        if course_total_lessons > 0:
            course_percentage = round((course_completed_lessons / course_total_lessons) * 100, 2)
            
        return {
            "course_id": course.id,
            "total_lessons": course_total_lessons,
            "completed_lessons": course_completed_lessons,
            "progress_percentage": course_percentage,
            "sections": section_progress_list
        }
