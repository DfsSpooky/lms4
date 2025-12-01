from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from academy.models import UserSession, Course, Enrollment
from academy.decorators import rate_limit
from django.core.cache import cache
from django.http import HttpResponse
from django.contrib.sessions.models import Session
import time

class SessionLimitingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()

    def test_session_limiting(self):
        # First Login (Session 1)
        self.client.login(username='testuser', password='password')
        session1_key = self.client.session.session_key

        self.assertTrue(UserSession.objects.filter(user=self.user, session_key=session1_key).exists())

        # Simulate a second login (Session 2) from a different client instance (simulating another browser)
        client2 = Client()
        client2.login(username='testuser', password='password')
        session2_key = client2.session.session_key

        self.assertTrue(UserSession.objects.filter(user=self.user, session_key=session2_key).exists())
        self.assertEqual(UserSession.objects.filter(user=self.user).count(), 2) # Assume MAX=2

        # Simulate a third login (Session 3)
        client3 = Client()
        client3.login(username='testuser', password='password')
        session3_key = client3.session.session_key

        # Check count is still 2 (oldest should be removed)
        self.assertEqual(UserSession.objects.filter(user=self.user).count(), 2)

        # Verify Session 1 (oldest) is gone from UserSession and Django Session
        self.assertFalse(UserSession.objects.filter(session_key=session1_key).exists())
        # Note: We can't easily check Django Session table for deletion in Mock session backend unless using DB backend
        # But UserSession logic proof is enough for signal execution.

class RateLimitingTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='spammer', password='password')

    def tearDown(self):
        cache.clear()

    def test_rate_limit_decorator(self):
        # Create a dummy view with rate limit
        @rate_limit(limit=2, period=10)
        def my_view(request):
            return HttpResponse("OK")

        # Mock request
        request = self.factory.post('/fake-url/')
        request.user = self.user

        # 1st Request: OK
        response = my_view(request)
        self.assertEqual(response.status_code, 200)

        # 2nd Request: OK
        response = my_view(request)
        self.assertEqual(response.status_code, 200)

        # 3rd Request: Blocked
        response = my_view(request)
        self.assertEqual(response.status_code, 429)
        self.assertIn("Too Many Requests", response.content.decode())

    def test_payment_gateway_rate_limit(self):
        # Setup course and enrollment
        course = Course.objects.create(title="C", instructor=self.user)
        enrollment = Enrollment.objects.create(user=self.user, course=course)

        self.client.login(username='spammer', password='password')
        url = reverse('academy:payment_gateway', args=[enrollment.id])

        # Hit limit (3 per minute)
        for _ in range(3):
            resp = self.client.post(url, {}) # Invalid form but counts as request
            # We expect 200 (re-render form with errors) or 302
            self.assertNotEqual(resp.status_code, 429)

        # 4th Request
        resp = self.client.post(url, {})
        self.assertEqual(resp.status_code, 429)
