from django.test import TestCase
from django.contrib.auth import get_user_model
from ninja.testing import TestClient
from config.urls import api
from ninja_jwt.tokens import RefreshToken

User = get_user_model()

class AuthRBACTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser('admin_test', 'admin@test.com', 'pass', role='admin')
        self.inst_user = User.objects.create_user('inst_test', 'inst@test.com', 'pass', role='instructor')
        self.student_user = User.objects.create_user('student_test', 'student@test.com', 'pass', role='student')
        
        self.client = TestClient(api)
        
        # Test endpoint to verify RBAC
        from apps.users.auth import AdminAuth
        
        @api.get("/test-admin-only", auth=AdminAuth())
        def test_admin_only(request):
            return {"msg": "success"}

    def get_headers(self, user):
        refresh = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {refresh.access_token}"}

    def test_login_returns_token(self):
        # Admin
        response = self.client.post("/api/auth/login", json={"username": "admin_test", "password": "pass"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        
        # Instructor
        response = self.client.post("/api/auth/login", json={"username": "inst_test", "password": "pass"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        
        # Student
        response = self.client.post("/api/auth/login", json={"username": "student_test", "password": "pass"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())

    def test_admin_endpoint_rejects_student(self):
        headers = self.get_headers(self.student_user)
        response = self.client.get("/api/test-admin-only", headers=headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "Admin permission required."})

    def test_admin_endpoint_allows_admin(self):
        headers = self.get_headers(self.admin_user)
        response = self.client.get("/api/test-admin-only", headers=headers)
        self.assertEqual(response.status_code, 200)
