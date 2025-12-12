from django.test import TestCase, Client
from django.contrib.auth.models import User
from academy.models import Event, TicketTier, Ticket
from django.utils import timezone

class TicketTierTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tieruser', password='password')
        self.event = Event.objects.create(
            title='Tier Event',
            description='Desc',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(hours=2),
            price=0,
            capacity=100
        )
        # Create Tiers
        self.vip_tier = TicketTier.objects.create(event=self.event, name='VIP', price=100, capacity=10)
        self.general_tier = TicketTier.objects.create(event=self.event, name='General', price=50, capacity=50)

        self.client = Client()
        self.client.login(username='tieruser', password='password')

    def test_registration_with_tier(self):
        # Register for VIP
        response = self.client.post(f'/events/{self.event.id}/register/', {'tier_id': self.vip_tier.id})

        self.assertEqual(response.status_code, 302) # Redirect to payment

        ticket = Ticket.objects.last()
        self.assertEqual(ticket.tier, self.vip_tier)
        self.assertEqual(ticket.status, 'pending') # Because price > 0

    def test_registration_tier_sold_out(self):
        # Set capacity to 0
        self.vip_tier.capacity = 0
        self.vip_tier.save()

        response = self.client.post(f'/events/{self.event.id}/register/', {'tier_id': self.vip_tier.id})

        # Should redirect back to detail with error
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("agotado" in m.message for m in messages))

        self.assertEqual(Ticket.objects.count(), 0)
