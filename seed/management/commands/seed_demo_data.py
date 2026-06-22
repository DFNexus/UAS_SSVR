from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.categories.models import Category
from apps.courses.models import Course, Section, Lesson
from apps.enrollments.models import Enrollment
from apps.progress.models import Progress
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed database with initial demo data'

    def handle(self, *args, **kwargs):
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.SUCCESS('Demo data already exists.'))
            return

        self.stdout.write('Seeding demo data...')

        # Users
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123', role='admin')
        instructor1 = User.objects.create_user('instructor1', 'instructor1@example.com', 'instructor123', role='instructor')
        instructor2 = User.objects.create_user('instructor2', 'instructor2@example.com', 'instructor123', role='instructor')
        student1 = User.objects.create_user('student1', 'student1@example.com', 'student123', role='student')
        student2 = User.objects.create_user('student2', 'student2@example.com', 'student123', role='student')
        student3 = User.objects.create_user('student3', 'student3@example.com', 'student123', role='student')

        # Categories
        cat_python = Category.objects.create(name='Python Programming', slug='python')
        cat_web = Category.objects.create(name='Web Development', slug='web-dev')

        # Courses
        course1 = Course.objects.create(
            title='Python for Beginners',
            slug='python-for-beginners',
            description='Learn Python from scratch.',
            category=cat_python,
            instructor=instructor1,
            level='beginner',
            status='published'
        )
        course2 = Course.objects.create(
            title='Django Web Development',
            slug='django-web-dev',
            description='Build web apps with Django.',
            category=cat_web,
            instructor=instructor2,
            level='intermediate',
            status='published'
        )

        # Sections and Lessons
        sec1 = Section.objects.create(course=course1, title='Introduction', order=1)
        Lesson.objects.create(section=sec1, title='What is Python?', content='Python is a programming language.', order=1)
        Lesson.objects.create(section=sec1, title='Installing Python', content='Download from python.org.', order=2)

        sec2 = Section.objects.create(course=course2, title='Django Basics', order=1)
        Lesson.objects.create(section=sec2, title='What is Django?', content='Django is a web framework.', order=1)

        # Enrollments
        enr1 = Enrollment.objects.create(student=student1, course=course1)
        Enrollment.objects.create(student=student2, course=course1)
        Enrollment.objects.create(student=student3, course=course2)

        # Progress
        Progress.objects.create(
            enrollment=enr1, 
            lesson=sec1.lessons.first(), 
            completed=True, 
            completed_at=timezone.now()
        )

        # Reviews
        from apps.reviews.models import Review
        Review.objects.create(student=student1, course=course1, rating=5, body='Great course!')
        Review.objects.create(student=student2, course=course1, rating=4, body='Very informative.')

        # Wishlist
        from apps.wishlist.models import Wishlist
        Wishlist.objects.create(student=student3, course=course1)

        self.stdout.write(self.style.SUCCESS('Successfully seeded demo data!'))
