from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from academy.models import Course, Institution

class CourseLaunchTest(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(username='instructor', password='password')
        self.institution = Institution.objects.create(name="Test Inst")

    def test_is_upcoming_future_date(self):
        future_date = timezone.now() + timedelta(days=5)
        course = Course.objects.create(
            title="Future Course",
            instructor=self.instructor,
            institution=self.institution,
            launch_date=future_date,
            description="Test"
        )
        self.assertTrue(course.is_upcoming)

    def test_is_upcoming_past_date(self):
        past_date = timezone.now() - timedelta(days=1)
        course = Course.objects.create(
            title="Past Course",
            instructor=self.instructor,
            institution=self.institution,
            launch_date=past_date,
            description="Test"
        )
        self.assertFalse(course.is_upcoming)

    def test_is_upcoming_no_date(self):
        course = Course.objects.create(
            title="Immediate Course",
            instructor=self.instructor,
            institution=self.institution,
            description="Test"
        )
        self.assertFalse(course.is_upcoming)
