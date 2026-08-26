from django import forms
from .models import ContactSubmission

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = [
            'name',
            'email',
            'phone',
            'subject',
            'message',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.keys():
            self.fields[field].required = True
            if field == 'message':
                self.fields[field].widget.attrs.update({
                    'rows': 4, 'cols': 50
                })

            self.fields[field].widget.attrs.update({
                'class': 'form-control',
            })