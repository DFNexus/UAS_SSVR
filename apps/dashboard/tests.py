from django.test import TestCase
from django.contrib.auth import get_user_model
from ninja.testing import TestClient
from config.urls import api
from ninja_jwt.tokens import RefreshToken
from apps.courses.models import Course, Section, Lesson
from apps.categories.models import Category
from apps.enrollments.models import Enrollment
from apps.progress.models import Progress
from .services import get_student_dashboard

User = get_user_model()

class DashboardTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user('student', 'student@test.com', 'pass', role='student')
        self.admin = User.objects.create_user('admin1', 'admin1@test.com', 'pass', role='admin')
        self.instructor = User.objects.create_user('inst', 'inst@test.com', 'pass', role='instructor')
        
        self.category = Category.objects.create(name='Cat', slug='cat')
        
        # Completed course
        self.c1 = Course.objects.create(title='C1', slug='c1', category=self.category, instructor=self.instructor, status='published')
        self.s1 = Section.objects.create(course=self.c1, title='S1', order=1)
        self.l1 = Lesson.objects.create(section=self.s1, title='L1', content='C', order=1)
        self.e1 = Enrollment.objects.create(student=self.student, course=self.c1)
        Progress.objects.create(enrollment=self.e1, lesson=self.l1, completed=True) # 100%
        
        # Active course
        self.c2 = Course.objects.create(title='C2', slug='c2', category=self.category, instructor=self.instructor, status='published')
        self.s2 = Section.objects.create(course=self.c2, title='S2', order=1)
        self.l2a = Lesson.objects.create(section=self.s2, title='L2A', content='C', order=1)
        self.l2b = Lesson.objects.create(section=self.s2, title='L2B', content='C', order=2)
        self.e2 = Enrollment.objects.create(student=self.student, course=self.c2)
        Progress.objects.create(enrollment=self.e2, lesson=self.l2a, completed=True) # 50%
        
        # Recommended course
        self.c3 = Course.objects.create(title='C3', slug='c3', category=self.category, instructor=self.instructor, status='published')
        
        self.client = TestClient(api)
        
    def get_headers(self, user):
        refresh = RefreshToken.for_user(user)
        return {"Authorization": f"Bearer {refresh.access_token}"}
        
    def test_student_dashboard_service(self):
        data = get_student_dashboard(self.student)
        
        self.assertEqual(data['total_enrolled'], 2)
        self.assertEqual(data['total_completed'], 1)
        self.assertEqual(len(data['course_completed']), 1)
        self.assertEqual(data['course_completed'][0]['id'], self.c1.id)
        
        self.assertEqual(len(data['course_active']), 1)
        self.assertEqual(data['course_active'][0]['course']['id'], self.c2.id)
        self.assertEqual(data['course_active'][0]['progress_percentage'], 50.0)
        
        self.assertIsNotNone(data['recent_lesson'])
        self.assertEqual(data['recent_lesson']['course_title'], 'C2')
        
        self.assertEqual(len(data['recommended_courses']), 1)
        self.assertEqual(data['recommended_courses'][0]['id'], self.c3.id)
        
    def test_dashboard_endpoint_student_only(self):
        # Admin
        res = self.client.get("/dashboard/student", headers=self.get_headers(self.admin))
        self.assertEqual(res.status_code, 403)
        
        # Instructor
        res = self.client.get("/dashboard/student", headers=self.get_headers(self.instructor))
        self.assertEqual(res.status_code, 403)
        
        # Student
        res = self.client.get("/dashboard/student", headers=self.get_headers(self.student))
        self.assertEqual(res.status_code, 200)
