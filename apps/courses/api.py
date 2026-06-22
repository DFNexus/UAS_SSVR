from ninja import Router, Query
from typing import List
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError
from django.utils.text import slugify
from django.db.models import Q, Count

from .models import Course, Section, Lesson
from apps.categories.models import Category
from .schemas import (
    CourseSchema, CourseDetailSchema, CourseCreateSchema, CourseUpdateSchema,
    SectionSchema, SectionCreateSchema,
    LessonSchema, LessonCreateSchema, CourseFilterSchema
)
from apps.users.auth import InstructorAuth, OptionalJWTAuth

course_router = Router(tags=["Courses"])
section_router = Router(tags=["Sections"])
lesson_router = Router(tags=["Lessons"])

# --- COURSES ---

@course_router.get("/", response=List[CourseSchema], auth=OptionalJWTAuth())
def list_courses(request, filters: CourseFilterSchema = Query(...)):
    user = getattr(request, 'user', None)
    
    # 1. Base Queryset (Visibility)
    if user and user.is_authenticated:
        if user.role == 'admin':
            qs = Course.objects.all()
        elif user.role == 'instructor':
            qs = Course.objects.filter(Q(status='published') | Q(instructor=user))
        else:
            qs = Course.objects.filter(status='published')
    else:
        qs = Course.objects.filter(status='published')
        
    qs = qs.select_related('category', 'instructor')
    
    # 2. Filters
    if filters.search:
        qs = qs.filter(Q(title__icontains=filters.search) | Q(description__icontains=filters.search))
    
    if filters.category:
        if filters.category.isdigit():
            qs = qs.filter(category_id=int(filters.category))
        else:
            qs = qs.filter(category__slug=filters.category)
            
    if filters.instructor:
        qs = qs.filter(instructor_id=filters.instructor)
        
    if filters.level:
        qs = qs.filter(level=filters.level)
        
    if filters.status:
        qs = qs.filter(status=filters.status)
        
    # 3. Ordering
    if filters.ordering == 'newest':
        qs = qs.order_by('-created_at')
    elif filters.ordering == 'oldest':
        qs = qs.order_by('created_at')
    elif filters.ordering == 'title':
        qs = qs.order_by('title')
    elif filters.ordering == 'popular':
        qs = qs.annotate(enrollments_count=Count('enrollments')).order_by('-enrollments_count')
    else:
        qs = qs.order_by('-created_at') # default
        
    return qs

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
