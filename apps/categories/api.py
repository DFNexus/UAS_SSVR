from ninja import Router
from typing import List
from django.utils.text import slugify
from ninja.errors import HttpError

from .models import Category
from .schemas import CategorySchema, CategoryCreateSchema
from apps.users.auth import AdminAuth

router = Router(tags=["Categories"])

@router.get("/", response=List[CategorySchema])
def list_categories(request):
    return Category.objects.all()

@router.post("/", response={201: CategorySchema}, auth=AdminAuth())
def create_category(request, payload: CategoryCreateSchema):
    slug = slugify(payload.name)
    if Category.objects.filter(slug=slug).exists():
        raise HttpError(400, "Category with this name/slug already exists")
    
    category = Category.objects.create(
        name=payload.name,
        slug=slug
    )
    from ninja.responses import Status
    return Status(201, category)
