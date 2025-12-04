from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from ..models import Event, Ticket, ServiceRequest
import datetime

class EventTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            start_date=timezone.now() + datetime.timedelta(days=1),
            end_date=timezone.now() + datetime.timedelta(days=1, hours=2),
            location='Test Location',
            capacity=10,
            price=0
        )

    def test_enterprise_page_load(self):
        response = self.client.get(reverse('academy:enterprise_services'))
        self.assertEqual(response.status_code, 200)

    def test_service_request_submission(self):
        response = self.client.post(reverse('academy:enterprise_services'), {
            'company_name': 'Test Corp',
            'contact_name': 'John Doe',
            'email': 'john@example.com',
            'phone': '123456789',
            'message': 'We need help'
        })
        self.assertRedirects(response, reverse('academy:enterprise_services'))
        self.assertTrue(ServiceRequest.objects.filter(company_name='Test Corp').exists())

    def test_event_list_load(self):
        response = self.client.get(reverse('academy:event_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Event')

    def test_event_detail_load(self):
        response = self.client.get(reverse('academy:event_detail', kwargs={'slug': self.event.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Event')

    def test_event_registration(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('academy:event_register', kwargs={'pk': self.event.pk}))

        # Should redirect to ticket detail
        ticket = Ticket.objects.filter(user=self.user, event=self.event).first()
        self.assertIsNotNone(ticket)
        self.assertRedirects(response, reverse('academy:ticket_detail', kwargs={'ticket_id': ticket.id}))

    def test_ticket_detail_access(self):
        self.client.login(username='testuser', password='password')
        ticket = Ticket.objects.create(user=self.user, event=self.event)
        response = self.client.get(reverse('academy:ticket_detail', kwargs={'ticket_id': ticket.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(ticket.id))
