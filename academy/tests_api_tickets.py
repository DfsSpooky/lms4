from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from academy.models import Event, Ticket
from django.utils import timezone

class ApiTicketTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.event = Event.objects.create(
            title='Test Event',
            description='Desc',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(hours=2),
            price=100, # Paid event
            capacity=100
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_register_paid_event_pending(self):
        """Registering for a paid event should return pending status."""
        response = self.client.post(f'/api/events/{self.event.id}/register/')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'pending')

        ticket_id = response.data['ticket_id']
        ticket = Ticket.objects.get(id=ticket_id)
        self.assertEqual(ticket.status, 'pending')

    def test_upload_voucher_via_api(self):
        """Test uploading a voucher via the new API endpoint."""
        # 1. Create pending ticket
        ticket = Ticket.objects.create(user=self.user, event=self.event, status='pending')

        # 2. Upload file
        import tempfile
        from django.core.files.uploadedfile import SimpleUploadedFile

        # Create a dummy image
        image = SimpleUploadedFile("voucher.jpg", b"file_content", content_type="image/jpeg")

        response = self.client.post(
            f'/api/events/{self.event.id}/upload-voucher/',
            {'ticket_id': str(ticket.id), 'file': image},
            format='multipart'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'uploaded')

        ticket.refresh_from_db()
        self.assertEqual(ticket.status, 'review')
        self.assertTrue(ticket.voucher_image)

    def test_upload_voucher_no_ticket(self):
        """Attempting to upload for non-existent ticket."""
        # Random UUID
        import uuid
        from django.core.files.uploadedfile import SimpleUploadedFile
        random_uuid = uuid.uuid4()
        image = SimpleUploadedFile("voucher.jpg", b"content", content_type="image/jpeg")

        response = self.client.post(
            f'/api/events/{self.event.id}/upload-voucher/',
            {'ticket_id': str(random_uuid), 'file': image},
            format='multipart'
        )
        self.assertEqual(response.status_code, 404)
