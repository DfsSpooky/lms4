from django.test import TestCase, Client
from django.contrib.auth.models import User
from academy.models import Event, Profile
from django.utils import timezone

class OrganizerIsolationTest(TestCase):
    def setUp(self):
        # Create Organizer A
        self.user_a = User.objects.create_user(username='org_a', password='password')
        Profile.objects.filter(user=self.user_a).update(role='organizer')

        # Create Organizer B
        self.user_b = User.objects.create_user(username='org_b', password='password')
        Profile.objects.filter(user=self.user_b).update(role='organizer')

        # Event for A
        self.event_a = Event.objects.create(
            title='Event A',
            organizer=self.user_a,
            start_date=timezone.now(),
            end_date=timezone.now(),
            location='Loc A',
            description='Desc A'
        )

        # Event for B
        self.event_b = Event.objects.create(
            title='Event B',
            organizer=self.user_b,
            start_date=timezone.now(),
            end_date=timezone.now(),
            location='Loc B',
            description='Desc B'
        )

        self.client = Client()

    def test_dashboard_isolation(self):
        """User A should only see Event A in dashboard"""
        self.client.login(username='org_a', password='password')
        response = self.client.get('/organizer/dashboard/', follow=True) # follow redirect
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Event A')
        self.assertNotContains(response, 'Event B')

    def test_edit_isolation(self):
        """User A should NOT be able to access edit page of Event B"""
        self.client.login(username='org_a', password='password')
        response = self.client.get(f'/organizer/event/{self.event_b.pk}/edit/', follow=True)
        self.assertEqual(response.status_code, 404)

    def test_detail_isolation(self):
        """User A should NOT be able to view details (attendees) of Event B"""
        self.client.login(username='org_a', password='password')
        response = self.client.get(f'/organizer/event/{self.event_b.pk}/detail/', follow=True)
        self.assertEqual(response.status_code, 404)
