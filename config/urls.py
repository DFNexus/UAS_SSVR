from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

api = NinjaAPI(title="Simple LMS API")

@api.get("/")
def welcome(request):
    return {"message": "Welcome to Simple LMS API"}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
