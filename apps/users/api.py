from ninja import Router
from django.contrib.auth import get_user_model, authenticate
from ninja.errors import HttpError
from ninja_jwt.tokens import RefreshToken
from ninja_jwt.exceptions import TokenError

from .schemas import RegisterSchema, LoginSchema, TokenSchema, UserSchema, RefreshSchema
from .auth import BaseAuth

User = get_user_model()
router = Router(tags=["Auth"])

@router.post("/register", response={201: UserSchema})
def register(request, payload: RegisterSchema):
    if User.objects.filter(username=payload.username).exists():
        raise HttpError(400, "Username already exists")
    if User.objects.filter(email=payload.email).exists():
        raise HttpError(400, "Email already exists")
        
    user = User.objects.create_user(
        username=payload.username,
        email=payload.email,
        password=payload.password,
        role='student'  # default role
    )
    return 201, user

@router.post("/login", response=TokenSchema)
def login(request, payload: LoginSchema):
    user = authenticate(username=payload.username, password=payload.password)
    if not user:
        raise HttpError(401, "Invalid credentials")
        
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token)
    }

@router.post("/refresh", response=TokenSchema)
def refresh_token(request, payload: RefreshSchema):
    try:
        refresh = RefreshToken(payload.refresh)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }
    except TokenError as e:
        raise HttpError(401, str(e))

@router.get("/me", response=UserSchema, auth=BaseAuth())
def get_me(request):
    return request.user
