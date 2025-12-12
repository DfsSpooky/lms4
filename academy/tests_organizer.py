from django.test import TestCase, Client
from django.contrib.auth.models import User
from academy.models import Event, Ticket, Profile
from django.utils import timezone
import json

class OrganizerCheckInTest(TestCase):
    def setUp(self):
        # Create organizer
        self.organizer = User.objects.create_user(username='organizer', password='password')
        # Profile is created automatically by signal, so we just update it
        self.organizer.profile.role = 'organizer'
        self.organizer.profile.save()

        # Create user/attendee
        self.attendee = User.objects.create_user(username='attendee', password='password')
        self.attendee.profile.role = 'student'
        self.attendee.profile.save()

        # Create Event
        self.event = Event.objects.create(
            title='Org Event',
            description='Desc',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(hours=2),
            organizer=self.organizer,
            price=0,
            capacity=100
        )

        self.client = Client()

    def test_checkin_flow(self):
        # 1. Create Ticket
        ticket = Ticket.objects.create(user=self.attendee, event=self.event, status='approved')

        # 2. Login as Organizer
        self.client.login(username='organizer', password='password')

        # 3. Check-in (Success)
        url = f'/organizer/event/{self.event.id}/checkin/'
        response = self.client.post(url, {'ticket_id': str(ticket.id)})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')

        ticket.refresh_from_db()
        self.assertTrue(ticket.is_used)

        # 4. Check-in Again (Duplicate Warning)
        response = self.client.post(url, {'ticket_id': str(ticket.id)})
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'warning')
        self.assertIn('YA FUE USADO', data['message'])

    def test_checkin_permissions(self):
        # Login as non-organizer (student)
        self.client.login(username='attendee', password='password')
        response = self.client.get(f'/organizer/event/{self.event.id}/checkin/')

        # Expect redirect or 403 (TeacherRequiredMixin redirects to dashboard)
        self.assertEqual(response.status_code, 302)

    def test_checkin_pending_ticket(self):
        ticket = Ticket.objects.create(user=self.attendee, event=self.event, status='pending')
        self.client.login(username='organizer', password='password')

        response = self.client.post(f'/organizer/event/{self.event.id}/checkin/', {'ticket_id': str(ticket.id)})
        data = json.loads(response.content)

        self.assertEqual(data['status'], 'error')
        self.assertIn('INVÁLIDO', data['message'])
