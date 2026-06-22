from django.test import TestCase
from django.contrib.auth import get_user_model
from ninja.testing import TestClient
from config.urls import api
from apps.categories.models import Category
from apps.courses.models import Course
from apps.enrollments.models import Enrollment
from ninja_jwt.tokens import RefreshToken

User = get_user_model()

class CourseSearchFilterTests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        
        # Users
        self.admin = User.objects.create_superuser('admin_c', 'adminc@test.com', 'pass', role='admin')
        self.inst1 = User.objects.create_user('inst1_c', 'inst1c@test.com', 'pass', role='instructor')
        self.inst2 = User.objects.create_user('inst2_c', 'inst2c@test.com', 'pass', role='instructor')
        self.student = User.objects.create_user('student_c', 'studentc@test.com', 'pass', role='student')
        
        # Categories
        self.cat_web = Category.objects.create(name='Web Dev', slug='web-dev')
        self.cat_data = Category.objects.create(name='Data Science', slug='data-science')
        
        # Courses
        self.c1 = Course.objects.create(title='Python Basics', slug='py-basics', description='Learn python programming', category=self.cat_web, instructor=self.inst1, level='beginner', status='published')
        self.c2 = Course.objects.create(title='Advanced Django', slug='adv-django', description='Master web frameworks', category=self.cat_web, instructor=self.inst1, level='advanced', status='draft')
        self.c3 = Course.objects.create(title='Data Science 101', slug='ds-101', description='Data science with python', category=self.cat_data, instructor=self.inst2, level='beginner', status='published')
        
        # Add enrollments for testing 'popular' ordering
        Enrollment.objects.create(student=self.student, course=self.c1)
        Enrollment.objects.create(student=self.admin, course=self.c1)
        Enrollment.objects.create(student=self.student, course=self.c3)
        # c1 has 2 enrollments, c3 has 1, c2 has 0
        
    def get_headers(self, user):
        refresh = RefreshToken.for_user(user)
        return {"Authorization": f"Bearer {refresh.access_token}"}

    def test_visibility_anonymous_and_student(self):
        # Anonymous
        res = self.client.get("/courses/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data), 2) # only published (c1, c3)
        
        # Student
        res = self.client.get("/courses/", headers=self.get_headers(self.student))
        self.assertEqual(len(res.json()), 2)
        
    def test_visibility_instructor_and_admin(self):
        # inst1 should see c1 (published) and c2 (draft but own), and c3 (published)
        res = self.client.get("/courses/", headers=self.get_headers(self.inst1))
        self.assertEqual(len(res.json()), 3)
        
        # inst2 should see c1 (published), c3 (published). Cannot see c2 (draft not own)
        res = self.client.get("/courses/", headers=self.get_headers(self.inst2))
        self.assertEqual(len(res.json()), 2)
        
        # Admin sees all
        res = self.client.get("/courses/", headers=self.get_headers(self.admin))
        self.assertEqual(len(res.json()), 3)
        
    def test_search_filter(self):
        res = self.client.get("/courses/?search=Python")
        self.assertEqual(len(res.json()), 2) # Python Basics, Data science with python
        
        res = self.client.get("/courses/?search=frameworks")
        self.assertEqual(len(res.json()), 0) # c2 is draft, anonymous can't see it
        
        res = self.client.get("/courses/?search=frameworks", headers=self.get_headers(self.admin))
        self.assertEqual(len(res.json()), 1) # c2
        
    def test_category_filter(self):
        res = self.client.get("/courses/?category=web-dev")
        self.assertEqual(len(res.json()), 1) # c1 (c2 is draft)
        
        res = self.client.get(f"/courses/?category={self.cat_data.id}")
        self.assertEqual(len(res.json()), 1) # c3
        
    def test_other_filters(self):
        # Instructor
        res = self.client.get(f"/courses/?instructor={self.inst1.id}")
        self.assertEqual(len(res.json()), 1) # c1
        
        # Level
        res = self.client.get("/courses/?level=beginner")
        self.assertEqual(len(res.json()), 2) # c1, c3
        
        # Status (Admin)
        res = self.client.get("/courses/?status=draft", headers=self.get_headers(self.admin))
        self.assertEqual(len(res.json()), 1) # c2
        
    def test_ordering(self):
        # Popular
        res = self.client.get("/courses/?ordering=popular")
        data = res.json()
        self.assertEqual(data[0]['id'], self.c1.id) # 2 enrollments
        self.assertEqual(data[1]['id'], self.c3.id) # 1 enrollment
        
        # Title
        res = self.client.get("/courses/?ordering=title", headers=self.get_headers(self.admin))
        data = res.json()
        self.assertEqual(data[0]['id'], self.c2.id) # Advanced Django
        self.assertEqual(data[1]['id'], self.c3.id) # Data Science 101
        self.assertEqual(data[2]['id'], self.c1.id) # Python Basics
