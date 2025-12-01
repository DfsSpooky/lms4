from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from academy.models import HeroSlide, Profile

class AdminDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.client.login(username='admin', password='password')

    def test_admin_dashboard_view(self):
        response = self.client.get(reverse('academy:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('pending_enrollments', response.context)
        self.assertIn('history_enrollments', response.context)
        self.assertIn('hero_slides', response.context)

    def test_admin_user_creation(self):
        url = reverse('academy:admin_user_add')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword',
            'role': 'teacher',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) # Redirects to dashboard

        new_user = User.objects.get(username='newuser')
        self.assertTrue(new_user.check_password('newpassword'))
        self.assertEqual(new_user.profile.role, 'teacher')

    def test_hero_slide_crud(self):
        # Create
        url_add = reverse('academy:hero_slide_add')
        data = {
            'title': 'Slide 1',
            'description': 'Desc 1',
            'style': 'promo',
            'order': 1,
            'is_active': True,
            'btn1_text': 'Btn 1', # Required field in model defaults but checked by form
            'btn1_url': '#'
        }
        response = self.client.post(url_add, data)
        if response.status_code != 302:
             print(response.content.decode()) # Debug if fails
        self.assertEqual(response.status_code, 302)
        self.assertEqual(HeroSlide.objects.count(), 1)
        slide = HeroSlide.objects.first()

        # Update
        url_edit = reverse('academy:hero_slide_edit', args=[slide.id])
        data['title'] = 'Slide Updated'
        response = self.client.post(url_edit, data)
        self.assertEqual(response.status_code, 302)
        slide.refresh_from_db()
        self.assertEqual(slide.title, 'Slide Updated')

        # Delete (via dashboard post action)
        url_dashboard = reverse('academy:admin_dashboard')
        response = self.client.post(url_dashboard, {'slide_id': slide.id, 'action': 'delete'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(HeroSlide.objects.count(), 0)
