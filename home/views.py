
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin

from .forms import ContactForm
from .models import Gym

class ContactUsView(FormMixin,DetailView):
    model = Gym
    template_name = 'home/contact_us.html'
    form_class = ContactForm
    context_object_name = 'gym'

    def get_object(self, queryset=None):
        return Gym.objects.first()