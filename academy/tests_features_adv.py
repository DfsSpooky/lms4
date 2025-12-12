from django.test import TestCase, Client
from django.contrib.auth.models import User
from academy.models import Event, Ticket
from django.utils import timezone

class TicketAssignmentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='assignuser', password='password')
        self.event = Event.objects.create(
            title='Assign Event',
            description='Desc',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(hours=2),
            price=0,
            capacity=100
        )
        self.ticket = Ticket.objects.create(user=self.user, event=self.event, status='approved')
        self.client = Client()
        self.client.login(username='assignuser', password='password')

    def test_assign_attendee(self):
        # Update details
        response = self.client.post(f'/ticket/{self.ticket.id}/assign/', {
            'attendee_first_name': 'Juan',
            'attendee_last_name': 'Perez',
            'attendee_email': 'juan@example.com'
        })

        self.assertEqual(response.status_code, 302)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.attendee_first_name, 'Juan')
        self.assertEqual(self.ticket.attendee_email, 'juan@example.com')

    def test_assign_block_if_used(self):
        # Set ticket as used
        self.ticket.is_used = True
        self.ticket.save()

        # Attempt update
        response = self.client.post(f'/ticket/{self.ticket.id}/assign/', {
            'attendee_first_name': 'New',
        })

        # Should redirect with error (not updated)
        self.assertEqual(response.status_code, 302)
        self.ticket.refresh_from_db()
        self.assertNotEqual(self.ticket.attendee_first_name, 'New')

class CertificateTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='certuser', password='password')
        self.event = Event.objects.create(
            title='Cert Event',
            description='Desc',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(hours=2),
            price=0,
            capacity=100
        )
        self.ticket = Ticket.objects.create(user=self.user, event=self.event, status='approved')
        self.client = Client()
        self.client.login(username='certuser', password='password')

    def test_download_cert_if_used(self):
        self.ticket.is_used = True
        self.ticket.save()

        response = self.client.get(f'/ticket/{self.ticket.id}/certificate/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_download_cert_block_if_unused(self):
        response = self.client.get(f'/ticket/{self.ticket.id}/certificate/')
        # Redirects or error
        self.assertEqual(response.status_code, 302)
