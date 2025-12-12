from django.test import TestCase, Client
from django.contrib.auth.models import User
from academy.models import Event, Ticket
from django.utils import timezone

class CalendarTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='caluser', password='password')
        self.event = Event.objects.create(
            title='Cal Event',
            description='Desc',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(hours=2),
            price=0,
            capacity=100
        )
        self.ticket = Ticket.objects.create(user=self.user, event=self.event, status='approved')
        self.client = Client()
        self.client.login(username='caluser', password='password')

    def test_download_ics(self):
        response = self.client.get(f'/ticket/{self.ticket.id}/ics/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/calendar')
        self.assertIn('BEGIN:VCALENDAR', response.content.decode())
        self.assertIn('SUMMARY:Cal Event', response.content.decode())
