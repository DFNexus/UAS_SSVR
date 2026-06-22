from ninja import Router
from .schemas import StudentDashboardSchema
from .services import get_student_dashboard
from apps.users.auth import StudentAuth

router = Router(tags=["Dashboard"])

from ninja.errors import HttpError

@router.get("/student", response=StudentDashboardSchema, auth=StudentAuth())
def get_dashboard(request):
    if request.user.role != 'student':
        raise HttpError(403, "Strictly student permission required.")
    return get_student_dashboard(request.user)
