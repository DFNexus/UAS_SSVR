from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from apps.users.api import router as auth_router
from apps.categories.api import router as categories_router
from apps.courses.api import course_router, section_router, lesson_router
from apps.enrollments.api import router as enrollments_router
from apps.progress.api import router as progress_router

api = NinjaAPI(title="Simple LMS API")

api.add_router("/auth/", auth_router)
api.add_router("/categories/", categories_router)
api.add_router("/courses/", course_router)
api.add_router("/sections/", section_router)
api.add_router("/lessons/", lesson_router)
api.add_router("/", enrollments_router)
api.add_router("/", progress_router)

@api.get("/")
def welcome(request):
    return {"message": "Welcome to Simple LMS API"}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
