from django.test import TestCase
from django.urls import reverse

from home.models import Gym, ContactSubmission
from home.forms import ContactForm
from django.contrib.auth.models import User

class ContactUsViewTest(TestCase):
    ''' test for contact us view'''
    @classmethod
    def setUpTestData(cls):
        cls.gym = Gym.objects.create(name='Test Gym',
                                     phone='1234567890',
                                     email='',
                                     description='Test Description',
                                     opening_hours='Test Opening Hours',
                                     address='Test Address'
                                     )
        cls.url = reverse('home:contact_us')

    def test_get_shows_form_and_gym(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/contact_us.html')
        self.assertIsInstance(response.context["form"], ContactForm)
        self.assertEqual(response.context["gym"], self.gym)

    def test_contact_form_submission(self):
        form_data = {
            'name': 'Test User',
            'email': 'johndoe16@gmail.com',
            'phone': '1234567890',
            'subject': 'Test Subject',
            'message': 'Test Message',

        }

        form = ContactForm(form_data)
        self.assertTrue(form.is_valid(), form.errors)
        contact = form.save()
        contact.refresh_from_db()

        self.assertEqual(ContactSubmission.objects.filter(pk=contact.pk).count(), 1)
        self.assertEqual(contact.name, form_data['name'])
        self.assertEqual(contact.email, form_data['email'])
        self.assertEqual(contact.phone, form_data['phone'])
        self.assertEqual(contact.subject, form_data['subject'])
        self.assertEqual(contact.message, form_data['message'])

