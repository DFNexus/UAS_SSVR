from django.test import TestCase
from django.contrib.auth import get_user_model
from ninja.testing import TestClient
from config.urls import api
from ninja_jwt.tokens import RefreshToken
from apps.courses.models import Course
from apps.categories.models import Category
from apps.enrollments.models import Enrollment
from .models import Review

User = get_user_model()

class ReviewTests(TestCase):
    def setUp(self):
        self.student1 = User.objects.create_user('st1', 'st1@test.com', 'pass', role='student')
        self.student2 = User.objects.create_user('st2', 'st2@test.com', 'pass', role='student')
        self.inst = User.objects.create_user('inst', 'inst@test.com', 'pass', role='instructor')
        
        self.cat = Category.objects.create(name='Test Cat', slug='test-cat')
        self.course = Course.objects.create(title='Test Course', slug='test-course', category=self.cat, instructor=self.inst, status='published')
        
        self.enr = Enrollment.objects.create(student=self.student1, course=self.course)
        
        self.client = TestClient(api)
        
    def get_headers(self, user):
        refresh = RefreshToken.for_user(user)
        return {"Authorization": f"Bearer {refresh.access_token}"}
        
    def test_student_must_be_enrolled_to_review(self):
        headers = self.get_headers(self.student2)
        res = self.client.post(f"/courses/{self.course.id}/reviews", json={"rating": 5, "body": "Great"}, headers=headers)
        self.assertEqual(res.status_code, 403)
        
    def test_student_can_create_review(self):
        headers = self.get_headers(self.student1)
        res = self.client.post(f"/courses/{self.course.id}/reviews", json={"rating": 4, "body": "Good"}, headers=headers)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Review.objects.count(), 1)
        
    def test_student_cannot_review_twice(self):
        Review.objects.create(student=self.student1, course=self.course, rating=3)
        headers = self.get_headers(self.student1)
        res = self.client.post(f"/courses/{self.course.id}/reviews", json={"rating": 5, "body": "Changed my mind"}, headers=headers)
        self.assertEqual(res.status_code, 400)
