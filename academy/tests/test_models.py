from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from academy.models import Course, Enrollment, User, Profile, Installment

class CourseModelTests(TestCase):
    def test_slug_generation(self):
        instructor = User.objects.create(username='inst')
        course = Course.objects.create(title="My Course Title", description="desc", instructor=instructor)
        self.assertEqual(course.slug, "my-course-title")

        course2 = Course.objects.create(title="My Course Title", description="desc", instructor=instructor)
        self.assertEqual(course2.slug, "my-course-title-1")

    def test_discount_percent(self):
        instructor = User.objects.create(username='inst2')
        course = Course.objects.create(title="Sale Course", description="desc", instructor=instructor, price=50, old_price=100)
        self.assertEqual(course.discount_percent, 50)

        course.price = 100
        course.save()
        self.assertEqual(course.discount_percent, 0)

    def test_is_upcoming(self):
        instructor = User.objects.create(username='inst3')
        future = timezone.now() + timedelta(days=10)
        past = timezone.now() - timedelta(days=10)

        course = Course.objects.create(title="Upcoming", description="d", instructor=instructor, launch_date=future)
        self.assertTrue(course.is_upcoming)

        course.launch_date = past
        course.save()
        self.assertFalse(course.is_upcoming)

class EnrollmentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='student')
        self.instructor = User.objects.create(username='teacher')
        self.course = Course.objects.create(
            title="Monthly Course",
            description="d",
            instructor=self.instructor,
            allow_monthly_payment=True,
            monthly_price=100,
            duration_months=3
        )

    def test_generate_installments(self):
        enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course,
            status='approved',
            selected_payment_plan='monthly'
        )
        enrollment.generate_installments()

        self.assertEqual(enrollment.installments.count(), 3)
        # First installment should be approved immediately if enrollment is approved
        first = enrollment.installments.get(installment_number=1)
        self.assertEqual(first.status, 'approved')

        second = enrollment.installments.get(installment_number=2)
        self.assertEqual(second.status, 'pending')

    def test_is_up_to_date(self):
        enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course,
            status='approved',
            selected_payment_plan='monthly'
        )
        enrollment.generate_installments()

        # All good initially
        self.assertTrue(enrollment.is_up_to_date)

        # Make second installment overdue
        second = enrollment.installments.get(installment_number=2)
        second.due_date = timezone.now().date() - timedelta(days=1)
        second.save()

        self.assertFalse(enrollment.is_up_to_date)

        # Pay it
        second.status = 'approved'
        second.save()
        self.assertTrue(enrollment.is_up_to_date)
