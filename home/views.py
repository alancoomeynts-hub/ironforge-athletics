
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin

from .forms import ContactForm
from .models import Gym

class ContactUsView(FormMixin,DetailView):
    model = Gym
    template_name = 'home/contact_us.html'
    form_class = ContactForm
    context_object_name = 'gym'
    success_url = '/'

    def get_object(self, queryset=None):
        return Gym.objects.first()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.form_valid(self.get_form())

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)