from ninja import Router
from typing import List
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError
from django.utils.text import slugify

from .models import Course, Section, Lesson
from apps.categories.models import Category
from .schemas import (
    CourseSchema, CourseDetailSchema, CourseCreateSchema, CourseUpdateSchema,
    SectionSchema, SectionCreateSchema,
    LessonSchema, LessonCreateSchema
)
from apps.users.auth import InstructorAuth

course_router = Router(tags=["Courses"])
section_router = Router(tags=["Sections"])
lesson_router = Router(tags=["Lessons"])

# --- COURSES ---

@course_router.get("/", response=List[CourseSchema])
def list_courses(request):
    return Course.objects.filter(status='published').select_related('category', 'instructor')

@course_router.get("/{course_id}", response=CourseDetailSchema)
def get_course_detail(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)
    return course

@course_router.post("/", response={201: CourseSchema}, auth=InstructorAuth())
def create_course(request, payload: CourseCreateSchema):
    category = get_object_or_404(Category, id=payload.category_id)
    slug = slugify(payload.title)
    
    course = Course.objects.create(
        title=payload.title,
        slug=slug,
        description=payload.description,
        category=category,
        instructor=request.user,
        level=payload.level,
        status=payload.status
    )
    return 201, course

@course_router.put("/{course_id}", response=CourseSchema, auth=InstructorAuth())
def update_course(request, course_id: int, payload: CourseUpdateSchema):
    course = get_object_or_404(Course, id=course_id)
    
    if course.instructor != request.user and request.user.role != 'admin':
        raise HttpError(403, "You can only edit your own courses.")
        
    for attr, value in payload.dict(exclude_unset=True).items():
        if attr == 'category_id':
            course.category = get_object_or_404(Category, id=value)
        else:
            setattr(course, attr, value)
            
        if attr == 'title':
            course.slug = slugify(value)
            
    course.save()
    return course

@course_router.delete("/{course_id}", auth=InstructorAuth())
def delete_course(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)
    if course.instructor != request.user and request.user.role != 'admin':
        raise HttpError(403, "You can only delete your own courses.")
    course.delete()
    return {"success": True}

# --- SECTIONS ---

@course_router.get("/{course_id}/sections", response=List[SectionSchema])
def list_sections(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)
    return course.sections.all()

@course_router.post("/{course_id}/sections", response={201: SectionSchema}, auth=InstructorAuth())
def create_section(request, course_id: int, payload: SectionCreateSchema):
    course = get_object_or_404(Course, id=course_id)
    if course.instructor != request.user and request.user.role != 'admin':
        raise HttpError(403, "You can only add sections to your own courses.")
        
    section = Section.objects.create(
        course=course,
        title=payload.title,
        order=payload.order
    )
    return 201, section

@section_router.put("/{section_id}", response=SectionSchema, auth=InstructorAuth())
def update_section(request, section_id: int, payload: SectionCreateSchema):
    section = get_object_or_404(Section, id=section_id)
    if section.course.instructor != request.user and request.user.role != 'admin':
        raise HttpError(403, "You can only edit your own sections.")
        
    section.title = payload.title
    section.order = payload.order
    section.save()
    return section

@section_router.delete("/{section_id}", auth=InstructorAuth())
def delete_section(request, section_id: int):
    section = get_object_or_404(Section, id=section_id)
    if section.course.instructor != request.user and request.user.role != 'admin':
        raise HttpError(403, "You can only delete your own sections.")
    section.delete()
    return {"success": True}

# --- LESSONS ---

@section_router.post("/{section_id}/lessons", response={201: LessonSchema}, auth=InstructorAuth())
def create_lesson(request, section_id: int, payload: LessonCreateSchema):
    section = get_object_or_404(Section, id=section_id)
    if section.course.instructor != request.user and request.user.role != 'admin':
        raise HttpError(403, "You can only add lessons to your own courses.")
        
    lesson = Lesson.objects.create(
        section=section,
        **payload.dict()
    )
    return 201, lesson

@lesson_router.put("/{lesson_id}", response=LessonSchema, auth=InstructorAuth())
def update_lesson(request, lesson_id: int, payload: LessonCreateSchema):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if lesson.section.course.instructor != request.user and request.user.role != 'admin':
        raise HttpError(403, "You can only edit your own lessons.")
        
    for attr, value in payload.dict().items():
        setattr(lesson, attr, value)
    lesson.save()
    return lesson

@lesson_router.delete("/{lesson_id}", auth=InstructorAuth())
def delete_lesson(request, lesson_id: int):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if lesson.section.course.instructor != request.user and request.user.role != 'admin':
        raise HttpError(403, "You can only delete your own lessons.")
    lesson.delete()
    return {"success": True}
