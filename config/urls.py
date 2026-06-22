from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from apps.users.api import router as auth_router

api = NinjaAPI(title="Simple LMS API")

api.add_router("/auth/", auth_router)

@api.get("/")
def welcome(request):
    return {"message": "Welcome to Simple LMS API"}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
