from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Course, Category, Module, Lesson, Enrollment, Profile

class AcademyTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='teststudent', password='password')
        self.instructor = User.objects.create_user(username='testteacher', password='password')
        Profile.objects.filter(user=self.instructor).update(role='teacher')

        self.category = Category.objects.create(name='Programming')
        self.course = Course.objects.create(
            title='Python 101',
            category=self.category,
            description='Intro to Python',
            instructor=self.instructor,
            price=10.00,
            status='published'
        )
        self.module = Module.objects.create(course=self.course, title='Basics')
        self.lesson = Lesson.objects.create(module=self.module, title='Hello World', content='Print hello')

    def test_course_list(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python 101')

    def test_course_detail(self):
        response = self.client.get(f'/course/{self.course.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python 101')

    def test_enrollment_flow(self):
        # The enrollment flow has changed to step1 -> payment -> approval
        self.client.login(username='teststudent', password='password')

        # Step 1: Data
        step1_url = f'/course/{self.course.slug}/enroll/step1/'
        response = self.client.post(step1_url, {
            'first_name': 'Test',
            'last_name': 'Student',
            'dni': '12345678',
            'address': 'Test Address',
            'academic_profile': 'student'
        })

        # Verify enrollment created with pending status
        enrollment = Enrollment.objects.get(user=self.user, course=self.course)
        self.assertEqual(enrollment.status, 'pending')

        # Should redirect to payment gateway
        self.assertRedirects(response, f'/enrollment/{enrollment.id}/payment/')

    def test_dashboard(self):
        self.client.login(username='teststudent', password='password')
        Enrollment.objects.create(user=self.user, course=self.course, status='approved')
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python 101')

    def test_lesson_access_denied_if_not_approved(self):
        self.client.login(username='teststudent', password='password')
        Enrollment.objects.create(user=self.user, course=self.course, status='pending')

        response = self.client.get(f'/lesson/{self.lesson.id}/')

        # Should redirect to dashboard
        self.assertRedirects(response, '/dashboard/')

    def test_lesson_access_allowed_if_approved(self):
        self.client.login(username='teststudent', password='password')
        Enrollment.objects.create(user=self.user, course=self.course, status='approved')
        response = self.client.get(f'/lesson/{self.lesson.id}/')
        self.assertEqual(response.status_code, 200)

    def test_admin_dashboard_access(self):
        # Student cannot access
        self.client.login(username='teststudent', password='password')
        response = self.client.get('/admin-dashboard/')
        self.assertEqual(response.status_code, 403)

        # Admin can access
        admin = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.client.login(username='admin', password='password')
        response = self.client.get('/admin-dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_teacher_content_management(self):
        self.client.login(username='testteacher', password='password')

        # Add module
        url = f'/teacher/course/{self.course.slug}/module/add/'
        response = self.client.post(url, {'title': 'New Module', 'order': 1})
        self.assertRedirects(response, f'/teacher/course/{self.course.slug}/content/')
        self.assertTrue(Module.objects.filter(title='New Module').exists())
