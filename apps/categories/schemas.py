from ninja import Schema

class CategorySchema(Schema):
    id: int
    name: str
    slug: str

class CategoryCreateSchema(Schema):
    name: str
