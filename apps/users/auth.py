from ninja_jwt.authentication import JWTAuth
from ninja.errors import HttpError

class BaseAuth(JWTAuth):
    """
    Base JWT Authentication that attaches user to request.
    """
    pass

class AdminAuth(JWTAuth):
    def authenticate(self, request, token):
        user = super().authenticate(request, token)
        if not user or user.role != 'admin':
            raise HttpError(403, "Admin permission required.")
        return user

class InstructorAuth(JWTAuth):
    def authenticate(self, request, token):
        user = super().authenticate(request, token)
        if not user or user.role not in ['admin', 'instructor']:
            raise HttpError(403, "Instructor permission required.")
        return user

class StudentAuth(JWTAuth):
    def authenticate(self, request, token):
        user = super().authenticate(request, token)
        # Students, instructors, and admins can all access student endpoints generally
        if not user or user.role not in ['admin', 'instructor', 'student']:
            raise HttpError(403, "Student permission required.")
        return user
