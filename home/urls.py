from django.urls import path
from django.views.generic import TemplateView, DetailView

from home.views import ContactUsView

app_name = 'home'

urlpatterns = [
    path('', TemplateView.as_view(template_name="home/index.html"),name='home'),
    path('about/', TemplateView.as_view(template_name="home/about.html"),name='about'),
    path('contact_us/', ContactUsView.as_view(template_name="home/contact_us.html"),name='contact_us')
]
