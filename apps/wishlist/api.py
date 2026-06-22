from ninja import Router
from django.shortcuts import get_object_or_404
from .models import Wishlist
from .schemas import WishlistSchema, WishlistCreateSchema
from apps.courses.models import Course
from apps.users.auth import StudentAuth
from ninja.responses import Status
from ninja.errors import HttpError

router = Router(tags=["Wishlist"])

@router.post("/", response={201: WishlistSchema, 400: dict}, auth=StudentAuth())
def add_to_wishlist(request, data: WishlistCreateSchema):
    course = get_object_or_404(Course, id=data.course_id)
    if Wishlist.objects.filter(student=request.user, course=course).exists():
        raise HttpError(400, "Course already in wishlist")
    
    wishlist = Wishlist.objects.create(student=request.user, course=course)
    return Status(201, wishlist)

@router.delete("/{course_id}", response={204: None, 404: dict}, auth=StudentAuth())
def remove_from_wishlist(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)
    wishlist = Wishlist.objects.filter(student=request.user, course=course).first()
    if not wishlist:
        raise HttpError(404, "Course not in wishlist")
    
    wishlist.delete()
    return Status(204, None)

@router.get("/", response=list[WishlistSchema], auth=StudentAuth())
def list_wishlist(request):
    return Wishlist.objects.filter(student=request.user).select_related('course', 'course__category', 'course__instructor')
