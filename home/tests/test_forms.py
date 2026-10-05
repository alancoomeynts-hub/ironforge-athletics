from django.test import TestCase
from home.forms import ContactForm


class ContactFormTests(TestCase):
    def test_valid_data(self):
        """ Test that the form validates with valid data"""
        data = {
            "name": "Alan Coomey",
            "email": "alan@example.com",
            "phone": "0871234567",
            "subject": "Membership query",
            "message": "Hello, I have a question.",
        }
        form = ContactForm(data)
        assert form.is_valid()

    def test_required_fields(self):
        """ Test Invalid form submission when required fields are missing"""
        form = ContactForm({})
        assert not form.is_valid()

        for field in ["name", "email", "phone", "subject", "message"]:
            assert field in form.errors

    def test_widget_attrs(self):
        """ Test that the form widgets have the correct attributes"""
        form = ContactForm()

        for field_name in ["name", "email", "phone", "subject", "message"]:
            attrs = form.fields[field_name].widget.attrs
            assert "form-control" in attrs.get("class", "")
            assert "placeholder" in attrs

        message_attrs = form.fields["message"].widget.attrs
        assert message_attrs.get("rows") == 4
        assert message_attrs.get("cols") == 50