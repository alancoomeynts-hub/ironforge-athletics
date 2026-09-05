from django.contrib.auth import get_user_model
from django import forms
from .models import Profile
from allauth.account.forms import SignupForm, LoginForm

class CustomSignupForm(SignupForm):
    first_name=forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder':'Enter your first name',}))
    last_name=forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder':'Enter your last name',}))
    phone=forms.CharField(max_length=15, widget=forms.TextInput(attrs={'placeholder':'Enter your phone number',}))

    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)

        for field in self.fields:
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

        for field in self.fields:
            if field != 'remember':
                self.fields[field].widget.attrs.update({
                    'class': 'form-control',
                })

class UserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["username",
                  "first_name",
                  "last_name",
                  "email"
                  ]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Enter your username","class": "form-control"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Enter your first name","class": "form-control"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Enter your last name","class": "form-control"}),
            "email": forms.EmailInput(attrs={"placeholder": "Enter your email","class": "form-control"}),
        }

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "profile_image",
            "bio",
            "goals",
            "date_of_birth",
            "height",
            "weight",
            "default_phone_number",
            "default_street_address1",
            "default_street_address2",
            "default_town_or_city",
            "default_county",
            "default_postcode",
        ]
        widgets = {
            "profile_image": forms.FileInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"placeholder": "Enter your bio","class": "form-control",'rows': 4, 'cols': 50,}),
            "goals": forms.Textarea(attrs={"placeholder": "Enter your goals","class": "form-control",'rows': 4, 'cols': 50,}),
            "date_of_birth": forms.DateInput(attrs={"type": "date","class": "form-control"}),
            "height": forms.NumberInput(attrs={"placeholder": "Enter your height","class": "form-control",}),
            "weight": forms.NumberInput(attrs={"placeholder": "Enter your weight","class": "form-control",}),
            "default_phone_number": forms.TextInput(attrs={"placeholder": "Enter your phone number","class": "form-control"}),
            "default_street_address1": forms.TextInput(attrs={"placeholder": "Enter your street address","class": "form-control"}),
            "default_street_address2": forms.TextInput(attrs={"placeholder": "Enter your street address","class": "form-control"}),
            "default_town_or_city": forms.TextInput(attrs={"placeholder": "Enter your town or city","class": "form-control"}),
            "default_county": forms.TextInput(attrs={"placeholder": "Enter your county","class": "form-control"}),
            "default_postcode": forms.TextInput(attrs={"placeholder": "Enter your postcode","class": "form-control"}),

        }

