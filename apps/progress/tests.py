from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Section, Lesson
from apps.enrollments.models import Enrollment
from apps.progress.models import Progress
from apps.progress.services import calculate_progress
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
        res = calculate_progress(self.enrollment)
        self.assertEqual(res['course_progress'], 0.0)
        self.assertEqual(res['section_progress'][self.sec1.id], 0.0)
        self.assertEqual(res['section_progress'][self.sec2.id], 0.0)
        self.assertFalse(res['lesson_progress'][self.s1l1.id])

    def test_progress_partial(self):
        Progress.objects.create(enrollment=self.enrollment, lesson=self.s1l1, completed=True)
        Progress.objects.create(enrollment=self.enrollment, lesson=self.s1l2, completed=True)
        Progress.objects.create(enrollment=self.enrollment, lesson=self.s2l1, completed=True)
        
        res = calculate_progress(self.enrollment)
        
        self.assertEqual(res['course_progress'], 75.0)
        self.assertEqual(res['section_progress'][self.sec1.id], 100.0)
        self.assertEqual(res['section_progress'][self.sec2.id], 50.0)
        self.assertTrue(res['lesson_progress'][self.s1l1.id])
        self.assertFalse(res['lesson_progress'][self.s2l2.id])

    def test_progress_complete(self):
        Progress.objects.create(enrollment=self.enrollment, lesson=self.s1l1, completed=True)
        Progress.objects.create(enrollment=self.enrollment, lesson=self.s1l2, completed=True)
        Progress.objects.create(enrollment=self.enrollment, lesson=self.s2l1, completed=True)
        Progress.objects.create(enrollment=self.enrollment, lesson=self.s2l2, completed=True)
        
        res = calculate_progress(self.enrollment)
        self.assertEqual(res['course_progress'], 100.0)
        self.assertEqual(res['section_progress'][self.sec2.id], 100.0)
