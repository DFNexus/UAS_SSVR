from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Section, Lesson
from apps.enrollments.models import Enrollment
from apps.progress.models import Progress
from apps.progress.services import ProgressService
from apps.categories.models import Category

User = get_user_model()

class ProgressServiceTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user('student', 'student@test.com', 'pass', role='student')
        self.instructor = User.objects.create_user('inst', 'inst@test.com', 'pass', role='instructor')
        
        self.category = Category.objects.create(name='Cat', slug='cat')
        self.course = Course.objects.create(
            title='Test Course', slug='test-course', description='desc', 
            category=self.category, instructor=self.instructor, level='beginner', status='published'
        )
        
        self.sec1 = Section.objects.create(course=self.course, title='Sec 1', order=1)
        self.s1l1 = Lesson.objects.create(section=self.sec1, title='S1L1', content='content', order=1)
        self.s1l2 = Lesson.objects.create(section=self.sec1, title='S1L2', content='content', order=2)
        
        self.sec2 = Section.objects.create(course=self.course, title='Sec 2', order=2)
        self.s2l1 = Lesson.objects.create(section=self.sec2, title='S2L1', content='content', order=1)
        self.s2l2 = Lesson.objects.create(section=self.sec2, title='S2L2', content='content', order=2)
        
        self.enrollment = Enrollment.objects.create(student=self.student, course=self.course)

    def test_progress_zero(self):
        res = ProgressService.calculate_course_progress(self.enrollment)
        self.assertEqual(res['total_lessons'], 4)
        self.assertEqual(res['completed_lessons'], 0)
        self.assertEqual(res['progress_percentage'], 0.0)
        self.assertEqual(len(res['sections']), 2)
        self.assertEqual(res['sections'][0]['progress_percentage'], 0.0)

    def test_progress_partial(self):
        Progress.objects.create(enrollment=self.enrollment, lesson=self.s1l1, completed=True)
        Progress.objects.create(enrollment=self.enrollment, lesson=self.s1l2, completed=True)
        Progress.objects.create(enrollment=self.enrollment, lesson=self.s2l1, completed=True)
        
        res = ProgressService.calculate_course_progress(self.enrollment)
        
        self.assertEqual(res['completed_lessons'], 3)
        self.assertEqual(res['progress_percentage'], 75.0)
        
        # Sec 1 is 100%
        sec1_prog = next(s for s in res['sections'] if s['section_id'] == self.sec1.id)
        self.assertEqual(sec1_prog['progress_percentage'], 100.0)
        
        # Sec 2 is 50%
        sec2_prog = next(s for s in res['sections'] if s['section_id'] == self.sec2.id)
        self.assertEqual(sec2_prog['progress_percentage'], 50.0)

    def test_progress_complete(self):
        Progress.objects.create(enrollment=self.enrollment, lesson=self.s1l1, completed=True)
        Progress.objects.create(enrollment=self.enrollment, lesson=self.s1l2, completed=True)
        Progress.objects.create(enrollment=self.enrollment, lesson=self.s2l1, completed=True)
        Progress.objects.create(enrollment=self.enrollment, lesson=self.s2l2, completed=True)
        
        res = ProgressService.calculate_course_progress(self.enrollment)
        self.assertEqual(res['completed_lessons'], 4)
        self.assertEqual(res['progress_percentage'], 100.0)
