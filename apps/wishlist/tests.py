from django.test import TestCase
from django.contrib.auth import get_user_model
from ninja.testing import TestClient
from config.urls import api
from ninja_jwt.tokens import RefreshToken
from apps.courses.models import Course
from apps.categories.models import Category
from .models import Wishlist

User = get_user_model()

class WishlistTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user('st1', 'st1@test.com', 'pass', role='student')
        self.inst = User.objects.create_user('inst', 'inst@test.com', 'pass', role='instructor')
        self.cat = Category.objects.create(name='Test Cat', slug='test-cat')
        self.course = Course.objects.create(title='Test Course', slug='test-course', category=self.cat, instructor=self.inst, status='published')
        self.client = TestClient(api)
        
    def get_headers(self, user):
        refresh = RefreshToken.for_user(user)
        return {"Authorization": f"Bearer {refresh.access_token}"}
        
    def test_add_and_remove_wishlist(self):
        headers = self.get_headers(self.student)
        
        # Add
        res = self.client.post("/wishlist/", json={"course_id": self.course.id}, headers=headers)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Wishlist.objects.count(), 1)
        
        # Duplicate Add
        res = self.client.post("/wishlist/", json={"course_id": self.course.id}, headers=headers)
        self.assertEqual(res.status_code, 400)
        
        # List
        res = self.client.get("/wishlist/", headers=headers)
        self.assertEqual(len(res.json()), 1)
        
        # Remove
        res = self.client.delete(f"/wishlist/{self.course.id}", headers=headers)
        self.assertEqual(res.status_code, 204)
        self.assertEqual(Wishlist.objects.count(), 0)
