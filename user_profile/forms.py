from django import forms
from .models import Profile
from allauth.account.forms import SignupForm, LoginForm

class CustomSignupForm(SignupForm):
    first_name=forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder':'Enter your first name',}))
    last_name=forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder':'Enter your last name',}))
    phone=forms.CharField(max_length=15, widget=forms.TextInput(attrs={'placeholder':'Enter your phone number',}))

    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)

        for field in self.fields.keys():
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
            })


    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        profile, _ = Profile.objects.get_or_create(user=user)
        profile.default_phone_number = self.cleaned_data.get('phone','')
        profile.save()

class CustomLoginForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)

        for field in self.fields.keys():
            if field != 'remember':
                self.fields[field].widget.attrs.update({
                    'class': 'form-control',
                })