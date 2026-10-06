from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render

from shop.models import Product
from membership.models import Membership
from community.models import Post


from .forms import ContactForm
from .models import Gym


class ContactUsView(FormMixin, DetailView):
    model = Gym
    template_name = "home/contact_us.html"
    form_class = ContactForm
    context_object_name = "gym"
    success_url = "/"

    def get_object(self, queryset=None):
        return Gym.objects.first()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.form_valid(self.get_form())

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your message has been sent successfully!")
        return super().form_valid(form)


def search_results(request):
    page = (request.GET.get("page", "shop") or "").lower()
    query = request.GET.get("q", "").strip()

    results = []
    result_type = ""

    if page == "shop":
        results = Product.objects.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )
        result_type = "Shop Products"

    elif page == "members":
        results = Membership.objects.filter(
            Q(user__username__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
        )
        result_type = "Members"

    elif page == "community":
        results = Post.objects.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(author__username__icontains=query)
            | Q(author__first_name__icontains=query)
            | Q(author__last_name__icontains=query),
            status=Post.Status.PUBLISHED,
        )
        result_type = "Community Posts"

    return render(
        request,
        "home/search_results.html",
        {
            "results": results,
            "result_type": result_type,
            "page": page,
            "query": query,
        },
    )
