from django.db.models import Count
from apps.courses.models import Course
from apps.enrollments.models import Enrollment
from apps.progress.models import Progress
from apps.progress.services import calculate_progress

def get_student_dashboard(user):
    enrollments = Enrollment.objects.filter(student=user).select_related('course')
    
    course_active = []
    course_completed = []
    enrolled_course_ids = []
    
    for enrollment in enrollments:
        enrolled_course_ids.append(enrollment.course.id)
        prog_data = calculate_progress(enrollment)
        
        course_data = {
            "id": enrollment.course.id,
            "title": enrollment.course.title,
            "slug": enrollment.course.slug
        }
        
        if prog_data['course_progress'] >= 100.0:
            course_completed.append(course_data)
        else:
            course_active.append({
                "course": course_data,
                "progress_percentage": prog_data['course_progress']
            })
            
    course_active.sort(key=lambda x: x['progress_percentage'], reverse=True)
    
    recent_progress = Progress.objects.filter(
        enrollment__student=user,
        completed=True
    ).select_related('lesson', 'lesson__section', 'lesson__section__course').order_by('-completed_at', '-id').first()
    
    recent_lesson = None
    if recent_progress:
        recent_lesson = {
            "lesson_title": recent_progress.lesson.title,
            "section_title": recent_progress.lesson.section.title,
            "course_title": recent_progress.lesson.section.course.title
        }
        
    recommended_courses = Course.objects.filter(
        status='published'
    ).exclude(
        id__in=enrolled_course_ids
    ).annotate(
        enrollments_count=Count('enrollments')
    ).order_by('-enrollments_count')[:5]
    
    recommended_list = [
        {
            "id": c.id,
            "title": c.title,
            "slug": c.slug
        } for c in recommended_courses
    ]
    
    return {
        "course_active": course_active,
        "course_completed": course_completed,
        "total_enrolled": len(enrollments),
        "total_completed": len(course_completed),
        "recent_lesson": recent_lesson,
        "recommended_courses": recommended_list
    }
