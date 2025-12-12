from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.utils import IntegrityError
from .models import Event, Ticket

class TicketModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.event = Event.objects.create(
            title='Test Event',
            description='Description',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(hours=2),
            location='Test Location',
            capacity=100,
            price=10.00
        )

    def test_multiple_tickets_allowed(self):
        """Test that multiple tickets for same user and event ARE allowed."""
        # Create first ticket
        Ticket.objects.create(user=self.user, event=self.event)

        # Create second ticket
        try:
            Ticket.objects.create(user=self.user, event=self.event)
        except IntegrityError:
            self.fail("IntegrityError raised but multiple tickets should be allowed.")

        # Verify count
        self.assertEqual(Ticket.objects.filter(user=self.user, event=self.event).count(), 2)
